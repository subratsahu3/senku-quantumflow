"""
Unit tests for TemporalMemory (Copy-on-Write State Store).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from quantumflow.core.memory import TemporalMemory, MemoryParadoxError


class TestTemporalMemory(unittest.TestCase):

    def setUp(self):
        self.root = TemporalMemory(parent=None, name="root")
        self.root.set("cluster", "primary")
        self.root.set("counter", 10)
        self.root.set("tags", ["alpha", "beta"])

    def test_basic_get_set(self):
        self.assertEqual(self.root.get("cluster"), "primary")
        self.assertEqual(self.root.get("counter"), 10)
        self.assertIsNone(self.root.get("nonexistent"))

    def test_child_isolation(self):
        child = self.root.fork("child-1")
        # Child reads parent state
        self.assertEqual(child.get("cluster"), "primary")
        self.assertEqual(child.get("counter"), 10)

        # Mutate child
        child.set("cluster", "speculative-cluster")
        child.set("counter", 999)
        child.set("new_var", "secret")

        # Verify child has mutated values
        self.assertEqual(child.get("cluster"), "speculative-cluster")
        self.assertEqual(child.get("counter"), 999)
        self.assertEqual(child.get("new_var"), "secret")

        # Parent MUST remain pristine (unpolluted)
        self.assertEqual(self.root.get("cluster"), "primary")
        self.assertEqual(self.root.get("counter"), 10)
        self.assertFalse(self.root.has("new_var"))

    def test_deletion_and_tombstones(self):
        child = self.root.fork("child-del")
        self.assertTrue(child.has("cluster"))
        
        # Delete in child
        self.assertTrue(child.delete("cluster"))
        self.assertFalse(child.has("cluster"))
        self.assertIsNone(child.get("cluster"))

        # Parent still has it
        self.assertTrue(self.root.has("cluster"))

    def test_atomic_commit_to_parent(self):
        child = self.root.fork("child-commit")
        child.set("counter", 42)
        child.set("status", "ACTIVE")
        child.delete("cluster")

        committed = child.commit_to_parent()
        self.assertEqual(len(committed), 3)

        # Parent state now updated
        self.assertEqual(self.root.get("counter"), 42)
        self.assertEqual(self.root.get("status"), "ACTIVE")
        self.assertFalse(self.root.has("cluster"))

    def test_rollback(self):
        child = self.root.fork("child-rb")
        child.set("counter", 777)
        self.assertEqual(child.get("counter"), 777)
        child.rollback()
        # Should revert to parent's value
        self.assertEqual(child.get("counter"), 10)
        self.assertEqual(child.delta_count(), 0)

    def test_fingerprint(self):
        fp1 = self.root.compute_fingerprint()
        self.assertEqual(len(fp1), 64)
        
        # Same state produces exact same hash
        fp2 = self.root.compute_fingerprint()
        self.assertEqual(fp1, fp2)

        # Mutation alters hash deterministically
        self.root.set("counter", 11)
        fp3 = self.root.compute_fingerprint()
        self.assertNotEqual(fp1, fp3)


if __name__ == "__main__":
    unittest.main()
