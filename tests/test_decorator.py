"""
Unit tests for @superposition decorator and branch context manager.
"""

import asyncio
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from quantumflow import Multiverse, CollapseStrategy


class TestMultiverseErgonomics(unittest.IsolatedAsyncioTestCase):

    def test_branch_context_manager(self):
        mv = Multiverse()
        mv.set_root_state("count", 1)

        # Non-committed branch
        with mv.branch("spec-1") as tl:
            tl.mutate("count", 999)
            self.assertEqual(tl.read("count"), 999)

        # Root unaffected
        self.assertEqual(mv.get_root_state("count"), 1)

        # Auto-committed branch
        with mv.branch("spec-commit", auto_commit=True) as tl:
            tl.mutate("count", 42)

        self.assertEqual(mv.get_root_state("count"), 42)

    async def test_superposition_decorator(self):
        mv = Multiverse()

        @mv.superposition(branches=["FastRoute", "SlowRoute"], strategy=CollapseStrategy.FASTEST_VALID)
        async def fetch_data(tl, branch_name, item_id: str):
            if branch_name == "FastRoute":
                await asyncio.sleep(0.01)
                tl.mutate("source", "fast")
                return f"fast_result_{item_id}"
            else:
                await asyncio.sleep(0.05)
                tl.mutate("source", "slow")
                return f"slow_result_{item_id}"

        result = await fetch_data("item-882")
        self.assertEqual(result, "fast_result_item-882")
        self.assertEqual(mv.get_root_state("source"), "fast")


if __name__ == "__main__":
    unittest.main()
