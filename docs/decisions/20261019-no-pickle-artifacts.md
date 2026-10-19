# ADR: No pickle or other code-executing serialization artifacts

**Date**: 2026-10-19
**Status**: Accepted
**Feature**: F001 (security hygiene)

## Context

The repository tracked `resources/tools/genetics/genetic_risk_predictor.pkl`, a scikit-learn model saved with `pickle`. Two scripts came with it:

- `resources/tools/genetics/train_dummy_model.py` trained a `RandomForestClassifier` on `make_classification` random data and pickled it.
- `resources/tools/genetics/genetic_predictor.py` loaded the pickle at import time and presented its output as a "probability of carrying a pathogenic variant".

Loading a pickle runs arbitrary code chosen by whoever wrote the file. GeneForgeLang is a public repository and package, so any contributor or compromised dependency could replace such a file. The provenance of the tracked `.pkl` was unknown. The scripts were also non-functional: the model expected 4 features and the loader sent 6, and the model path was relative to the wrong directory. No code, test, workflow or entry point referenced them, and `resources/` is not part of the built package.

The output was also misleading: random-data scores labelled as genetic risk. That conflicts with the project's intended use (research software, not for clinical use).

## Decision

1. Delete the three files: `genetic_risk_predictor.pkl`, `genetic_predictor.py` and `train_dummy_model.py`.
2. Adopt the rule: **no pickle or other code-executing serialization artifact is tracked in the repository or shipped in the package.** This covers `pickle`, `joblib`, `dill`, `cloudpickle`, `shelve`, PyTorch checkpoints loaded with `torch.load`, and NumPy files loaded with `allow_pickle=True`.
3. Library and tool code does not deserialize such formats. Models or data that GFL needs are stored in data-only formats (JSON, YAML, CSV, Parquet, safetensors, ONNX) with documented provenance, or fetched by the user from a named, versioned source.
4. Enforcement:
   - `.gitignore` ignores `*.pkl`, `*.pickle` and `*.joblib`.
   - `tests/security/test_repository_hygiene.py` fails if such a file is tracked, or if tracked Python code outside `tests/` calls a code-executing deserializer.

`pickle.dumps` used only to build in-memory cache keys (`src/geneforgelang/core/performance.py`) does not load untrusted data and is outside this rule.

## Consequences

- **Positive**: removes an arbitrary-code-execution vector and a misleading pseudo-clinical output from a public repository. The rule is checked automatically.
- **Negative**: a contributor who needs a trained model must use a data-only format or an external, versioned source, which takes more work than pickling.
- **Neutral**: the deleted files remain in git history. Purging history is a separate owner decision, tracked with the `.devcontainer/.env` purge.
