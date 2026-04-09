"""Burn executor — performs actual data destruction and verification."""

from __future__ import annotations

from ..audit import AuditLogger
from ..clock import SimulationClock
from ..models import BurnState, World
from .worlds import WorldStoreManager


class BurnExecutor:
    """Executes burn operations: deletes data from world stores and verifies."""

    def __init__(self, stores: WorldStoreManager, audit: AuditLogger, clock: SimulationClock):
        self.stores = stores
        self.audit = audit
        self.clock = clock
        self._max_retries = 3
        self._retry_counts: dict[str, int] = {}
        self.stats = {"executed": 0, "verified": 0, "failed": 0}

    def execute_burns(self, eligible: list[tuple[str, World]]) -> list[tuple[str, bool]]:
        """Execute burns for eligible items. Returns list of (item_id, success)."""
        results: list[tuple[str, bool]] = []
        burned_count = 0
        failed_count = 0

        for item_id, world in eligible:
            store = self.stores[world]
            item = store.get(item_id)
            if item is None:
                results.append((item_id, True))
                continue
            if item.burn_state != BurnState.BURN_ELIGIBLE:
                continue

            store.update_burn_state(item_id, BurnState.BURN_EXECUTING)
            deleted = store.delete(item_id)
            verification = store.get(item_id)
            verified = verification is None and deleted

            if verified:
                self.stats["executed"] += 1
                self.stats["verified"] += 1
                self._retry_counts.pop(item_id, None)
                burned_count += 1
                results.append((item_id, True))
            else:
                retries = self._retry_counts.get(item_id, 0) + 1
                self._retry_counts[item_id] = retries
                if retries >= self._max_retries:
                    self.stats["failed"] += 1
                    failed_count += 1
                    results.append((item_id, False))
                else:
                    store.update_burn_state(item_id, BurnState.BURN_ELIGIBLE)
                    results.append((item_id, False))

        if burned_count > 0 or failed_count > 0:
            self.audit.log(
                "burn_complete",
                details={"burned": burned_count, "failed": failed_count, "mechanism": "delete"},
                sim_time=self.clock.now,
            )

        return results
