# GeneForge Language (GFL) Specification v0.1

GFL is a declarative YAML-based language for defining biological workflows.

## Root Object
The root of any GFL file must be a `plan` object.

## The `plan` Object
- `goal` (string, required): A high-level description of the scientific objective.
- `steps` (list, required): A list of one or more step objects to be executed.