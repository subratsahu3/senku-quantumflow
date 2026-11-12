"""
QuantumFlow - Causal Paradox & Concurrency Conflict Sentinel.

Detects subtle race conditions, type divergence, and write-write state
contradictions across concurrently superposed execution branches.
"""

from __future__ import annotations
from typing import Any, Dict, List, Set
from quantumflow.core.timeline import Timeline


class ConflictType:
    WRITE_WRITE_COLLISION = "WRITE_WRITE_COLLISION"
    TYPE_MUTATION_DIVERGENCE = "TYPE_MUTATION_DIVERGENCE"
    CONTRADICTORY_INVARIANTS = "CONTRADICTORY_INVARIANTS"


class ParadoxConflict:
    def __init__(self, conflict_type: str, key: str, timelines: List[str], details: Dict[str, Any]):
        self.conflict_type = conflict_type
        self.key = key
        self.timelines = timelines
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.conflict_type,
            "key": self.key,
            "timelines": self.timelines,
            "details": self.details
        }


class ParadoxSentinel:
    """
    Analyzes active speculative timelines for causal paradoxes and state drift.
    """

    @staticmethod
    def inspect(timelines: List[Timeline]) -> List[ParadoxConflict]:
        conflicts: List[ParadoxConflict] = []
        if len(timelines) < 2:
            return conflicts

        # Map: key -> list of (timeline_id, value, value_type)
        key_mutations: Dict[str, List[Dict[str, Any]]] = {}

        for tl in timelines:
            deltas = tl.memory.get_local_deltas()
            for key, val in deltas.items():
                if key not in key_mutations:
                    key_mutations[key] = []
                key_mutations[key].append({
                    "timeline_id": tl.id,
                    "timeline_name": tl.name,
                    "value": val,
                    "type": type(val).__name__
                })

        for key, mutations in key_mutations.items():
            if len(mutations) > 1:
                # Check for distinct values written by multiple timelines
                distinct_values = {str(m["value"]) for m in mutations}
                distinct_types = {m["type"] for m in mutations}

                if len(distinct_types) > 1:
                    conflicts.append(ParadoxConflict(
                        conflict_type=ConflictType.TYPE_MUTATION_DIVERGENCE,
                        key=key,
                        timelines=[m["timeline_id"] for m in mutations],
                        details={
                            "types_found": list(distinct_types),
                            "mutations": mutations
                        }
                    ))
                elif len(distinct_values) > 1:
                    conflicts.append(ParadoxConflict(
                        conflict_type=ConflictType.WRITE_WRITE_COLLISION,
                        key=key,
                        timelines=[m["timeline_id"] for m in mutations],
                        details={
                            "competing_values": list(distinct_values),
                            "mutations": mutations
                        }
                    ))

        return conflicts

    @staticmethod
    def calculate_entropy_drift(t1: Timeline, t2: Timeline) -> float:
        """
        Calculates symmetric divergence score between two timelines (0.0 = identical, 1.0 = completely divergent).
        """
        d1 = t1.memory.get_local_deltas()
        d2 = t2.memory.get_local_deltas()
        all_keys = set(d1.keys()) | set(d2.keys())
        if not all_keys:
            return 0.0

        differences = 0
        for k in all_keys:
            if k not in d1 or k not in d2 or d1[k] != d2[k]:
                differences += 1

        return round(differences / len(all_keys), 4)
