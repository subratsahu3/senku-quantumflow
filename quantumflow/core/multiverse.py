"""
QuantumFlow - Multiverse Core Orchestrator.

Manages root canonical reality, spawns concurrent speculative universes,
tracks timeline lifecycles, and executes Wavefunction Collapse to select
and commit the optimal reality.
"""

from __future__ import annotations
import asyncio
from contextlib import contextmanager
import functools
import inspect
import random
import threading
import time
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union

from quantumflow.core.memory import TemporalMemory
from quantumflow.core.timeline import Timeline, TimelineStatus
from quantumflow.core.invariants import InvariantRegistry, DecoherenceError
from quantumflow.core.entanglement import EntanglementHub
from quantumflow.causality.paradox import ParadoxSentinel, ParadoxConflict


class NoValidTimelineError(Exception):
    """Raised when all speculative branches suffer decoherence or failure."""
    pass


class CollapseStrategy:
    """Standard collapse heuristics."""

    @staticmethod
    def FASTEST_VALID(candidates: List[Timeline]) -> Timeline:
        """Selects the first valid timeline that finished with lowest latency."""
        return min(candidates, key=lambda t: t.latency_ms)

    @staticmethod
    def LOWEST_ENTROPY(candidates: List[Timeline]) -> Timeline:
        """Selects the timeline with the minimal entropy / disturbance."""
        return min(candidates, key=lambda t: t.entropy)

    @staticmethod
    def MAX_METRIC(key: str) -> Callable[[List[Timeline]], Timeline]:
        """Factory for maximizing a specific metric key."""
        def strategy(candidates: List[Timeline]) -> Timeline:
            valid = [c for c in candidates if key in c.metrics]
            if not valid:
                return candidates[0]
            return max(valid, key=lambda t: t.metrics[key])
        return strategy

    @staticmethod
    def MIN_METRIC(key: str) -> Callable[[List[Timeline]], Timeline]:
        """Factory for minimizing a specific metric key."""
        def strategy(candidates: List[Timeline]) -> Timeline:
            valid = [c for c in candidates if key in c.metrics]
            if not valid:
                return candidates[0]
            return min(valid, key=lambda t: t.metrics[key])
        return strategy


