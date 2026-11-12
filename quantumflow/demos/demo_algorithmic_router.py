"""
Demo 2: Algorithmic Quantitative Order Router with Strict Invariant Guard.

Demonstrates multi-timeline financial routing where aggressive strategies
that violate risk invariants suffer decoherence, collapsing safely onto
the reality with maximum alpha.
"""

import asyncio
import time
from quantumflow import Multiverse, CollapseStrategy, Timeline


async def run_algorithmic_router_demo():
    print("\n" + "="*70)
    print("  DEMO 2: QUANTITATIVE SMART ORDER ROUTER WITH INVARIANT GUARD")
    print("="*70)

    mv = Multiverse(name="FinTechMultiverse")
    mv.set_root_state("cash_reserves", 1_000_000.00)
    mv.set_root_state("total_alpha_generated", 0.0)

    # Invariant: Portfolio cash reserves must never dip below 950,000 under any condition
    mv.register_invariant(
        "CapitalPreservation",
        lambda state: state.get("cash_reserves", 0) >= 950_000.00,
        "Solvency risk: cash reserves breached minimum threshold ($950,000.00)"
    )

    print("\n[*] Initial Portfolio Reality:")
    print(f"    Reserves: ${mv.get_root_state('cash_reserves'):,.2f}")
    print("[*] Dispatching order: 50,000 shares of NVDA across 4 speculative market venues...")

    async def strategy_aggressive_market_sweep(tl: Timeline):
        """Sweeps order books aggressively. Incurs catastrophic slippage violating capital reserve!"""
        await asyncio.sleep(0.02)
        # Heavy slippage consumes $65,000 cash, dropping reserve to $935,000
        tl.mutate("cash_reserves", 935_000.00)
        tl.mutate("shares_filled", 50000)
        tl.metrics["net_alpha"] = 14200.00
        # Will fail CapitalPreservation invariant!

    async def strategy_twap_conservative(tl: Timeline):
        """Safe time-weighted average price."""
        await asyncio.sleep(0.04)
        tl.mutate("cash_reserves", 970_000.00)
        tl.mutate("shares_filled", 50000)
        tl.metrics["net_alpha"] = 4500.00
        tl.mutate("total_alpha_generated", tl.read("total_alpha_generated", 0.0) + 4500.00)
        return {"venue": "TWAP-Conservative", "alpha": 4500.00}

    async def strategy_darkpool_liquidity_cross(tl: Timeline):
        """Institutional dark pool cross with midpoint peg."""
        await asyncio.sleep(0.03)
        tl.mutate("cash_reserves", 985_000.00)
        tl.mutate("shares_filled", 50000)
        tl.metrics["net_alpha"] = 8900.00
        tl.mutate("total_alpha_generated", tl.read("total_alpha_generated", 0.0) + 8900.00)
        return {"venue": "DarkPool-Midpoint", "alpha": 8900.00}

    async def strategy_flash_dex_hop(tl: Timeline):
        """Speculative liquidity pool bridge."""
        await asyncio.sleep(0.01)
        # Reverts / crashes
        raise RuntimeError("Liquidity pool front-run by MEV sandwich bot")

    tasks = {
        "Aggressive-Sweep": strategy_aggressive_market_sweep,
        "TWAP-Conservative": strategy_twap_conservative,
        "DarkPool-Midpoint": strategy_darkpool_liquidity_cross,
        "Flash-DEX-Bridge": strategy_flash_dex_hop,
    }

    winner, result = await mv.run_superposition(
        tasks=tasks,
        strategy=CollapseStrategy.MAX_METRIC("net_alpha")
    )

    print(f"\n[★] OBSERVATION COLLAPSE WINNER: '{winner.name}'")
    print(f"    Observed Result: {result}")
    print(f"    Selected Metric (Alpha): +${winner.metrics['net_alpha']:,.2f}")
    print(f"    New Canonical Reserves:  ${mv.get_root_state('cash_reserves'):,.2f}")
    print(f"    Total Alpha Generated:   ${mv.get_root_state('total_alpha_generated'):,.2f}")


if __name__ == "__main__":
    asyncio.run(run_algorithmic_router_demo())
