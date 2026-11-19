"""Tests for Catalytic Motif and Enzyme Design Declarative Syntax in GFL.

Verifies strict boundary adherence (ADR-ARCH-001):
GFL provides pure syntactic representation and observational contracts
for catalytic motifs, triads, and transition-state substrates, without
crossing into active kinetic solvers or generative diffusion.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath("src"))

from geneforgelang.core.gftypes import (
    CatalyticMotif,
    CatalyticResidue,
    CatalyticResidueRole,
    EnzymeDesignContract,
    SubstrateLigandContainer,
)
from geneforgelang.core.parser import parse_gfl


def test_catalytic_residue_and_motif_declaration():
    """Verify syntactic representation of classical Ser-His-Asp catalytic triad."""
    ser195 = CatalyticResidue(
        residue_name="SER",
        role=CatalyticResidueRole.NUCLEOPHILE,
        position=195,
        chain="A",
        target_atom="OG",
        ideal_coordinates=(12.4, 5.8, -3.2),
    )
    his57 = CatalyticResidue(
        residue_name="HIS",
        role=CatalyticResidueRole.GENERAL_BASE,
        position=57,
        chain="A",
        target_atom="NE2",
        ideal_coordinates=(14.2, 7.1, -2.8),
    )
    asp102 = CatalyticResidue(
        residue_name="ASP",
        role=CatalyticResidueRole.TRANSITION_STATE_STABILIZER,
        position=102,
        chain="A",
        target_atom="OD1",
        ideal_coordinates=(16.0, 8.5, -1.9),
    )

    motif = CatalyticMotif(
        motif_id="SERINE_PROTEASE_TRIAD_001",
        residues=[ser195, his57, asp102],
        max_active_site_rmsd=0.8,
        spatial_distance_constraints={
            "SER:OG-HIS:NE2": (2.6, 3.2),
            "HIS:ND1-ASP:OD1": (2.5, 3.0),
        },
    )

    assert motif.residue_count == 3
    assert motif.max_active_site_rmsd == 0.8
    assert "SER:OG-HIS:NE2" in motif.spatial_distance_constraints
    d = motif.to_dict()
    assert d["motif_id"] == "SERINE_PROTEASE_TRIAD_001"
    assert len(d["residues"]) == 3
    assert d["residues"][0]["role"] == "NUCLEOPHILE"


def test_substrate_container_and_enzyme_design_contract():
    """Verify EnzymeDesignContract IO container binding motif and substrate analog."""
    ser195 = CatalyticResidue(residue_name="SER", role=CatalyticResidueRole.NUCLEOPHILE, position=195)
    his57 = CatalyticResidue(residue_name="HIS", role=CatalyticResidueRole.GENERAL_BASE, position=57)
    asp102 = CatalyticResidue(residue_name="ASP", role=CatalyticResidueRole.TRANSITION_STATE_STABILIZER, position=102)

    motif = CatalyticMotif(
        motif_id="CAT_TRIAD",
        residues=[ser195, his57, asp102],
    )

    substrate = SubstrateLigandContainer(
        substrate_name="p-nitrophenyl_acetate",
        smiles="CC(=O)Oc1ccc([N+](=O)[O-])cc1",
        charge=0,
        transition_state_analog=True,
        reactive_atom_indices=[1, 2],
    )

    contract = EnzymeDesignContract(
        enzyme_family="ESTERASE_SERINE_HYDROLase",
        catalytic_motif=motif,
        substrate=substrate,
        target_transition_state_distance=3.2,
        max_scaffold_pocket_clash=0.0,
    )

    assert contract.enzyme_family == "ESTERASE_SERINE_HYDROLase"
    assert contract.target_transition_state_distance == 3.2
    assert contract.substrate.transition_state_analog is True

    d = contract.to_dict()
    assert d["substrate"]["smiles"] == "CC(=O)Oc1ccc([N+](=O)[O-])cc1"
    assert d["catalytic_motif"]["residue_count"] == 3


def test_parse_de_novo_enzyme_gfl_workflow():
    """Verify GFL declarative parser on a de novo catalytic enzyme design script."""
    gfl_source = """
metadata:
  experiment_id: DE_NOVO_ESTERASE_DESIGN_001
  researcher: Dr. Manuel Menendez Gonzalez
  project: alpha_protein_novo_synergy
  date: 2026-10-06

design:
  entity: ProteinSequence
  model: de_novo_catalytic_scaffolder
  objective:
    minimize: active_site_rmsd
    target: 0.5
  count: 5
  output: catalytic_scaffold_candidates
  constraints:
    - catalytic_motif("SER:OG", "HIS:NE2", "ASP:OD1")
    - transition_state_distance(<= 3.5)
    - pocket_steric_clash(0.0)

experiment:
  tool: catalytic_motif_validator
  type: analysis
  strategy: structural_signature
  params:
    enzyme_family: "ESTERASE"
    substrate_smiles: "CC(=O)Oc1ccc([N+](=O)[O-])cc1"
    catalytic_residues:
      - { residue: "SER", role: "NUCLEOPHILE", atom: "OG" }
      - { residue: "HIS", role: "GENERAL_BASE", atom: "NE2" }
      - { residue: "ASP", role: "TRANSITION_STATE_STABILIZER", atom: "OD1" }
    distance_bounds:
      "SER:OG-HIS:NE2": [2.6, 3.2]

analyze:
  strategy: structural_observation
  thresholds:
    max_active_site_rmsd: 0.8
    require_all_catalytic_residues: true
"""
    ast = parse_gfl(gfl_source)
    assert ast is not None
    assert "design" in ast
    assert "experiment" in ast
    assert ast["experiment"]["params"]["enzyme_family"] == "ESTERASE"
    assert len(ast["experiment"]["params"]["catalytic_residues"]) == 3
