"""Unit tests for AlphaGenome 2 (DeepMind 2026) in GeneForgeLang.

Tests:
- 1 Mb dedicated sequence context window validation.
- Dedicated cellular state representation and zero-shot conditioning.
- Cross-modality epigenetic imputation (including 5mC DNA methylation).
- Distal enhancer-to-gene mapping and contact decay mechanics.
- Semantic validation traps and compiler error detection.
"""

from __future__ import annotations

import pytest
from geneforgelang.core.alphagenome2_engine import (
    AlphaGenome2Engine,
)
from geneforgelang.core.gftypes import (
    GFLAST,
    AG2CellularContextContract,
    AG2ConditioningMode,
    AG2EnhancerGeneLinkContract,
    AG2EpigeneticModality,
    AlphaGenome2Contract,
    ReferenceGenomeBuild,
)
from geneforgelang.core.parser import parse_gfl
from geneforgelang.core.validator import EnhancedSemanticValidator, ErrorCodes


class TestAlphaGenome2Types:
    """Test AlphaGenome 2 enums and dataclass contracts."""

    def test_enums(self) -> None:
        """Verify conditioning modes and epigenetic output modalities."""
        assert AG2ConditioningMode.CELL_ONTOLOGY_CURIE.value == "cell_ontology_curie"
        assert AG2ConditioningMode.SCRNA_PROFILE.value == "scrna_profile"
        assert AG2ConditioningMode.CELL_STATE_AXIS.value == "cell_state_axis"

        assert AG2EpigeneticModality.CHROMATIN_ACCESSIBILITY.value == "chromatin_accessibility"
        assert AG2EpigeneticModality.DNA_METHYLATION_5MC.value == "dna_methylation_5mc"
        assert AG2EpigeneticModality.HISTONE_H3K27AC.value == "histone_h3k27ac"
        assert AG2EpigeneticModality.HISTONE_H3K4ME3.value == "histone_h3k4me3"
        assert AG2EpigeneticModality.HISTONE_H3K27ME3.value == "histone_h3k27me3"
        assert AG2EpigeneticModality.CAGE_TSS.value == "cage_tss"
        assert AG2EpigeneticModality.RNA_EXPRESSION.value == "rna_expression"

    def test_cellular_context_contract(self) -> None:
        """Verify AG2CellularContextContract roundtrip."""
        ctx = AG2CellularContextContract(
            cell_type_curie="CL:0000938",
            cell_type_name="NK_CD56_dim",
            conditioning_mode=AG2ConditioningMode.CELL_ONTOLOGY_CURIE,
            profile_vector_or_uri="lakehouse://profiles/nk.arrow",
            continuous_state_value=0.82,
        )
        d = ctx.to_dict()
        assert d["cell_type_curie"] == "CL:0000938"
        assert d["continuous_state_value"] == 0.82

        restored = AG2CellularContextContract.from_dict(d)
        assert restored.cell_type_curie == "CL:0000938"
        assert restored.conditioning_mode == AG2ConditioningMode.CELL_ONTOLOGY_CURIE
        assert restored.profile_vector_or_uri == "lakehouse://profiles/nk.arrow"

    def test_enhancer_gene_link_contract(self) -> None:
        """Verify AG2EnhancerGeneLinkContract roundtrip."""
        eg = AG2EnhancerGeneLinkContract(
            target_gene_id="ENSG00000100453",
            promoter_tss_bp=24597470,
            max_distance_bp=500000,
            min_contact_probability=0.65,
            predicted_contact_probability=0.78,
            expression_fold_change=1.45,
        )
        d = eg.to_dict()
        assert d["target_gene_id"] == "ENSG00000100453"
        assert d["min_contact_probability"] == 0.65

        restored = AG2EnhancerGeneLinkContract.from_dict(d)
        assert restored.target_gene_id == "ENSG00000100453"
        assert restored.promoter_tss_bp == 24597470
        assert restored.max_distance_bp == 500000

    def test_alphagenome2_contract_roundtrip(self) -> None:
        """Verify AlphaGenome2Contract parsing, coordinate extraction, and Atlas URL."""
        contract = AlphaGenome2Contract(
            contract_id="test_ag2_gzmb",
            locus_window_1mb="chr14:24100000-25100000",
            genome_build=ReferenceGenomeBuild.GRCH38,
            variant="chr14:24598100:C>T",
            impute_modalities=[
                AG2EpigeneticModality.CHROMATIN_ACCESSIBILITY,
                AG2EpigeneticModality.DNA_METHYLATION_5MC,
            ],
            enhancer_gene_linking=AG2EnhancerGeneLinkContract(
                target_gene_id="GZMB",
                promoter_tss_bp=24597470,
            ),
        )
        assert contract.chromosome == "chr14"
        assert contract.start_bp == 24100000
        assert contract.end_bp == 25100000
        assert "deepmind.google.com/science/alphagenome/atlas/variant" in contract.atlas_url

        d = contract.to_dict()
        assert d["contract_id"] == "test_ag2_gzmb"
        assert d["locus_window_1mb"] == "chr14:24100000-25100000"
        assert len(d["impute_modalities"]) == 2

        restored = AlphaGenome2Contract.from_dict(d)
        assert restored.contract_id == "test_ag2_gzmb"
        assert restored.chromosome == "chr14"
        assert len(restored.impute_modalities) == 2
        assert restored.enhancer_gene_linking is not None
        assert restored.enhancer_gene_linking.target_gene_id == "GZMB"

    def test_gflast_roundtrip_and_aliases(self) -> None:
        """Verify GFLAST support for alphagenome2, ag2_locus, and cellular_regulation_1mb."""
        contract = AlphaGenome2Contract(
            contract_id="c1",
            locus_window_1mb="chr14:24000000-25000000",
        )
        ast1 = GFLAST(alphagenome2=contract)
        d = ast1.to_dict()
        assert "alphagenome2" in d

        # Restore from ag2_locus alias
        ast_alias1 = GFLAST.from_dict({"ag2_locus": contract.to_dict()})
        assert ast_alias1.alphagenome2 is not None
        assert ast_alias1.alphagenome2.contract_id == "c1"

        # Restore from cellular_regulation_1mb alias
        ast_alias2 = GFLAST.from_dict({"cellular_regulation_1mb": contract.to_dict()})
        assert ast_alias2.alphagenome2 is not None
        assert ast_alias2.alphagenome2.contract_id == "c1"


