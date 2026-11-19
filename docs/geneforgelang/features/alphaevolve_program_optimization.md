# AlphaEvolve Program Evolution in GeneForgeLang (GFL)

## 1. Overview and Rationale

Traditional computational biology and wet-lab orchestration rely on fixed, hand-crafted heuristics:
- Rigid scoring functions for docking, folding, and kinetic simulations.
- Fixed liquid-handler scheduling and pipetting parameters.
- Manual trial-and-error parameter tuning.

**AlphaEvolve** (Google DeepMind / Google Cloud) represents a paradigm shift: evolving the **code representations, heuristics, and algorithmic protocols** via LLM code-mutation engines guided by rigorous, deterministic fitness evaluators.

## 2. Declarative Separation of Concerns (ADR-ARCH-001)

In the GeneForge ecosystem:
- **GeneForgeLang (GFL)** defines the **declarative contract**: population size, seed program path, mutation engine identity, generations, elitism rates, and deterministic harness requirements.
- **GeneForge (GF / runtime)** manages the evolutionary search loop, sandbox code execution, AST mutations, and API calls to LLM coding agents.

## 3. GFL Contract Specification

```gfl
program_evolution AlphaEvolvePipettingFoundry {
  seed_program: "protocols/hts_liquid_handling_v1.py"
  mutation_engine: "gemini-1.5-pro"
  population_size: 25
  generations: 15
  elitism_rate: 0.20
  mutation_operators: [
    "diff_prompt",
    "semantic_refactor",
    "hyperparameter_tune",
    "algorithmic_crossover"
  ]
  deterministic_eval_harness: "evals/eval_pipetting_precision.py"
  timeout_per_eval_seconds: 45.0
  target_fitness_threshold: 0.985
}

optimize PipettingProtocolOptimization {
  strategy: "AlphaEvolve"
  alpha_evolve: {
    seed_program: "protocols/hts_liquid_handling_v1.py"
    population_size: 25
    generations: 15
    elitism_rate: 0.20
  }
  objective: {
    maximize: "liquid_transfer_accuracy_f1"
  }
}
```

## 4. Semantic Validation Rules

`EnhancedSemanticValidator` enforces the following invariants:
- `population_size`: Must be a strictly positive integer ($> 0$).
- `generations`: Must be a strictly positive integer ($> 0$).
- `elitism_rate`: Must be a float within $[0.0, 1.0]$.
- `seed_program`: Must be a non-empty string path or identifier.
