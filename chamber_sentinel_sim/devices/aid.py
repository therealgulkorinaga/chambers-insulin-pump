"""Simplified AID (Automated Insulin Delivery) algorithm stub."""

from __future__ import annotations

import math
from collections import deque

import numpy as np

from ..clock import SimulationClock
from ..models import DataItem, DataType, PatientProfile


class AIDAlgorithm:
    """Simplified closed-loop algorithm producing realistic AID decision data.

    Not production-grade. Generates the data types a real AID system would produce:
    predictions, adjustments, mode changes, IOB tracking.
    """

    def __init__(self, profile: PatientProfile, clock: SimulationClock, rng: np.random.Generator):
        self.profile = profile
        self.clock = clock
        self.rng = rng
        self.target = (profile.target_low + profile.target_high) / 2
        self.isf = profile.insulin_sensitivity
        self.history: deque[tuple[float, float]] = deque(maxlen=60)  # (time, glucose)
        self.iob: float = 0.0
        self.iob_items: list[tuple[float, float]] = []  # (time, units) for decay
        self.mode: str = "auto"  # auto, manual, safe
        self._mode_exit_glucose = 300.0
        self._mode_enter_glucose = 250.0
        self.insulin_action_minutes = 300.0  # 5 hours

    def update_iob(self, t: float) -> float:
        """Decay insulin-on-board based on time."""
        active = []
        total = 0.0
        for dose_time, units in self.iob_items:
            elapsed = t - dose_time
            if elapsed < self.insulin_action_minutes:
                remaining = units * (1 - elapsed / self.insulin_action_minutes)
                total += max(0, remaining)
                active.append((dose_time, units))
        self.iob_items = active
        self.iob = total
        return total

    def record_dose(self, t: float, units: float) -> None:
        self.iob_items.append((t, units))

    def process_glucose(self, glucose: float) -> list[DataItem]:
        """Process a glucose reading and produce AID decision data."""
        t = self.clock.now
        items: list[DataItem] = []
        self.history.append((t, glucose))
        self.update_iob(t)

        # Predict future glucose (simple linear extrapolation)
        pred_30 = glucose
        pred_60 = glucose
        pred_90 = glucose
        if len(self.history) >= 3:
            recent = list(self.history)[-6:]
            if len(recent) >= 2:
                dt = recent[-1][0] - recent[0][0]
                if dt > 0:
                    slope = (recent[-1][1] - recent[0][1]) / dt  # mg/dL per min
                    pred_30 = glucose + slope * 30
                    pred_60 = glucose + slope * 60
                    pred_90 = glucose + slope * 90

        items.append(DataItem(
            patient_id=self.profile.id,
            data_type=DataType.AID_PREDICTION,
            timestamp=t,
            value={
                "current_glucose": round(glucose, 1),
                "predicted_30min": round(max(40, min(500, pred_30)), 1),
                "predicted_60min": round(max(40, min(500, pred_60)), 1),
                "predicted_90min": round(max(40, min(500, pred_90)), 1),
            },
            source_device="aid_algorithm",
            created_at=t,
        ))

        # IOB data item
        items.append(DataItem(
            patient_id=self.profile.id,
            data_type=DataType.AID_IOB,
            timestamp=t,
            value={"iob_units": round(self.iob, 3)},
            source_device="aid_algorithm",
            created_at=t,
        ))

        # Mode management
        old_mode = self.mode
        if self.mode == "auto" and glucose > self._mode_exit_glucose:
            self.mode = "safe"
        elif self.mode == "safe" and glucose < self._mode_enter_glucose:
            self.mode = "auto"

        if old_mode != self.mode:
            items.append(DataItem(
                patient_id=self.profile.id,
                data_type=DataType.AID_MODE_CHANGE,
                timestamp=t,
                value={"from_mode": old_mode, "to_mode": self.mode, "trigger_glucose": round(glucose, 1)},
                source_device="aid_algorithm",
                created_at=t,
            ))

        # Calculate adjustment
        adjustment = 0.0
        if self.mode == "auto":
            error = glucose - self.target
            correction_needed = error / self.isf
            net = correction_needed - self.iob
            # Clamp adjustments
            adjustment = max(-self.profile.basal_rate * 0.8, min(2.0, net * 0.3))

        if abs(adjustment) > 0.01:
            items.append(DataItem(
                patient_id=self.profile.id,
                data_type=DataType.AID_ADJUSTMENT,
                timestamp=t,
                value={
                    "adjustment_type": "auto_basal" if adjustment != 0 else "none",
                    "adjustment_u_hr": round(adjustment, 3),
                    "target_glucose": self.target,
                    "current_iob": round(self.iob, 3),
                    "mode": self.mode,
                },
                source_device="aid_algorithm",
                created_at=t,
            ))
            if adjustment > 0:
                self.record_dose(t, adjustment * (self.clock.tick_minutes / 60.0))

        return items
