"""
QuantumFlow - Quantum Entanglement Engine.

Allows selective state variables (such as cancellation signals, distributed locks,
or shared invariants) to be quantum-entangled across otherwise strictly isolated
speculative timelines. When an entangled variable is mutated in one timeline,
the mutation teleports instantaneously to all entangled sibling universes.
"""

from __future__ import annotations
import threading
from typing import Any, Dict, List, Set
from quantumflow.core.timeline import Timeline


class EntanglementHub:
    """Coordinates instantaneous state teleportation for entangled keys across timelines."""

    def __init__(self):
        self._entangled_keys: Set[str] = set()
        self._timelines: List[Timeline] = []
        self._lock = threading.RLock()

    def register_key(self, key: str) -> None:
        """Mark a state variable as entangled across all participating timelines."""
        with self._lock:
            self._entangled_keys.add(key)

    def bind_timeline(self, timeline: Timeline) -> None:
        """Bind a timeline into the entanglement field."""
        with self._lock:
            if timeline not in self._timelines:
                self._timelines.append(timeline)

    def broadcast_mutation(self, source_timeline_id: str, key: str, value: Any) -> int:
        """
        Teleports an entangled mutation to all sibling timelines.
        Returns the number of timelines updated.
        """
        with self._lock:
            if key not in self._entangled_keys:
                return 0

            count = 0
            for tl in self._timelines:
                if tl.id != source_timeline_id:
                    # Direct shadow memory mutation bypassing isolation for this specific key
                    tl.memory.set(key, value)
                    tl.log_event("ENTANGLED_SYNC", f"Received teleported mutation for '{key}' from {source_timeline_id}")
                    count += 1
            return count

    def is_entangled(self, key: str) -> bool:
        with self._lock:
            return key in self._entangled_keys
