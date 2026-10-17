"""Unit tests for Viral Interactome Complexes and AlphaGenome Locus Link contracts in GeneForgeLang."""

from geneforgelang.core.gftypes import (
    AlphaGenomeLocusLink,
    ViralInteractomeComplexContract,
    ViralInteractomeType,
)
from geneforgelang.core.validator import EnhancedSemanticValidator


def test_viral_interactome_complex_contract_instantiation_and_dict() -> None:
    """Test creating and serializing a ViralInteractomeComplexContract."""
    locus_link = AlphaGenomeLocusLink(
        variant="chrX:15579998:G>A",
        gene="ACE2",
        biosample="Lung",
        modalities=["RNA_SEQ", "DNASE", "CHIP_TF"],
    )

    data_link = locus_link.to_dict()
    assert data_link["variant"] == "chrX:15579998:G>A"
    assert data_link["gene"] == "ACE2"
    assert data_link["biosample"] == "Lung"
    assert locus_link.to_atlas_query() == "chrX:15579998:G>A"

    contract = ViralInteractomeComplexContract(
        complex_id="ViralEntryDimer",
        subunits=["P0DTC2", "Q9BYF1"],
        interactome_type=ViralInteractomeType.HETERODIMER,
        portal="alphafold_pandemic_preparedness",
        viral_family="coronaviridae",
        proteome_id="UP000464024",
        iplddt_threshold=80.0,
        iptm_threshold=0.75,
        is_high_confidence_portal_hit=True,
        host_locus_link=locus_link,
    )

    data = contract.to_dict()
    assert data["complex_id"] == "ViralEntryDimer"
    assert data["subunits"] == ["P0DTC2", "Q9BYF1"]
    assert data["interactome_type"] == "heterodimer"
    assert data["portal"] == "alphafold_pandemic_preparedness"
    assert data["viral_family"] == "coronaviridae"
    assert data["host_locus_link"]["variant"] == "chrX:15579998:G>A"

    assert contract.passes_confidence_gate(82.5, 0.78) is True
    assert contract.passes_confidence_gate(70.0, 0.78) is False
    assert contract.passes_confidence_gate(85.0, 0.65) is False


def test_validator_accepts_valid_complexes_with_alphagenome_link() -> None:
    """Test validator accepts complexes block with AlphaGenome locus link."""
    validator = EnhancedSemanticValidator()
    ast = {
        "complexes": {
            "SpikeACE2Complex": {
                "subunits": ["P0DTC2", "Q9BYF1"],
                "interactome_type": "heterodimer",
                "iplddt_threshold": 80.0,
                "iptm_threshold": 0.75,
                "host_locus_link": {
                    "variant": "chrX:15579998:G>A",
                    "gene": "ACE2",
                    "biosample": "Lung",
                },
            }
        }
    }
    result = validator.validate_ast(ast)
    assert result.is_valid is True
    assert len(result.errors) == 0


def test_validator_accepts_viral_contract_object_in_complexes() -> None:
    """Test validator accepts ViralInteractomeComplexContract object directly in complexes dict."""
    validator = EnhancedSemanticValidator()
    contract = ViralInteractomeComplexContract(
        complex_id="EbolaGlycoproteinDimer",
        subunits=["Q05320", "P87666"],
        interactome_type=ViralInteractomeType.HOMODIMER,
        viral_family="filoviridae",
    )
    ast = {
        "complexes": {
            "EbolaGlycoproteinDimer": contract,
        }
    }
    result = validator.validate_ast(ast)
    assert result.is_valid is True
    assert len(result.errors) == 0


def test_validator_catches_invalid_alphagenome_variant_format() -> None:
    """Test validator catches invalid non-AlphaGenome variant format (e.g. rsID or missing >)."""
    validator = EnhancedSemanticValidator()
    ast = {
        "complexes": {
            "InvalidLinkComplex": {
                "subunits": ["P0DTC2", "Q9BYF1"],
                "host_locus_link": {
                    "variant": "rs123456",  # invalid rsID instead of chr:pos:ref>alt
                },
            }
        }
    }
    result = validator.validate_ast(ast)
    assert result.is_valid is False
    assert any("Invalid AlphaGenome variant format" in e.message for e in result.errors)


def test_validator_catches_invalid_complex_thresholds() -> None:
    """Test validator catches out-of-range confidence thresholds."""
    validator = EnhancedSemanticValidator()
    ast = {
        "complexes": {
            "BadThresholdsComplex": {
                "subunits": ["P0DTC2", "Q9BYF1"],
                "iplddt_threshold": 120.0,  # invalid > 100
                "iptm_threshold": -0.5,  # invalid negative
            }
        }
    }
    result = validator.validate_ast(ast)
    assert result.is_valid is False
    assert any("iplddt_threshold must be between 0.0 and 100.0" in e.message for e in result.errors)
    assert any("iptm_threshold must be between 0.0 and 1.0" in e.message for e in result.errors)
