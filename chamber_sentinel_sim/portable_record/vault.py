"""Simulated portable record — encrypted patient-controlled data vault."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from typing import Any

from ..audit import AuditLogger
from ..clock import SimulationClock
from ..models import DataItem, DataType

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    _HAS_CRYPTO = True
except ImportError:
    _HAS_CRYPTO = False


class PortableRecord:
    """Encrypted local patient data vault.

    Stores data in an encrypted SQLite database. Sends delivery confirmations
    back to the manufacturer relay to trigger burn eligibility.
    """

    def __init__(self, patient_id: str, base_dir: str, audit: AuditLogger, clock: SimulationClock):
        self.patient_id = patient_id
        self.audit = audit
        self.clock = clock
        self._dir = os.path.join(base_dir, "portable_record", patient_id)
        os.makedirs(self._dir, exist_ok=True)
        self._db_path = os.path.join(self._dir, "vault.db")
        self._available = True

        # Encryption key (in real system, patient-held; here, generated per patient)
        if _HAS_CRYPTO:
            self._key = AESGCM.generate_key(bit_length=256)
        else:
            self._key = os.urandom(32)

        self._conn = sqlite3.connect(self._db_path)
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                data_type TEXT NOT NULL,
                timestamp REAL NOT NULL,
                value_enc BLOB NOT NULL,
                source_device TEXT,
                received_at REAL
            );
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                report_type TEXT NOT NULL,
                timestamp REAL NOT NULL,
                value TEXT NOT NULL,
                received_at REAL
            );
            CREATE INDEX IF NOT EXISTS idx_ts ON items(timestamp);
        """)

    @property
    def available(self) -> bool:
        return self._available

    def simulate_loss(self) -> None:
        """Simulate portable record loss (device destroyed)."""
        self._available = False
        self._conn.close()

    def simulate_recovery(self) -> None:
        """Simulate creating a new portable record after loss."""
        self._available = True
        self._conn = sqlite3.connect(self._db_path)

    def receive_items(self, items: list[DataItem]) -> tuple[list[str], str]:
        """Receive data items. Returns (list of received item_ids, confirmation_hash)."""
        if not self._available:
            return [], ""

        received_ids: list[str] = []
        hash_input = b""

        for item in items:
            raw = json.dumps(item.value).encode()
            if _HAS_CRYPTO:
                nonce = os.urandom(12)
                aesgcm = AESGCM(self._key)
                encrypted = nonce + aesgcm.encrypt(nonce, raw, None)
            else:
                encrypted = raw  # fallback: no encryption if library unavailable

            self._conn.execute(
                "INSERT OR REPLACE INTO items (id, data_type, timestamp, value_enc, source_device, received_at) "
                "VALUES (?,?,?,?,?,?)",
                (item.id, item.data_type.value, item.timestamp, encrypted,
                 item.source_device, self.clock.now),
            )
            received_ids.append(item.id)
            hash_input += item.id.encode()

        self._conn.commit()

        confirmation_hash = hashlib.sha256(hash_input + self.patient_id.encode()).hexdigest()

        self.audit.log(
            "portable_record_received",
            patient_id=self.patient_id,
            details={"item_count": len(received_ids), "confirmation_hash": confirmation_hash[:16]},
            sim_time=self.clock.now,
        )
        return received_ids, confirmation_hash

    def receive_report(self, report: DataItem) -> str:
        """Receive a clinical report. Returns confirmation hash."""
        if not self._available:
            return ""

        self._conn.execute(
            "INSERT OR REPLACE INTO reports (id, report_type, timestamp, value, received_at) VALUES (?,?,?,?,?)",
            (report.id, report.data_type.value, report.timestamp,
             json.dumps(report.value), self.clock.now),
        )
        self._conn.commit()

        confirmation = hashlib.sha256(
            (report.id + self.patient_id).encode()
        ).hexdigest()

        self.audit.log(
            "portable_record_report_received",
            item_id=report.id,
            patient_id=self.patient_id,
            details={"report_type": report.value.get("report_type", "unknown")},
            sim_time=self.clock.now,
        )
        return confirmation

    def count_items(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) FROM items").fetchone()
        return row[0] if row else 0

    def count_reports(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) FROM reports").fetchone()
        return row[0] if row else 0

    def patient_burn(self, item_ids: list[str] | None = None) -> int:
        """Patient-initiated selective burn. Returns count burned."""
        if item_ids:
            count = 0
            for iid in item_ids:
                cur = self._conn.execute("DELETE FROM items WHERE id=?", (iid,))
                count += cur.rowcount
        else:
            cur = self._conn.execute("DELETE FROM items")
            count = cur.rowcount
        self._conn.commit()
        self.audit.log(
            "patient_burn",
            patient_id=self.patient_id,
            details={"items_burned": count, "selective": item_ids is not None},
            sim_time=self.clock.now,
        )
        return count

    def close(self) -> None:
        if self._available:
            self._conn.close()


class VaultManager:
    """Manages portable records for all patients."""

    def __init__(self, base_dir: str, audit: AuditLogger, clock: SimulationClock):
        self.base_dir = base_dir
        self.audit = audit
        self.clock = clock
        self.vaults: dict[str, PortableRecord] = {}

    def get_or_create(self, patient_id: str) -> PortableRecord:
        if patient_id not in self.vaults:
            self.vaults[patient_id] = PortableRecord(patient_id, self.base_dir, self.audit, self.clock)
        return self.vaults[patient_id]

    def close_all(self) -> None:
        for v in self.vaults.values():
            v.close()
