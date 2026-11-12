"""
Demo 3: Time Travel & Counterfactual Debugging.

Demonstrates how engineers can rewind reality to historical checkpoints,
simulate 'What-If' scenarios with synthetic perturbations, and compute
divergence diffs to debug complex distributed state regressions.
"""

from quantumflow import Multiverse, TimeTravelEngine


def run_counterfactual_debug_demo():
    print("\n" + "="*70)
    print("  DEMO 3: TIME-TRAVEL COUNTERFACTUAL ROOT-CAUSE ANALYSIS")
    print("="*70)

    mv = Multiverse(name="E-CommerceEngine")
    tt = TimeTravelEngine(mv)

    # Initial state
    mv.set_root_state("user_id", "usr_9912")
    mv.set_root_state("cart_subtotal", 100.00)
    mv.set_root_state("tax_amount", 0.00)
    mv.set_root_state("shipping_cost", 15.00)
    mv.set_root_state("total_charge", 115.00)

    # Create immutable checkpoint before checkout confirmation
    cp = tt.checkpoint("pre-checkout-v1")
    print(f"[*] Checkpoint 'pre-checkout-v1' created. Fingerprint: {mv.root_memory.compute_fingerprint()[:12]}")

    # Reality: A production bug occurs! The checkout applies a coupon that incorrectly wipes shipping cost
    mv.set_root_state("coupon_code", "FREESHIP_BUG")
    mv.set_root_state("shipping_cost", 0.00)
    mv.set_root_state("total_charge", 80.00)  # Inadvertent $20 discount!
    mv.set_root_state("order_status", "FULFILLED")

    print("[!] Reality resulted in an accidental $20 pricing loss (Total charge = $80.00).")
    print("[*] Launching Counterfactual Investigation: 'What if coupon validation had rejected expired coupon?'")

    # Define the counterfactual hypothesis
    def counterfactual_workflow(memory):
        # In this alternate universe, coupon is rejected
        memory.set("coupon_code", "EXPIRED_REJECTED")
        subtotal = memory.get("cart_subtotal")
        shipping = memory.get("shipping_cost")
        memory.set("total_charge", subtotal + shipping)
        memory.set("order_status", "FULFILLED_CORRECT")

    # Run the counterfactual simulation against the pre-checkout checkpoint
    result = tt.simulate_counterfactual(
        base_checkpoint_name="pre-checkout-v1",
        simulation_name="strict-coupon-validator",
        perturbations={"coupon_valid": False},
        workflow_fn=counterfactual_workflow
    )

    print("\n" + result.summary())
    print("\n[✓] Root cause isolated: Reality divergence caused by improper coupon discount application.")


if __name__ == "__main__":
    run_counterfactual_debug_demo()
