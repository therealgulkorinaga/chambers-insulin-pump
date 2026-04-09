"""Scenario runner — orchestrates the full simulation loop."""

from __future__ import annotations

import json
import os
import shutil
import time
from typing import Any

import numpy as np

from ..audit import AuditLogger
from ..clock import SimulationClock
from ..config import EventSchedule, ScenarioConfig
from ..devices.cgm import CGMEngine
from ..devices.pump import PumpEngine
from ..devices.aid import AIDAlgorithm
from ..devices.pen import PenEngine
from ..models import BurnState, DataItem, DataType, PatientProfile, World
from ..network import enable_network_isolation
from ..phone.app import PhoneApp
from ..portable_record.vault import VaultManager
from ..relay.burn_executor import BurnExecutor
from ..relay.burn_scheduler import BurnScheduler
from ..relay.classifier import WorldClassifier
from ..relay.reports import ReportGenerator
from ..relay.worlds import WorldStoreManager
from ..third_party.apps import ThirdPartyManager


class PatientSimState:
    """Runtime state for a single simulated patient."""

    def __init__(self, profile: PatientProfile, clock: SimulationClock, rng: np.random.Generator):
        self.profile = profile
        self.cgm = CGMEngine(profile, clock, rng)
        self.pump = PumpEngine(profile, clock, rng) if profile.pump_model else None
        self.aid = AIDAlgorithm(profile, clock, rng) if profile.aid_enabled and profile.pump_model else None
        self.pen = PenEngine(profile, clock, rng) if profile.pen_model else None
        self.phone = PhoneApp(profile, clock)
        self._rng = rng
        self._clock = clock
        self._next_meal: float = 0.0
        self._meals_today: int = 0

    def schedule_meals(self) -> None:
        """Schedule meals based on time of day."""
        day_minute = self._clock.now % (24 * 60)
        # Breakfast ~7am, lunch ~12pm, dinner ~6pm
        meal_times = [7 * 60, 12 * 60, 18 * 60]
        for mt in meal_times:
            if abs(day_minute - mt) < self._clock.tick_minutes:
                carbs = self._rng.uniform(20, 80)
                self.cgm.inject_meal(carbs)
                if self.aid:
                    bolus_units = carbs / self.profile.carb_ratio
                    self.aid.record_dose(self._clock.now, bolus_units)
                    if self.pump:
                        self.phone.receive_from_device([self.pump.deliver_bolus(bolus_units, "meal")])
                elif self.pen:
                    bolus = carbs / self.profile.carb_ratio
                    injection = self.pen.inject(bolus, "meal_bolus")
                    if injection:
                        self.phone.receive_from_device([injection])


