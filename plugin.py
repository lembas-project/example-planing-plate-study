"""Planing flat plate case handler for planingfsi simulations."""

from __future__ import annotations
import shutil
import subprocess
from pathlib import Path
from typing import NamedTuple

from planingfsi.dictionary import load_dict_from_file

from lembas import Case
from lembas import InputParameter
from lembas import result
from lembas import step


class PlaningPlateResults(NamedTuple):
    """Results from a planing plate simulation."""

    drag: float
    lift: float
    moment: float


class PlaningPlateCase(Case):
    """Case handler for planing flat plate simulations.

    Runs planingfsi to simulate a flat plate planing on a water surface.
    Characterized by Froude number (flow speed) and angle of attack.
    """

    froude_num = InputParameter(type=float, min=0.2, max=3.0)
    angle_of_attack = InputParameter(type=float, min=-5.0, max=20.0)

    @property
    def case_dir(self) -> Path:
        """The directory in which to run the case."""
        return Path(
            Path.cwd(),
            "cases",
            f"Fr={self.froude_num:0.2f}_AOA={self.angle_of_attack:0.2f}",
        )

    @step(condition=lambda self: not (self.case_dir / "configDict").exists())
    def create_input_files(self) -> None:
        """Create input files from base template."""
        case_dir_base = Path.cwd() / "flat_plate_base"
        if not case_dir_base.exists():
            raise FileNotFoundError(
                f"Base case directory not found: {case_dir_base}. "
                "Copy flat_plate_base from planingfsi examples."
            )
        shutil.copytree(case_dir_base, self.case_dir, dirs_exist_ok=True)
        with (self.case_dir / "configDict").open("w") as fp:
            fp.write("baseDict: './configDict.base'\n")
            fp.write(f"Fr: {self.froude_num}\n")
            fp.write(f"AOA: {self.angle_of_attack}\n")

    @step(condition=lambda self: not (self.case_dir / "mesh").exists())
    def generate_mesh(self) -> None:
        """Generate the computational mesh."""
        subprocess.run(["planingfsi", "mesh"], cwd=str(self.case_dir), check=True)

    @step(condition=lambda self: not list(self.case_dir.glob("[0-9]*")))
    def run_solver(self) -> None:
        """Run the planingfsi solver."""
        subprocess.run(["planingfsi", "run"], cwd=str(self.case_dir), check=True)

    @result("drag", "lift", "moment")
    def forces(self) -> PlaningPlateResults:
        """Load force results from simulation output."""
        results_dirs = sorted(
            self.case_dir.glob("[0-9]*"),
            key=lambda d: int(d.name),
            reverse=True,
        )
        if not results_dirs:
            raise FileNotFoundError(f"No results found in {self.case_dir}")
        results_dir = results_dirs[0]
        results_dict = load_dict_from_file(results_dir / "forces_total.txt")
        return PlaningPlateResults(
            drag=results_dict["Drag"],
            lift=results_dict["Lift"],
            moment=results_dict["Moment"],
        )
