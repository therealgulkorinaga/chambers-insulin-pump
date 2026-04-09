"""Core data models shared across all simulation components."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class World(Enum):
    REAL_TIME_THERAPEUTIC = "real_time_therapeutic"
    CLINICAL_REVIEW = "clinical_review"
    DEVICE_MAINTENANCE = "device_maintenance"
    RESEARCH = "research"
    PATIENT = "patient"
    THIRD_PARTY = "third_party"


class DataType(Enum):
    GLUCOSE_READING = "glucose_reading"
    INSULIN_BASAL = "insulin_basal"
    INSULIN_BOLUS = "insulin_bolus"
    INSULIN_TEMP_BASAL = "insulin_temp_basal"
    AID_PREDICTION = "aid_prediction"
    AID_ADJUSTMENT = "aid_adjustment"
    AID_MODE_CHANGE = "aid_mode_change"
    AID_IOB = "aid_iob"
    SENSOR_METADATA = "sensor_metadata"
    PUMP_METADATA = "pump_metadata"
    PEN_INJECTION = "pen_injection"
    ALARM = "alarm"
    MEAL_LOG = "meal_log"
    EXERCISE_LOG = "exercise_log"
    AGP_REPORT = "agp_report"
    CLINICAL_SUMMARY = "clinical_summary"


class BurnState(Enum):
    PENDING_CLASSIFICATION = "pending_classification"
    CLASSIFIED = "classified"
    REPORT_PENDING = "report_pending"
    DELIVERY_PENDING = "delivery_pending"
    DELIVERY_CONFIRMED = "delivery_confirmed"
    BURN_ELIGIBLE = "burn_eligible"
    BURN_QUEUED = "burn_queued"
    BURN_EXECUTING = "burn_executing"
    BURN_COMPLETE = "burn_complete"
    BURN_FAILED = "burn_failed"
    HELD = "held"


class SensorModel(Enum):
    DEXCOM_G7 = "dexcom_g7"
    LIBRE_3 = "libre_3"
    GUARDIAN_4 = "guardian_4"
    EVERSENSE_365 = "eversense_365"


class PumpModel(Enum):
    TANDEM_TSLIM_X2 = "tandem_tslim_x2"
    OMNIPOD_5 = "omnipod_5"
    MINIMED_780G = "minimed_780g"


class PenModel(Enum):
    NOVOPEN_6 = "novopen_6"
    ECHO_PLUS = "echo_plus"
    LILLY_TEMPO = "lilly_tempo"


class PatientCondition(Enum):
    T1D_CHILD = "t1d_child"
    T1D_ADOLESCENT = "t1d_adolescent"
    T1D_ADULT_GOOD = "t1d_adult_good"
    T1D_ADULT_POOR = "t1d_adult_poor"
    T2D_ADULT = "t2d_adult"
    GESTATIONAL = "gestational"
    T2D_ELDERLY = "t2d_elderly"
    WELLNESS = "wellness"


class AlarmSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# --- Sensor specs ---

SENSOR_SPECS: dict[SensorModel, dict[str, Any]] = {
    SensorModel.DEXCOM_G7: {
        "interval_minutes": 5,
        "wear_days": 10,
        "warmup_hours": 0.5,
        "mard_pct": 8.2,
    },
    SensorModel.LIBRE_3: {
        "interval_minutes": 1,
        "wear_days": 14,
        "warmup_hours": 1.0,
        "mard_pct": 7.9,
    },
    SensorModel.GUARDIAN_4: {
        "interval_minutes": 5,
        "wear_days": 7,
        "warmup_hours": 2.0,
        "mard_pct": 8.7,
    },
    SensorModel.EVERSENSE_365: {
        "interval_minutes": 5,
        "wear_days": 365,
        "warmup_hours": 24.0,
        "mard_pct": 9.0,
    },
}

PUMP_SPECS: dict[PumpModel, dict[str, Any]] = {
    PumpModel.TANDEM_TSLIM_X2: {
        "reservoir_units": 300,
        "increment_units": 0.001,
        "max_basal_rate": 15.0,
        "max_bolus_units": 25.0,
    },
    PumpModel.OMNIPOD_5: {
        "reservoir_units": 200,
        "increment_units": 0.05,
        "max_basal_rate": 30.0,
        "max_bolus_units": 30.0,
        "pod_wear_hours": 72,
    },
    PumpModel.MINIMED_780G: {
        "reservoir_units": 300,
        "increment_units": 0.025,
        "max_basal_rate": 35.0,
        "max_bolus_units": 25.0,
    },
}


@dataclass
class DataItem:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    patient_id: str = ""
    data_type: DataType = DataType.GLUCOSE_READING
    timestamp: float = 0.0
    value: dict[str, Any] = field(default_factory=dict)
    source_device: str = ""
    world: World | None = None
    burn_state: BurnState = BurnState.PENDING_CLASSIFICATION
    burn_eligible_at: float | None = None
    created_at: float = 0.0
    classified_at: float | None = None
    delivered_at: float | None = None
    burned_at: float | None = None
    held: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "data_type": self.data_type.value,
            "timestamp": self.timestamp,
            "value": self.value,
            "source_device": self.source_device,
            "world": self.world.value if self.world else None,
            "burn_state": self.burn_state.value,
            "burn_eligible_at": self.burn_eligible_at,
            "created_at": self.created_at,
            "classified_at": self.classified_at,
            "delivered_at": self.delivered_at,
            "burned_at": self.burned_at,
            "held": self.held,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> DataItem:
        item = cls()
        item.id = d["id"]
        item.patient_id = d["patient_id"]
        item.data_type = DataType(d["data_type"])
        item.timestamp = d["timestamp"]
        item.value = d.get("value", {})
        item.source_device = d.get("source_device", "")
        item.world = World(d["world"]) if d.get("world") else None
        item.burn_state = BurnState(d["burn_state"])
        item.burn_eligible_at = d.get("burn_eligible_at")
        item.created_at = d.get("created_at", 0.0)
        item.classified_at = d.get("classified_at")
        item.delivered_at = d.get("delivered_at")
        item.burned_at = d.get("burned_at")
        item.held = d.get("held", False)
        return item


@dataclass
class PatientProfile:
    id: str = "P001"
    name: str = "Simulated Patient"
    age: int = 35
    condition: PatientCondition = PatientCondition.T1D_ADULT_GOOD
    cgm_model: SensorModel = SensorModel.DEXCOM_G7
    pump_model: PumpModel | None = PumpModel.TANDEM_TSLIM_X2
    pen_model: PenModel | None = None
    aid_enabled: bool = True
    target_low: float = 70.0
    target_high: float = 180.0
    insulin_sensitivity: float = 50.0  # mg/dL per unit
    carb_ratio: float = 10.0  # grams per unit
    basal_rate: float = 1.0  # units/hour
    meals_per_day: int = 3
    seed: int = 42

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "condition": self.condition.value,
            "cgm_model": self.cgm_model.value,
            "pump_model": self.pump_model.value if self.pump_model else None,
            "pen_model": self.pen_model.value if self.pen_model else None,
            "aid_enabled": self.aid_enabled,
            "target_low": self.target_low,
            "target_high": self.target_high,
            "insulin_sensitivity": self.insulin_sensitivity,
            "carb_ratio": self.carb_ratio,
            "basal_rate": self.basal_rate,
            "meals_per_day": self.meals_per_day,
            "seed": self.seed,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> PatientProfile:
        return cls(
            id=d.get("id", "P001"),
            name=d.get("name", "Simulated Patient"),
            age=d.get("age", 35),
            condition=PatientCondition(d.get("condition", "t1d_adult_good")),
            cgm_model=SensorModel(d.get("cgm_model", "dexcom_g7")),
            pump_model=PumpModel(d["pump_model"]) if d.get("pump_model") else None,
            pen_model=PenModel(d["pen_model"]) if d.get("pen_model") else None,
            aid_enabled=d.get("aid_enabled", True),
            target_low=d.get("target_low", 70.0),
            target_high=d.get("target_high", 180.0),
            insulin_sensitivity=d.get("insulin_sensitivity", 50.0),
            carb_ratio=d.get("carb_ratio", 10.0),
            basal_rate=d.get("basal_rate", 1.0),
            meals_per_day=d.get("meals_per_day", 3),
            seed=d.get("seed", 42),
        )


@dataclass
class BurnScheduleConfig:
    """Burn timing per world (in simulated minutes)."""
    clinical_review_minutes: float = 90 * 24 * 60  # 90 days
    device_maintenance_minutes: float = 10 * 24 * 60  # sensor wear
    research_minutes: float = 365 * 24 * 60  # 1 year
    third_party_sla_minutes: float = 72 * 60  # 72 hours
    emergency_burn_minutes: float = 60  # 1 hour

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> BurnScheduleConfig:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
