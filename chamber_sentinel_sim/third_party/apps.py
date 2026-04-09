"""Simulated third-party app stubs with burn-propagation endpoints."""

from __future__ import annotations

import json
import os
import sqlite3
from typing import Any

from ..audit import AuditLogger
from ..clock import SimulationClock
from ..config import ThirdPartyAppConfig
from ..models import DataItem


_APP_SCHEMA = """
CREATE TABLE IF NOT EXISTS data (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    data_type TEXT NOT NULL,
    timestamp REAL NOT NULL,
    value TEXT NOT NULL,
    received_at REAL
);
"""


class ThirdPartyApp:
    """Simulated third-party app with configurable burn compliance."""

    def __init__(self, config: ThirdPartyAppConfig, base_dir: str, audit: AuditLogger, clock: SimulationClock):
        self.config = config
        self.name = config.name
        self.app_type = config.app_type
        self.compliance = config.compliance
        self.delay_minutes = config.delay_minutes
        self.audit = audit
        self.clock = clock

        app_dir = os.path.join(base_dir, self.name)
        os.makedirs(app_dir, exist_ok=True)
        self._db_path = os.path.join(app_dir, f"{self.name}.db")
        self._conn = sqlite3.connect(self._db_path)
        self._conn.executescript(_APP_SCHEMA)

        # Sub-processor (4th party) for App A
        self.sub_processor: ThirdPartyApp | None = None
        if config.has_sub_processor:
            sub_config = ThirdPartyAppConfig(
                name=f"{self.name}_sub",
                app_type="sub_processor",
                port=config.port + 100,
                compliance=config.compliance,
            )
            self.sub_processor = ThirdPartyApp(sub_config, base_dir, audit, clock)

        self._pending_burns: list[tuple[float, str]] = []  # (deadline, patient_id)

    def receive_data(self, items: list[DataItem]) -> int:
        """Receive data items from manufacturer relay API."""
        count = 0
        for item in items:
            self._conn.execute(
                "INSERT OR REPLACE INTO data (id, patient_id, data_type, timestamp, value, received_at) "
                "VALUES (?,?,?,?,?,?)",
                (item.id, item.patient_id, item.data_type.value, item.timestamp,
                 json.dumps(item.value), self.clock.now),
            )
            count += 1
            # Re-share to sub-processor
            if self.sub_processor:
                self.sub_processor.receive_data([item])
        self._conn.commit()
        self.audit.log(
            "third_party_data_received",
            patient_id=items[0].patient_id if items else "",
            details={"app": self.name, "item_count": count},
            sim_time=self.clock.now,
        )
        return count

    def request_burn(self, patient_id: str, deadline_minutes: float) -> str:
        """Receive burn-propagation signal. Returns acknowledgement status."""
        self.audit.log(
            "burn_propagation_received",
            patient_id=patient_id,
            details={"app": self.name, "compliance": self.compliance, "deadline": deadline_minutes},
            sim_time=self.clock.now,
        )

        if self.compliance == "non_compliant":
            self.audit.log(
                "burn_propagation_refused",
                patient_id=patient_id,
                details={"app": self.name, "reason": "non_compliant"},
                sim_time=self.clock.now,
            )
            return "refused"

        if self.compliance == "delayed":
            self._pending_burns.append((self.clock.now + self.delay_minutes, patient_id))
            return "acknowledged_delayed"

        # Compliant: burn immediately
        self._execute_burn(patient_id)
        return "confirmed"

    def _execute_burn(self, patient_id: str) -> int:
        cur = self._conn.execute("DELETE FROM data WHERE patient_id=?", (patient_id,))
        self._conn.commit()
        count = cur.rowcount

        self.audit.log(
            "third_party_burn_executed",
            patient_id=patient_id,
            details={"app": self.name, "items_burned": count},
            sim_time=self.clock.now,
        )

        # Propagate to sub-processor
        if self.sub_processor:
            self.sub_processor.request_burn(patient_id, 72 * 60)

        return count

    def tick(self) -> None:
        """Process pending delayed burns."""
        t = self.clock.now
        remaining = []
        for deadline, patient_id in self._pending_burns:
            if t >= deadline:
                self._execute_burn(patient_id)
            else:
                remaining.append((deadline, patient_id))
        self._pending_burns = remaining

    def count(self, patient_id: str | None = None) -> int:
        if patient_id:
            row = self._conn.execute("SELECT COUNT(*) FROM data WHERE patient_id=?", (patient_id,)).fetchone()
        else:
            row = self._conn.execute("SELECT COUNT(*) FROM data").fetchone()
        return row[0] if row else 0

    def close(self) -> None:
        self._conn.close()
        if self.sub_processor:
            self.sub_processor.close()


class ThirdPartyManager:
    """Manages all simulated third-party apps."""

    def __init__(self, configs: list[ThirdPartyAppConfig], base_dir: str, audit: AuditLogger, clock: SimulationClock):
        self.apps: dict[str, ThirdPartyApp] = {}
        tp_dir = os.path.join(base_dir, "third_party")
        os.makedirs(tp_dir, exist_ok=True)
        for cfg in configs:
            self.apps[cfg.name] = ThirdPartyApp(cfg, tp_dir, audit, clock)

    def share_data(self, app_name: str, items: list[DataItem]) -> int:
        app = self.apps.get(app_name)
        if app:
            return app.receive_data(items)
        return 0

    def propagate_burn(self, patient_id: str, deadline_minutes: float = 72 * 60) -> dict[str, str]:
        """Send burn-propagation signal to all apps. Returns {app_name: status}."""
        results = {}
        for name, app in self.apps.items():
            results[name] = app.request_burn(patient_id, deadline_minutes)
        return results

    def tick(self) -> None:
        for app in self.apps.values():
            app.tick()

    def close_all(self) -> None:
        for app in self.apps.values():
            app.close()
