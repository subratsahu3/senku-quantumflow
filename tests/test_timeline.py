"""
Unit tests for Timeline & Invariants.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from quantumflow.core.timeline import Timeline, TimelineStatus
from quantumflow.core.invariants import DecoherenceError


class TestTimeline(unittest.TestCase):

    def test_timeline_lifecycle(self):
        tl = Timeline(name="test-tl")
        self.assertEqual(tl.status, TimelineStatus.PENDING)
        self.assertEqual(tl.entropy, 0.0)

        # Mutate
        tl.mutate("x", 100)
        self.assertEqual(tl.read("x"), 100)
        self.assertGreater(tl.entropy, 0.0)

        # Collapse
        tl.mark_collapsed()
        self.assertEqual(tl.status, TimelineStatus.COLLAPSED)
        self.assertIsNotNone(tl.closed_at)

    def test_invariant_decoherence(self):
        tl = Timeline(name="fragile-tl")
        # Invariant: x must be positive
        tl.invariants.register("PositiveX", lambda s: s.get("x", 0) > 0, "x must be > 0")

        # Mutate with valid state
        tl.mutate("x", 5)
        tl.validate_invariants() # Should pass

        # Mutate to violate invariant
        tl.mutate("x", -1)
        with self.assertRaises(DecoherenceError):
            tl.validate_invariants()

        self.assertEqual(tl.status, TimelineStatus.DECOHERENT)
        self.assertIn("x must be > 0", tl.error)

    def test_timeline_dissolution(self):
        tl = Timeline(name="loser-tl")
        tl.mark_dissolved(winning_timeline_id="winner-123")
        self.assertEqual(tl.status, TimelineStatus.DISSOLVED)


if __name__ == "__main__":
    unittest.main()
