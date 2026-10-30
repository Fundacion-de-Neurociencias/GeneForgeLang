"""Unit test suite for Carbon-X Genomic Foundation LLM integration in GeneForgeLang."""

from __future__ import annotations

import pytest
import yaml
from geneforgelang.core.carbonx_engine import (
    MAX_CARBONX_CONTEXT_TOKENS,
    MAX_CONTIGUOUS_DNA_BP,
    CarbonXEngine,
    CarbonXPromptCompiler,
    CarbonXTokenizer,
)
from geneforgelang.core.gftypes import (
    GFLAST,
    CarbonXModelSize,
    CarbonXQuery,
    CarbonXReasoningResult,
    CarbonXTargetLocus,
    CarbonXTaskType,
    GenomicLLMContract,
)
from geneforgelang.core.validator import EnhancedSemanticValidator


class TestCarbonXTypes:
    """Test data structures, enums, and serialization round-trips for Carbon-X."""

    def test_enums_and_dataclasses(self) -> None:
        assert CarbonXTaskType.VARIANT_EFFECT_REASONING.value == "variant_effect_reasoning"
        assert CarbonXTaskType.LOCUS_ANNOTATION.value == "locus_annotation"
        assert CarbonXTaskType.PROMOTER_GENERATION.value == "promoter_generation"
        assert CarbonXTaskType.PATHWAY_IMPACT.value == "pathway_impact"
        assert CarbonXTaskType.CHAT_WITH_DNA.value == "chat_with_dna"

        assert CarbonXModelSize.CARBONX_14B.value == "carbonx-14b"
        assert CarbonXModelSize.CARBONX_BASE.value == "carbonx-base"

        locus = CarbonXTargetLocus(
            chrom="chr2",
            start=74588200,
            end=74591200,
            strand="+",
            assembly="GRCh38",
            gene_symbol="DCTN1",
        )
        l_dict = locus.to_dict()
        assert l_dict["chrom"] == "chr2"
        assert l_dict["gene_symbol"] == "DCTN1"
        l_round = CarbonXTargetLocus.from_dict(l_dict)
        assert l_round.chrom == "chr2"
        assert l_round.start == 74588200

        query = CarbonXQuery(
            prompt="Analyze DCTN1 promoter variant",
            task_type=CarbonXTaskType.VARIANT_EFFECT_REASONING,
            sequence="GGGCGGCCGCTA",
            locus=locus,
            variant_delta={"ref": "C", "alt": "T", "pos": 74589320},
            max_new_tokens=512,
            temperature=0.3,
        )
        q_dict = query.to_dict()
        assert q_dict["max_new_tokens"] == 512
        q_round = CarbonXQuery.from_dict(q_dict)
        assert q_round.task_type == CarbonXTaskType.VARIANT_EFFECT_REASONING
        assert q_round.locus is not None
        assert q_round.locus.gene_symbol == "DCTN1"

        contract = GenomicLLMContract(
            name="dctn1_test",
            model=CarbonXModelSize.CARBONX_14B,
            task_type=CarbonXTaskType.VARIANT_EFFECT_REASONING,
            query=query,
            target_locus=locus,
            sequence_payload="GGGCGGCCGCTA",
            max_context_tokens=40960,
            temperature=0.2,
        )
        c_dict = contract.to_dict()
        assert c_dict["name"] == "dctn1_test"
        c_round = GenomicLLMContract.from_dict(c_dict)
        assert c_round.name == "dctn1_test"
        assert c_round.model == CarbonXModelSize.CARBONX_14B
        assert c_round.task_type == CarbonXTaskType.VARIANT_EFFECT_REASONING

    def test_gflast_roundtrip(self) -> None:
        contract = GenomicLLMContract(
            name="ast_carbonx_test",
            model=CarbonXModelSize.CARBONX_14B,
            task_type=CarbonXTaskType.LOCUS_ANNOTATION,
            sequence_payload="ATCGATCGATCG",
        )
        ast = GFLAST(genomic_llm=contract)
        d = ast.to_dict()
        assert "genomic_llm" in d
        assert d["genomic_llm"]["name"] == "ast_carbonx_test"

        ast_recovered = GFLAST.from_dict(d)
        assert ast_recovered.genomic_llm is not None
        assert ast_recovered.genomic_llm.name == "ast_carbonx_test"
        assert ast_recovered.genomic_llm.task_type == CarbonXTaskType.LOCUS_ANNOTATION

        # Test carbonx alias
        alias_dict = {"carbonx": contract.to_dict()}
        ast_alias = GFLAST.from_dict(alias_dict)
        assert ast_alias.genomic_llm is not None
        assert ast_alias.genomic_llm.name == "ast_carbonx_test"


