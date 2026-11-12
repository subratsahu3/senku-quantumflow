"""
Demo 4: Quantum Entanglement & Fast-Cancel Synchronization.

Demonstrates state teleportation across isolated timelines using
the Entanglement Hub, and verifies causal integrity using Paradox Sentinel.
"""

import asyncio
import time
from quantumflow import Multiverse, CollapseStrategy, ParadoxSentinel


async def run_entanglement_demo():
    print("\n" + "="*70)
    print("  DEMO 4: QUANTUM ENTANGLEMENT & CROSS-TIMELINE TELEPORTATION")
    print("="*70)

    mv = Multiverse(name="EntangledCosmos")
    mv.set_root_state("active_job", "JOB-909")
    mv.set_root_state("execution_status", "PENDING")

    # Mark cancellation beacon as quantum-entangled
    mv.entangle("abort_signal")

    print("[*] State variable 'abort_signal' is now QUANTUM-ENTANGLED.")
    print("[*] Forking 2 isolated speculative branches (Heavy-Compute and Watchdog)...")

    async def path_heavy_compute(tl):
        """Simulates an expensive 10-step distributed calculation."""
        for step in range(1, 10):
            await asyncio.sleep(0.02)
            # Check if an entangled abort signal arrived
            if tl.read("abort_signal"):
                print(f"    [!] Heavy-Compute caught teleported abort signal at step {step}! Aborting early.")
                tl.mutate("execution_status", "ABORTED_BY_WATCHDOG")
                return "ABORTED"
            tl.mutate("compute_step", step)
        tl.mutate("execution_status", "COMPLETED")
        return "COMPLETED"

    async def path_watchdog(tl):
        """Monitors system telemetry. Detects a severe external spike and fires entangled cancel!"""
        await asyncio.sleep(0.05)
        print("    [⚡] Watchdog detected external telemetry anomaly! Teleporting 'abort_signal = True'...")
        mv.mutate_entangled(tl, "abort_signal", True)
        tl.mutate("watchdog_flagged", True)
        return "TRIGGERED_ABORT"

    tasks = {
        "Heavy-Compute": path_heavy_compute,
        "Watchdog-Monitor": path_watchdog
    }

    winner, result = await mv.run_superposition(
        tasks=tasks,
        strategy=CollapseStrategy.FASTEST_VALID
    )

    print(f"\n[★] COLLAPSE COMPLETE: Reality selected '{winner.name}'")
    print(f"    Final Root State: {mv.root_memory.to_dict()}")

    # Run Paradox Sentinel to verify zero unhandled collisions
    conflicts = mv.inspect_conflicts()
    print(f"[*] Paradox Sentinel Scan: {len(conflicts)} state collisions detected.")


if __name__ == "__main__":
    asyncio.run(run_entanglement_demo())
