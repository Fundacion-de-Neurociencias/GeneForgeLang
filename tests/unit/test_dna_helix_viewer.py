"""Unit tests for Multi-Dimensional Dynamic DNA Helix Explorer (GF-HelixView).

Validates:
1. HelixConformation, ViewerTrackType, VariantPathogenicity enums.
2. DNAViewerContract, ViewerVariantAnnotation, ViewerExonAnnotation roundtrip serialization.
3. GFLAST integration with dna_viewer block.
4. EnhancedSemanticValidator enforcement of nucleic acid alphabet and coordinate invariants.
5. HTML5/SVG self-contained interactive viewer generation.
6. Validation of examples/dmd_gene_helix_viewer.gfl exemplar protocol.
"""

from pathlib import Path

import pytest
import yaml
from geneforgelang.core.gftypes import (
    GFLAST,
    DNAViewerContract,
    HelixConformation,
    VariantPathogenicity,
    ViewerCrisprPamSite,
    ViewerEpigeneticMark,
    ViewerExonAnnotation,
    ViewerTrackType,
    ViewerVariantAnnotation,
)
from geneforgelang.core.validator import EnhancedSemanticValidator
from geneforgelang.visualization.dna_helix_viewer import (
    generate_dna_helix_viewer_html,
    get_complementary_base,
    load_sequence_for_contract,
    render_dna_helix_viewer,
)


def test_helix_viewer_enums_and_dataclasses() -> None:
    """Test enum representations and sub-annotation serialization."""
    assert str(HelixConformation.B_DNA) == "b_dna"
    assert str(ViewerTrackType.EXONS) == "exons"
    assert str(ViewerTrackType.CLINVAR_VARIANTS) == "clinvar_variants"
    assert str(VariantPathogenicity.PATHOGENIC) == "pathogenic"

    # Variant annotation
    variant = ViewerVariantAnnotation(
        coordinate=161,
        ref_allele="T",
        alt_allele="A",
        variant_id="VCV000098451",
        pathogenicity=VariantPathogenicity.PATHOGENIC,
        molecular_consequence="nonsense (p.Arg54Ter)",
        clinical_significance="Pathogenic",
        condition="Duchenne Muscular Dystrophy",
        hgvs_c="c.161T>A",
        hgvs_p="p.Arg54Ter",
    )
    v_dict = variant.to_dict()
    assert v_dict["coordinate"] == 161
    assert v_dict["pathogenicity"] == "pathogenic"
    v_restored = ViewerVariantAnnotation.from_dict(v_dict)
    assert v_restored.coordinate == 161
    assert v_restored.variant_id == "VCV000098451"
    assert v_restored.pathogenicity == VariantPathogenicity.PATHOGENIC

    # Exon annotation
    exon = ViewerExonAnnotation(
        exon_number=45,
        start_coord=149,
        end_coord=324,
        phase=1,
        splice_donor="GT",
        splice_acceptor="AG",
    )
    e_dict = exon.to_dict()
    assert e_dict["exon_number"] == 45
    e_restored = ViewerExonAnnotation.from_dict(e_dict)
    assert e_restored.exon_number == 45
    assert e_restored.start_coord == 149
    assert e_restored.end_coord == 324

    # Epigenetic mark
    epi = ViewerEpigeneticMark(coordinate=105, modification_type="5hmC", modification_probability=0.94)
    epi_restored = ViewerEpigeneticMark.from_dict(epi.to_dict())
    assert epi_restored.modification_type == "5hmC"
    assert epi_restored.modification_probability == 0.94

    # CRISPR site
    crispr = ViewerCrisprPamSite(
        pam_sequence="TGG",
        start_coord=155,
        strand="+",
        target_grna_20nt="TCAGTGACCTACAGGATGGG",
        cleavage_offset=-3,
    )
    crispr_restored = ViewerCrisprPamSite.from_dict(crispr.to_dict())
    assert crispr_restored.pam_sequence == "TGG"
    assert crispr_restored.cleavage_offset == -3


def test_dna_viewer_contract_roundtrip() -> None:
    """Test DNAViewerContract creation and dictionary roundtrip."""
    contract = DNAViewerContract(
        viewer_id="test_dmd_viewer",
        target_gene="DMD",
        genomic_range="chrX:31119222-31139222",
        reference_build="GRCh38",
        helix_type=HelixConformation.B_DNA,
        active_coordinate=161,
        tracks=[
            ViewerTrackType.EXONS,
            ViewerTrackType.READING_FRAMES,
            ViewerTrackType.CLINVAR_VARIANTS,
        ],
        raw_sequence="ATGCTTTGGTGGGAAGAAGTAGAGGACTGTTATGAAAGAGAAGATGTT",
    )

    d = contract.to_dict()
    assert d["viewer_id"] == "test_dmd_viewer"
    assert d["target_gene"] == "DMD"
    assert d["helix_type"] == "b_dna"
    assert d["active_coordinate"] == 161
    assert "exons" in d["tracks"]

    restored = DNAViewerContract.from_dict(d)
    assert restored.viewer_id == "test_dmd_viewer"
    assert restored.target_gene == "DMD"
    assert restored.helix_type == HelixConformation.B_DNA
    assert restored.active_coordinate == 161
    assert restored.raw_sequence == "ATGCTTTGGTGGGAAGAAGTAGAGGACTGTTATGAAAGAGAAGATGTT"


