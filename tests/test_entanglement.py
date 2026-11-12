"""
Unit tests for Quantum Entanglement and state teleportation.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from quantumflow import Multiverse


class TestQuantumEntanglement(unittest.TestCase):

    def test_entangled_state_teleportation(self):
        mv = Multiverse(name="EntangledCosmos")
        # Mark 'cancellation_signal' as quantum entangled
        mv.entangle("cancellation_signal")

        # Fork two speculative universes
        tl_a = mv.fork("Universe-A")
        tl_b = mv.fork("Universe-B")

        # Universe A writes standard isolated state
        tl_a.mutate("local_token", "AAA")
        # Universe B must NOT see A's non-entangled mutation
        self.assertIsNone(tl_b.read("local_token"))

        # Universe A mutates the entangled cancellation signal
        synced = mv.mutate_entangled(tl_a, "cancellation_signal", True)
        self.assertEqual(synced, 1)

        # Universe B MUST instantly have received the teleported mutation!
        self.assertTrue(tl_b.read("cancellation_signal"))
        self.assertTrue(tl_a.read("cancellation_signal"))


if __name__ == "__main__":
    unittest.main()