class Multiverse:
    """
    The Multiverse Engine. Manages root reality, forks speculative timelines,
    and conducts wavefunction collapses.
    """

    def __init__(self, name: str = "PrimeUniverse"):
        self.name = name
        self.root_memory = TemporalMemory(parent=None, name="root_reality")
        self.global_invariants = InvariantRegistry()
        self.entanglement_hub = EntanglementHub()
        self._timelines: Dict[str, Timeline] = {}
        self._lock = threading.RLock()
        self._subscribers: List[Callable[[Dict[str, Any]], None]] = []
        self._collapse_history: List[Dict[str, Any]] = []

    def set_root_state(self, key: str, value: Any) -> None:
        """Initialize or update canonical reality state directly."""
        with self._lock:
            self.root_memory.set(key, value)
            self._notify_subscribers({
                "event": "ROOT_STATE_UPDATE",
                "key": key,
                "value": value,
                "timestamp": time.time()
            })

    def get_root_state(self, key: str, default: Any = None) -> Any:
        return self.root_memory.get(key, default)

    def subscribe(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register an event listener (for dashboard, logging, or alerting)."""
        with self._lock:
            self._subscribers.append(callback)

    def _notify_subscribers(self, payload: Dict[str, Any]) -> None:
        for sub in list(self._subscribers):
            try:
                sub(payload)
            except Exception:
                pass

    def register_invariant(self, name: str, predicate: Callable[[Dict[str, Any]], bool], error_msg: str = "") -> None:
        """Register a universal invariant that every timeline must respect."""
        self.global_invariants.register(name, predicate, error_msg)

    def entangle(self, key: str) -> None:
        """Mark a state variable as entangled across all speculative timelines."""
        self.entanglement_hub.register_key(key)

    def mutate_entangled(self, timeline: Timeline, key: str, value: Any) -> int:
        """
        Mutates key in local timeline and teleports it to all sibling timelines.
        """
        timeline.mutate(key, value)
        synced_count = self.entanglement_hub.broadcast_mutation(timeline.id, key, value)
        self._notify_subscribers({
            "event": "QUANTUM_ENTANGLEMENT_SYNC",
            "sourceTimeline": timeline.id,
            "key": key,
            "syncedBranches": synced_count,
            "timestamp": time.time()
        })
        return synced_count

    @contextmanager
    def branch(self, name: str = "speculative_branch", auto_commit: bool = False):
        """
        Context manager for temporary speculative timeline execution.
        If auto_commit is True and no exception is raised, commits to parent reality.
        """
        tl = self.fork(name=name)
        try:
            yield tl
            if auto_commit:
                tl.mark_collapsed()
        except Exception as exc:
            tl.mark_decoherent(str(exc))
            raise
        finally:
            if tl.status == TimelineStatus.PENDING:
                tl.mark_dissolved("context_exit")

    def superposition(self, branches: List[str], strategy: Callable[[List[Timeline]], Timeline] = CollapseStrategy.FASTEST_VALID):
        """
        Function decorator for declarative multiverse execution.
        Decorated async function must accept `(timeline, branch_name, *args, **kwargs)`.
        """
        def decorator(fn):
            @functools.wraps(fn)
            async def wrapper(*args, **kwargs):
                tasks = {
                    b_name: (lambda b: (lambda tl: fn(tl, b, *args, **kwargs)))(b_name)
                    for b_name in branches
                }
                winner, result = await self.run_superposition(tasks=tasks, strategy=strategy)
                return result
            return wrapper
        return decorator

    def inspect_conflicts(self) -> List[Dict[str, Any]]:
        """Run paradox and concurrency conflict sentinel across active timelines."""
        conflicts = ParadoxSentinel.inspect(list(self._timelines.values()))
        return [c.to_dict() for c in conflicts]

    def inject_chaos(self, target: str = "random", chaos_type: str = "LATENCY_SPIKE") -> Optional[Dict[str, Any]]:
        """
        Inject synthetic entropy or faults into active superpositions.
        Used for chaos engineering, resilience auditing, and live UI testing.
        """
        active = [t for t in self._timelines.values() if t.status == TimelineStatus.SUPERPOSED]
        if not active:
            return None

        victim = random.choice(active) if target == "random" else self._timelines.get(target)
        if not victim:
            return None

        if chaos_type == "LATENCY_SPIKE":
            victim.latency_ms += random.uniform(150, 400)
            victim.entropy += 0.5
            victim.log_event("CHAOS_INJECTION", "Synthetic latency dilation storm applied")
        elif chaos_type == "CORRUPTION":
            victim.mutate("packet_checksum", "0xDEADBEEF")
            victim.entropy += 0.8
            victim.mark_decoherent("Cosmic ray bitflip / data corruption chaos injected")
        elif chaos_type == "INVARIANT_BREACH":
            victim.mutate("balance", -9999)
            victim.mark_decoherent("Synthetic balance drain chaos injected")

        report = {
            "timelineId": victim.id,
            "timelineName": victim.name,
            "chaosType": chaos_type,
            "newStatus": victim.status.value,
            "entropy": round(victim.entropy, 2),
            "timestamp": time.time()
        }
        self._notify_subscribers({
            "event": "CHAOS_INJECTED",
            "report": report
        })
        return report

    def fork(self, name: str, parent: Optional[Timeline] = None, metadata: Optional[Dict[str, Any]] = None) -> Timeline:
        """
        Fork a new speculative timeline from root reality or an existing timeline.
        """
        with self._lock:
            parent_id = parent.id if parent else "root"
            parent_mem = parent.memory if parent else self.root_memory

            tl = Timeline(
                name=name,
                parent_id=parent_id,
                parent_memory=parent_mem,
                metadata=metadata
            )

            # Inherit global invariants
            for inv in self.global_invariants:
                tl.invariants.register(inv.name, inv.predicate, inv.error_msg)

            self.entanglement_hub.bind_timeline(tl)
            self._timelines[tl.id] = tl
            self._notify_subscribers({
                "event": "TIMELINE_FORKED",
                "timeline": tl.to_dict(),
                "timestamp": time.time()
            })
            return tl

    async def execute_timeline_task(
        self,
        timeline: Timeline,
        task_fn: Callable[[Timeline], Coroutine[Any, Any, Any]]
    ) -> Any:
        """
        Executes a task inside a speculative timeline while measuring latency,
        entropy, and invariants.
        """
        timeline.status = TimelineStatus.SUPERPOSED
        self._notify_subscribers({
            "event": "TIMELINE_SUPERPOSED",
            "timelineId": timeline.id,
            "timestamp": time.time()
        })

        t_start = time.perf_counter()
        try:
            # Validate invariants at start of timeline
            timeline.validate_invariants()

            res = task_fn(timeline)
            if inspect.isawaitable(res):
                res = await res

            timeline.result = res
            # Validate invariants at end of timeline
            timeline.validate_invariants()

        except DecoherenceError as dec_err:
            timeline.mark_decoherent(str(dec_err))
            self._notify_subscribers({
                "event": "TIMELINE_DECOHERED",
                "timelineId": timeline.id,
                "reason": str(dec_err),
                "timestamp": time.time()
            })
            return None
        except Exception as exc:
            timeline.mark_decoherent(f"Runtime exception: {str(exc)}")
            self._notify_subscribers({
                "event": "TIMELINE_DECOHERED",
                "timelineId": timeline.id,
                "reason": f"Exception: {str(exc)}",
                "timestamp": time.time()
            })
            return None
        finally:
            timeline.latency_ms = (time.perf_counter() - t_start) * 1000.0

        return timeline.result

    async def run_superposition(
        self,
        tasks: Dict[str, Callable[[Timeline], Coroutine[Any, Any, Any]]],
        strategy: Callable[[List[Timeline]], Timeline] = CollapseStrategy.FASTEST_VALID,
        metadata_map: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Tuple[Timeline, Any]:
        """
        Spawns multiple timelines concurrently in superposition, executes their tasks,
        evaluates outcomes, applies the collapse strategy, and commits the winner.
        """
        timelines: List[Timeline] = []
        coros = []

        for name, task_fn in tasks.items():
            meta = (metadata_map or {}).get(name, {})
            tl = self.fork(name=name, metadata=meta)
            timelines.append(tl)
            coros.append(self.execute_timeline_task(tl, task_fn))

        # Run all speculative realities concurrently
        await asyncio.gather(*coros, return_exceptions=True)

        # Collect surviving coherent timelines
        coherent = [t for t in timelines if t.status == TimelineStatus.SUPERPOSED and t.error is None]

        if not coherent:
            raise NoValidTimelineError(
                f"All {len(timelines)} speculative timelines suffered decoherence or exceptions: "
                f"{[t.error for t in timelines]}"
            )

        # Apply Wavefunction Collapse
        winner = strategy(coherent)
        committed = winner.mark_collapsed()

        # Dissolve competing timelines
        for t in timelines:
            if t.id != winner.id:
                t.mark_dissolved(winner.id)

        collapse_record = {
            "winner": winner.to_dict(),
            "committedDeltas": committed,
            "totalTimelines": len(timelines),
            "survivingTimelines": len(coherent),
            "timestamp": time.time()
        }
        self._collapse_history.append(collapse_record)

        self._notify_subscribers({
            "event": "WAVEFUNCTION_COLLAPSED",
            "winner": winner.to_dict(),
            "allTimelines": [t.to_dict() for t in timelines],
            "timestamp": time.time()
        })

        return winner, winner.result

    def get_topology(self) -> Dict[str, Any]:
        """Return complete snapshot of the Multiverse for visualization."""
        with self._lock:
            return {
                "multiverse": self.name,
                "rootState": self.root_memory.to_dict(),
                "rootFingerprint": self.root_memory.compute_fingerprint()[:12],
                "invariants": [inv.name for inv in self.global_invariants],
                "timelines": {tid: tl.to_dict() for tid, tl in self._timelines.items()},
                "collapseHistory": self._collapse_history[-20:]
            }

    def clear_closed_timelines(self) -> int:
        """Clean up dissolved or old timelines to prevent memory bloat."""
        with self._lock:
            to_remove = [
                tid for tid, tl in self._timelines.items()
                if tl.status in (TimelineStatus.DISSOLVED, TimelineStatus.DECOHERENT)
            ]
            for tid in to_remove:
                del self._timelines[tid]
            return len(to_remove)
