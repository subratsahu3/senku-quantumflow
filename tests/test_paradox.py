"""
Unit tests for Paradox Sentinel & Concurrency Conflict Detection.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from quantumflow import Multiverse, ParadoxSentinel, ConflictType


class TestParadoxSentinel(unittest.TestCase):

    def test_write_write_collision_detection(self):
        mv = Multiverse(name="ConflictCosmos")
        tl_a = mv.fork("Branch-A")
        tl_b = mv.fork("Branch-B")

        # Conflicting writes to same key
        tl_a.mutate("order_status", "APPROVED")
        tl_b.mutate("order_status", "CANCELLED")

        conflicts = mv.inspect_conflicts()
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["type"], ConflictType.WRITE_WRITE_COLLISION)
        self.assertEqual(conflicts[0]["key"], "order_status")

    def test_type_mutation_divergence(self):
        mv = Multiverse(name="TypeCosmos")
        tl_a = mv.fork("Branch-1")
        tl_b = mv.fork("Branch-2")

        # Type divergence: integer vs list
        tl_a.mutate("payload", 42)
        tl_b.mutate("payload", ["alpha", "beta"])

        conflicts = ParadoxSentinel.inspect([tl_a, tl_b])
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0].conflict_type, ConflictType.TYPE_MUTATION_DIVERGENCE)

    def test_entropy_drift_calculation(self):
        mv = Multiverse(name="DriftCosmos")
        t1 = mv.fork("T1")
        t2 = mv.fork("T2")

        t1.mutate("k1", "v1")
        t2.mutate("k1", "v1")
        # Identical deltas
        self.assertEqual(ParadoxSentinel.calculate_entropy_drift(t1, t2), 0.0)

        # Mutate divergent key
        t2.mutate("k2", "v2_divergent")
        drift = ParadoxSentinel.calculate_entropy_drift(t1, t2)
        self.assertGreater(drift, 0.0)


if __name__ == "__main__":
    unittest.main()