class SimulationRunner:
    """Orchestrates the full simulation loop: devices → relay → burn → portable record."""

    def __init__(self, config: ScenarioConfig, output_dir: str):
        self.config = config
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Save config
        with open(os.path.join(output_dir, "config.json"), "w") as f:
            json.dump({"name": config.name, "duration_days": config.duration_days, "seed": config.seed}, f, indent=2)

        # Initialize core
        self.clock = SimulationClock(start_time=0.0, tick_minutes=config.tick_minutes)
        self.audit = AuditLogger(os.path.join(output_dir, "audit", "audit.jsonl"))

        # Relay components
        relay_dir = os.path.join(output_dir, "relay")
        self.worlds = WorldStoreManager(relay_dir)
        self.classifier = WorldClassifier(self.worlds, self.audit, self.clock)
        self.reports = ReportGenerator(self.worlds, self.audit, self.clock)
        self.scheduler = BurnScheduler(self.worlds, self.audit, self.clock, config.burn_schedule)
        self.executor = BurnExecutor(self.worlds, self.audit, self.clock)

        # Portable records
        self.vaults = VaultManager(output_dir, self.audit, self.clock)

        # Third-party apps
        self.third_party = ThirdPartyManager(config.third_party_apps, output_dir, self.audit, self.clock)

        # Patient states
        self.patients: dict[str, PatientSimState] = {}
        for p in config.patients:
            rng = np.random.default_rng(p.seed)
            self.patients[p.id] = PatientSimState(p, self.clock, rng)

        # Event queue sorted by time
        self._events = sorted(config.events, key=lambda e: e.sim_time_minutes)
        self._event_idx = 0

        # Third-party sharing state
        self._sharing: dict[str, set[str]] = {}  # patient_id -> set of app names

        # Stats
        self.stats = {
            "ticks": 0,
            "items_generated": 0,
            "items_classified": 0,
            "items_burned": 0,
            "reports_generated": 0,
            "items_delivered_to_vault": 0,
        }

    def _process_events(self) -> None:
        """Process any scheduled events at the current time."""
        t = self.clock.now
        while self._event_idx < len(self._events) and self._events[self._event_idx].sim_time_minutes <= t:
            ev = self._events[self._event_idx]
            self._event_idx += 1
            self._handle_event(ev)

    def _handle_event(self, ev: EventSchedule) -> None:
        t = self.clock.now
        pid = ev.target_patient

        if ev.event_type == "meal":
            if pid in self.patients:
                carbs = ev.params.get("carbs", 50.0)
                self.patients[pid].cgm.inject_meal(carbs)

        elif ev.event_type == "sensor_change":
            if pid in self.patients:
                meta = self.patients[pid].cgm.replace_sensor()
                self.patients[pid].phone.receive_from_device([meta])

        elif ev.event_type == "offline_start":
            if pid in self.patients:
                self.patients[pid].phone.go_offline()
                self.audit.log("offline_start", patient_id=pid, sim_time=t)

        elif ev.event_type == "offline_end":
            if pid in self.patients:
                self.patients[pid].phone.go_online()
                self.audit.log("offline_end", patient_id=pid, sim_time=t)
                # Force flush queued data
                items = self.patients[pid].phone.force_flush()
                self._upload_to_relay(items)

        elif ev.event_type == "consent_grant":
            app_name = ev.params.get("app_name", "")
            if pid not in self._sharing:
                self._sharing[pid] = set()
            self._sharing[pid].add(app_name)
            self.audit.log("consent_grant", patient_id=pid, details={"app": app_name}, sim_time=t)

        elif ev.event_type == "consent_revoke":
            app_name = ev.params.get("app_name", "")
            if pid in self._sharing:
                self._sharing[pid].discard(app_name)
            # Trigger burn propagation
            if app_name:
                app = self.third_party.apps.get(app_name)
                if app:
                    app.request_burn(pid, self.config.burn_schedule.third_party_sla_minutes)
            else:
                self.third_party.propagate_burn(pid)
            self.audit.log("consent_revoke", patient_id=pid, details={"app": app_name or "all"}, sim_time=t)

        elif ev.event_type == "emergency_burn":
            eligible = self.scheduler.emergency_burn_all(pid)
            results = self.executor.execute_burns(eligible)
            self.third_party.propagate_burn(pid, self.config.burn_schedule.emergency_burn_minutes)
            self.stats["items_burned"] += sum(1 for _, ok in results if ok)

        elif ev.event_type == "legal_hold":
            self.scheduler.place_hold(pid)

        elif ev.event_type == "legal_hold_lift":
            self.scheduler.lift_hold(pid)

        elif ev.event_type == "portable_record_loss":
            vault = self.vaults.get_or_create(pid)
            vault.simulate_loss()
            self.audit.log("portable_record_lost", patient_id=pid, sim_time=t)

        elif ev.event_type == "portable_record_recovery":
            vault = self.vaults.get_or_create(pid)
            vault.simulate_recovery()
            self.audit.log("portable_record_recovered", patient_id=pid, sim_time=t)

    def _upload_to_relay(self, items: list[DataItem]) -> None:
        """Upload items from phone to manufacturer relay (classify + store)."""
        if not items:
            return
        self.classifier.classify_batch(items)
        self.stats["items_classified"] += len(items)

        # Share with third-party apps if consent granted
        for item in items:
            if item.patient_id in self._sharing:
                for app_name in self._sharing[item.patient_id]:
                    self.third_party.share_data(app_name, [item])

    def _deliver_to_vaults(self) -> None:
        """Deliver data from relay to portable records and confirm."""
        for pid, pstate in self.patients.items():
            vault = self.vaults.get_or_create(pid)
            if not vault.available:
                continue

            # Deliver items from clinical review that are pending delivery
            items_to_deliver: list[DataItem] = []
            for world in (World.CLINICAL_REVIEW, World.DEVICE_MAINTENANCE):
                items = self.worlds[world].query(patient_id=pid, burn_state=BurnState.CLASSIFIED)
                items_to_deliver.extend(items)
                items2 = self.worlds[world].query(patient_id=pid, burn_state=BurnState.DELIVERY_PENDING)
                items_to_deliver.extend(items2)

            if items_to_deliver:
                received_ids, confirmation = vault.receive_items(items_to_deliver)
                if received_ids:
                    count = self.scheduler.mark_delivered(pid, received_ids)
                    self.stats["items_delivered_to_vault"] += count

    def _generate_reports(self) -> None:
        """Check if any patient needs a report generated."""
        for pid in self.patients:
            report = self.reports.check_and_generate(pid)
            if report:
                vault = self.vaults.get_or_create(pid)
                if vault.available:
                    vault.receive_report(report)
                self.stats["reports_generated"] += 1

    def _run_burn_cycle(self) -> None:
        """Run one burn cycle: check eligibility, execute burns."""
        eligible = self.scheduler.tick()
        if eligible:
            results = self.executor.execute_burns(eligible)
            self.stats["items_burned"] += sum(1 for _, ok in results if ok)

    def run(self, verbose: bool = False) -> dict[str, Any]:
        """Run the full simulation. Returns stats dict."""
        enable_network_isolation()

        total_ticks = self.clock.days_to_ticks(self.config.duration_days)
        start_wall = time.time()

        self.audit.log("simulation_start", details={
            "scenario": self.config.name,
            "duration_days": self.config.duration_days,
            "patients": len(self.patients),
            "total_ticks": total_ticks,
        }, sim_time=0.0)

        for tick_num in range(total_ticks):
            self.clock.advance()
            self.stats["ticks"] += 1

            # 1. Process scheduled events
            self._process_events()

            # 2. Generate device data for each patient
            for pid, pstate in self.patients.items():
                pstate.schedule_meals()

                # CGM readings
                cgm_items = pstate.cgm.tick()
                self.stats["items_generated"] += len(cgm_items)

                # AID processing
                aid_items: list[DataItem] = []
                for item in cgm_items:
                    if item.data_type == DataType.GLUCOSE_READING and pstate.aid:
                        glucose = item.value.get("glucose_mg_dl", 100)
                        aid_items.extend(pstate.aid.process_glucose(glucose))
                        # Apply AID insulin effect to CGM model
                        for ai in aid_items:
                            if ai.data_type == DataType.AID_ADJUSTMENT:
                                adj = ai.value.get("adjustment_u_hr", 0)
                                if adj > 0:
                                    pstate.cgm.inject_insulin_effect(adj * (self.clock.tick_minutes / 60))

                # Pump
                pump_items: list[DataItem] = []
                if pstate.pump:
                    pump_items = pstate.pump.tick()
                    self.stats["items_generated"] += len(pump_items)

                # Send to phone
                all_device_items = cgm_items + aid_items + pump_items
                self.stats["items_generated"] += len(aid_items)
                pstate.phone.receive_from_device(all_device_items)

                # 3. Upload from phone to relay
                upload = pstate.phone.flush_upload_queue()
                if upload:
                    self._upload_to_relay(upload)

            # 4. Third-party tick (process delayed burns)
            self.third_party.tick()

            # 5. Deliver to portable records (every 100 ticks to reduce overhead)
            if tick_num % 100 == 0:
                self._deliver_to_vaults()

            # 6. Generate reports
            if tick_num % 100 == 0:
                self._generate_reports()

            # 7. Run burn cycle (every 50 ticks)
            if tick_num % 50 == 0:
                self._run_burn_cycle()

            # Progress
            if verbose and tick_num % 5000 == 0 and tick_num > 0:
                elapsed = time.time() - start_wall
                pct = tick_num / total_ticks * 100
                print(f"  [{pct:5.1f}%] day {self.clock.now_days:.0f} | "
                      f"items={self.stats['items_generated']} burned={self.stats['items_burned']} | "
                      f"{elapsed:.1f}s wall")

        # Final delivery + burn pass
        self._deliver_to_vaults()
        self._generate_reports()
        for _ in range(3):
            self._run_burn_cycle()

        wall_time = time.time() - start_wall

        self.audit.log("simulation_complete", details={
            "wall_time_seconds": round(wall_time, 2),
            **self.stats,
        }, sim_time=self.clock.now)

        # Cleanup
        self.worlds.close_all()
        self.vaults.close_all()
        self.third_party.close_all()

        self.stats["wall_time_seconds"] = round(wall_time, 2)
        self.stats["sim_days"] = self.config.duration_days

        # Write stats
        with open(os.path.join(self.output_dir, "stats.json"), "w") as f:
            json.dump(self.stats, f, indent=2)

        return self.stats
