"""Parametric study of planing flat plate across Froude numbers and angles of attack."""

from __future__ import annotations

from itertools import product
from pathlib import Path
from typing import Any

import toml
import yaml

from lembas import CaseList
from lembas import load_local_plugins
from lembas import registry


def load_cases_from_manifest(manifest_path: Path | None = None) -> CaseList[Any]:
    """Load case definitions from cases file referenced in lembas.toml.

    The [study] section should have a `cases` key pointing to a YAML file:
        [study]
        cases = "cases.yaml"

    Supports expansion strategies:
    - "cartesian": Cartesian product of all parameter arrays
    - "zip": Pair parameters by index (all arrays must have same length)
    - "explicit": Single case with scalar parameter values
    """
    if manifest_path is None:
        manifest_path = Path.cwd() / "lembas.toml"

    manifest = toml.load(manifest_path)
    study_config = manifest.get("study", {})
    cases_file = study_config.get("cases")

    if cases_file is None:
        return CaseList()

    cases_path = manifest_path.parent / cases_file
    with cases_path.open() as f:
        cases_config = yaml.safe_load(f) or []

    cases: CaseList[Any] = CaseList()

    for case_def in cases_config:
        handler_name = case_def["handler"]
        expansion = case_def.get("expansion", "cartesian")
        parameters = case_def.get("parameters", {})

        handler_cls = registry.get(handler_name)

        if expansion == "cartesian":
            # Cartesian product of all parameter arrays
            param_names = list(parameters.keys())
            param_values = [
                v if isinstance(v, list) else [v] for v in parameters.values()
            ]

            for combo in product(*param_values):
                params = dict(zip(param_names, combo))
                cases.add(handler_cls(**params))

        elif expansion == "zip":
            # Pair by index - all arrays must have same length
            param_names = list(parameters.keys())
            param_values = list(parameters.values())
            lengths = [len(v) if isinstance(v, list) else 1 for v in param_values]

            if len(set(lengths)) > 1:
                raise ValueError(
                    f"All parameter arrays must have same length for 'zip' expansion. "
                    f"Got lengths: {dict(zip(param_names, lengths))}"
                )

            param_values = [v if isinstance(v, list) else [v] for v in param_values]
            for values in zip(*param_values):
                params = dict(zip(param_names, values))
                cases.add(handler_cls(**params))

        elif expansion == "explicit":
            # Single case with scalar values
            cases.append(handler_cls(**parameters))

        else:
            raise ValueError(f"Unknown expansion strategy: {expansion}")

    return cases


def main() -> None:
    """Run the parametric sweep."""
    # Load local plugins defined in [local-plugins] section of lembas.toml
    load_local_plugins()

    # Load cases from [[cases]] in lembas.toml
    cases = load_cases_from_manifest()

    print(f"Running {len(cases)} cases...")

    # Run all cases
    cases.run_all()

    # Print summary
    print("\nResults summary:")
    for case in cases:
        print(
            f"  Fr={case.froude_num:.2f}, AOA={case.angle_of_attack:.1f}: "
            f"L={case.results.lift:.3f}, D={case.results.drag:.3f}"
        )


if __name__ == "__main__":
    main()
