"""
Baseline delayed feedback control loop.

System model:
  - Plant: first-order integrator
      x[n+1] = x[n] + dt * u[n]
  - Controller: proportional gain on error
      u[n] = gain * (reference - x_sensed[n])
  - Sensor: delayed observation
      x_sensed[n] = x[n - delay_steps]

No domain enforcement. Accepts any gain and delay combination.
"""
import numpy as np


def run(
    gain: float,
    delay_steps: int = 0,
    reference: float = 100.0,
    dt: float = 0.1,
    steps: int = 200,
    initial: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Simulate the delayed feedback loop.

    Returns (states, controls, errors) as arrays.
    """
    states = np.zeros(steps + 1)
    controls = np.zeros(steps)
    errors = np.zeros(steps)
    states[0] = initial

    for n in range(steps):
        # Sensor reads delayed state
        if n >= delay_steps:
            x_sensed = states[n - delay_steps]
        else:
            x_sensed = initial  # no data yet, use initial

        # Controller computes error and control signal
        error = reference - x_sensed
        u = gain * error

        # Plant integrates
        states[n + 1] = states[n] + dt * u

        controls[n] = u
        errors[n] = error

    return states, controls, errors