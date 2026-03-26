"""
Demonstrates that a feedback control system with individually
reasonable parameters can diverge through the interaction of
gain and delay.

The gain is moderate. The delay is modest. Neither parameter
alone suggests instability. The closed-loop interaction creates
an amplifying feedback mode — oscillations that grow without
bound because the controller acts on stale information and
overshoots progressively.
"""
import numpy as np
from solver.baseline_solver import run


def show_run(label, gain, delay_steps, steps=200):
    states, controls, errors = run(
        gain=gain, delay_steps=delay_steps, steps=steps
    )

    max_state = np.max(np.abs(states))
    final_state = states[-1]
    oscillating = np.sum(np.diff(np.sign(states[50:] - 100)) != 0) > 10

    print(f"\n--- {label} ---")
    print(f"  Gain:            {gain}")
    print(f"  Delay steps:     {delay_steps}")
    print(f"  Final state:     {final_state:.4f}")
    print(f"  Max |state|:     {max_state:.4f}")
    print(f"  Oscillating:     {'YES' if oscillating else 'no'}")
    print(f"  Bounded:         {'YES' if max_state < 1000 else 'NO — left domain'}")

    # Show trajectory at key points
    print(f"\n  Trajectory (reference = 100.0):")
    print(f"  {'step':>6}  {'state':>12}  {'control':>12}  visualization")
    print(f"  {'-'*6}  {'-'*12}  {'-'*12}  {'-'*30}")
    for i in [0, 10, 25, 50, 75, 100, 150, 200]:
        if i <= len(states) - 1:
            s = states[i]
            c = controls[i] if i < len(controls) else 0
            bar_pos = int(min(max(s / 5, -30), 30))
            bar = " " * (30 + bar_pos) + "#" if bar_pos >= 0 else " " * (30 + bar_pos) + "#"
            ref_mark = " " * 20 + "|"
            print(f"  {i:>6}  {s:>12.2f}  {c:>12.2f}")


def main():
    print("=== Delayed Feedback Divergence Demo ===")
    print("Reference = 100.0, dt = 0.1")

    # Case 1: No delay — stable
    show_run("No delay (gain=5.0, delay=0)", gain=5.0, delay_steps=0)

    # Case 2: Moderate delay — still stable
    show_run("Moderate delay (gain=5.0, delay=3)", gain=5.0, delay_steps=3)

    # Case 3: Same gain, more delay — divergent
    show_run("Higher delay (gain=5.0, delay=8)", gain=5.0, delay_steps=8)

    # Case 4: Higher gain with delay — divergent
    show_run("High gain + delay (gain=12.0, delay=5)", gain=12.0, delay_steps=5)

    print("\n=== Key Observation ===")
    print("Gain = 5.0 is stable without delay and with short delay.")
    print("The same gain becomes unstable with longer delay.")
    print("Instability is an interaction property of gain and delay,")
    print("not a property of either parameter alone.")


if __name__ == "__main__":
    main()