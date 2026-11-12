"""
QuantumFlow - Live Visualizer Launcher & Multiverse Traffic Simulator.

Spins up the zero-dependency Dashboard Server on http://localhost:8080
and simulates continuous real-time speculative multiverse traffic.
"""

import asyncio
import os
import random
import sys
import time

# Ensure package is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quantumflow import Multiverse, CollapseStrategy, Timeline
from quantumflow.server.dashboard import DashboardServer


async def traffic_simulator(mv: Multiverse):
    """Generates continuous realistic speculative executions for the visualizer."""
    req_counter = 1
    endpoints = ["/v1/auth", "/v1/checkout", "/v1/telemetry", "/v1/pricing", "/v1/stream"]

    while True:
        req_counter += 1
        endpoint = random.choice(endpoints)
        order_val = random.randint(50, 500)

        async def branch_optimistic(tl: Timeline):
            await asyncio.sleep(random.uniform(0.04, 0.12))
            if random.random() < 0.35:
                # 35% chance of network fault causing decoherence
                tl.mutate("fault_injected", True)
                raise RuntimeError("Downstream packet loss spike")
            tl.mutate(f"req_{req_counter}_status", "200_OK")
            tl.mutate("active_route", "DirectMesh")
            tl.metrics["score"] = random.uniform(85, 99)
            return {"status": "SUCCESS", "route": "DirectMesh"}

        async def branch_redundant(tl: Timeline):
            await asyncio.sleep(random.uniform(0.06, 0.15))
            tl.mutate(f"req_{req_counter}_status", "200_OK")
            tl.mutate("active_route", "MultiRegionReplica")
            tl.metrics["score"] = random.uniform(80, 95)
            return {"status": "SUCCESS", "route": "MultiRegionReplica"}

        async def branch_conservative(tl: Timeline):
            await asyncio.sleep(random.uniform(0.08, 0.20))
            if random.random() < 0.2:
                # Invariant violation: simulated negative balance
                tl.mutate("balance", -50)
            else:
                tl.mutate(f"req_{req_counter}_status", "200_OK")
            tl.mutate("active_route", "ColdStorageFallback")
            tl.metrics["score"] = random.uniform(70, 85)
            return {"status": "SUCCESS", "route": "Fallback"}

        tasks = {
            f"Opt-{req_counter}": branch_optimistic,
            f"Replica-{req_counter}": branch_redundant,
            f"Fallback-{req_counter}": branch_conservative
        }

        try:
            winner, _ = await mv.run_superposition(
                tasks=tasks,
                strategy=CollapseStrategy.FASTEST_VALID
            )
        except Exception:
            pass

        # Cleanup older timelines periodically
        if len(mv._timelines) > 25:
            mv.clear_closed_timelines()

        await asyncio.sleep(random.uniform(1.5, 3.0))


def main():
    mv = Multiverse(name="QuantumFlow-Live")
    mv.set_root_state("cluster_id", "qflow-us-east-1")
    mv.set_root_state("system_health", "100%")
    mv.set_root_state("total_events_processed", 0)

    # Invariant: balance must be non-negative
    mv.register_invariant(
        "NonNegativeBalance",
        lambda state: state.get("balance", 0) >= 0,
        "Balance dipped below zero (Entropic violation)"
    )

    port = 8080
    server = DashboardServer(multiverse=mv, port=port)
    server.start()

    print("\n" + "="*70)
    print("  QUANTUMFLOW MULTIVERSE VISUALIZER STARTED")
    print(f"  Open your browser to:  http://localhost:{port}")
    print("  Press Ctrl+C to terminate.")
    print("="*70 + "\n")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(traffic_simulator(mv))
    except KeyboardInterrupt:
        print("\nShutting down QuantumFlow visualizer...")
    finally:
        server.stop()


if __name__ == "__main__":
    main()
