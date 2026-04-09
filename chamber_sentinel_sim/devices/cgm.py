"""Simulated CGM engine with physiological glucose trace generation."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from ..clock import SimulationClock
from ..models import (
    DataItem,
    DataType,
    PatientCondition,
    PatientProfile,
    SensorModel,
    SENSOR_SPECS,
)


# Condition-specific baseline glucose parameters (mean, sd, meal_peak_delta)
_CONDITION_PARAMS: dict[PatientCondition, tuple[float, float, float]] = {
    PatientCondition.T1D_CHILD:       (160.0, 50.0, 100.0),
    PatientCondition.T1D_ADOLESCENT:  (170.0, 55.0, 110.0),
    PatientCondition.T1D_ADULT_GOOD:  (130.0, 30.0,  80.0),
    PatientCondition.T1D_ADULT_POOR:  (200.0, 65.0, 130.0),
    PatientCondition.T2D_ADULT:       (150.0, 35.0,  70.0),
    PatientCondition.GESTATIONAL:     (120.0, 25.0,  60.0),
    PatientCondition.T2D_ELDERLY:     (155.0, 40.0,  65.0),
    PatientCondition.WELLNESS:        (95.0,  12.0,  30.0),
}


@dataclass
class SensorState:
    serial: str = ""
    model: SensorModel = SensorModel.DEXCOM_G7
    started_at: float = 0.0
    wear_minutes: float = 0.0
    warmup_minutes: float = 0.0
    expired: bool = False
    failed: bool = False
    readings_generated: int = 0


class CGMEngine:
    """Generates synthetic glucose traces using a simplified physiological model.

    The model combines:
    - Baseline sinusoidal circadian rhythm (dawn phenomenon)
    - Meal absorption curves (exponential rise/decay)
    - Random walk for glucose variability
    - Sensor noise calibrated to manufacturer MARD
    """

    def __init__(self, profile: PatientProfile, clock: SimulationClock, rng: np.random.Generator):
        self.profile = profile
        self.clock = clock
        self.rng = rng
        specs = SENSOR_SPECS[profile.cgm_model]
        self.interval = specs["interval_minutes"]
        self.wear_minutes = specs["wear_days"] * 24 * 60
        self.warmup_minutes = specs["warmup_hours"] * 60
        self.mard = specs["mard_pct"] / 100.0

        cond = _CONDITION_PARAMS.get(profile.condition, _CONDITION_PARAMS[PatientCondition.T1D_ADULT_GOOD])
        self.baseline_mean = cond[0]
        self.baseline_sd = cond[1]
        self.meal_peak_delta = cond[2]

        self._glucose = self.baseline_mean
        self._sensor = self._new_sensor()
        self._meal_active = False
        self._meal_start: float = 0.0
        self._meal_carbs: float = 0.0
        self._insulin_effect: float = 0.0
        self._last_tick: float = -1.0
        self._failure_rate = 0.002  # per reading

    def _new_sensor(self) -> SensorState:
        serial = f"SN-{self.profile.cgm_model.value[:4].upper()}-{self.rng.integers(10000, 99999)}"
        return SensorState(
            serial=serial,
            model=self.profile.cgm_model,
            started_at=self.clock.now,
            wear_minutes=self.wear_minutes,
            warmup_minutes=self.warmup_minutes,
        )

    @property
    def sensor(self) -> SensorState:
        return self._sensor

    def replace_sensor(self) -> DataItem:
        """Replace sensor and return metadata item for the old sensor."""
        old = self._sensor
        old.expired = True
        meta = DataItem(
            patient_id=self.profile.id,
            data_type=DataType.SENSOR_METADATA,
            timestamp=self.clock.now,
            value={
                "event": "sensor_replaced",
                "old_serial": old.serial,
                "readings_generated": old.readings_generated,
                "wear_minutes": self.clock.now - old.started_at,
            },
            source_device=old.serial,
            created_at=self.clock.now,
        )
        self._sensor = self._new_sensor()
        return meta

    def inject_meal(self, carbs: float) -> None:
        self._meal_active = True
        self._meal_start = self.clock.now
        self._meal_carbs = carbs

    def inject_insulin_effect(self, units: float) -> None:
        self._insulin_effect += units * self.profile.insulin_sensitivity

    def tick(self) -> list[DataItem]:
        """Generate readings for the current clock tick. Returns 0 or more DataItems."""
        items: list[DataItem] = []
        t = self.clock.now

        # Check if this tick aligns with the sensor interval
        if self._last_tick >= 0:
            elapsed = t - self._last_tick
            if elapsed < self.interval - 0.01:
                return items
        self._last_tick = t

        # Check sensor lifecycle
        sensor_age = t - self._sensor.started_at
        if sensor_age < self._sensor.warmup_minutes:
            return items  # warmup period, no readings
        if sensor_age > self._sensor.wear_minutes:
            meta = self.replace_sensor()
            items.append(meta)
            return items  # new sensor just started, in warmup

        # Check for random sensor failure
        if self.rng.random() < self._failure_rate:
            self._sensor.failed = True
            items.append(DataItem(
                patient_id=self.profile.id,
                data_type=DataType.ALARM,
                timestamp=t,
                value={"alarm_type": "sensor_signal_loss", "sensor_serial": self._sensor.serial},
                source_device=self._sensor.serial,
                created_at=t,
            ))
            self._sensor.failed = False  # transient failure
            return items

        # Physiological glucose model
        day_frac = (t % (24 * 60)) / (24 * 60)

        # Circadian: dawn phenomenon peaks around 4-8am
        circadian = 15.0 * math.sin(2 * math.pi * (day_frac - 0.2))

        # Meal effect
        meal_effect = 0.0
        if self._meal_active:
            meal_elapsed = t - self._meal_start
            if meal_elapsed > 0:
                # Simplified meal absorption: peaks ~45 min, decays over ~3 hours
                peak_min = 45.0
                decay_rate = 0.015
                meal_effect = (self._meal_carbs / 30.0) * self.meal_peak_delta * (
                    (meal_elapsed / peak_min) * math.exp(1 - meal_elapsed / peak_min)
                )
                if meal_elapsed > 240:
                    self._meal_active = False
                    self._meal_carbs = 0.0

        # Insulin effect (decays over time)
        if self._insulin_effect > 0:
            decay = min(self._insulin_effect, 0.5)
            self._insulin_effect -= decay
            self._glucose -= decay

        # Random walk
        walk = self.rng.normal(0, self.baseline_sd * 0.02)

        # Combine
        true_glucose = self.baseline_mean + circadian + meal_effect + walk
        self._glucose = 0.9 * self._glucose + 0.1 * true_glucose

        # Clamp to physiological range
        self._glucose = max(30.0, min(500.0, self._glucose))

        # Apply sensor noise (MARD-calibrated)
        noise = self.rng.normal(0, self._glucose * self.mard * 0.5)
        reported = max(40.0, min(500.0, self._glucose + noise))

        # Rate of change
        trend = "flat"
        if hasattr(self, "_prev_glucose"):
            roc = (reported - self._prev_glucose) / self.interval  # mg/dL per min
            if roc > 2:
                trend = "rising_fast"
            elif roc > 1:
                trend = "rising"
            elif roc < -2:
                trend = "falling_fast"
            elif roc < -1:
                trend = "falling"
        self._prev_glucose = reported

        self._sensor.readings_generated += 1

        items.append(DataItem(
            patient_id=self.profile.id,
            data_type=DataType.GLUCOSE_READING,
            timestamp=t,
            value={
                "glucose_mg_dl": round(reported, 1),
                "trend": trend,
                "sensor_serial": self._sensor.serial,
                "sensor_age_hours": round(sensor_age / 60, 1),
            },
            source_device=self._sensor.serial,
            created_at=t,
        ))

        # Generate alarms for out-of-range
        if reported < 54:
            items.append(DataItem(
                patient_id=self.profile.id,
                data_type=DataType.ALARM,
                timestamp=t,
                value={"alarm_type": "urgent_low", "glucose_mg_dl": round(reported, 1)},
                source_device=self._sensor.serial,
                created_at=t,
            ))
        elif reported < 70:
            items.append(DataItem(
                patient_id=self.profile.id,
                data_type=DataType.ALARM,
                timestamp=t,
                value={"alarm_type": "low", "glucose_mg_dl": round(reported, 1)},
                source_device=self._sensor.serial,
                created_at=t,
            ))
        elif reported > 250:
            items.append(DataItem(
                patient_id=self.profile.id,
                data_type=DataType.ALARM,
                timestamp=t,
                value={"alarm_type": "high", "glucose_mg_dl": round(reported, 1)},
                source_device=self._sensor.serial,
                created_at=t,
            ))

        return items
