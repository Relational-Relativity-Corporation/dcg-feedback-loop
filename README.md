# DCG Feedback Loop

Domain Closure Guard applied to delayed feedback control systems.

---

## The Problem

A controller reads a sensor. The sensor measures the system the controller is driving. The controller's output changes the system state. The sensor reads the changed state. The loop repeats.

Each component is correct in isolation:
- The controller applies a valid gain
- The sensor reads accurately
- The plant responds predictably

Yet the closed-loop system can diverge — not because any component fails, but because the **interaction between components through delay** creates an amplifying feedback mode, even though no individual parameter violates constraints.

This is the same structural gap identified in scalar systems (domain-closure-demonstration) and coupled systems (dcg-coupled-state), now appearing in its most operationally common form: **the feedback control loop**.

---

## What This Repository Does Not Claim

This repository does not introduce a new stability condition.

Delay-induced instability in feedback systems is well understood in control theory. The Nyquist criterion, root locus methods, and state-space eigenvalue analysis have characterized these conditions for decades.

What is not enforced in practice is: **whether a given gain/delay combination preserves bounded behavior before the control loop executes.**

Control theory provides the analysis. DCG converts that analysis into enforcement — a pre-execution constraint layer that rejects non-admissible parameter combinations before the first control step runs.

DCG does not tune parameters. It rejects parameter combinations that cannot preserve bounded behavior. The distinction matters: tuning optimizes within the admissible region. DCG defines and enforces the boundary of that region.

---

## The Demonstration

A discrete-time feedback control system with sensor delay:

```
           +-------+     +-------+     +-------+
  ref ---->| error |---->| gain  |---->| plant |----+
           +-------+     +-------+     +-------+   |
               ^                                     |
               |          +-------+                  |
               +----------| delay |<-----------------+
                          +-------+
```

The plant is a first-order integrator: state accumulates control input.
The sensor introduces a fixed delay: the controller acts on stale information.
The gain determines how aggressively the controller responds.

**Without delay**, any positive gain below a critical threshold is stable.

**With delay**, the stability boundary shifts. Gain values that are stable without delay become unstable with delay — because the controller overshoots based on stale sensor data, and the overshoot feeds back through the delay to produce a larger correction, which overshoots further.

The closed-loop system contains an amplifying feedback mode, even though no individual parameter violates constraints. The divergence is not visible from inspecting the gain alone. It emerges from the interaction between gain and delay — the closed-loop transfer function contains an oscillatory amplifying mode that the open-loop parameters do not reveal.

---

## Repository Structure

```
solver/                         # Unguarded baseline
  baseline_solver.py            # Feedback loop simulation — no domain check
  divergence_demo.py            # Shows silent divergence from stable-looking parameters
  delay_comparison.py           # Same gain, different delays — stability boundary shift

metatron/                       # Domain-enforced solver
  closure_check.py              # Closed-loop stability analysis via eigenvalues
  guarded_solver.py             # Rejects non-admissible gain/delay combinations
  domain.yaml                   # Formal domain declaration

analysis/
  closure_argument.md           # Mathematical closure argument for delayed feedback
  plot_demo.py                  # Visual comparison: stable vs oscillatory vs divergent

tests/
  test_closure.py               # Automated validation suite
```

---

## Key Insight

**Instability in feedback systems is an interaction property, not a component property.**

A gain that is safe without delay becomes unsafe with delay. The stability condition depends on the closed-loop structure — the interaction between gain, delay, and plant dynamics — not on any parameter in isolation.

DCG evaluates the closed-loop transformation before execution, rejecting gain/delay combinations that contain amplifying feedback modes.

---

## Running

```bash
pip install -e .

# Unguarded demos
python -m solver.divergence_demo
python -m solver.delay_comparison

# Guarded demo
python -m metatron.guarded_solver

# Visual comparison (requires matplotlib)
python analysis/plot_demo.py

# Full test suite
pytest tests/ -v
```

---

## Validation

```powershell
.\validate.ps1
```