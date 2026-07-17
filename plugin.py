"""Planing flat plate case handler for planingfsi simulations."""

from __future__ import annotations
import shutil
import subprocess
from pathlib import Path
from typing import NamedTuple

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

    froude_num = InputParameter(
        type=float, min=0.2, max=3.0, short_name="Fr", path_format="0.2f"
    )
    angle_of_attack = InputParameter(
        type=float, min=-5.0, max=20.0, short_name="AOA", path_format="0.2f"
    )

    @step(condition=lambda self: not (self.case_dir / "configDict").exists())
    def create_input_files(self) -> None:
        """Create input files from Jinja2 template."""
        from jinja2 import Environment
        from jinja2 import FileSystemLoader

        template_dir = Path.cwd() / "case-template"
        if not template_dir.exists():
            raise FileNotFoundError(
                f"Template directory not found: {template_dir}. "
                "Copy case-template from planingfsi examples."
            )

        # Copy non-template files
        shutil.copytree(template_dir, self.case_dir, dirs_exist_ok=True)

        # Render configDict template
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("configDict")
        rendered = template.render(
            froude_num=self.froude_num,
            angle_of_attack=self.angle_of_attack,
        )
        (self.case_dir / "configDict").write_text(rendered)

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
        from planingfsi.dictionary import load_dict_from_file

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
