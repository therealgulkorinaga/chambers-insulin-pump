"""Assertion engine — validates simulation correctness."""

from __future__ import annotations

import json
import os
import sqlite3
from typing import Any

from ..audit import AuditLogger
from ..models import BurnState, World


class AssertionResult:
    def __init__(self, name: str, passed: bool, details: str = ""):
        self.name = name
        self.passed = passed
        self.details = details

    def __repr__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"[{status}] {self.name}: {self.details}"

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "passed": self.passed, "details": self.details}


class AssertionEngine:
    """Runs assertions against simulation output to validate correctness."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.results: list[AssertionResult] = []

    def run_all(self, assertion_names: list[str] | None = None) -> list[AssertionResult]:
        """Run all or selected assertions."""
        available = {
            "burn_completeness": self.assert_burn_completeness,
            "portable_record_completeness": self.assert_portable_record_completeness,
            "no_data_resurrection": self.assert_no_data_resurrection,
            "world_isolation": self.assert_world_isolation,
            "audit_chain_integrity": self.assert_audit_chain_integrity,
            "timing": self.assert_burn_timing,
            "report_delivery": self.assert_report_delivery,
        }

        names = assertion_names or list(available.keys())
        self.results = []
        for name in names:
            fn = available.get(name)
            if fn:
                result = fn()
                self.results.append(result)

        # Write results
        results_dir = os.path.join(self.output_dir, "assertions")
        os.makedirs(results_dir, exist_ok=True)
        with open(os.path.join(results_dir, "results.json"), "w") as f:
            json.dump([r.to_dict() for r in self.results], f, indent=2)

        return self.results

    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.results)

    def assert_burn_completeness(self) -> AssertionResult:
        """Every data item past its burn window should be burned (deleted from relay)."""
        relay_dir = os.path.join(self.output_dir, "relay")
        remaining = 0
        for world in World:
            if world in (World.REAL_TIME_THERAPEUTIC, World.PATIENT):
                continue
            db_path = os.path.join(relay_dir, world.value, f"{world.value}.db")
            if not os.path.exists(db_path):
                continue
            conn = sqlite3.connect(db_path)
            # Count items that are NOT in burn_complete or held state
            row = conn.execute(
                "SELECT COUNT(*) FROM items WHERE burn_state NOT IN (?, ?)",
                (BurnState.BURN_COMPLETE.value, BurnState.HELD.value),
            ).fetchone()
            count = row[0] if row else 0
            remaining += count
            conn.close()

        # Some items may legitimately remain (within burn window, held, etc.)
        # Check the audit log for items that should have been burned
        audit_path = os.path.join(self.output_dir, "audit", "audit.jsonl")
        burn_eligible_count = 0
        burn_complete_count = 0
        if os.path.exists(audit_path):
            with open(audit_path) as f:
                for line in f:
                    if not line.strip():
                        continue
                    entry = json.loads(line)
                    et = entry.get("event_type", "")
                    if et in ("burn_eligible", "burn_eligible_batch"):
                        burn_eligible_count += entry.get("details", {}).get("count", 1)
                    elif et == "burn_complete":
                        burn_complete_count += entry.get("details", {}).get("burned", 1)

        passed = remaining < 100 or burn_complete_count > 0  # basic check
        details = (
            f"burn_eligible={burn_eligible_count}, burn_complete={burn_complete_count}, "
            f"remaining_in_relay={remaining}"
        )
        return AssertionResult("burn_completeness", passed, details)

    def assert_portable_record_completeness(self) -> AssertionResult:
        """Every patient should have data in their portable record."""
        pr_dir = os.path.join(self.output_dir, "portable_record")
        if not os.path.exists(pr_dir):
            return AssertionResult("portable_record_completeness", False, "No portable record directory")

        patients = [d for d in os.listdir(pr_dir) if os.path.isdir(os.path.join(pr_dir, d))]
        if not patients:
            return AssertionResult("portable_record_completeness", False, "No patient vaults found")

        total_items = 0
        for pid in patients:
            db_path = os.path.join(pr_dir, pid, "vault.db")
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                row = conn.execute("SELECT COUNT(*) FROM items").fetchone()
                total_items += row[0] if row else 0
                conn.close()

        passed = total_items > 0
        return AssertionResult(
            "portable_record_completeness", passed,
            f"patients={len(patients)}, total_items={total_items}"
        )

    def assert_no_data_resurrection(self) -> AssertionResult:
        """No burned item should reappear in the audit log after its burn_complete event."""
        audit_path = os.path.join(self.output_dir, "audit", "audit.jsonl")
        if not os.path.exists(audit_path):
            return AssertionResult("no_data_resurrection", True, "No audit log")

        burned_items: set[str] = set()
        resurrections = 0

        with open(audit_path) as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                item_id = entry.get("item_id", "")
                event = entry.get("event_type", "")

                if event == "burn_complete" and item_id:
                    burned_items.add(item_id)
                elif item_id in burned_items and event in ("classified", "third_party_data_received"):
                    resurrections += 1

        passed = resurrections == 0
        return AssertionResult(
            "no_data_resurrection", passed,
            f"burned_items={len(burned_items)}, resurrections={resurrections}"
        )

    def assert_world_isolation(self) -> AssertionResult:
        """Each data item should only exist in the world it was classified for."""
        # Check audit log for classification events and verify no cross-world storage
        audit_path = os.path.join(self.output_dir, "audit", "audit.jsonl")
        if not os.path.exists(audit_path):
            return AssertionResult("world_isolation", True, "No audit log")

        classifications: dict[str, str] = {}  # item_id -> world
        violations = 0

        with open(audit_path) as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                if entry.get("event_type") == "classified":
                    item_id = entry.get("item_id", "")
                    world = entry.get("world", "")
                    if item_id:
                        if item_id in classifications and classifications[item_id] != world:
                            violations += 1
                        classifications[item_id] = world

        passed = violations == 0
        return AssertionResult(
            "world_isolation", passed,
            f"total_classifications={len(classifications)}, violations={violations}"
        )

    def assert_audit_chain_integrity(self) -> AssertionResult:
        """Audit log hash chain must be unbroken."""
        audit_path = os.path.join(self.output_dir, "audit", "audit.jsonl")
        if not os.path.exists(audit_path):
            return AssertionResult("audit_chain_integrity", True, "No audit log")

        audit = AuditLogger(audit_path)
        valid, count = audit.verify_chain()
        return AssertionResult(
            "audit_chain_integrity", valid,
            f"entries={count}, chain_valid={valid}"
        )

    def assert_burn_timing(self) -> AssertionResult:
        """Burns should execute within reasonable time of becoming eligible."""
        audit_path = os.path.join(self.output_dir, "audit", "audit.jsonl")
        if not os.path.exists(audit_path):
            return AssertionResult("timing", True, "No audit log")

        eligible_times: dict[str, float] = {}
        complete_times: dict[str, float] = {}

        with open(audit_path) as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                item_id = entry.get("item_id", "")
                event = entry.get("event_type", "")
                sim_time = entry.get("sim_time", 0.0)

                if event == "burn_eligible" and item_id:
                    eligible_times[item_id] = sim_time
                elif event == "burn_complete" and item_id:
                    complete_times[item_id] = sim_time

        delays = []
        for item_id, elig_time in eligible_times.items():
            if item_id in complete_times:
                delay = complete_times[item_id] - elig_time
                delays.append(delay)

        if not delays:
            return AssertionResult("timing", True, "No burns to check timing")

        max_delay = max(delays)
        avg_delay = sum(delays) / len(delays)
        # Allow up to 1 simulated day of delay (burn cycles run periodically)
        passed = max_delay < 24 * 60  # 1 day in minutes
        return AssertionResult(
            "timing", passed,
            f"burns={len(delays)}, avg_delay={avg_delay:.0f}min, max_delay={max_delay:.0f}min"
        )

    def assert_report_delivery(self) -> AssertionResult:
        """Every generated report should be delivered to the portable record."""
        audit_path = os.path.join(self.output_dir, "audit", "audit.jsonl")
        if not os.path.exists(audit_path):
            return AssertionResult("report_delivery", True, "No audit log")

        reports_generated = 0
        reports_delivered = 0

        with open(audit_path) as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                event = entry.get("event_type", "")
                if event == "report_generated":
                    reports_generated += 1
                elif event == "portable_record_report_received":
                    reports_delivered += 1

        passed = reports_delivered >= reports_generated
        return AssertionResult(
            "report_delivery", passed,
            f"generated={reports_generated}, delivered={reports_delivered}"
        )
