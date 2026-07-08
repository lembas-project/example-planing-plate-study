"""Parametric study of planing flat plate across Froude numbers and angles of attack."""

from __future__ import annotations

from lembas import load_cases
from lembas import load_local_plugins


def main() -> None:
    """Run the parametric sweep."""
    load_local_plugins()
    cases = load_cases()

    print(f"Running {len(cases)} cases...")
    cases.run_all()

    print("\nResults summary:")
    for case in cases:
        print(
            f"  Fr={case.froude_num:.2f}, AOA={case.angle_of_attack:.1f}: "
            f"L={case.results.lift:.3f}, D={case.results.drag:.3f}"
        )


if __name__ == "__main__":
    main()
