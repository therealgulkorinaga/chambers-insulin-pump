"""World Classifier — assigns each data item to exactly one Typed World."""

from __future__ import annotations

import os
from typing import Any

import yaml

from ..audit import AuditLogger
from ..clock import SimulationClock
from ..models import BurnState, DataItem, DataType, World
from .worlds import WorldStoreManager


# Default classification policy
DEFAULT_POLICY: dict[str, str] = {
    "glucose_reading": "clinical_review",
    "insulin_basal": "clinical_review",
    "insulin_bolus": "clinical_review",
    "insulin_temp_basal": "clinical_review",
    "aid_prediction": "research",
    "aid_adjustment": "clinical_review",
    "aid_mode_change": "clinical_review",
    "aid_iob": "clinical_review",
    "sensor_metadata": "device_maintenance",
    "pump_metadata": "device_maintenance",
    "pen_injection": "clinical_review",
    "alarm": "clinical_review",
    "meal_log": "clinical_review",
    "exercise_log": "clinical_review",
    "agp_report": "patient",
    "clinical_summary": "patient",
}


class WorldClassifier:
    """Classifies incoming data items into Typed Worlds based on policy."""

    def __init__(
        self,
        stores: WorldStoreManager,
        audit: AuditLogger,
        clock: SimulationClock,
        policy_path: str | None = None,
    ):
        self.stores = stores
        self.audit = audit
        self.clock = clock
        self._policy = dict(DEFAULT_POLICY)
        self._policy_path = policy_path
        self._policy_mtime: float = 0.0
        if policy_path:
            self._load_policy(policy_path)

    def _load_policy(self, path: str) -> None:
        if not os.path.exists(path):
            return
        mtime = os.path.getmtime(path)
        if mtime != self._policy_mtime:
            with open(path) as f:
                loaded = yaml.safe_load(f)
            if isinstance(loaded, dict):
                self._policy.update(loaded)
            self._policy_mtime = mtime

    def _hot_reload(self) -> None:
        if self._policy_path:
            self._load_policy(self._policy_path)

    def classify(self, item: DataItem) -> World:
        """Classify a single data item."""
        dt_key = item.data_type.value
        world_str = self._policy.get(dt_key)
        world = World(world_str) if world_str else World.CLINICAL_REVIEW

        item.world = world
        item.burn_state = BurnState.CLASSIFIED
        item.classified_at = self.clock.now
        self.stores[world].insert(item)
        return world

    def classify_batch(self, items: list[DataItem]) -> None:
        """Classify a batch of items efficiently."""
        self._hot_reload()
        t = self.clock.now
        batches: dict[World, list[DataItem]] = {}

        for item in items:
            dt_key = item.data_type.value
            world_str = self._policy.get(dt_key)
            world = World(world_str) if world_str else World.CLINICAL_REVIEW
            item.world = world
            item.burn_state = BurnState.CLASSIFIED
            item.classified_at = t
            batches.setdefault(world, []).append(item)

        for world, batch in batches.items():
            self.stores[world].insert_batch(batch)
            self.stores[world].commit()

        # Single audit entry for the batch
        if items:
            self.audit.log(
                "classified_batch",
                patient_id=items[0].patient_id,
                details={"count": len(items), "worlds": {w.value: len(b) for w, b in batches.items()}},
                sim_time=t,
            )
