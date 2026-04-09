"""Append-only, hash-chained audit logger."""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any


class AuditLogger:
    """Append-only JSON Lines audit log with SHA-256 hash chain."""

    def __init__(self, log_path: str):
        self._path = log_path
        self._prev_hash = "0" * 64  # genesis hash
        self._count = 0
        os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
        # If file exists, recover the chain tail
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        self._prev_hash = entry["hash"]
                        self._count += 1

    def log(
        self,
        event_type: str,
        *,
        item_id: str = "",
        patient_id: str = "",
        world: str = "",
        data_type: str = "",
        details: dict[str, Any] | None = None,
        sim_time: float = 0.0,
    ) -> dict[str, Any]:
        entry = {
            "seq": self._count,
            "sim_time": sim_time,
            "event_type": event_type,
            "item_id": item_id,
            "patient_id": patient_id,
            "world": world,
            "data_type": data_type,
            "details": details or {},
            "prev_hash": self._prev_hash,
        }
        raw = json.dumps(entry, sort_keys=True, separators=(",", ":"))
        entry["hash"] = hashlib.sha256(raw.encode()).hexdigest()
        with open(self._path, "a") as f:
            f.write(json.dumps(entry, separators=(",", ":")) + "\n")
        self._prev_hash = entry["hash"]
        self._count += 1
        return entry

    def verify_chain(self) -> tuple[bool, int]:
        """Verify the hash chain. Returns (valid, entry_count)."""
        prev = "0" * 64
        count = 0
        with open(self._path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                if entry["prev_hash"] != prev:
                    return False, count
                check = dict(entry)
                stored_hash = check.pop("hash")
                raw = json.dumps(check, sort_keys=True, separators=(",", ":"))
                computed = hashlib.sha256(raw.encode()).hexdigest()
                if computed != stored_hash:
                    return False, count
                prev = stored_hash
                count += 1
        return True, count

    def query(
        self,
        item_id: str | None = None,
        patient_id: str | None = None,
        event_type: str | None = None,
        world: str | None = None,
    ) -> list[dict[str, Any]]:
        results = []
        if not os.path.exists(self._path):
            return results
        with open(self._path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                if item_id and entry.get("item_id") != item_id:
                    continue
                if patient_id and entry.get("patient_id") != patient_id:
                    continue
                if event_type and entry.get("event_type") != event_type:
                    continue
                if world and entry.get("world") != world:
                    continue
                results.append(entry)
        return results

    @property
    def count(self) -> int:
        return self._count
