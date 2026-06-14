from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EquivalenceClass:
    name: str
    members: tuple[str | dict[str, Any], ...]


@dataclass(frozen=True)
class SignalPair:
    name: str
    baseline: str | dict[str, Any]
    mutated: str | dict[str, Any]


EQUIVALENCE_CLASSES = (
    EquivalenceClass(
        name="casing_variants",
        members=(
            """
            experiment:
              tool: CRISPR_cas9
              type: gene_editing
              params:
                target_gene: TP53
            """,
            """
            Experiment:
              TOOL: crispr_CAS9
              TYPE: GENE_EDITING
              params:
                target_gene: tp53
            """,
        ),
    ),
    EquivalenceClass(
        name="whitespace_variants",
        members=(
            """
            experiment:
              tool: CRISPR_cas9
              type: gene_editing
              params:
                target_gene: TP53
            """,
            """
            experiment:
                tool:   CRISPR_cas9
                type:   gene_editing
                params:
                    target_gene:   TP53
            """,
        ),
    ),
    EquivalenceClass(
        name="parser_artifacts",
        members=(
            {
                "experiment": {
                    "tool": "CRISPR_cas9",
                    "type": "gene_editing",
                    "params": {"target_gene": "TP53"},
                }
            },
            {
                "__parser__": "yaml",
                "experiment": {
                    "__line__": 1,
                    "_meta": {"source": "test.gfl"},
                    "normalization_path": ["legacy-parser", "fallback"],
                    "parser_fallback": True,
                    "tool": "CRISPR_cas9",
                    "type": "gene_editing",
                    "params": {"target_gene": "tp53"},
                },
            },
        ),
    ),
    EquivalenceClass(
        name="ordering_neutral_annotations",
        members=(
            {
                "experiment": {
                    "tool": "CRISPR_cas9",
                    "type": "gene_editing",
                    "params": {"target_gene": "TP53"},
                    "annotations": ["clinically_relevant", "tumor_suppressor"],
                }
            },
            {
                "experiment": {
                    "annotations": ["tumor_suppressor", "clinically_relevant"],
                    "params": {"target_gene": "TP53"},
                    "type": "gene_editing",
                    "tool": "CRISPR_cas9",
                }
            },
        ),
    ),
    EquivalenceClass(
        name="syntax_sugar_variants",
        members=(
            {
                "entity": "EGFR",
                "interacts_with": "ligand X",
                "effect": "activation(MAPK)",
            },
            {
                "ENTITY": "egfr",
                "interacts_with": {"role": "ligand", "target": "X"},
                "effect": {"type": "activation", "target": "MAPK"},
            },
        ),
    ),
)


NOISE_MUTATIONS = (
    {
        "experiment": {
            "tool": "CRISPR_cas9",
            "type": "gene_editing",
            "params": {"target_gene": "TP53"},
        }
    },
    {
        "__trace__": {"events": ["parse", "normalize"]},
        "experiment": {
            "source_loc": {"line": 12, "column": 4},
            "tool": "CRISPR_cas9",
            "type": "gene_editing",
            "params": {"target_gene": "TP53"},
        },
    },
)


SIGNAL_PAIRS = (
    SignalPair(
        name="target_gene_change",
        baseline="""
        experiment:
          tool: CRISPR_cas9
          type: gene_editing
          params:
            target_gene: TP53
        """,
        mutated="""
        experiment:
          tool: CRISPR_cas9
          type: gene_editing
          params:
            target_gene: BRCA1
        """,
    ),
    SignalPair(
        name="interaction_effect_change",
        baseline={
            "entity": "EGFR",
            "interacts_with": {"role": "ligand", "target": "X"},
            "effect": {"type": "activation", "target": "MAPK"},
        },
        mutated={
            "entity": "EGFR",
            "interacts_with": {"role": "ligand", "target": "X"},
            "effect": {"type": "inhibition", "target": "MAPK"},
        },
    ),
    SignalPair(
        name="ordered_workflow_change",
        baseline={"workflow": [{"step": "load"}, {"step": "analyze"}]},
        mutated={"workflow": [{"step": "analyze"}, {"step": "load"}]},
    ),
)
