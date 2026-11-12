"""
Unit tests for Multiverse Superposition & Wavefunction Collapse.
"""

import asyncio
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from quantumflow.core.multiverse import Multiverse, CollapseStrategy, NoValidTimelineError
from quantumflow.core.timeline import Timeline, TimelineStatus


class TestMultiverse(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.mv = Multiverse(name="TestCosmos")
        self.mv.set_root_state("balance", 1000)

    async def test_superposition_and_collapse(self):
        async def fast_task(tl: Timeline):
            await asyncio.sleep(0.01)
            tl.mutate("balance", 1200)
            return "FAST"

        async def slow_task(tl: Timeline):
            await asyncio.sleep(0.05)
            tl.mutate("balance", 1500)
            return "SLOW"

        winner, res = await self.mv.run_superposition(
            tasks={"FastBranch": fast_task, "SlowBranch": slow_task},
            strategy=CollapseStrategy.FASTEST_VALID
        )

        self.assertEqual(winner.name, "FastBranch")
        self.assertEqual(res, "FAST")
        self.assertEqual(self.mv.get_root_state("balance"), 1200)

    async def test_decoherence_pruning(self):
        # Register global invariant: balance >= 500
        self.mv.register_invariant("MinBalance", lambda s: s.get("balance", 0) >= 500)

        async def toxic_task(tl: Timeline):
            await asyncio.sleep(0.01)
            # Breaches invariant
            tl.mutate("balance", 100)
            return "BAD"

        async def safe_task(tl: Timeline):
            await asyncio.sleep(0.02)
            tl.mutate("balance", 800)
            return "GOOD"

        winner, res = await self.mv.run_superposition(
            tasks={"Toxic": toxic_task, "Safe": safe_task},
            strategy=CollapseStrategy.FASTEST_VALID
        )

        self.assertEqual(winner.name, "Safe")
        self.assertEqual(res, "GOOD")
        self.assertEqual(self.mv.get_root_state("balance"), 800)

        # Check toxic timeline status
        toxic_tl = [t for t in self.mv._timelines.values() if t.name == "Toxic"][0]
        self.assertEqual(toxic_tl.status, TimelineStatus.DECOHERENT)

    async def test_all_decoherent_raises_error(self):
        self.mv.register_invariant("Impossible", lambda s: False, "Always fails")

        async def task_a(tl: Timeline):
            return "A"

        with self.assertRaises(NoValidTimelineError):
            await self.mv.run_superposition(tasks={"BranchA": task_a})


if __name__ == "__main__":
    unittest.main()
