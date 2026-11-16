# Simulated, stub and dead components

State is one of `simulated` (returns random or hash-derived values), `stub` (returns constants or canned text) or `dead` (cannot run). No component is `real`: promotion needs the oracle in the last column. The registry in `src/geneforgelang/provenance.py` (`list_simulated_components()`) lists the first seven rows; a test keeps this table and the registry in agreement.

| Component | State | Location | Promotion oracle |
|---|---|---|---|
| `SimpleProteinGenerator` | simulated | `src/geneforgelang/plugins/builtin/protein_generator.py` | A generative model with a held-out benchmark of expressed, folded proteins |
| `SimpleOptimizer` | simulated | `src/geneforgelang/plugins/builtin/simple_optimizer.py` | An objective function backed by a real model or assay, with a test that the search beats chance |
| `AlphaGenomePlugin` | stub | `src/geneforgelang/plugins/alpha_genome.py` | Access to the real AlphaGenome service and a test against its published predictions |
| `OpenMedConnector` | stub | `src/geneforgelang/ir/external/openmed_connector.py` | A connected OpenMed service and, for privacy, a validated de-identification filter with a recall test on labelled notes |
| `ProteinVAEGenerator` | simulated | `src/geneforgelang/utils/example_implementations.py` | A trained protein VAE and a held-out benchmark of expressed, folded sequences |
| `MoleculeTransformerGenerator` | simulated | `src/geneforgelang/utils/example_implementations.py` | A trained molecular transformer and a benchmark against measured molecular properties |
| `BayesianOptimizer` | simulated | `src/geneforgelang/utils/example_implementations.py` | A Gaussian-process model fitted to real experiment results, with a test that it beats random search |
| `execute_genesis_real` | simulated | `examples/real_project/execute_genesis_real.py` | Real engine and assay results replacing the random scores; the script registers itself when run |
| `VariantSimulationPlugin` | dead | `src/geneforgelang/plugins/variant_sim.py` | The missing `simulate_variant_effect.py` and a variant-effect benchmark; construction raises `FileNotFoundError` today |

Not in the table: the rule-based inference path (`HeuristicModel`, `DummyGeneModel`, `InferenceResult`). It is deterministic and already labelled `simulated` in the public contract; a type-level label is proposed as its own feature, with the oracle of a model validated on measured data.
