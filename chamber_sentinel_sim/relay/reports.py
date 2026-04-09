"""AGP and clinical report generator."""

from __future__ import annotations

import json
import statistics
from typing import Any

from ..audit import AuditLogger
from ..clock import SimulationClock
from ..models import BurnState, DataItem, DataType, World
from .worlds import WorldStoreManager


class ReportGenerator:
    """Generates AGP-style clinical reports from raw glucose data."""

    def __init__(self, stores: WorldStoreManager, audit: AuditLogger, clock: SimulationClock):
        self.stores = stores
        self.audit = audit
        self.clock = clock
        self._report_interval_minutes = 14 * 24 * 60  # every 14 days
        self._last_report: dict[str, float] = {}  # patient_id -> last report time

    def check_and_generate(self, patient_id: str) -> DataItem | None:
        """Check if a report is due and generate it."""
        t = self.clock.now
        last = self._last_report.get(patient_id, 0.0)
        if t - last < self._report_interval_minutes:
            return None

        # Get glucose readings from clinical review world
        items = self.stores[World.CLINICAL_REVIEW].query(
            patient_id=patient_id,
            data_type=DataType.GLUCOSE_READING,
        )
        if len(items) < 100:  # need meaningful data
            return None

        report = self._generate_agp(patient_id, items)
        self._last_report[patient_id] = t
        return report

    def _generate_agp(self, patient_id: str, readings: list[DataItem]) -> DataItem:
        """Generate an AGP report from glucose readings."""
        values = [r.value.get("glucose_mg_dl", 0) for r in readings if "glucose_mg_dl" in r.value]
        if not values:
            values = [100.0]

        n = len(values)
        mean_g = statistics.mean(values)
        median_g = statistics.median(values)
        sd_g = statistics.stdev(values) if n > 1 else 0.0
        cv = (sd_g / mean_g * 100) if mean_g > 0 else 0.0

        # GMI (Glucose Management Indicator)
        gmi = 3.31 + 0.02392 * mean_g

        # Time in range breakdown
        very_low = sum(1 for v in values if v < 54) / n * 100
        low = sum(1 for v in values if 54 <= v < 70) / n * 100
        in_range = sum(1 for v in values if 70 <= v <= 180) / n * 100
        high = sum(1 for v in values if 180 < v <= 250) / n * 100
        very_high = sum(1 for v in values if v > 250) / n * 100

        # Percentiles
        sorted_v = sorted(values)
        p10 = sorted_v[int(n * 0.1)] if n > 10 else sorted_v[0]
        p25 = sorted_v[int(n * 0.25)] if n > 4 else sorted_v[0]
        p75 = sorted_v[int(n * 0.75)] if n > 4 else sorted_v[-1]
        p90 = sorted_v[int(n * 0.9)] if n > 10 else sorted_v[-1]

        time_span_days = (readings[-1].timestamp - readings[0].timestamp) / (24 * 60)

        report_data = {
            "report_type": "agp",
            "period_days": round(time_span_days, 1),
            "readings_count": n,
            "mean_glucose": round(mean_g, 1),
            "median_glucose": round(median_g, 1),
            "sd_glucose": round(sd_g, 1),
            "cv_pct": round(cv, 1),
            "gmi": round(gmi, 1),
            "time_very_low_pct": round(very_low, 1),
            "time_low_pct": round(low, 1),
            "time_in_range_pct": round(in_range, 1),
            "time_high_pct": round(high, 1),
            "time_very_high_pct": round(very_high, 1),
            "p10": round(p10, 1),
            "p25": round(p25, 1),
            "p75": round(p75, 1),
            "p90": round(p90, 1),
            "min_glucose": round(min(values), 1),
            "max_glucose": round(max(values), 1),
        }

        report_item = DataItem(
            patient_id=patient_id,
            data_type=DataType.AGP_REPORT,
            timestamp=self.clock.now,
            value=report_data,
            source_device="report_generator",
            created_at=self.clock.now,
            world=World.PATIENT,
            burn_state=BurnState.DELIVERY_PENDING,
        )

        self.audit.log(
            "report_generated",
            item_id=report_item.id,
            patient_id=patient_id,
            world=World.PATIENT.value,
            data_type="agp_report",
            details={
                "period_days": report_data["period_days"],
                "readings_count": n,
                "tir_pct": report_data["time_in_range_pct"],
            },
            sim_time=self.clock.now,
        )
        return report_item
