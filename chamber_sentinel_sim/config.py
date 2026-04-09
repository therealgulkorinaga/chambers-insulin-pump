"""Configuration loading from YAML scenario files."""

from __future__ import annotations

import yaml
from dataclasses import dataclass, field
from typing import Any

from .models import BurnScheduleConfig, PatientProfile


@dataclass
class ThirdPartyAppConfig:
    name: str = "app_a"
    app_type: str = "fitness"  # fitness, clinical, aggregator
    port: int = 9001
    compliance: str = "compliant"  # compliant, delayed, non_compliant
    delay_minutes: float = 0.0
    has_sub_processor: bool = False

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ThirdPartyAppConfig:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class EventSchedule:
    sim_time_minutes: float = 0.0
    event_type: str = ""  # meal, sensor_change, consent_revoke, consent_grant, offline_start, offline_end, emergency_burn, legal_hold, legal_hold_lift, custody_transition, failure_inject
    target_patient: str = ""
    params: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> EventSchedule:
        return cls(
            sim_time_minutes=d.get("sim_time_minutes", 0.0),
            event_type=d.get("event_type", ""),
            target_patient=d.get("target_patient", ""),
            params=d.get("params", {}),
        )


@dataclass
class ScenarioConfig:
    name: str = "unnamed"
    description: str = ""
    duration_days: float = 90.0
    acceleration: float = 1440.0  # 1 day = 1 minute wall-clock
    tick_minutes: float = 5.0
    seed: int = 42
    patients: list[PatientProfile] = field(default_factory=list)
    third_party_apps: list[ThirdPartyAppConfig] = field(default_factory=list)
    burn_schedule: BurnScheduleConfig = field(default_factory=BurnScheduleConfig)
    events: list[EventSchedule] = field(default_factory=list)
    assertions: list[str] = field(default_factory=lambda: [
        "burn_completeness",
        "portable_record_completeness",
        "no_data_resurrection",
        "world_isolation",
        "audit_chain_integrity",
        "timing",
        "report_delivery",
    ])
    relay_port: int = 8080

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ScenarioConfig:
        patients = [PatientProfile.from_dict(p) for p in d.get("patients", [])]
        if not patients:
            patients = [PatientProfile()]
        apps = [ThirdPartyAppConfig.from_dict(a) for a in d.get("third_party_apps", [])]
        events = [EventSchedule.from_dict(e) for e in d.get("events", [])]
        burn = BurnScheduleConfig.from_dict(d["burn_schedule"]) if "burn_schedule" in d else BurnScheduleConfig()
        return cls(
            name=d.get("name", "unnamed"),
            description=d.get("description", ""),
            duration_days=d.get("duration_days", 90.0),
            acceleration=d.get("acceleration", 1440.0),
            tick_minutes=d.get("tick_minutes", 5.0),
            seed=d.get("seed", 42),
            patients=patients,
            third_party_apps=apps,
            burn_schedule=burn,
            events=events,
            assertions=d.get("assertions", [
                "burn_completeness", "portable_record_completeness", "no_data_resurrection",
                "world_isolation", "audit_chain_integrity", "timing", "report_delivery",
            ]),
            relay_port=d.get("relay_port", 8080),
        )

    @classmethod
    def load(cls, path: str) -> ScenarioConfig:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)
