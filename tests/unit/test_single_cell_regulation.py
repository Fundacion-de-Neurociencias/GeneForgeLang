"""Unit tests for Single-Cell Immune Regulation and Cell-State Dynamics Layer.

Grounded in the TenK10K Phase 1 landmark dataset:
Cuomo, A. S. E., Spenceley, E., Tanudisastro, H. A., et al., Powell, J. E., MacArthur, D. G., et al.
"Rare and common genetic variants shape single-cell immune gene expression."
Nature (2026). DOI: 10.1038/s41586-026-10721-2.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from geneforgelang.core.gftypes import (
    GFLAST,
    CellAbundanceQTLContract,
    CellStateAxis,
    CellStateInteractionContract,
    ColocalizationGateContract,
    RegulatoryQTLType,
    SingleCellRegulatoryContract,
    TandemRepeatContract,
    TenK10KImmuneCellType,
)
from geneforgelang.core.single_cell_engine import (
    SingleCellRegulatoryEngine,
)
from geneforgelang.core.validator import EnhancedSemanticValidator


class TestSingleCellTypes:
    """Test single-cell enums and dataclass contracts."""

    def test_enums_and_curies(self) -> None:
        """Verify 28 PBMC immune cell types map to valid Cell Ontology CURIEs."""
        assert TenK10KImmuneCellType.NK_CD56_DIM.value == "CL:0000938"
        assert TenK10KImmuneCellType.MONOCYTE_CLASSICAL.value == "CL:0000860"
        assert TenK10KImmuneCellType.CD4_TREG.value == "CL:0000815"
        assert TenK10KImmuneCellType.CD8_CYTOTOXIC.value == "CL:0000911"
        assert len(TenK10KImmuneCellType) == 28

        assert str(RegulatoryQTLType.CELL_STATE_INTERACTION) == "cell_state_interaction"
        assert str(CellStateAxis.CYTOTOXICITY) == "cytotoxicity"

    def test_contract_roundtrip(self) -> None:
        """Test serialization and deserialization of SingleCellRegulatoryContract."""
        contract = SingleCellRegulatoryContract(
            contract_id="test_sc_contract",
            target_gene="GZMB",
            variant="chr19:45823101:A>G",
            variant_type="snv",
            cell_type=TenK10KImmuneCellType.NK_CD56_DIM,
            qtl_type=RegulatoryQTLType.CELL_STATE_INTERACTION,
            is_cell_type_specific=True,
            is_distal_enhancer=False,
            distance_to_tss_bp=1250,
            beta_marginal=0.28,
            state_interaction=CellStateInteractionContract(
                state_axis=CellStateAxis.CYTOTOXICITY,
                beta_baseline=0.14,
                gamma_interaction=0.52,
                state_range=(0.1, 0.95),
            ),
            abundance_qtl=CellAbundanceQTLContract(
                target_cell_type="CL:0000860",
                effect_size_delta=-0.18,
                baseline_fraction=0.12,
                driver_gene="LYZ",
            ),
            colocalization_gate=ColocalizationGateContract(
                gwas_trait_id="EFO:0003885",
                candidate_gene="GZMB",
                posterior_prob_h4=0.92,
                pp4_threshold=0.80,
            ),
            tandem_repeat=TandemRepeatContract(
                repeat_unit_motif="CAG",
                reference_copy_number=10,
                alternate_copy_number=14,
                delta_copies=4,
            ),
        )

        d = contract.to_dict()
        assert d["target_gene"] == "GZMB"
        assert d["cell_type"] == "CL:0000938"
        assert d["state_interaction"]["gamma_interaction"] == 0.52
        assert d["colocalization_gate"]["is_colocalized"] is True

        restored = SingleCellRegulatoryContract.from_dict(d)
        assert restored.target_gene == contract.target_gene
        assert restored.cell_type == TenK10KImmuneCellType.NK_CD56_DIM
        assert restored.state_interaction is not None
        assert restored.state_interaction.gamma_interaction == 0.52
        assert restored.abundance_qtl is not None
        assert restored.abundance_qtl.effect_size_delta == -0.18

    def test_gflast_roundtrip(self) -> None:
        """Test embedding of single_cell_regulation inside GFLAST."""
        contract = SingleCellRegulatoryContract(
            contract_id="ast_test",
            target_gene="IL2RA",
            variant="chr10:6058312:G>A",
            cell_type=TenK10KImmuneCellType.CD4_TREG,
            beta_marginal=0.45,
        )

        ast = GFLAST(single_cell_regulation=contract)
        ast_dict = ast.to_dict()
        assert "single_cell_regulation" in ast_dict
        assert ast_dict["single_cell_regulation"]["target_gene"] == "IL2RA"

        restored_ast = GFLAST.from_dict(ast_dict)
        assert restored_ast.single_cell_regulation is not None
        assert restored_ast.single_cell_regulation.target_gene == "IL2RA"


class TestSingleCellEngine:
    """Test computational physics and statistics in SingleCellRegulatoryEngine."""

    @pytest.fixture
    def engine(self) -> SingleCellRegulatoryEngine:
        return SingleCellRegulatoryEngine()

    def test_state_dependent_interaction_monotonicity(self, engine: SingleCellRegulatoryEngine) -> None:
        """Ensure positive gamma yields strictly increasing beta across activation axis."""
        interaction = CellStateInteractionContract(
            state_axis=CellStateAxis.CYTOTOXICITY,
            beta_baseline=0.10,
            gamma_interaction=0.60,
            state_range=(0.0, 1.0),
        )

        trajectory = engine.evaluate_state_trajectory(interaction, steps=5)
        betas = [p.effective_beta for p in trajectory.state_points]

        # Monotonically increasing
        for i in range(len(betas) - 1):
            assert betas[i + 1] > betas[i]

        assert trajectory.min_beta == pytest.approx(0.10, abs=1e-5)
        assert trajectory.max_beta == pytest.approx(0.70, abs=1e-5)
        assert trajectory.dynamic_range_delta == pytest.approx(0.60, abs=1e-5)

    def test_clamped_state_boundaries(self, engine: SingleCellRegulatoryEngine) -> None:
        """Ensure state values outside specified bounds are safely clamped."""
        interaction = CellStateInteractionContract(
            state_axis=CellStateAxis.INTERFERON_STIMULATION,
            beta_baseline=0.20,
            gamma_interaction=0.40,
            state_range=(0.2, 0.8),
        )

        p_low = engine.evaluate_state_point(interaction, state_value=-0.5)
        assert p_low.state_value == 0.2
        assert p_low.effective_beta == pytest.approx(0.20 + 0.40 * 0.2, abs=1e-5)

        p_high = engine.evaluate_state_point(interaction, state_value=1.5)
        assert p_high.state_value == 0.8
        assert p_high.effective_beta == pytest.approx(0.20 + 0.40 * 0.8, abs=1e-5)

    def test_abundance_shift_simplex_conservation(self, engine: SingleCellRegulatoryEngine) -> None:
        """Ensure cell frequency shifts conserve valid subpopulation bounds in (0, 1)."""
        depletion_contract = CellAbundanceQTLContract(
            target_cell_type="CL:0000860",
            baseline_fraction=0.15,
            effect_size_delta=-0.40,
        )
        res_dep = engine.evaluate_abundance_shift(depletion_contract)
        assert res_dep.direction == "DEPLETION"
        assert res_dep.perturbed_frequency < res_dep.baseline_frequency
        assert 0.0 < res_dep.perturbed_frequency < 1.0

        expansion_contract = CellAbundanceQTLContract(
            target_cell_type="CL:0000860",
            baseline_fraction=0.15,
            effect_size_delta=0.80,
        )
        res_exp = engine.evaluate_abundance_shift(expansion_contract)
        assert res_exp.direction == "EXPANSION"
        assert res_exp.perturbed_frequency > res_exp.baseline_frequency
        assert 0.0 < res_exp.perturbed_frequency < 1.0

    def test_bayesian_colocalization_abf(self, engine: SingleCellRegulatoryEngine) -> None:
        """Test Wakefield ABF colocalization posterior probabilities."""
        # Highly concordant strong signals
        res_coloc = engine.evaluate_colocalization_abf(
            gwas_beta=0.45,
            gwas_se=0.05,
            eqtl_beta=0.50,
            eqtl_se=0.06,
            pp4_threshold=0.80,
            gwas_trait_id="MS_GWAS",
            candidate_gene="IL2RA",
        )
        assert res_coloc.is_colocalized is True
        assert res_coloc.pp4 >= 0.80

        # Discordant / null signals
        res_null = engine.evaluate_colocalization_abf(
            gwas_beta=0.01,
            gwas_se=0.10,
            eqtl_beta=0.02,
            eqtl_se=0.12,
            pp4_threshold=0.80,
        )
        assert res_null.is_colocalized is False
        assert res_null.pp4 < 0.10

    def test_full_circuit_simulation(self, engine: SingleCellRegulatoryEngine) -> None:
        """Execute full circuit simulation on a realistic TenK10K contract."""
        contract = SingleCellRegulatoryContract(
            contract_id="sim_test",
            target_gene="GZMB",
            variant="chr19:45823101:A>G",
            cell_type=TenK10KImmuneCellType.NK_CD56_DIM,
            distance_to_tss_bp=25000,  # Distal enhancer
            beta_marginal=0.30,
            standard_error=0.04,
            state_interaction=CellStateInteractionContract(
                state_axis=CellStateAxis.CYTOTOXICITY,
                beta_baseline=0.12,
                gamma_interaction=0.48,
            ),
            abundance_qtl=CellAbundanceQTLContract(
                effect_size_delta=-0.15,
                baseline_fraction=0.10,
            ),
            colocalization_gate=ColocalizationGateContract(
                posterior_prob_h4=0.88,
                pp4_threshold=0.80,
            ),
        )

        sim = engine.simulate_circuit(contract)
        assert sim.is_distal_enhancer is True
        assert sim.state_trajectory is not None
        assert len(sim.state_trajectory.state_points) == 11
        assert sim.abundance_result is not None
        assert sim.abundance_result.direction == "DEPLETION"
        assert sim.colocalization_result is not None
        assert sim.colocalization_result.is_colocalized is True


class TestSingleCellValidator:
    """Test validation rules and error traps in EnhancedSemanticValidator."""

    @pytest.fixture
    def validator(self) -> EnhancedSemanticValidator:
        return EnhancedSemanticValidator()

    def test_validate_exemplar_file(self, validator: EnhancedSemanticValidator) -> None:
        """Ensure the exemplar protocol passes validation with 0 errors."""
        example_path = Path("examples/single_cell_immune_regulation_tenk10k.gfl")
        assert example_path.exists(), f"Exemplar file {example_path} not found"

        with open(example_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        result = validator.validate_ast(data)
        assert len(result.errors) == 0, f"Validation failed: {[e.message for e in result.errors]}"

    def test_validator_rejections(self, validator: EnhancedSemanticValidator) -> None:
        """Test semantic validator catches invalid configurations."""
        # 1. Missing target_gene
        r1 = validator.validate_ast(
            {
                "single_cell_regulation": {
                    "variant": "chr1:100:A>G",
                    "cell_type": "CL:0000938",
                }
            }
        )
        assert any("target_gene" in e.message for e in r1.errors)

        # 2. Missing variant
        r2 = validator.validate_ast(
            {
                "single_cell_regulation": {
                    "target_gene": "GZMB",
                    "cell_type": "CL:0000938",
                }
            }
        )
        assert any("variant" in e.message for e in r2.errors)

        # 3. Malformed Cell Ontology CURIE
        r3 = validator.validate_ast(
            {
                "single_cell_regulation": {
                    "target_gene": "GZMB",
                    "variant": "chr19:45823101:A>G",
                    "cell_type": "CL:938",  # Should be 7 digits: CL:0000938
                }
            }
        )
        assert any("Malformed Cell Ontology" in e.message for e in r3.errors)

        # 4. Negative distance_to_tss_bp
        r4 = validator.validate_ast(
            {
                "single_cell_regulation": {
                    "target_gene": "GZMB",
                    "variant": "chr19:45823101:A>G",
                    "cell_type": "CL:0000938",
                    "distance_to_tss_bp": -500,
                }
            }
        )
        assert any("cannot be negative" in e.message for e in r4.errors)

        # 5. Invalid state_range
        r5 = validator.validate_ast(
            {
                "single_cell_regulation": {
                    "target_gene": "GZMB",
                    "variant": "chr19:45823101:A>G",
                    "cell_type": "CL:0000938",
                    "state_interaction": {
                        "state_range": [0.8, 0.2],  # min > max
                    },
                }
            }
        )
        assert any("state_range" in e.message for e in r5.errors)

        # 6. Invalid abundance effect_size_delta outside [-1, 1]
        r6 = validator.validate_ast(
            {
                "single_cell_regulation": {
                    "target_gene": "GZMB",
                    "variant": "chr19:45823101:A>G",
                    "cell_type": "CL:0000938",
                    "abundance_qtl": {
                        "effect_size_delta": 2.5,
                    },
                }
            }
        )
        assert any("effect_size_delta" in e.message for e in r6.errors)

        # 7. Non-DNA repeat_unit_motif in tandem_repeat
        r7 = validator.validate_ast(
            {
                "single_cell_regulation": {
                    "target_gene": "GZMB",
                    "variant": "chr19:45823101:A>G",
                    "cell_type": "CL:0000938",
                    "tandem_repeat": {
                        "repeat_unit_motif": "CAGX",
                    },
                }
            }
        )
        assert any("repeat_unit_motif" in e.message for e in r7.errors)
