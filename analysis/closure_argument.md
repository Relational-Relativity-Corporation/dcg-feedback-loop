# Domain Closure Argument — Delayed Feedback Control Systems

## System Definition

A discrete-time feedback control loop:

    Plant:       x[n+1] = x[n] + dt * u[n]
    Controller:  u[n] = gain * (reference - x_sensed[n])
    Sensor:      x_sensed[n] = x[n - delay_steps]

## Domain Declaration

    state x in [-1000, 1000]
    gain in [0, inf)
    delay_steps in [0, inf)
    dt = 0.1 (fixed)

## The Scalar Intuition (and Why It Fails Again)

Without delay (delay_steps = 0), the closed-loop dynamics reduce to:

    x[n+1] = x[n] + dt * gain * (reference - x[n])
           = (1 - dt * gain) * x[n] + dt * gain * reference

Stability requires |1 - dt * gain| < 1, which gives:

    0 < gain < 2/dt = 20

Any gain below 20 is stable. This is a scalar condition, visible by inspection.

## Why Delay Changes Everything

With delay, the controller acts on stale information. The closed-loop
system must be lifted into an augmented state space:

    z[n] = [x[n], x[n-1], x[n-2], ..., x[n-delay]]

The augmented system matrix A_cl has dimension (delay_steps + 1).
Its eigenvalues — which determine stability — depend on the interaction
of gain AND delay simultaneously.

A gain of 5.0 with dt = 0.1:
- delay = 0: spectral radius < 1 (stable)
- delay = 3: spectral radius < 1 (stable)
- delay = 8: spectral radius > 1 (divergent)

**The gain did not change. The delay shifted the stability boundary.**

## The Amplifying Feedback Mode

When the closed-loop system is unstable, the dominant eigenvalue of A_cl
is typically complex — indicating an oscillatory mode. The system does not
diverge monotonically. It oscillates with growing amplitude.

This is the operational signature of delay-induced instability:
- The controller overshoots because it acts on stale data
- The overshoot propagates through the delay buffer
- The delayed sensor reading causes a larger correction
- The correction overshoots further
- Each cycle amplifies the previous one

The oscillatory amplifying mode is a property of the closed-loop
interaction structure. It does not exist in any component individually.
The gain is stable in isolation. The delay is passive. The plant is a
simple integrator. The instability emerges only from their interaction.

## Formal Closure Condition

Build the augmented closed-loop matrix A_cl from gain, delay, and dt.

    spectral_radius(A_cl) <= 1  <=>  T(D) subset D

If spectral_radius(A_cl) > 1, the feedback interaction contains an
amplifying mode. The system will oscillate with growing amplitude until
it exits the bounded domain.

## Connection to Real Systems

The delayed feedback loop maps directly onto CPU control systems:

- **DVFS**: The controller adjusts voltage/frequency. The thermal sensor
  reads with latency. The gain is the aggressiveness of the frequency
  response. Delay is the sensor and actuator latency. Instability produces
  thermal oscillation — the system overshoots its thermal target, throttles
  down, undershoots, ramps back up, overshoots further.

- **Power management across chiplets**: Each tile's local power controller
  reads a global power budget with communication delay. Aggressive local
  controllers acting on stale global state produce coordinated overshoot.

- **Branch prediction confidence**: The predictor updates its confidence
  model based on outcomes that arrive with pipeline delay. Under workload
  phase changes, the stale confidence drives speculative commitment that
  the actual outcomes contradict, producing a cascade of wasted work.

In every case: the component parameters are individually reasonable.
The interaction through delay creates the amplifying mode.

## Key Insight

**Stability in feedback systems is an interaction property, not a component property.**

Domain closure for feedback systems requires evaluating the closed-loop
transformation — the full interaction of gain, delay, and plant dynamics.
Component-level parameter checks cannot detect the instability because
the instability does not exist at the component level.

This is what DCG provides: pre-execution evaluation of the closed-loop
interaction structure, rejecting gain/delay combinations that contain
amplifying feedback modes before the first control step executes.