class TestCarbonXTokenizer:
    """Test 6-mer DNA token accounting and context boundary validation."""

    def test_6mer_token_calculation(self) -> None:
        assert CarbonXTokenizer.count_dna_tokens("") == 0
        assert CarbonXTokenizer.count_dna_tokens("A") == 1
        assert CarbonXTokenizer.count_dna_tokens("AAAAAA") == 1
        assert CarbonXTokenizer.count_dna_tokens("AAAAAAA") == 2
        assert CarbonXTokenizer.count_dna_tokens("ATGCATGCATGC") == 2  # 12 bp -> 2 tokens
        assert CarbonXTokenizer.count_dna_tokens("ATGCATGCATGCA") == 3  # 13 bp -> 3 tokens

    def test_sanitization_and_iupac_validation(self) -> None:
        raw = "  atgc\nATGC  \t "
        clean = CarbonXTokenizer.sanitize_dna(raw)
        assert clean == "ATGCATGC"

        with pytest.raises(ValueError, match="Invalid nucleotide characters"):
            CarbonXTokenizer.sanitize_dna("ATGCXATGC")

        with pytest.raises(ValueError, match="Invalid nucleotide characters"):
            CarbonXTokenizer.sanitize_dna("ATGC123ATGC")

    def test_context_window_boundaries(self) -> None:
        # Fit within context
        seq_ok = "A" * 6000  # 1000 tokens
        fits, d_tok, t_tok, msg = CarbonXTokenizer.validate_context_window(seq_ok, "Explain this sequence")
        assert fits is True
        assert d_tok == 1000

        # Max allowed DNA sequence: 245,760 bp (40,960 tokens)
        assert MAX_CONTIGUOUS_DNA_BP == 245760
        assert MAX_CARBONX_CONTEXT_TOKENS == 40960

        # Sequence exceeding capacity
        excess_seq = "A" * (MAX_CONTIGUOUS_DNA_BP + 60)
        fits_over, d_over, _, msg_over = CarbonXTokenizer.validate_context_window(excess_seq, "Prompt")
        assert fits_over is False
        assert "Context window exceeded" in msg_over


class TestCarbonXPromptCompiler:
    """Test ChatML compilation and genomic special token framing."""

    def test_chatml_prompt_structure(self) -> None:
        query = CarbonXQuery(
            prompt="Assess SP1 promoter motif disruption.",
            task_type=CarbonXTaskType.VARIANT_EFFECT_REASONING,
            sequence="GGGCGGGGCGGG",
            locus=CarbonXTargetLocus(chrom="chr2", start=100, end=200, gene_symbol="DCTN1"),
            variant_delta={"ref": "C", "alt": "T", "pos": 150},
        )
        compiled = CarbonXPromptCompiler.compile_chatml(query)

        assert "<|im_start|>system" in compiled
        assert "<|im_start|>user" in compiled
        assert "<|im_start|>assistant" in compiled
        assert "<|dna_start|>GGGCGG GGCGGG<|dna_end|>" in compiled
        assert "Target Locus: GRCh38 chr2:100-200" in compiled
        assert "Variant Alteration: C > T at position 150" in compiled
        assert "Assess SP1 promoter motif disruption." in compiled


class TestCarbonXEngine:
    """Test local execution, biophysical fallback, and reasoning results."""

    def test_engine_offline_evaluation(self) -> None:
        engine = CarbonXEngine()
        contract = GenomicLLMContract(
            name="dctn1_eval",
            task_type=CarbonXTaskType.VARIANT_EFFECT_REASONING,
            sequence_payload="GGGCGGGGCGGGCCGCTAGCTAGCTAGCGATCGATCGATCGATCGATCGCGCTAGCTA",
            query=CarbonXQuery(
                prompt="Evaluate C>T transition impact on promoter",
                task_type=CarbonXTaskType.VARIANT_EFFECT_REASONING,
                variant_delta={"ref": "C", "alt": "T", "pos": 74589320},
            ),
        )

        result = engine.execute(contract, timeout_seconds=0.1)

        assert isinstance(result, CarbonXReasoningResult)
        assert result.confidence_score >= 0.70
        assert result.token_count_dna == 10  # 59 bp -> ceil(59/6) = 10 tokens
        assert result.evidence_status == "exploratory_hypothesis"
        assert result.metadata["experimental_validation"] == "unvalidated_by_wet_lab"
        assert "scientific_disclaimer" in result.metadata
        assert len(result.predicted_effects) > 0
        assert "transition" in str(result.predicted_effects[0]).lower()
        assert contract.verified_result is not None


