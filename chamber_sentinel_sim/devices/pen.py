"""Simulated connected insulin pen engine."""

from __future__ import annotations

import numpy as np

from ..clock import SimulationClock
from ..models import DataItem, DataType, PatientProfile, PenModel


class PenEngine:
    """Generates injection events for connected insulin pens."""

    def __init__(self, profile: PatientProfile, clock: SimulationClock, rng: np.random.Generator):
        self.profile = profile
        self.clock = clock
        self.rng = rng
        self.model = profile.pen_model or PenModel.NOVOPEN_6
        self.serial = f"PEN-{self.model.value[:4].upper()}-{rng.integers(10000, 99999)}"
        self._last_injection: float = -1.0
        self._missed_dose_rate = 0.05
        self._cartridge_units = 300.0
        self._cartridge_remaining = 300.0

    def inject(self, units: float, injection_type: str = "bolus") -> DataItem | None:
        """Record a pen injection. Returns None if dose is 'missed'."""
        t = self.clock.now
        if self.rng.random() < self._missed_dose_rate:
            return None  # missed dose

        actual = min(units, self._cartridge_remaining)
        self._cartridge_remaining -= actual
        self._last_injection = t

        if self._cartridge_remaining < 5:
            self._cartridge_remaining = 300.0

        return DataItem(
            patient_id=self.profile.id,
            data_type=DataType.PEN_INJECTION,
            timestamp=t,
            value={
                "dose_units": round(actual, 1),
                "injection_type": injection_type,
                "pen_serial": self.serial,
                "pen_model": self.model.value,
                "cartridge_remaining": round(self._cartridge_remaining, 1),
            },
            source_device=self.serial,
            created_at=t,
        )
