"""
Visual comparison: stable vs oscillatory vs divergent feedback.

Produces a single figure with three subplots showing:
  1. Stable: gain=5.0, delay=0 — smooth convergence
  2. Marginally unstable: gain=5.0, delay=3 — growing oscillation
  3. Strongly unstable: gain=5.0, delay=8 — rapid divergence

Same gain in all three cases. Only delay changes.

Requires: matplotlib (pip install matplotlib)
Saves to: analysis/feedback_comparison.png
"""
import numpy as np
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solver.baseline_solver import run
from metatron.closure_check import check_domain, build_closed_loop_matrix, spectral_radius


def main():
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed. Install with: pip install matplotlib")
        print("Skipping plot generation.")
        return

    cases = [
        ("Stable (delay=0)", 5.0, 0, 200),
        ("Oscillatory divergence (delay=3)", 5.0, 3, 200),
        ("Rapid divergence (delay=8)", 5.0, 8, 100),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle(
        "Same Gain (5.0) — Delay Changes Admissibility",
        fontsize=14, fontweight='bold', y=1.02,
    )

    for ax, (label, gain, delay, steps) in zip(axes, cases):
        states, controls, _ = run(gain=gain, delay_steps=delay, steps=steps)
        ok, msg = check_domain(gain, delay)
        A_cl = build_closed_loop_matrix(gain, delay)
        sr = spectral_radius(A_cl)

        time = np.arange(len(states))
        reference = np.full_like(time, 100.0, dtype=float)

        ax.plot(time, states, 'b-', linewidth=1.5, label='state')
        ax.plot(time, reference, 'r--', linewidth=1.0, alpha=0.5, label='reference')
        ax.axhline(y=1000, color='gray', linestyle=':', alpha=0.4, label='domain bound')
        ax.axhline(y=-1000, color='gray', linestyle=':', alpha=0.4)

        ax.set_title(f"{label}\nρ(A_cl) = {sr:.4f}", fontsize=11)
        ax.set_xlabel("step")
        ax.set_ylabel("state")
        ax.legend(fontsize=8, loc='best')

        # Set reasonable y-limits for divergent cases
        if not ok:
            y_max = min(np.max(np.abs(states[:steps//2])), 2000)
            ax.set_ylim(-y_max * 1.2, y_max * 1.2)

        status = "ADMISSIBLE" if ok else "NON-ADMISSIBLE"
        ax.text(
            0.02, 0.02, status,
            transform=ax.transAxes,
            fontsize=9, fontweight='bold',
            color='green' if ok else 'red',
            verticalalignment='bottom',
        )

    plt.tight_layout()

    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "feedback_comparison.png"
    )
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Plot saved to: {output_path}")


if __name__ == "__main__":
    main()