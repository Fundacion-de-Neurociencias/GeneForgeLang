"""Unit tests for measurement-consistent ensembles, co-folding consensus, and physics refinement.

Validates the integration of:
1. ConsensusModel expansion (Chai-1, Protenix, AF3, RF3, Boltz-1)
2. Runs N' Poses benchmark metric gates
3. ExperimentalRestraintsContract (NMR, Cryo-EM, SAXS, XL-MS)
4. LigandConditionedPocketContract (Apo vs Holo cryptic pocket induction)
5. PhysicsRefinementPolicy (OpenMM / force-field clash relief)
6. EnhancedSemanticValidator compatibility for new tools and models
"""

import pytest
from geneforgelang.core.gftypes import (
    ConsensusModel,
    ExperimentalRestraintsContract,
    LigandConditionedPocketContract,
    MultiModelConsensus,
    PhysicsRefinementPolicy,
    RestraintType,
    RunsNPosesMetric,
)
from geneforgelang.core.validator import EnhancedSemanticValidator


def test_consensus_model_expansion() -> None:
    """Verify that ConsensusModel correctly includes Chai-1 and Protenix."""
    assert ConsensusModel.CHAI_1 == "chai1"
    assert ConsensusModel.PROTENIX == "protenix"
    assert ConsensusModel.AF3 == "alphafold3"
    assert ConsensusModel.RF3 == "rosettafold3"
    assert ConsensusModel.BOLTZ == "boltz1"
    assert str(ConsensusModel.CHAI_1) == "chai1"
    assert str(ConsensusModel.PROTENIX) == "protenix"


def test_multimodel_consensus_five_models() -> None:
    """Verify multi-model consensus evaluation across AF3, RF3, Boltz, Chai-1, and Protenix."""
    # All 5 models meet strict threshold
    consensus = MultiModelConsensus(
        af3_iptm=0.88,
        af3_ipae=1.8,
        rf3_confidence=0.85,
        boltz_confidence=0.89,
        chai1_confidence=0.87,
        protenix_confidence=0.91,
        plddt_mean=92.4,
    )
    assert consensus.passes_consensus(min_iptm=0.8, max_ipae=2.5, min_confidence=0.8) is True
    assert consensus.is_near_miss() is False

    # Chai-1 confidence below threshold
    discordant_consensus = MultiModelConsensus(
        af3_iptm=0.88,
        af3_ipae=1.8,
        rf3_confidence=0.85,
        boltz_confidence=0.89,
        chai1_confidence=0.62,  # fails min_confidence 0.8
        protenix_confidence=0.91,
    )
    assert discordant_consensus.passes_consensus() is False

    # Protenix confidence below threshold
    protenix_discordant = MultiModelConsensus(
        af3_iptm=0.88,
        af3_ipae=1.8,
        rf3_confidence=0.85,
        boltz_confidence=0.89,
        chai1_confidence=0.85,
        protenix_confidence=0.71,  # fails min_confidence 0.8
    )
    assert protenix_discordant.passes_consensus() is False

    # Serialization check
    d = consensus.to_dict()
    assert d["chai1_confidence"] == 0.87
    assert d["protenix_confidence"] == 0.91
    assert d["passes_consensus"] is True


def test_experimental_restraints_contract() -> None:
    """Verify measurement-guided ensemble restraints contract evaluation."""
    assert RestraintType.NMR_NOE == "nmr_noe"
    assert RestraintType.CRYO_EM_MAP == "cryo_em_map"
    assert RestraintType.XL_MS == "xl_ms"
    assert RestraintType.SAXS_ENVELOPE == "saxs_envelope"
    assert RestraintType.EPR_DEER == "epr_deer"

    # Default contract without explicit ratio is satisfied
    contract_default = ExperimentalRestraintsContract(
        restraint_type=RestraintType.NMR_NOE,
        restraint_file="data/restraints/bmrb_noe_gpcr.tbl",
        tolerance_angstrom=2.5,
    )
    assert contract_default.is_satisfied() is True

    # High satisfaction ratio
    contract_satisfied = ExperimentalRestraintsContract(
        restraint_type=RestraintType.CRYO_EM_MAP,
        restraint_file="data/maps/emd_30421.mrc",
        satisfaction_ratio=0.88,
        min_satisfaction_threshold=0.80,
    )
    assert contract_satisfied.is_satisfied() is True

    # Unsatisfied experimental restraints
    contract_unsatisfied = ExperimentalRestraintsContract(
        restraint_type=RestraintType.SAXS_ENVELOPE,
        satisfaction_ratio=0.62,
        min_satisfaction_threshold=0.80,
    )
    assert contract_unsatisfied.is_satisfied() is False

    d = contract_satisfied.to_dict()
    assert d["restraint_type"] == "cryo_em_map"
    assert d["is_satisfied"] is True


