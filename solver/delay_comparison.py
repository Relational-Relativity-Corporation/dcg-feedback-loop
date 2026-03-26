"""
Systematic comparison: same gain across different delay values.

Shows the stability boundary shifting as delay increases.
A gain that is admissible at delay=0 becomes non-admissible
as delay increases — the closed-loop interaction structure
changes even though the open-loop parameters are identical.
"""
import numpy as np
from solver.baseline_solver import run


def main():
    print("=== Delay Comparison: Gain = 5.0 across delays ===")
    print(f"  Reference = 100.0, dt = 0.1, steps = 300\n")

    gain = 5.0
    print(f"  {'delay':>6}  {'max |state|':>14}  {'final state':>14}  {'bounded':>8}  status")
    print(f"  {'-'*6}  {'-'*14}  {'-'*14}  {'-'*8}  {'-'*24}")

    for delay in range(0, 15):
        states, _, _ = run(gain=gain, delay_steps=delay, steps=300)
        max_s = np.max(np.abs(states))
        final = states[-1]
        bounded = max_s < 1000
        status = "admissible" if bounded else "NON-ADMISSIBLE — amplifying mode"
        print(f"  {delay:>6}  {max_s:>14.2f}  {final:>14.2f}  {'YES' if bounded else 'NO':>8}  {status}")

    print(f"\n=== Same gain. Same plant. Different delay. Different admissibility. ===")
    print(f"The stability boundary is a property of the closed-loop interaction,")
    print(f"not of any individual parameter.")


if __name__ == "__main__":
    main()