class TestAlphaGenome2Engine:
    """Test computational algorithms and physics in AlphaGenome2Engine."""

    @pytest.fixture
    def engine(self) -> AlphaGenome2Engine:
        return AlphaGenome2Engine()

    def test_parse_locus_1mb_valid(self, engine: AlphaGenome2Engine) -> None:
        """Verify parsing exactly 1 Mb sequence locus window."""
        chrom, start, end, span = engine.parse_locus_1mb("chr14:24100000-25100000")
        assert chrom == "chr14"
        assert start == 24100000
        assert end == 25100000
        assert span == 1_000_000

    def test_parse_locus_1mb_rejects_over_1mb(self, engine: AlphaGenome2Engine) -> None:
        """Engine must reject sequence windows exceeding 1,000,000 bp."""
        with pytest.raises(ValueError, match="exceeds maximum AlphaGenome 2 window limit"):
            engine.parse_locus_1mb("chr14:24000000-25200000")  # 1.2 Mb

    def test_parse_locus_1mb_rejects_negative_or_inverted(self, engine: AlphaGenome2Engine) -> None:
        """Engine must reject inverted coordinates."""
        with pytest.raises(ValueError, match="strictly less than"):
            engine.parse_locus_1mb("chr14:25000000-24000000")

    def test_compute_enhancer_gene_contact(self, engine: AlphaGenome2Engine) -> None:
        """Verify distance decay and active chromatin boosting in E-G linking."""
        link_contract = AG2EnhancerGeneLinkContract(
            target_gene_id="GZMB",
            promoter_tss_bp=24597470,
            max_distance_bp=500000,
            min_contact_probability=0.30,
        )

        # Proximal enhancer (20 kb away)
        proximal = engine.compute_enhancer_gene_contact(
            enhancer_pos_bp=24597470 + 20000,
            link_contract=link_contract,
            active_histone_signal=2.0,
        )
        assert proximal.distance_bp == 20000
        assert proximal.loop_contact_probability > 0.60
        assert proximal.is_functionally_linked is True
        assert proximal.direction in ("ACTIVATION", "NEUTRAL")

        # Distal enhancer (450 kb away)
        distal = engine.compute_enhancer_gene_contact(
            enhancer_pos_bp=24597470 + 450000,
            link_contract=link_contract,
            active_histone_signal=0.5,
        )
        assert distal.distance_bp == 450000
        assert distal.loop_contact_probability < proximal.loop_contact_probability

    def test_impute_epigenetic_modalities(self, engine: AlphaGenome2Engine) -> None:
        """Verify cross-modality imputation for ATAC, 5mC methylation, and H3K27ac."""
        cell_ctx = AG2CellularContextContract(
            cell_type_curie="CL:0000938",
            continuous_state_value=0.85,
        )
        modalities = [
            AG2EpigeneticModality.CHROMATIN_ACCESSIBILITY,
            AG2EpigeneticModality.DNA_METHYLATION_5MC,
            AG2EpigeneticModality.HISTONE_H3K27AC,
        ]
        results = engine.impute_epigenetic_modalities(
            modalities=modalities,
            cell_context=cell_ctx,
            variant_str="chr14:24598100:C>T",
        )
        assert len(results) == 3
        mod_map = {r.modality: r for r in results}

        # 5mC DNA methylation fraction must be in [0.0, 1.0]
        m5c = mod_map[AG2EpigeneticModality.DNA_METHYLATION_5MC]
        assert 0.0 <= m5c.imputed_signal <= 1.0
        assert m5c.assay_unit == "methylation_fraction"
        assert m5c.confidence_score >= 0.90

        # Chromatin accessibility
        atac = mod_map[AG2EpigeneticModality.CHROMATIN_ACCESSIBILITY]
        assert atac.imputed_signal > 0.0
        assert atac.assay_unit == "RPKM_norm"

    def test_compute_thermodynamic_dna_coupling(self, engine: AlphaGenome2Engine) -> None:
        """Verify coupling between 5mC shifts and PBD opening free energy."""
        cell_ctx = AG2CellularContextContract(cell_type_curie="CL:0000938")
        imputations = engine.impute_epigenetic_modalities(
            modalities=[AG2EpigeneticModality.DNA_METHYLATION_5MC],
            cell_context=cell_ctx,
            variant_str="chr14:24598100:C>T",
        )
        delta_g = engine.compute_thermodynamic_dna_coupling(imputations)
        assert isinstance(delta_g, float)

    def test_full_simulation_execution(self, engine: AlphaGenome2Engine) -> None:
        """Verify full AlphaGenome2 simulation report generation."""
        contract = AlphaGenome2Contract(
            contract_id="sim_gzmb_test",
            locus_window_1mb="chr14:24100000-25100000",
            variant="chr14:24598100:C>T",
            cellular_context=AG2CellularContextContract(
                cell_type_curie="CL:0000938",
                continuous_state_value=0.80,
            ),
            enhancer_gene_linking=AG2EnhancerGeneLinkContract(
                target_gene_id="ENSG00000100453",
                promoter_tss_bp=24597470,
            ),
            min_avi_phred_threshold=15.0,
        )
        report = engine.execute_simulation(contract, use_cache=False)
        assert report.contract_id == "sim_gzmb_test"
        assert report.span_bp == 1_000_000
        assert report.prediction is not None
        assert report.prediction.avi_phred >= 10.0
        assert report.prediction.enhancer_gene_link is not None
        assert report.prediction.enhancer_gene_link.target_gene_id == "ENSG00000100453"

        d = report.to_dict()
        assert d["span_bp"] == 1_000_000
        assert "prediction" in d