def test_runs_n_poses_metric() -> None:
    """Verify protein-ligand co-folding pose gating under Runs N' Poses benchmark criteria."""
    # Favorable pose: low RMSD, minimal clashes
    favorable_pose = RunsNPosesMetric(
        pose_rmsd=1.25,
        clash_score=3.5,
        contact_recovery=0.92,
        force_field_energy_kcal_mol=-48.2,
    )
    assert favorable_pose.passes_pose_gate(max_rmsd=2.0, max_clash=10.0) is True

    # Steric clash failure (typical in unrefined GPCR co-folding predictions)
    clashing_pose = RunsNPosesMetric(
        pose_rmsd=1.8,
        clash_score=28.4,  # Severe steric collision
        contact_recovery=0.75,
        force_field_energy_kcal_mol=145.0,
    )
    assert clashing_pose.passes_pose_gate() is False

    # Pose divergence failure
    distorted_pose = RunsNPosesMetric(
        pose_rmsd=4.2,  # Divergent pose
        clash_score=4.0,
    )
    assert distorted_pose.passes_pose_gate() is False

    d = favorable_pose.to_dict()
    assert d["pose_rmsd"] == 1.25
    assert d["passes_pose_gate"] is True


def test_ligand_conditioned_pocket_contract() -> None:
    """Verify cryptic pocket induction contract (apo closed vs holo open)."""
    # Holo state: ligand presence induces pocket expansion
    induced_pocket = LigandConditionedPocketContract(
        target_receptor="ADRB2_HUMAN",
        probe_ligand_smiles="CC(C)NCC(O)C1=CC(=C(O)C=C1)O",
        pocket_mode="differential",
        cryptic_delta_score=0.48,
        min_cryptic_delta_threshold=0.35,
    )
    assert induced_pocket.is_cryptic_induced() is True

    # Apo state: pocket remains collapsed or negligible delta
    uninduced_pocket = LigandConditionedPocketContract(
        target_receptor="ADRB2_HUMAN",
        pocket_mode="apo_uninduced",
        cryptic_delta_score=0.12,
        min_cryptic_delta_threshold=0.35,
    )
    assert uninduced_pocket.is_cryptic_induced() is False

    d = induced_pocket.to_dict()
    assert d["target_receptor"] == "ADRB2_HUMAN"
    assert d["is_cryptic_induced"] is True


def test_physics_refinement_policy() -> None:
    """Verify physics-based force field refinement configuration."""
    policy = PhysicsRefinementPolicy(
        engine="openmm",
        force_field="amber14sb",
        max_iterations=1000,
        tolerance_kj_mol=5.0,
        restrain_backbone=True,
    )
    assert policy.engine == "openmm"
    assert policy.force_field == "amber14sb"
    d = policy.to_dict()
    assert d["engine"] == "openmm"
    assert d["tolerance_kj_mol"] == 5.0
    assert d["restrain_backbone"] is True


def test_semantic_validator_structural_tools_and_models() -> None:
    """Verify that EnhancedSemanticValidator accepts the new co-folding and physics tools."""
    validator = EnhancedSemanticValidator()

    # Valid Chai-1 co-folding analysis AST
    ast_chai = {
        "metadata": {"experiment_name": "Chai1 GPCR Co-folding", "version": "2.0.0"},
        "experiment": {
            "tool": "chai1",
            "type": "analysis",
            "params": {"target_receptor": "HTR2A", "ligand": "LSD"},
        },
    }
    result_chai = validator.validate_ast(ast_chai)
    assert result_chai.is_valid is True
    assert len(result_chai.errors) == 0

    # Valid Protenix simulation AST
    ast_protenix = {
        "metadata": {"experiment_name": "Protenix Structural Ensemble", "version": "2.0.0"},
        "experiment": {
            "tool": "protenix",
            "type": "simulation",
            "params": {"sequence": "MKVLWAALLVTFLAGCQAKVEQAVETEPEPELRQQTEWQSGQR"},
        },
    }
    result_protenix = validator.validate_ast(ast_protenix)
    assert result_protenix.is_valid is True

    # Valid OpenMM physics refinement AST
    ast_openmm = {
        "metadata": {"experiment_name": "OpenMM Energy Minimization", "version": "2.0.0"},
        "experiment": {
            "tool": "openmm",
            "type": "simulation",
            "params": {"force_field": "amber14sb", "tolerance_kj_mol": 10.0},
        },
    }
    result_openmm = validator.validate_ast(ast_openmm)
    assert result_openmm.is_valid is True

    # Valid Runs N' Poses validation AST
    ast_rnp = {
        "metadata": {"experiment_name": "Runs N Poses Benchmark Gate", "version": "2.0.0"},
        "experiment": {
            "tool": "runs_n_poses",
            "type": "validation",
            "params": {"max_rmsd": 2.0, "max_clash": 10.0},
        },
    }
    result_rnp = validator.validate_ast(ast_rnp)
    assert result_rnp.is_valid is True
