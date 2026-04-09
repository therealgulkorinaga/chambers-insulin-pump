"""Simulated insulin pump engine."""

from __future__ import annotations

import numpy as np

from ..clock import SimulationClock
from ..models import DataItem, DataType, PatientProfile, PumpModel, PUMP_SPECS


class PumpEngine:
    """Generates insulin delivery events: basal, bolus, temp basal, alarms."""

    def __init__(self, profile: PatientProfile, clock: SimulationClock, rng: np.random.Generator):
        self.profile = profile
        self.clock = clock
        self.rng = rng
        self.model = profile.pump_model or PumpModel.TANDEM_TSLIM_X2
        specs = PUMP_SPECS[self.model]
        self.reservoir_capacity = specs["reservoir_units"]
        self.reservoir_remaining = self.reservoir_capacity
        self.max_bolus = specs["max_bolus_units"]
        self.serial = f"PUMP-{self.model.value[:4].upper()}-{rng.integers(10000, 99999)}"
        self.basal_rate = profile.basal_rate  # U/hr
        self._temp_basal: float | None = None
        self._temp_basal_end: float = 0.0
        self._last_basal_tick: float = -1.0
        self._occlusion_rate = 0.0005  # per tick

    def tick(self) -> list[DataItem]:
        items: list[DataItem] = []
        t = self.clock.now

        # Basal delivery every tick
        if self._last_basal_tick < 0:
            self._last_basal_tick = t

        elapsed_hr = (t - self._last_basal_tick) / 60.0
        if elapsed_hr <= 0:
            return items
        self._last_basal_tick = t

        # Check temp basal
        rate = self.basal_rate
        if self._temp_basal is not None and t < self._temp_basal_end:
            rate = self._temp_basal
        elif self._temp_basal is not None:
            self._temp_basal = None

        delivered = rate * elapsed_hr
        self.reservoir_remaining -= delivered

        # Reservoir low
        if self.reservoir_remaining < 10:
            items.append(DataItem(
                patient_id=self.profile.id,
                data_type=DataType.ALARM,
                timestamp=t,
                value={"alarm_type": "reservoir_low", "remaining_units": round(self.reservoir_remaining, 1)},
                source_device=self.serial,
                created_at=t,
            ))
        if self.reservoir_remaining <= 0:
            self.reservoir_remaining = self.reservoir_capacity
            items.append(DataItem(
                patient_id=self.profile.id,
                data_type=DataType.PUMP_METADATA,
                timestamp=t,
                value={"event": "reservoir_change", "pump_serial": self.serial},
                source_device=self.serial,
                created_at=t,
            ))

        # Random occlusion
        if self.rng.random() < self._occlusion_rate:
            items.append(DataItem(
                patient_id=self.profile.id,
                data_type=DataType.ALARM,
                timestamp=t,
                value={"alarm_type": "occlusion", "pump_serial": self.serial},
                source_device=self.serial,
                created_at=t,
            ))

        items.append(DataItem(
            patient_id=self.profile.id,
            data_type=DataType.INSULIN_BASAL,
            timestamp=t,
            value={
                "rate_u_hr": round(rate, 3),
                "delivered_u": round(delivered, 4),
                "reservoir_remaining": round(self.reservoir_remaining, 1),
                "pump_serial": self.serial,
                "is_temp": self._temp_basal is not None and t < self._temp_basal_end,
            },
            source_device=self.serial,
            created_at=t,
        ))
        return items

    def deliver_bolus(self, units: float, bolus_type: str = "normal") -> DataItem:
        t = self.clock.now
        actual = min(units, self.reservoir_remaining, self.max_bolus)
        self.reservoir_remaining -= actual
        return DataItem(
            patient_id=self.profile.id,
            data_type=DataType.INSULIN_BOLUS,
            timestamp=t,
            value={
                "requested_u": round(units, 2),
                "delivered_u": round(actual, 2),
                "bolus_type": bolus_type,
                "pump_serial": self.serial,
                "reservoir_remaining": round(self.reservoir_remaining, 1),
            },
            source_device=self.serial,
            created_at=t,
        )

    def set_temp_basal(self, rate: float, duration_minutes: float) -> DataItem:
        t = self.clock.now
        self._temp_basal = rate
        self._temp_basal_end = t + duration_minutes
        return DataItem(
            patient_id=self.profile.id,
            data_type=DataType.INSULIN_TEMP_BASAL,
            timestamp=t,
            value={
                "rate_u_hr": round(rate, 3),
                "duration_minutes": duration_minutes,
                "pump_serial": self.serial,
            },
            source_device=self.serial,
            created_at=t,
        )
