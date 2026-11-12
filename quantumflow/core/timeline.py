"""
QuantumFlow - Timeline Entity.

Represents an individual speculative universe with isolated memory,
causal event logs, entropy tracking, and decoherence status.
"""

from __future__ import annotations
import enum
import time
import uuid
from typing import Any, Dict, List, Optional
from quantumflow.core.memory import TemporalMemory
from quantumflow.core.invariants import DecoherenceError, InvariantRegistry


class TimelineStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUPERPOSED = "SUPERPOSED"
    COLLAPSED = "COLLAPSED"        # Selected by wavefunction collapse -> committed to root reality
    DECOHERENT = "DECOHERENT"      # Invariant broken / crashed / disqualified
    DISSOLVED = "DISSOLVED"        # Cleanly pruned because another timeline was chosen


class Timeline:
    """
    An isolated branch of execution.
    Holds its own copy-on-write memory scope and causal event telemetry.
    """

    def __init__(
        self,
        name: str,
        parent_id: Optional[str] = None,
        parent_memory: Optional[TemporalMemory] = None,
        timeline_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = timeline_id or f"tl-{uuid.uuid4().hex[:8]}"
        self.name = name
        self.parent_id = parent_id or "root"
        self.status = TimelineStatus.PENDING
        self.memory = TemporalMemory(parent=parent_memory, name=self.name)
        self.invariants = InvariantRegistry()
        
        # Telemetry & Metrics
        self.created_at = time.time()
        self.closed_at: Optional[float] = None
        self.latency_ms: float = 0.0
        self.entropy: float = 0.0
        self.metrics: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = metadata or {}
        
        # Execution outcome
        self.result: Any = None
        self.error: Optional[str] = None
        
        # Causal event log
        self.events: List[Dict[str, Any]] = []
        self.log_event("FORKED", f"Spawned timeline '{self.name}' from parent '{self.parent_id}'")

    def log_event(self, event_type: str, detail: str) -> None:
        """Append to timeline's causal log."""
        self.events.append({
            "timestamp": time.time(),
            "type": event_type,
            "detail": detail
        })

    def mutate(self, key: str, value: Any) -> None:
        """Mutate a key in this timeline's local memory and adjust entropy."""
        self.memory.set(key, value)
        self.entropy += 0.05
        self.log_event("MUTATION", f"set {key} = {value}")

    def read(self, key: str, default: Any = None) -> Any:
        """Read a key from this timeline's memory scope."""
        return self.memory.get(key, default)

    def validate_invariants(self) -> None:
        """
        Validate all invariants for this timeline against current state.
        Marks timeline as DECOHERENT if an invariant fails.
        """
        try:
            current_state = self.memory.to_dict()
            self.invariants.validate_all(current_state, timeline_id=self.id)
        except DecoherenceError as err:
            self.mark_decoherent(str(err))
            raise

    def mark_decoherent(self, reason: str) -> None:
        """Flag timeline as decoherent/invalid."""
        self.status = TimelineStatus.DECOHERENT
        self.closed_at = time.time()
        self.error = reason
        self.log_event("DECOHERENCE", reason)

    def mark_dissolved(self, winning_timeline_id: str) -> None:
        """Flag timeline as dissolved following collapse of another branch."""
        if self.status != TimelineStatus.DECOHERENT:
            self.status = TimelineStatus.DISSOLVED
            self.closed_at = time.time()
            self.log_event("DISSOLVED", f"Dissolved; timeline '{winning_timeline_id}' collapsed to reality")

    def mark_collapsed(self) -> Dict[str, Any]:
        """
        Wavefunction collapse operator: commits local deltas to parent memory.
        """
        self.validate_invariants()
        self.status = TimelineStatus.COLLAPSED
        self.closed_at = time.time()
        committed_deltas = self.memory.commit_to_parent()
        self.log_event("COLLAPSED", f"Wavefunction collapsed. Committed {len(committed_deltas)} deltas to parent.")
        return committed_deltas

    def to_dict(self) -> Dict[str, Any]:
        """Serialize timeline for REST API, telemetry, or dashboard visualizer."""
        return {
            "id": self.id,
            "name": self.name,
            "parentId": self.parent_id,
            "status": self.status.value,
            "createdAt": self.created_at,
            "closedAt": self.closed_at,
            "latencyMs": round(self.latency_ms, 2),
            "entropy": round(self.entropy, 3),
            "deltasCount": self.memory.delta_count(),
            "deltas": self.memory.get_local_deltas(),
            "metrics": self.metrics,
            "metadata": self.metadata,
            "error": self.error,
            "events": self.events,
            "stateSnapshot": self.memory.to_dict(),
            "fingerprint": self.memory.compute_fingerprint()[:12]
        }

    def __repr__(self) -> str:
        return f"<Timeline {self.id} '{self.name}' status={self.status.value} entropy={self.entropy:.2f}>"
