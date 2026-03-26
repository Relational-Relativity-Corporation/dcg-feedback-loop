"""
Domain closure check for delayed feedback control systems.

For a discrete-time feedback loop with proportional gain and
sensor delay, domain closure requires that the closed-loop
system matrix has spectral radius <= 1.

The system is lifted into state-space form:

    z[n+1] = A_cl @ z[n] + B_cl * reference

where z is the augmented state vector containing the current
state and the delay buffer. A_cl encodes the interaction between
gain, delay, and plant dynamics.

The spectral radius of A_cl determines whether the closed-loop
system contains an amplifying mode. This condition depends on
the interaction of gain and delay — not on either parameter alone.

Domain declaration (see domain.yaml):
    state bounds: [-1000, 1000]
    gain: [0, inf) — but admissibility depends on delay
    delay_steps: [0, inf) — but admissibility depends on gain
    constraint: spectral_radius(A_cl) <= 1
"""
import numpy as np

# Tolerance for floating-point spectral radius comparison.
# Avoids false positives from numerical eigenvalue computation.
_SR_TOLERANCE = 1e-12


class DomainViolation(Exception):
    """Raised when parameters violate domain closure constraints."""
    pass


def build_closed_loop_matrix(
    gain: float,
    delay_steps: int,
    dt: float = 0.1,
) -> np.ndarray:
    """
    Build the closed-loop system matrix for the delayed feedback system.

    Augmented state: z = [x, x_{n-1}, x_{n-2}, ..., x_{n-delay}]
    Dimension: delay_steps + 1

    Plant: x[n+1] = x[n] + dt * gain * (ref - x[n - delay])
    The reference term is an affine offset and does not affect
    the eigenvalues of the homogeneous system matrix.

    The homogeneous dynamics (around equilibrium) are:
      x[n+1] = x[n] - dt * gain * x_delayed[n]
    with the delay buffer shifting each step.
    """
    dim = delay_steps + 1

    A = np.zeros((dim, dim))

    # First row: x[n+1] = 1.0 * x[n] - dt*gain * x[n-delay]
    A[0, 0] = 1.0
    A[0, delay_steps] = -dt * gain

    # Delay buffer: shift register
    # z[i+1, n+1] = z[i, n] for i = 0..delay-2
    for i in range(1, dim):
        A[i, i - 1] = 1.0

    return A


def spectral_radius(matrix: np.ndarray) -> float:
    """Compute spectral radius of a matrix."""
    eigenvalues = np.linalg.eigvals(matrix)
    return float(np.max(np.abs(eigenvalues)))


def dominant_mode(matrix: np.ndarray) -> tuple[complex, np.ndarray]:
    """Return dominant eigenvalue and eigenvector."""
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    idx = np.argmax(np.abs(eigenvalues))
    return eigenvalues[idx], eigenvectors[:, idx]


def check_domain(
    gain: float,
    delay_steps: int = 0,
    dt: float = 0.1,
    state_bounds: tuple = (-1000.0, 1000.0),
) -> tuple[bool, str]:
    """
    Check whether a gain/delay combination satisfies domain closure.

    Builds the closed-loop system matrix and evaluates whether it
    contains any amplifying mode (spectral radius > 1).

    Returns (ok, message).
    """
    if gain < 0:
        return False, f"gain {gain} < 0: outside declared domain"

    if delay_steps < 0:
        return False, f"delay_steps {delay_steps} < 0: outside declared domain"

    A_cl = build_closed_loop_matrix(gain, delay_steps, dt)
    sr = spectral_radius(A_cl)

    if sr > 1.0 + _SR_TOLERANCE:
        ev, _ = dominant_mode(A_cl)
        # Characterize the mode
        if abs(ev.imag) > 1e-10:
            mode_type = "oscillatory amplifying mode (complex eigenvalue)"
        else:
            mode_type = "monotonic amplifying mode (real eigenvalue)"

        return False, (
            f"spectral radius {sr:.6f} > 1: closed-loop contains {mode_type}. "
            f"Gain {gain} with delay {delay_steps} creates a non-admissible "
            f"feedback interaction. Neither parameter alone violates constraints."
        )

    return True, (
        f"domain closure satisfied — all closed-loop modes contractive "
        f"(spectral radius = {sr:.6f})"
    )


def enforce_domain(
    gain: float,
    delay_steps: int = 0,
    dt: float = 0.1,
) -> None:
    """Raise DomainViolation if gain/delay fails closure check."""
    ok, msg = check_domain(gain, delay_steps, dt)
    if not ok:
        raise DomainViolation(msg)


if __name__ == "__main__":
    print("=== Domain Closure Check — Feedback Loop ===\n")

    cases = [
        ("no delay, moderate gain", 5.0, 0),
        ("short delay, moderate gain", 5.0, 2),
        ("boundary delay", 5.0, 3),
        ("longer delay, moderate gain", 5.0, 8),
        ("high gain, moderate delay", 12.0, 5),
        ("low gain, long delay", 2.0, 10),
    ]

    for label, g, d in cases:
        ok, msg = check_domain(g, d)
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] gain={g:<5} delay={d:<3} | {msg}")