class TestAlphaGenome2Validator:
    """Test semantic validation rules and rejection traps in EnhancedSemanticValidator."""

    @pytest.fixture
    def validator(self) -> EnhancedSemanticValidator:
        return EnhancedSemanticValidator()

    def test_validate_exemplar_file(self, validator: EnhancedSemanticValidator) -> None:
        """Exemplar GFL program must validate cleanly with 0 errors."""
        with open("examples/alphagenome2_cell_specific_enhancer_triage.gfl", encoding="utf-8") as f:
            content = f.read()

        ast = parse_gfl(content)
        assert ast is not None
        result = validator.validate_ast(ast)
        assert len(result.errors) == 0, f"Validation errors: {[e.message for e in result.errors]}"

    def test_validator_rejects_span_over_1mb(self, validator: EnhancedSemanticValidator) -> None:
        """Validator must reject locus windows exceeding 1,000,000 bp."""
        ast = {
            "alphagenome2": {
                "contract_id": "test_over_1mb",
                "locus_window_1mb": "chr14:24000000-25500000",  # 1.5 Mb
            }
        }
        res = validator.validate_ast(ast)
        assert any(e.code == ErrorCodes.SEMANTIC_INVALID_PARAMETER for e in res.errors)
        assert any("exceeds maximum AlphaGenome 2 window limit" in e.message for e in res.errors)

    def test_validator_rejects_invalid_locus_format(self, validator: EnhancedSemanticValidator) -> None:
        """Validator must reject malformed coordinates."""
        ast = {
            "alphagenome2": {
                "contract_id": "test_bad_coord",
                "locus_window_1mb": "not_a_valid_coordinate",
            }
        }
        res = validator.validate_ast(ast)
        assert any(e.code == ErrorCodes.SEMANTIC_INVALID_PARAMETER for e in res.errors)
        assert any("Invalid locus format" in e.message for e in res.errors)

    def test_validator_rejects_invalid_cell_curie(self, validator: EnhancedSemanticValidator) -> None:
        """Validator must reject malformed Cell Ontology CURIEs."""
        ast = {
            "alphagenome2": {
                "contract_id": "test_bad_curie",
                "locus_window_1mb": "chr14:24100000-25100000",
                "cellular_context": {
                    "cell_type_curie": "invalid_cell_curie_string",
                },
            }
        }
        res = validator.validate_ast(ast)
        assert any(e.code == ErrorCodes.SEMANTIC_INVALID_PARAMETER for e in res.errors)
        assert any("Invalid cell_type CURIE" in e.message for e in res.errors)

    def test_validator_rejects_invalid_modality(self, validator: EnhancedSemanticValidator) -> None:
        """Validator must reject unrecognized epigenetic modalities."""
        ast = {
            "alphagenome2": {
                "contract_id": "test_bad_modality",
                "locus_window_1mb": "chr14:24100000-25100000",
                "impute_modalities": ["quantum_spin_imaging"],
            }
        }
        res = validator.validate_ast(ast)
        assert any(e.code == ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE for e in res.errors)
        assert any("Invalid modality 'quantum_spin_imaging'" in e.message for e in res.errors)

    def test_validator_rejects_invalid_variant_iupac(self, validator: EnhancedSemanticValidator) -> None:
        """Validator must reject non-IUPAC variants."""
        ast = {
            "alphagenome2": {
                "contract_id": "test_bad_var",
                "locus_window_1mb": "chr14:24100000-25100000",
                "variant": "chr14_24598100_C_T_BAD_FORMAT",
            }
        }
        res = validator.validate_ast(ast)
        assert any(e.code == ErrorCodes.SEMANTIC_INVALID_PARAMETER for e in res.errors)
        assert any("Invalid variant format" in e.message for e in res.errors)

    def test_validator_rejects_distance_over_1mb(self, validator: EnhancedSemanticValidator) -> None:
        """Validator must reject enhancer-gene distance exceeding 1,000,000 bp."""
        ast = {
            "alphagenome2": {
                "contract_id": "test_dist_over_1mb",
                "locus_window_1mb": "chr14:24100000-25100000",
                "enhancer_gene_linking": {
                    "target_gene_id": "GZMB",
                    "max_distance_bp": 2_500_000,
                },
            }
        }
        res = validator.validate_ast(ast)
        assert any(e.code == ErrorCodes.SEMANTIC_INVALID_PARAMETER for e in res.errors)
        assert any("max_distance_bp" in e.message for e in res.errors)
