"""Simulated phone/app layer — receives device data, runs AID, uploads to relay."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ..clock import SimulationClock
from ..models import DataItem, DataType, PatientProfile


class PhoneApp:
    """Simulated smartphone app that mediates between devices and manufacturer relay.

    Handles: local caching, AID algorithm hosting, offline queuing, and upload batching.
    """

    def __init__(self, profile: PatientProfile, clock: SimulationClock):
        self.profile = profile
        self.clock = clock
        self._cache: list[DataItem] = []
        self._upload_queue: list[DataItem] = []
        self._offline = False
        self._batch_interval_minutes = 5.0
        self._last_upload: float = 0.0

    @property
    def offline(self) -> bool:
        return self._offline

    def go_offline(self) -> None:
        self._offline = True

    def go_online(self) -> None:
        self._offline = False

    def receive_from_device(self, items: list[DataItem]) -> None:
        """Receive data items from simulated BLE devices."""
        for item in items:
            self._cache.append(item)
            self._upload_queue.append(item)

    def get_latest_glucose(self) -> float | None:
        """Get most recent glucose reading (real-time therapeutic use)."""
        for item in reversed(self._cache):
            if item.data_type == DataType.GLUCOSE_READING:
                return item.value.get("glucose_mg_dl")
        return None

    def flush_upload_queue(self) -> list[DataItem]:
        """Return items ready for upload and clear the queue.

        Returns empty if offline or batch interval not reached.
        """
        if self._offline:
            return []
        t = self.clock.now
        if t - self._last_upload < self._batch_interval_minutes:
            return []
        self._last_upload = t
        items = list(self._upload_queue)
        self._upload_queue.clear()
        return items

    def force_flush(self) -> list[DataItem]:
        """Force flush regardless of interval (used on reconnect)."""
        items = list(self._upload_queue)
        self._upload_queue.clear()
        self._last_upload = self.clock.now
        return items

    @property
    def cache_size(self) -> int:
        return len(self._cache)

    @property
    def queue_size(self) -> int:
        return len(self._upload_queue)
