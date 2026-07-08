"""Parametric study of planing flat plate across Froude numbers and angles of attack."""

from __future__ import annotations

import numpy as np

from lembas import CaseList
from lembas import load_local_plugins
from lembas import registry

# Load local plugins defined in [local-plugins] section of lembas.toml
load_local_plugins()
PlaningPlateCase = registry.get("PlaningPlateCase")


def main() -> None:
    """Run the parametric sweep."""
    # Define parameter ranges
    froude_nums = np.arange(0.5, 2.5, 0.5)
    angles_of_attack = np.arange(5.0, 15.1, 2.5)

    # Create case list and add parameter sweep
    cases: CaseList[PlaningPlateCase] = CaseList()
    cases.add_cases_by_parameter_sweep(
        PlaningPlateCase,
        froude_num=froude_nums,
        angle_of_attack=angles_of_attack,
    )

    print(f"Running {len(cases)} cases...")

    # Run all cases
    cases.run_all()

    # Print summary
    print("\nResults summary:")
    for case in cases:
        print(
            f"  Fr={case.froude_num:.2f}, AOA={case.angle_of_attack:.1f}°: "
            f"L={case.results.lift:.3f}, D={case.results.drag:.3f}"
        )


if __name__ == "__main__":
    main()
