"""Typed World data stores — in-memory with SQLite persistence on flush/close."""

from __future__ import annotations

import json
import os
import sqlite3
from typing import Any

from ..models import BurnState, DataItem, DataType, World


_SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    data_type TEXT NOT NULL,
    timestamp REAL NOT NULL,
    value TEXT NOT NULL,
    source_device TEXT,
    burn_state TEXT NOT NULL,
    burn_eligible_at REAL,
    created_at REAL,
    classified_at REAL,
    delivered_at REAL,
    burned_at REAL,
    held INTEGER DEFAULT 0
);
"""


class WorldStore:
    """In-memory store for a single Typed World, with SQLite persistence."""

    def __init__(self, world: World, db_dir: str):
        self.world = world
        self._dir = os.path.join(db_dir, world.value)
        os.makedirs(self._dir, exist_ok=True)
        self._db_path = os.path.join(self._dir, f"{world.value}.db")
        # Primary store is in-memory dict for speed
        self._items: dict[str, DataItem] = {}

    def insert(self, item: DataItem) -> None:
        self._items[item.id] = item

    def insert_batch(self, items: list[DataItem]) -> None:
        for item in items:
            self._items[item.id] = item

    def commit(self) -> None:
        pass  # no-op; persistence handled by flush/close

    def get(self, item_id: str) -> DataItem | None:
        return self._items.get(item_id)

    def query(
        self,
        patient_id: str | None = None,
        burn_state: BurnState | None = None,
        data_type: DataType | None = None,
        limit: int = 100000,
    ) -> list[DataItem]:
        results = []
        for item in self._items.values():
            if patient_id and item.patient_id != patient_id:
                continue
            if burn_state and item.burn_state != burn_state:
                continue
            if data_type and item.data_type != data_type:
                continue
            results.append(item)
            if len(results) >= limit:
                break
        return results

    def update_burn_state(self, item_id: str, state: BurnState, **kwargs: Any) -> None:
        item = self._items.get(item_id)
        if item:
            item.burn_state = state
            for k, v in kwargs.items():
                if hasattr(item, k):
                    setattr(item, k, v)

    def delete(self, item_id: str) -> bool:
        return self._items.pop(item_id, None) is not None

    def count(self, patient_id: str | None = None) -> int:
        if patient_id:
            return sum(1 for i in self._items.values() if i.patient_id == patient_id)
        return len(self._items)

    def count_by_state(self, state: BurnState) -> int:
        return sum(1 for i in self._items.values() if i.burn_state == state)

    def all_patient_ids(self) -> list[str]:
        return list({i.patient_id for i in self._items.values()})

    def flush_to_sqlite(self) -> None:
        """Persist current state to SQLite (for post-simulation inspection)."""
        conn = sqlite3.connect(self._db_path)
        conn.executescript(_SCHEMA)
        conn.execute("DELETE FROM items")
        conn.executemany(
            "INSERT INTO items (id, patient_id, data_type, timestamp, value, "
            "source_device, burn_state, burn_eligible_at, created_at, classified_at, "
            "delivered_at, burned_at, held) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            [
                (i.id, i.patient_id, i.data_type.value, i.timestamp,
                 json.dumps(i.value), i.source_device, i.burn_state.value,
                 i.burn_eligible_at, i.created_at, i.classified_at,
                 i.delivered_at, i.burned_at, int(i.held))
                for i in self._items.values()
            ],
        )
        conn.commit()
        conn.close()

    def close(self) -> None:
        self.flush_to_sqlite()


class WorldStoreManager:
    """Manages all six world stores."""

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.stores: dict[World, WorldStore] = {}
        for w in World:
            self.stores[w] = WorldStore(w, base_dir)

    def __getitem__(self, world: World) -> WorldStore:
        return self.stores[world]

    def close_all(self) -> None:
        for s in self.stores.values():
            s.close()
