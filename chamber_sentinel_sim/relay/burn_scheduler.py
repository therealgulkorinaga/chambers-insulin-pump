"""Burn scheduler — tracks data item lifecycle and burn eligibility."""

from __future__ import annotations

from typing import Any

from ..audit import AuditLogger
from ..clock import SimulationClock
from ..models import BurnScheduleConfig, BurnState, DataType, World
from .worlds import WorldStoreManager


# Which burn states are eligible for transition to BURN_ELIGIBLE
_ELIGIBLE_FROM = {BurnState.DELIVERY_CONFIRMED, BurnState.CLASSIFIED}


class BurnScheduler:
    """Tracks every data item's lifecycle and determines burn eligibility."""

    def __init__(
        self,
        stores: WorldStoreManager,
        audit: AuditLogger,
        clock: SimulationClock,
        config: BurnScheduleConfig,
    ):
        self.stores = stores
        self.audit = audit
        self.clock = clock
        self.config = config
        self._holds: dict[str, set[str]] = {}  # patient_id -> set of held item_ids

    def _burn_window(self, world: World) -> float:
        """Get burn window in minutes for a world."""
        return {
            World.CLINICAL_REVIEW: self.config.clinical_review_minutes,
            World.DEVICE_MAINTENANCE: self.config.device_maintenance_minutes,
            World.RESEARCH: self.config.research_minutes,
            World.THIRD_PARTY: self.config.third_party_sla_minutes,
        }.get(world, self.config.clinical_review_minutes)

    def place_hold(self, patient_id: str, item_ids: list[str] | None = None) -> None:
        """Place a legal hold. If item_ids is None, hold all items for patient."""
        if patient_id not in self._holds:
            self._holds[patient_id] = set()
        if item_ids:
            self._holds[patient_id].update(item_ids)
        else:
            # Hold all current items
            for world in (World.CLINICAL_REVIEW, World.DEVICE_MAINTENANCE, World.RESEARCH, World.THIRD_PARTY):
                for item in self.stores[world].query(patient_id=patient_id):
                    self._holds[patient_id].add(item.id)
                    self.stores[world].update_burn_state(item.id, BurnState.HELD, held=1)
        self.audit.log(
            "legal_hold_placed",
            patient_id=patient_id,
            details={"item_count": len(self._holds.get(patient_id, set()))},
            sim_time=self.clock.now,
        )

    def lift_hold(self, patient_id: str) -> None:
        """Lift legal hold for a patient."""
        held = self._holds.pop(patient_id, set())
        for world in (World.CLINICAL_REVIEW, World.DEVICE_MAINTENANCE, World.RESEARCH, World.THIRD_PARTY):
            for item in self.stores[world].query(patient_id=patient_id, burn_state=BurnState.HELD):
                if item.id in held:
                    self.stores[world].update_burn_state(item.id, BurnState.CLASSIFIED, held=0)
        self.audit.log(
            "legal_hold_lifted",
            patient_id=patient_id,
            details={"items_released": len(held)},
            sim_time=self.clock.now,
        )

    def _is_held(self, patient_id: str, item_id: str) -> bool:
        return item_id in self._holds.get(patient_id, set())

    def tick(self) -> list[tuple[str, World]]:
        """Check all worlds for burn-eligible items. Returns list of (item_id, world)."""
        eligible: list[tuple[str, World]] = []
        t = self.clock.now

        for world in (World.CLINICAL_REVIEW, World.DEVICE_MAINTENANCE, World.RESEARCH, World.THIRD_PARTY):
            window = self._burn_window(world)
            store = self.stores[world]

            # Find items that are classified/confirmed and past their burn window
            for state in _ELIGIBLE_FROM:
                items = store.query(burn_state=state)
                for item in items:
                    if self._is_held(item.patient_id, item.id):
                        continue
                    age = t - (item.classified_at or item.created_at)
                    if age >= window:
                        # For clinical review, require delivery confirmation
                        if world == World.CLINICAL_REVIEW and item.burn_state != BurnState.DELIVERY_CONFIRMED:
                            # Mark as delivery pending if not yet confirmed
                            if item.burn_state == BurnState.CLASSIFIED:
                                store.update_burn_state(item.id, BurnState.DELIVERY_PENDING)
                            continue

                        store.update_burn_state(
                            item.id,
                            BurnState.BURN_ELIGIBLE,
                            burn_eligible_at=t,
                        )
                        eligible.append((item.id, world))

        if eligible:
            self.audit.log(
                "burn_eligible_batch",
                details={"count": len(eligible)},
                sim_time=t,
            )
        return eligible

    def mark_delivered(self, patient_id: str, item_ids: list[str] | None = None) -> int:
        """Mark items as delivered to portable record. Returns count."""
        t = self.clock.now
        count = 0
        for world in (World.CLINICAL_REVIEW, World.DEVICE_MAINTENANCE, World.RESEARCH):
            items = self.stores[world].query(patient_id=patient_id)
            for item in items:
                if item_ids and item.id not in item_ids:
                    continue
                if item.burn_state in (BurnState.CLASSIFIED, BurnState.DELIVERY_PENDING):
                    self.stores[world].update_burn_state(
                        item.id, BurnState.DELIVERY_CONFIRMED, delivered_at=t
                    )
                    count += 1
        return count

    def get_pending_burns(self) -> list[tuple[str, World]]:
        """Get all items in BURN_ELIGIBLE state."""
        result = []
        for world in (World.CLINICAL_REVIEW, World.DEVICE_MAINTENANCE, World.RESEARCH, World.THIRD_PARTY):
            items = self.stores[world].query(burn_state=BurnState.BURN_ELIGIBLE)
            for item in items:
                result.append((item.id, world))
        return result

    def emergency_burn_all(self, patient_id: str) -> list[tuple[str, World]]:
        """Mark all items for a patient as burn-eligible (emergency burn)."""
        t = self.clock.now
        eligible = []
        for world in (World.CLINICAL_REVIEW, World.DEVICE_MAINTENANCE, World.RESEARCH, World.THIRD_PARTY):
            items = self.stores[world].query(patient_id=patient_id)
            for item in items:
                if item.burn_state not in (BurnState.BURN_COMPLETE, BurnState.BURN_EXECUTING):
                    self.stores[world].update_burn_state(item.id, BurnState.BURN_ELIGIBLE, burn_eligible_at=t)
                    eligible.append((item.id, world))
        self.audit.log(
            "emergency_burn_initiated",
            patient_id=patient_id,
            details={"items_count": len(eligible)},
            sim_time=t,
        )
        return eligible
