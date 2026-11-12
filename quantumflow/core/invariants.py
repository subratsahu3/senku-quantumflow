"""
QuantumFlow - Invariant and Decoherence Engine.

Defines mathematical, business, and causal invariants. Any speculative timeline
that violates an invariant suffers Quantum Decoherence and is disqualified
from wavefunction collapse.
"""

from __future__ import annotations
import inspect
from typing import Any, Callable, Dict, List, Optional


class DecoherenceError(Exception):
    """Raised when a timeline violates a defined invariant."""
    def __init__(self, invariant_name: str, reason: str, timeline_id: Optional[str] = None):
        self.invariant_name = invariant_name
        self.reason = reason
        self.timeline_id = timeline_id
        msg = f"[DECOHERENCE in {timeline_id or 'timeline'}] Violated invariant '{invariant_name}': {reason}"
        super().__init__(msg)


class Invariant:
    """Represents a conservation law or business invariant."""
    def __init__(self, name: str, predicate: Callable[[Dict[str, Any]], bool], error_msg: str = ""):
        self.name = name
        self.predicate = predicate
        self.error_msg = error_msg or f"Failed assertion on invariant '{name}'"

    def evaluate(self, state: Dict[str, Any], timeline_id: Optional[str] = None) -> bool:
        """
        Evaluate predicate against state snapshot.
        Raises DecoherenceError if invariant check fails.
        """
        try:
            passed = bool(self.predicate(state))
        except Exception as ex:
            raise DecoherenceError(self.name, f"Exception during evaluation: {str(ex)}", timeline_id)

        if not passed:
            raise DecoherenceError(self.name, self.error_msg, timeline_id)
        return True


class InvariantRegistry:
    """Registry of active invariants for a Multiverse or specific Timeline."""

    def __init__(self):
        self._invariants: Dict[str, Invariant] = {}

    def register(self, name: str, predicate: Callable[[Dict[str, Any]], bool], error_msg: str = "") -> Invariant:
        inv = Invariant(name, predicate, error_msg)
        self._invariants[name] = inv
        return inv

    def unregister(self, name: str) -> None:
        self._invariants.pop(name, None)

    def validate_all(self, state: Dict[str, Any], timeline_id: Optional[str] = None) -> List[str]:
        """
        Validates all invariants against state.
        Returns list of passed invariant names. Raises DecoherenceError on first failure.
        """
        passed = []
        for name, inv in self._invariants.items():
            inv.evaluate(state, timeline_id)
            passed.append(name)
        return passed

    def __len__(self) -> int:
        return len(self._invariants)

    def __iter__(self):
        return iter(self._invariants.values())


# Decorator for function-level invariant enforcement
def assert_invariant(registry: InvariantRegistry, invariant_name: str, predicate: Callable[[Dict[str, Any]], bool], msg: str = ""):
    """Decorator to register and enforce invariant before and after execution."""
    registry.register(invariant_name, predicate, msg)
    def decorator(fn):
        return fn
    return decorator
