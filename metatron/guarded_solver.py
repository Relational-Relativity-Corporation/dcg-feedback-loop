"""
Guarded delayed feedback solver.

Identical to the baseline solver, with one addition:
closed-loop domain closure is verified BEFORE the first
control step executes.

The verification builds the augmented closed-loop system matrix
from the gain and delay parameters and evaluates whether the
feedback interaction contains any amplifying mode. This condition
depends on the interaction of gain and delay — not on either
parameter in isolation.
"""
import numpy as np
from solver.baseline_solver import run as _raw_run
from metatron.closure_check import enforce_domain, DomainViolation


def guarded_run(
    gain: float,
    delay_steps: int = 0,
    reference: float = 100.0,
    dt: float = 0.1,
    steps: int = 200,
    initial: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Run the feedback loop after verifying closed-loop domain closure.

    Raises DomainViolation if the gain/delay combination creates
    an amplifying feedback mode.
    """
    enforce_domain(gain, delay_steps, dt)
    return _raw_run(gain, delay_steps, reference, dt, steps, initial)


if __name__ == "__main__":
    print("=== Guarded Feedback Loop Demo ===\n")

    cases = [
        ("stable, no delay",       5.0,  0),
        ("stable, short delay",    5.0,  3),
        ("divergent, long delay",  5.0,  8),
        ("divergent, high gain",  12.0,  5),
    ]

    for label, g, d in cases:
        try:
            states, _, _ = guarded_run(gain=g, delay_steps=d)
            final = states[-1]
            print(f"  [{label}] gain={g}, delay={d} -> final state = {final:.4f}")
        except DomainViolation as e:
            print(f"  [{label}] gain={g}, delay={d} -> REJECTED: {e}")