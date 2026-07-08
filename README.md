# Planing Plate Parametric Study

Example [lembas](https://github.com/lembas-project/lembas-core) study that runs parametric simulations of a flat plate planing on water using [planingfsi](https://github.com/mattkram/planingfsi).

## Prerequisites

- [pixi](https://pixi.sh) for environment management
- lembas CLI installed globally: `pixi global install lembas`

## Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/lembas-project/example-planing-plate-study.git
cd example-planing-plate-study
lembas install
```

## Running the study

Run all cases defined in `cases.yaml`:

```bash
lembas run
```

This runs 22 cases across a parameter sweep of Froude numbers and angles of attack.

## Project structure

```
├── lembas.toml      # Project manifest
├── cases.yaml       # Case definitions with parameter sweeps
├── plugin.py        # PlaningPlateCase handler
├── case-template/   # Base input files for planingfsi
└── cases/           # Generated case directories (after running)
```

## Case definitions

Cases are defined in `cases.yaml` using expansion strategies:

```yaml
# Cartesian product: 4 x 5 = 20 cases
- handler: PlaningPlateCase
  expansion: cartesian
  parameters:
    froude_num: [0.5, 1.0, 1.5, 2.0]
    angle_of_attack: [5.0, 7.5, 10.0, 12.5, 15.0]

# Zip: pairs by index = 2 cases
- handler: PlaningPlateCase
  expansion: zip
  parameters:
    froude_num: [2.5, 3.0]
    angle_of_attack: [2.0, 3.0]
```

## License

MIT
