"""
QuantumFlow - Temporal Copy-on-Write Memory Layer.

Provides isolated, hierarchical, transactional state storage for speculative
execution timelines. Allows concurrent speculative universes to mutate state
without cross-contamination or locking overhead.
"""

from __future__ import annotations
import copy
import hashlib
import json
import threading
from typing import Any, Dict, Iterator, List, Optional, Tuple

# Unique tombstone sentinel for deleted keys
_TOMBSTONE = object()


class MemoryParadoxError(Exception):
    """Raised when an illegal memory operation occurs, such as committing a stale delta."""
    pass


class TemporalMemory:
    """
    Copy-on-Write (CoW) hierarchical transactional state store.

    When forked from a parent TemporalMemory, reads traverse up the ancestry tree.
    Local mutations and deletions are captured exclusively in `_deltas`.
    Upon Wavefunction Collapse, deltas can be atomically merged into the parent.
    """

    def __init__(self, parent: Optional[TemporalMemory] = None, name: str = "root"):
        self.parent: Optional[TemporalMemory] = parent
        self.name: str = name
        self._deltas: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._version: int = 0
        self._mutation_log: List[Tuple[str, str, Any]] = []  # (op, key, val)

    def fork(self, child_name: str) -> TemporalMemory:
        """Create a speculative child memory scope."""
        with self._lock:
            return TemporalMemory(parent=self, name=child_name)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve value for key, checking local deltas first, then traversing ancestors.
        """
        with self._lock:
            if key in self._deltas:
                val = self._deltas[key]
                return default if val is _TOMBSTONE else copy.deepcopy(val)
            
            if self.parent is not None:
                return self.parent.get(key, default)
            
            return default

    def set(self, key: str, value: Any) -> None:
        """
        Set value in local memory. Deep-copies value to prevent accidental shared-mutation leaks.
        """
        with self._lock:
            self._deltas[key] = copy.deepcopy(value)
            self._version += 1
            self._mutation_log.append(("SET", key, copy.deepcopy(value)))

    def delete(self, key: str) -> bool:
        """
        Delete key in local memory scope (records tombstone).
        """
        with self._lock:
            if self.has(key):
                self._deltas[key] = _TOMBSTONE
                self._version += 1
                self._mutation_log.append(("DEL", key, None))
                return True
            return False

    def has(self, key: str) -> bool:
        """Check if key exists and has not been tombstoned."""
        with self._lock:
            if key in self._deltas:
                return self._deltas[key] is not _TOMBSTONE
            if self.parent is not None:
                return self.parent.has(key)
            return False

    def items(self) -> List[Tuple[str, Any]]:
        """Return all active key-value pairs visible in this temporal scope."""
        with self._lock:
            result = self.to_dict()
            return list(result.items())

    def to_dict(self) -> Dict[str, Any]:
        """
        Flatten the entire lineage into a single concrete dictionary snapshot.
        """
        with self._lock:
            if self.parent is not None:
                base = self.parent.to_dict()
            else:
                base = {}

            for k, v in self._deltas.items():
                if v is _TOMBSTONE:
                    base.pop(k, None)
                else:
                    base[k] = copy.deepcopy(v)
            return base

    def get_local_deltas(self) -> Dict[str, Any]:
        """Return only mutations made locally in this timeline."""
        with self._lock:
            clean = {}
            for k, v in self._deltas.items():
                clean[k] = "<DELETED>" if v is _TOMBSTONE else copy.deepcopy(v)
            return clean

    def delta_count(self) -> int:
        """Return the number of local mutations made in this memory scope."""
        with self._lock:
            return len(self._deltas)

    def rollback(self) -> None:
        """Discard all local mutations in this timeline."""
        with self._lock:
            self._deltas.clear()
            self._mutation_log.clear()
            self._version += 1

    def commit_to_parent(self) -> Dict[str, Any]:
        """
        Atomically flush all local deltas into the parent memory store.
        Used when this timeline's wavefunction collapses onto reality.
        """
        with self._lock:
            if self.parent is None:
                # Root memory has no parent; deltas are already at root
                return self.get_local_deltas()

            committed: Dict[str, Any] = {}
            with self.parent._lock:
                for k, v in self._deltas.items():
                    if v is _TOMBSTONE:
                        self.parent.delete(k)
                        committed[k] = "<DELETED>"
                    else:
                        self.parent.set(k, copy.deepcopy(v))
                        committed[k] = copy.deepcopy(v)
            return committed

    def compute_fingerprint(self) -> str:
        """
        Compute deterministic SHA-256 hash of the complete active state.
        Ensures cryptographic causal consistency and auditability.
        """
        with self._lock:
            full = self.to_dict()
            try:
                serialized = json.dumps(full, sort_keys=True, default=str)
            except Exception:
                serialized = str(sorted(full.items()))
            return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def __getitem__(self, key: str) -> Any:
        val = self.get(key, _TOMBSTONE)
        if val is _TOMBSTONE:
            raise KeyError(key)
        return val

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        if not self.delete(key):
            raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return self.has(key)

    def __repr__(self) -> str:
        return f"<TemporalMemory '{self.name}' deltas={len(self._deltas)} parent={self.parent.name if self.parent else None}>"
