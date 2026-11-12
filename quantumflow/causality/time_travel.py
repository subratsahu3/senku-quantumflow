"""
QuantumFlow - Time Travel & Counterfactual Analysis Engine.

Allows engineers to rewind the universe to historical checkpoints,
inject counterfactual mutations or synthetic chaos ("What if the database timed out?"),
and compute the divergence diff between actual history and counterfactual timelines.
"""

from __future__ import annotations
import copy
import time
from typing import Any, Callable, Dict, List, Optional
from quantumflow.core.memory import TemporalMemory
from quantumflow.core.multiverse import Multiverse
from quantumflow.core.timeline import Timeline


class Checkpoint:
    """An immutable temporal snapshot of the universe."""
    def __init__(self, name: str, state_snapshot: Dict[str, Any], timestamp: float):
        self.name = name
        self.state_snapshot = copy.deepcopy(state_snapshot)
        self.timestamp = timestamp


class CounterfactualResult:
    """Results of a counterfactual 'What-If' simulation."""
    def __init__(
        self,
        base_checkpoint: str,
        counterfactual_name: str,
        injected_perturbations: Dict[str, Any],
        actual_final_state: Dict[str, Any],
        counterfactual_final_state: Dict[str, Any],
        divergence_diff: Dict[str, Dict[str, Any]],
        diverged_keys: List[str]
    ):
        self.base_checkpoint = base_checkpoint
        self.counterfactual_name = counterfactual_name
        self.injected_perturbations = injected_perturbations
        self.actual_final_state = actual_final_state
        self.counterfactual_final_state = counterfactual_final_state
        self.divergence_diff = divergence_diff
        self.diverged_keys = diverged_keys

    def summary(self) -> str:
        lines = [
            f"=== Counterfactual Divergence Analysis: '{self.counterfactual_name}' ===",
            f"Base Checkpoint: {self.base_checkpoint}",
            f"Perturbations: {self.injected_perturbations}",
            f"Diverged State Keys: {len(self.diverged_keys)} ({', '.join(self.diverged_keys)})",
            "--- Divergence Diffs ---"
        ]
        for key, diff in self.divergence_diff.items():
            lines.append(f"  Key '{key}':")
            lines.append(f"    Reality:        {diff.get('reality')}")
            lines.append(f"    Counterfactual: {diff.get('counterfactual')}")
        return "\n".join(lines)


class TimeTravelEngine:
    """Manages checkpoints and runs counterfactual simulations."""

    def __init__(self, multiverse: Multiverse):
        self.multiverse = multiverse
        self.checkpoints: Dict[str, Checkpoint] = {}

    def checkpoint(self, name: str) -> Checkpoint:
        """Capture immutable checkpoint of current root state."""
        current_state = self.multiverse.root_memory.to_dict()
        cp = Checkpoint(name=name, state_snapshot=current_state, timestamp=time.time())
        self.checkpoints[name] = cp
        return cp

    def simulate_counterfactual(
        self,
        base_checkpoint_name: str,
        simulation_name: str,
        perturbations: Dict[str, Any],
        workflow_fn: Callable[[TemporalMemory], None]
    ) -> CounterfactualResult:
        """
        Runs a 'What-If' counterfactual experiment starting from a checkpoint.
        Injects perturbations, runs the workflow function, and compares against actual reality.
        """
        if base_checkpoint_name not in self.checkpoints:
            raise ValueError(f"Checkpoint '{base_checkpoint_name}' not found.")

        base_cp = self.checkpoints[base_checkpoint_name]
        
        # Create an isolated sandbox memory seeded with the checkpoint state
        sim_mem = TemporalMemory(parent=None, name=f"cf-{simulation_name}")
        for k, v in base_cp.state_snapshot.items():
            sim_mem.set(k, copy.deepcopy(v))

        # Inject counterfactual perturbations
        for k, v in perturbations.items():
            sim_mem.set(k, copy.deepcopy(v))

        # Run the workflow in the counterfactual timeline
        workflow_fn(sim_mem)

        # Compute divergence against current actual reality
        actual_state = self.multiverse.root_memory.to_dict()
        sim_final_state = sim_mem.to_dict()

        divergence_diff: Dict[str, Dict[str, Any]] = {}
        all_keys = set(actual_state.keys()) | set(sim_final_state.keys())
        diverged_keys: List[str] = []

        for key in all_keys:
            r_val = actual_state.get(key)
            c_val = sim_final_state.get(key)
            if r_val != c_val:
                diverged_keys.append(key)
                divergence_diff[key] = {
                    "reality": r_val,
                    "counterfactual": c_val
                }

        return CounterfactualResult(
            base_checkpoint=base_checkpoint_name,
            counterfactual_name=simulation_name,
            injected_perturbations=perturbations,
            actual_final_state=actual_state,
            counterfactual_final_state=sim_final_state,
            divergence_diff=divergence_diff,
            diverged_keys=diverged_keys
        )
