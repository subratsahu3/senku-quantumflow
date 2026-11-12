"""
Demo 1: Resilient Speculative Microservice RPC Gateway.

Demonstrates how QuantumFlow eliminates p99 latency spikes and packet loss
by executing speculative request realities concurrently and collapsing
onto the optimal healthy timeline.
"""

import asyncio
import random
import time
from quantumflow import Multiverse, CollapseStrategy, Timeline


async def run_resilient_gateway_demo():
    print("\n" + "="*70)
    print("  DEMO 1: SPECULATIVE ZERO-LATENCY RESILIENT GATEWAY")
    print("="*70)

    mv = Multiverse(name="GatewayCosmos")
    mv.set_root_state("processed_orders", 0)
    mv.set_root_state("gateway_status", "ONLINE")

    # Invariant: if status is set, response status must be 200
    mv.register_invariant(
        "ResponseIntegrity",
        lambda state: "last_status" not in state or state["last_status"] == 200,
        "Order response failed HTTP status invariant (must be 200)"
    )

    print("\n[*] Incoming User Request: POST /api/v1/orders (Payment: $250.00)")
    print("[*] Spawning 3 concurrent speculative universes across multi-region mesh...")

    async def path_primary_rpc(tl: Timeline):
        """Simulates primary upstream RPC experiencing severe network partition / packet corruption."""
        await asyncio.sleep(0.08)
        # Simulate network packet corruption
        tl.mutate("last_status", 502) # Bad gateway!
        tl.mutate("routed_via", "us-east-primary")
        tl.metrics["latency"] = 80
        # This will violate the ResponseIntegrity invariant and cause decoherence!

    async def path_hedged_replica(tl: Timeline):
        """Hedged secondary replica with sub-millisecond route."""
        await asyncio.sleep(0.03)
        tl.mutate("last_status", 200)
        tl.mutate("routed_via", "us-central-replica")
        tl.mutate("processed_orders", tl.read("processed_orders", 0) + 1)
        tl.mutate("last_order_id", "ORD-88219")
        tl.metrics["latency"] = 30
        return {"orderId": "ORD-88219", "status": "APPROVED", "region": "us-central"}

    async def path_edge_cache_interpolator(tl: Timeline):
        """Speculative edge cache fallback."""
        await asyncio.sleep(0.05)
        tl.mutate("last_status", 200)
        tl.mutate("routed_via", "edge-cache-proxy")
        tl.mutate("processed_orders", tl.read("processed_orders", 0) + 1)
        tl.mutate("last_order_id", "ORD-88219-CACHED")
        tl.metrics["latency"] = 50
        return {"orderId": "ORD-88219-CACHED", "status": "APPROVED", "region": "edge"}

    tasks = {
        "Primary-RPC (Volatile)": path_primary_rpc,
        "Hedged-Replica (Optimized)": path_hedged_replica,
        "Edge-Cache (Fallback)": path_edge_cache_interpolator,
    }

    t0 = time.perf_counter()
    winner, result = await mv.run_superposition(
        tasks=tasks,
        strategy=CollapseStrategy.FASTEST_VALID
    )
    elapsed = (time.perf_counter() - t0) * 1000.0

    print(f"\n[★] WAVEFUNCTION COLLAPSE COMPLETED in {elapsed:.1f}ms")
    print(f"    Winning Reality:     '{winner.name}' (ID: {winner.id})")
    print(f"    Observed Result:     {result}")
    print(f"    Canonical State:     {mv.root_memory.to_dict()}")
    print("\n[*] Audit of Alternate Realities:")
    for tid, tl in mv._timelines.items():
        symbol = "★" if tl.status == "COLLAPSED" else ("✗" if tl.status == "DECOHERENT" else "◌")
        print(f"    [{symbol}] {tl.name:<30} Status: {tl.status:<12} Latency: {tl.latency_ms:.1f}ms Error: {tl.error or 'None'}")


if __name__ == "__main__":
    asyncio.run(run_resilient_gateway_demo())
