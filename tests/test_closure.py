"""
Test suite for delayed feedback domain closure demonstration.

Tests validate the core argument:
  1. No-delay system converges to reference
  2. Short-delay system converges to reference
  3. Long-delay system diverges (leaves domain)
  4. Domain check accepts stable gain/delay combinations
  5. Domain check rejects unstable gain/delay combinations
  6. Same gain changes admissibility with delay (interaction property)
  7. Guarded solver rejects what unguarded solver silently runs
  8. Negative gain is rejected
  9. Negative delay is rejected
"""
import numpy as np
import pytest
from solver.baseline_solver import run
from metatron.closure_check import (
    check_domain, enforce_domain, build_closed_loop_matrix,
    spectral_radius, DomainViolation,
)
from metatron.guarded_solver import guarded_run


# --- Solver behavior ---

def test_no_delay_converges():
    """No delay, moderate gain must converge to reference."""
    states, _, _ = run(gain=5.0, delay_steps=0, steps=200)
    assert abs(states[-1] - 100.0) < 1.0, (
        f"expected convergence to 100.0, got {states[-1]:.4f}"
    )


def test_short_delay_converges():
    """Short delay (delay=2) with moderate gain must still converge."""
    states, _, _ = run(gain=5.0, delay_steps=2, steps=300)
    assert abs(states[-1] - 100.0) < 5.0, (
        f"expected convergence near 100.0, got {states[-1]:.4f}"
    )


def test_long_delay_diverges():
    """Long delay with same gain must diverge."""
    states, _, _ = run(gain=5.0, delay_steps=8, steps=500)
    assert np.max(np.abs(states)) > 1000.0, (
        f"expected divergence, max |state| = {np.max(np.abs(states)):.4f}"
    )


# --- Domain check ---

def test_check_accepts_stable():
    """Domain check must accept stable gain/delay combinations."""
    ok, msg = check_domain(5.0, delay_steps=0)
    assert ok, f"expected acceptance, got: {msg}"

    ok, msg = check_domain(5.0, delay_steps=2)
    assert ok, f"expected acceptance, got: {msg}"


def test_check_rejects_unstable():
    """Domain check must reject unstable gain/delay combinations."""
    ok, msg = check_domain(5.0, delay_steps=8)
    assert not ok
    assert "amplifying mode" in msg


def test_interaction_property():
    """
    Same gain must be admissible at one delay and non-admissible
    at another. This proves instability is an interaction property.
    """
    ok_short, _ = check_domain(5.0, delay_steps=2)
    ok_long, _ = check_domain(5.0, delay_steps=8)
    assert ok_short, "gain=5.0 should be admissible at delay=2"
    assert not ok_long, "gain=5.0 should be non-admissible at delay=8"


# --- Guarded vs unguarded ---

def test_guarded_rejects_divergent():
    """
    Core demonstration:
    Unguarded run accepts divergent gain/delay and diverges.
    Guarded run rejects the same combination before execution.
    """
    states, _, _ = run(gain=5.0, delay_steps=8, steps=500)
    assert np.max(np.abs(states)) > 1000.0

    with pytest.raises(DomainViolation):
        guarded_run(gain=5.0, delay_steps=8)


# --- Edge cases ---

def test_rejects_negative_gain():
    """Domain check must reject negative gain."""
    ok, msg = check_domain(-1.0, delay_steps=0)
    assert not ok
    assert "outside declared domain" in msg


def test_rejects_negative_delay():
    """Domain check must reject negative delay."""
    ok, msg = check_domain(5.0, delay_steps=-1)
    assert not ok
    assert "outside declared domain" in msg