class TestCarbonXValidator:
    """Test semantic validation rules and rejection criteria for genomic_llm."""

    def test_validate_valid_gfl_file(self) -> None:
        gfl_content = """
genomic_llm:
  name: "dctn1_promoter_variant_reasoning"
  model: "carbonx-14b"
  task_type: "variant_effect_reasoning"
  max_context_tokens: 40960
  temperature: 0.2
  target_locus:
    chrom: "chr2"
    start: 74588200
    end: 74591200
    strand: "+"
    assembly: "GRCh38"
    gene_symbol: "DCTN1"
  query:
    prompt: "Analyze the regulatory consequence of the C>T transition."
    task_type: "variant_effect_reasoning"
    sequence: "GGGCGGGGCGGGCCGCTAGCTAGCTA"
"""
        ast = yaml.safe_load(gfl_content)
        validator = EnhancedSemanticValidator()
        res = validator.validate_ast(ast)
        assert res.is_valid is True
        assert len(res.errors) == 0

    def test_validator_rejections(self) -> None:
        validator = EnhancedSemanticValidator()

        # 1. Missing name
        res1 = validator.validate_ast({"genomic_llm": {"task_type": "variant_effect_reasoning"}})
        assert res1.is_valid is False
        assert any("missing required 'name'" in e.message for e in res1.errors)

        # 2. Invalid task_type
        res2 = validator.validate_ast(
            {
                "genomic_llm": {
                    "name": "test",
                    "task_type": "invalid_cosmic_task",
                }
            }
        )
        assert res2.is_valid is False
        assert any("Unknown task_type" in e.message for e in res2.errors)

        # 3. Invalid model
        res3 = validator.validate_ast(
            {
                "genomic_llm": {
                    "name": "test",
                    "task_type": "variant_effect_reasoning",
                    "model": "gpt-5-unsupported",
                }
            }
        )
        assert res3.is_valid is False
        assert any("Unknown model checkpoint" in e.message for e in res3.errors)

        # 4. Over max_context_tokens
        res4 = validator.validate_ast(
            {
                "genomic_llm": {
                    "name": "test",
                    "task_type": "variant_effect_reasoning",
                    "max_context_tokens": 100000,
                }
            }
        )
        assert res4.is_valid is False
        assert any("exceeds Carbon-X hardware limit" in e.message for e in res4.errors)

        # 5. Invalid locus coordinates (start > end)
        res5 = validator.validate_ast(
            {
                "genomic_llm": {
                    "name": "test",
                    "task_type": "variant_effect_reasoning",
                    "target_locus": {"chrom": "chr1", "start": 500, "end": 200},
                }
            }
        )
        assert res5.is_valid is False
        assert any("Invalid locus coordinates: start" in e.message for e in res5.errors)

        # 6. Invalid nucleotide characters
        res6 = validator.validate_ast(
            {
                "genomic_llm": {
                    "name": "test",
                    "task_type": "variant_effect_reasoning",
                    "sequence": "ATGCXGCTA",
                }
            }
        )
        assert res6.is_valid is False
        assert any("invalid IUPAC nucleotide characters" in e.message for e in res6.errors)

    def test_validator_warning_on_exceeding_50kb(self) -> None:
        validator = EnhancedSemanticValidator()
        # Sequence of 52,000 bp (exceeds 50 kb pre-training chunk size)
        long_seq = "ATGC" * 13000
        res = validator.validate_ast(
            {
                "genomic_llm": {
                    "name": "long_locus_test",
                    "task_type": "locus_annotation",
                    "sequence": long_seq,
                }
            }
        )
        assert res.is_valid is True  # Warning does not invalidate document
        assert len(res.warnings) > 0
        assert any("exceeds Carbon-X pretraining chunk limit (~50,000 bp)" in w.message for w in res.warnings)
