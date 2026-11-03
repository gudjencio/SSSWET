"""Bounded deterministic cache for pure research computations."""
from __future__ import annotations

import hashlib
import json


class ResultCache:
    def __init__(self, max_entries: int = 256):
        if max_entries < 1:
            raise ValueError("max_entries must be positive")
        self.max_entries = max_entries
        self._data = {}

    def _key(self, payload: dict) -> str:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(encoded.encode()).hexdigest()

    def get(self, payload: dict):
        return self._data.get(self._key(payload))

    def put(self, payload: dict, result):
        key = self._key(payload)
        if key not in self._data and len(self._data) >= self.max_entries:
            self._data.pop(next(iter(self._data)))
        self._data[key] = result
        return key

    def stats(self) -> dict:
        return {"entries": len(self._data), "max_entries": self.max_entries, "bounded": True}