def test_gfl_ast_roundtrip_with_dna_viewer_block() -> None:
    """Test GFLAST integration with dna_viewer block."""
    contract = DNAViewerContract(
        viewer_id="ast_helix_test",
        target_gene="DMD",
        active_coordinate=45,
    )
    ast = GFLAST(dna_viewer=contract)

    ast_dict = ast.to_dict()
    assert "dna_viewer" in ast_dict
    assert ast_dict["dna_viewer"]["viewer_id"] == "ast_helix_test"

    restored_ast = GFLAST.from_dict(ast_dict)
    assert restored_ast.dna_viewer is not None
    assert isinstance(restored_ast.dna_viewer, DNAViewerContract)
    assert restored_ast.dna_viewer.viewer_id == "ast_helix_test"
    assert restored_ast.dna_viewer.active_coordinate == 45


def test_validator_rejects_invalid_dna_viewer_parameters() -> None:
    """Test that EnhancedSemanticValidator rejects malformed DNA viewer blocks."""
    validator = EnhancedSemanticValidator()

    # Invalid nucleic acid base in raw sequence
    invalid_seq_ast = {
        "dna_viewer": {
            "viewer_id": "bad_seq",
            "target_gene": "DMD",
            "raw_sequence": "ATGCX_INVALID_123",
        }
    }
    res = validator.validate_ast(invalid_seq_ast)
    assert any("contains invalid nucleic acid bases" in e.message for e in res.errors)

    # Invalid active_coordinate (< 1)
    invalid_coord_ast = {
        "dna_viewer": {
            "viewer_id": "bad_coord",
            "target_gene": "DMD",
            "active_coordinate": 0,
        }
    }
    validator = EnhancedSemanticValidator()
    res2 = validator.validate_ast(invalid_coord_ast)
    assert any("active_coordinate must be a positive" in e.message for e in res2.errors)

    # Invalid exon coordinate range (start > end)
    invalid_exon_ast = {
        "dna_viewer": {
            "viewer_id": "bad_exon",
            "target_gene": "DMD",
            "exons": [
                {"exon_number": 1, "start_coord": 200, "end_coord": 50},
            ],
        }
    }
    validator = EnhancedSemanticValidator()
    res3 = validator.validate_ast(invalid_exon_ast)
    assert any("invalid coordinate range" in e.message for e in res3.errors)


def test_dna_helix_html_generation_and_rendering(tmp_path: Path) -> None:
    """Test that HTML generator produces complete self-contained SVG interactive application."""
    contract = DNAViewerContract(
        viewer_id="html_test_viewer",
        target_gene="DMD",
        raw_sequence="ATGCTTTGGTGGGAAGAAGTAGAGGACTGTTATGAAAGAGAAGATGTTCAAAAGAAAACATTCACAAAATGGGTAAAT",
        active_coordinate=10,
    )

    # Base complement utility
    assert get_complementary_base("A") == "T"
    assert get_complementary_base("T") == "A"
    assert get_complementary_base("C") == "G"
    assert get_complementary_base("G") == "C"

    # Sequence loading
    loaded_seq = load_sequence_for_contract(contract)
    assert loaded_seq.startswith("ATGCTTTGGT")

    # Generate HTML
    html = generate_dna_helix_viewer_html(contract)
    assert "<!DOCTYPE html>" in html
    assert "DNA <span>viewer</span>" in html
    assert "Double helix (B-DNA, right-handed)" in html
    assert "Reading head" in html
    assert "Sequence window" in html
    assert "Exon & Splicing Architecture" in html
    assert "Codon & Reading Frame Translation" in html
    assert "ClinVar & Known Variants" in html
    assert "Helix facts (B-DNA)" in html
    assert "renderHelixSVG" in html

    # Render to file
    out_file = tmp_path / "test_viewer.html"
    rendered = render_dna_helix_viewer(contract, output_path=out_file)
    assert out_file.is_file()
    assert out_file.stat().st_size > 10000
    assert rendered == html


def test_dmd_exemplar_gfl_file_validates() -> None:
    """Test that examples/dmd_gene_helix_viewer.gfl parses and validates cleanly."""
    example_path = Path("examples/dmd_gene_helix_viewer.gfl")
    if not example_path.exists():
        example_path = Path("GeneForgeLang/examples/dmd_gene_helix_viewer.gfl")

    assert example_path.is_file(), f"Exemplar file not found: {example_path}"

    with open(example_path, encoding="utf-8") as f:
        ast_dict = yaml.safe_load(f)

    validator = EnhancedSemanticValidator()
    result = validator.validate_ast(ast_dict)
    assert result.is_valid, f"Validation failed with errors: {[e.message for e in result.errors]}"

    # Verify GFLAST roundtrip
    ast = GFLAST.from_dict(ast_dict)
    assert ast.dna_viewer is not None
    assert ast.dna_viewer.target_gene == "DMD"
    assert ast.dna_viewer.active_coordinate == 161
    assert len(ast.dna_viewer.exons) == 3
    assert len(ast.dna_viewer.variants) == 2
