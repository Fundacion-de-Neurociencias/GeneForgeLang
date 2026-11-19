"""Unit tests for Autonomous Wet-Lab Protocol Execution & Synthesizability Engine.

Grounded in AutoDNA (Nature 2026; Heidi Ledford; Chen, Wu et al., Shanghai Jiao Tong University):
"An AI-native experimental laboratory for autonomous biomolecular operations"
DOI: 10.1038/d41586-026-03552-8.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from geneforgelang.core.gftypes import (
    GFLAST,
    AutonomousExecutionContract,
    BiosecurityClearanceContract,
    BiosecurityRiskTier,
    ExperimentalTelemetryContract,
    SynthesisChemistry,
    SynthesizabilityGateContract,
    TelemetryReadoutType,
    WetLabInstrumentType,
    WetLabStepContract,
)
from geneforgelang.core.validator import EnhancedSemanticValidator
from geneforgelang.core.wet_lab_engine import (
    AutonomousExecutionEngine,
    BiosecurityScreener,
    SynthesizabilityAnalyzer,
)


class TestAutonomousExecutionTypes:
    """Test enums, dataclasses, and GFLAST serialization for autonomous execution."""

    def test_enums(self) -> None:
        """Verify enum string representations and value sets."""
        assert SynthesisChemistry.ENZYMATIC_TDT.value == "enzymatic_tdt"
        assert SynthesisChemistry.CHEMICAL_PHOSPHORAMIDITE.value == "chemical_phosphoramidite"
        assert WetLabInstrumentType.SYNTHESIZER.value == "synthesizer"
        assert WetLabInstrumentType.SEQUENCER.value == "sequencer"
        assert BiosecurityRiskTier.BENIGN_RESEARCH.value == "benign_research"
        assert BiosecurityRiskTier.PROHIBITED_TOXIN.value == "prohibited_toxin"
        assert TelemetryReadoutType.STEPWISE_SYNTHESIS_YIELD.value == "stepwise_synthesis_yield"
        assert TelemetryReadoutType.NGS_FASTQ_READS.value == "ngs_fastq_reads"

    def test_contract_roundtrip(self) -> None:
        """Test serialization and deserialization of all sub-contracts and root contract."""
        step = WetLabStepContract(
            step_id="step_test_01",
            instrument=WetLabInstrumentType.SYNTHESIZER,
            operation="EnzymaticSynthesis_TdT",
            parameters={"cycles": 100, "temp": 37.0},
            duration_seconds=3600,
            temperature_celsius=37.0,
        )
        synth = SynthesizabilityGateContract(
            chemistry=SynthesisChemistry.ENZYMATIC_TDT,
            max_homopolymer=4,
            min_gc_content=0.40,
            max_gc_content=0.60,
        )
        bio = BiosecurityClearanceContract(
            risk_tier=BiosecurityRiskTier.BENIGN_RESEARCH,
            screening_passed=True,
            clearance_hash="abc123hash",
            authorization_token="auth789token",
        )
        telem = ExperimentalTelemetryContract(
            readout_type=TelemetryReadoutType.NGS_FASTQ_READS,
            observed_yield=0.977,
            observed_sequence="ACGTACGT",
            concordance_rate=1.0,
        )

        contract = AutonomousExecutionContract(
            protocol_id="PROTO-001",
            target_sequence="ACGTACGTACGTACGT",
            target_entity="TestAmplicon",
            synthesizability=synth,
            biosecurity=bio,
            steps=[step],
            telemetry=telem,
        )

        data = contract.to_dict()
        restored = AutonomousExecutionContract.from_dict(data)

        assert restored.protocol_id == "PROTO-001"
        assert restored.target_sequence == "ACGTACGTACGTACGT"
        assert restored.synthesizability is not None
        assert restored.synthesizability.chemistry == SynthesisChemistry.ENZYMATIC_TDT
        assert restored.biosecurity is not None
        assert restored.biosecurity.risk_tier == BiosecurityRiskTier.BENIGN_RESEARCH
        assert len(restored.steps) == 1
        assert restored.steps[0].instrument == WetLabInstrumentType.SYNTHESIZER
        assert restored.telemetry is not None
        assert restored.telemetry.observed_yield == 0.977

    def test_gflast_roundtrip_and_aliases(self) -> None:
        """Test GFLAST integration with primary name and aliases."""
        contract = AutonomousExecutionContract(
            protocol_id="PROTO-ALIAS",
            target_sequence="GATTACA",
        )

        # Primary name
        ast1 = GFLAST.from_dict({"autonomous_execution": contract.to_dict()})
        assert ast1.autonomous_execution is not None
        assert ast1.autonomous_execution.protocol_id == "PROTO-ALIAS"
        dict1 = ast1.to_dict()
        assert "autonomous_execution" in dict1

        # Alias: wet_lab_dispatch
        ast2 = GFLAST.from_dict({"wet_lab_dispatch": contract.to_dict()})
        assert ast2.autonomous_execution is not None
        assert ast2.autonomous_execution.protocol_id == "PROTO-ALIAS"

        # Alias: laboratory_protocol
        ast3 = GFLAST.from_dict({"laboratory_protocol": contract.to_dict()})
        assert ast3.autonomous_execution is not None
        assert ast3.autonomous_execution.protocol_id == "PROTO-ALIAS"


class TestSynthesizabilityAnalyzer:
    """Test biophysical synthesizability checks."""

    def test_gc_content_calculation(self) -> None:
        """Verify GC percentage calculations."""
        assert SynthesizabilityAnalyzer.calculate_gc_content("GGCC") == 1.0
        assert SynthesizabilityAnalyzer.calculate_gc_content("AATT") == 0.0
        assert SynthesizabilityAnalyzer.calculate_gc_content("ACGT") == 0.5

    def test_homopolymer_detection(self) -> None:
        """Verify detection of longest homopolymers."""
        length, base = SynthesizabilityAnalyzer.find_longest_homopolymer("ACGTGGGGGACGT")
        assert length == 5
        assert base == "G"

        length, base = SynthesizabilityAnalyzer.find_longest_homopolymer("ACGT")
        assert length == 1

    def test_hairpin_free_energy_approximation(self) -> None:
        """Verify stem-loop hairpin detection and Delta G calculation."""
        # Clean non-palindromic sequence with no hairpins
        stable_delta_g = SynthesizabilityAnalyzer.calculate_hairpin_delta_g("ACTGACCAAGTTCGAATCC")
        assert stable_delta_g >= -8.0

        # Artificially constructed strong hairpin: GCGCGC + TTTT + GCGCGC (complementary stem)
        strong_hairpin = "GCGCGC" + "TTTT" + "GCGCGC"
        hairpin_delta_g = SynthesizabilityAnalyzer.calculate_hairpin_delta_g(strong_hairpin)
        assert hairpin_delta_g <= -8.0  # Strong stable hairpin

    def test_linguistic_complexity(self) -> None:
        """Verify sequence complexity calculation."""
        # Simple repetitive sequence
        rep_seq = "AT" * 50
        comp_rep = SynthesizabilityAnalyzer.calculate_linguistic_complexity(rep_seq)
        assert comp_rep < 0.45

        # Complex sequence
        rand_seq = "ATGACTGAATATAAACTTGTGGTAGTTGGAGCTGGTGGCGTAGGCAAGAGTGCCTTGACGATACAGCTAATTCAGA"
        comp_rand = SynthesizabilityAnalyzer.calculate_linguistic_complexity(rand_seq)
        assert comp_rand >= 0.45

    def test_synthesizability_evaluation_pass_and_fail(self) -> None:
        """Test full synthesizability gate evaluation."""
        gate = SynthesizabilityGateContract(
            chemistry=SynthesisChemistry.ENZYMATIC_TDT,
            max_homopolymer=4,
            min_gc_content=0.40,
            max_gc_content=0.60,
            min_hairpin_free_energy=-8.0,
        )

        # Good sequence
        valid_seq = "ATGACTGAATATAAACTTGTGGTAGTTGGAGCTGGTGGCGTAGGCAAGAGTGCCTTGACGATACAGCTAATTCAGA"
        rep_good = SynthesizabilityAnalyzer.evaluate(valid_seq, gate)
        assert rep_good.passed is True
        assert len(rep_good.issues) == 0

        # Bad sequence: excessive homopolymer for TdT (> 4 bp)
        bad_seq = "ATGACTGAATATAAACTTGTGGTAGTTGGAGCTGGGGGGTAGGCAAGAGTGCCTTGACGATACAGCTAATTCAGA"
        rep_bad = SynthesizabilityAnalyzer.evaluate(bad_seq, gate)
        assert rep_bad.passed is False
        assert any("Homopolymer" in issue for issue in rep_bad.issues)


class TestBiosecurityScreener:
    """Test biosecurity screening and cryptographic clearance."""

    def test_benign_screening_and_token_generation(self) -> None:
        """Verify benign sequence passes and receives SHA-256 authorization token."""
        seq = "ATGACTGAATATAAACTTGTGGTAGTTGGAGCTGGTGGCGTAGGCAAGAGTGCCTTGACG"
        clearance = BiosecurityScreener.screen_sequence(seq, operator_id="test_agent")
        assert clearance.risk_tier == BiosecurityRiskTier.BENIGN_RESEARCH
        assert clearance.screening_passed is True
        assert len(clearance.clearance_hash) == 64
        assert len(clearance.authorization_token) == 64

    def test_toxin_signature_detection(self) -> None:
        """Verify detection of controlled select agent signature triggers strict block."""
        # Embed variola signature
        toxin_seq = "AAAAATGACGACGAACAACTACTTTT"
        clearance = BiosecurityScreener.screen_sequence(toxin_seq, operator_id="malicious_agent")
        assert clearance.risk_tier == BiosecurityRiskTier.PROHIBITED_TOXIN
        assert clearance.screening_passed is False
        assert "VARIOLA_MAJOR_HEMAGGLUTININ" in clearance.matched_signatures
        assert clearance.authorization_token == ""


class TestAutonomousExecutionEngine:
    """Test multi-instrument compilation and closed-loop telemetry reconciliation."""

    def test_sila2_ir_compilation(self) -> None:
        """Verify compilation into SiLA 2 / AutoDNA JSON IR manifest."""
        contract = AutonomousExecutionContract(
            protocol_id="TEST-IR-001",
            target_sequence="ACGTACGT",
            target_entity="Amplicon_X",
            steps=[
                WetLabStepContract(
                    step_id="step_01",
                    instrument=WetLabInstrumentType.SYNTHESIZER,
                    operation="EnzymaticSynthesis_TdT",
                    duration_seconds=3600,
                    temperature_celsius=37.0,
                ),
                WetLabStepContract(
                    step_id="step_02",
                    instrument=WetLabInstrumentType.SEQUENCER,
                    operation="Nanopore_Sequencing",
                    duration_seconds=7200,
                ),
            ],
        )

        ir = AutonomousExecutionEngine.compile_to_sila2_ir(contract)
        assert ir["protocol_meta"]["protocol_id"] == "TEST-IR-001"
        assert ir["protocol_meta"]["total_steps"] == 2
        assert ir["protocol_meta"]["estimated_duration_seconds"] == 10800
        assert len(ir["hardware_dispatch_manifest"]) == 2
        assert ir["hardware_dispatch_manifest"][0]["sila2_device_class"] == "org.silastandard.device.synthesizer"
        assert ir["hardware_dispatch_manifest"][1]["sila2_device_class"] == "org.silastandard.device.sequencer"

    def test_telemetry_reconciliation_success(self) -> None:
        """Verify successful telemetry reconciliation promotes evidence status to EMPIRICAL_VERIFIED."""
        contract = AutonomousExecutionContract(
            protocol_id="TEST-TELEM-001",
            target_sequence="ATGACTGAATATAAAC",
            evidence_promotion="EMPIRICAL_VERIFIED",
        )
        telemetry = ExperimentalTelemetryContract(
            readout_type=TelemetryReadoutType.NGS_FASTQ_READS,
            observed_sequence="ATGACTGAATATAAAC",
            observed_yield=0.977,
        )

        result = AutonomousExecutionEngine.reconcile_telemetry(contract, telemetry)
        assert result.reconciled is True
        assert result.concordance_rate == 1.0
        assert result.promoted_evidence_status == "EMPIRICAL_VERIFIED"
        assert len(result.audit_proof_hash) == 64

    def test_telemetry_reconciliation_discordance(self) -> None:
        """Verify discordant telemetry marks synthesis failure."""
        contract = AutonomousExecutionContract(
            protocol_id="TEST-TELEM-FAIL",
            target_sequence="AAAAAAAAAAAAAAAA",
            evidence_promotion="EMPIRICAL_VERIFIED",
        )
        telemetry = ExperimentalTelemetryContract(
            readout_type=TelemetryReadoutType.NGS_FASTQ_READS,
            observed_sequence="TTTTTTTTTTTTTTTT",  # 0% match
            concordance_rate=0.0,
            observed_yield=0.40,
        )

        result = AutonomousExecutionEngine.reconcile_telemetry(contract, telemetry)
        assert result.reconciled is False
        assert result.concordance_rate == 0.0
        assert result.promoted_evidence_status == "SYNTHESIS_DISCORDANT"

    def test_full_closed_loop_execution(self) -> None:
        """Test full closed-loop pipeline execution."""
        contract = AutonomousExecutionContract(
            protocol_id="CLOSED-LOOP-001",
            target_sequence="ATGACTGAATATAAACTTGTGGTAGTTGGAGCTGGTGGCGTAGGCAAGAGTGCCTTGACGATACAGCTAATTCAGA",
            synthesizability=SynthesizabilityGateContract(
                chemistry=SynthesisChemistry.ENZYMATIC_TDT,
                max_homopolymer=4,
            ),
            steps=[
                WetLabStepContract(
                    step_id="step_01",
                    instrument=WetLabInstrumentType.SYNTHESIZER,
                    operation="EnzymaticSynthesis_TdT",
                    duration_seconds=3600,
                )
            ],
            telemetry=ExperimentalTelemetryContract(
                readout_type=TelemetryReadoutType.STEPWISE_SYNTHESIS_YIELD,
                observed_yield=0.977,
                concordance_rate=1.0,
            ),
        )

        result = AutonomousExecutionEngine.execute_closed_loop(contract)
        assert result["execution_status"] == "VERIFIED"
        assert result["synthesizability_report"]["passed"] is True
        assert result["biosecurity_clearance"]["screening_passed"] is True
        assert result["telemetry_reconciliation"]["reconciled"] is True


class TestAutonomousExecutionValidator:
    """Test EnhancedSemanticValidator integration and rejection rules."""

    def test_validate_exemplar_file(self) -> None:
        """Verify exemplar protocol file passes with 0 errors."""
        example_path = Path(__file__).parent.parent.parent / "examples" / "autonomous_wet_lab_autodna_dispatch.gfl"
        assert example_path.exists(), f"Missing exemplar file: {example_path}"

        with open(example_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        validator = EnhancedSemanticValidator(file_path=str(example_path))
        result = validator.validate_ast(data)

        assert len(result.errors) == 0, f"Validation errors: {[e.message for e in result.errors]}"
        assert len(result.warnings) == 0, f"Validation warnings: {[w.message for w in result.warnings]}"

    def test_validator_rejections(self) -> None:
        """Verify semantic validator rejects malformed contracts."""
        validator = EnhancedSemanticValidator()

        # 1. Missing protocol_id
        r1 = validator.validate_ast(
            {
                "autonomous_execution": {
                    "target_sequence": "ACGT",
                }
            }
        )
        assert any("protocol_id" in e.message for e in r1.errors)

        # 2. Missing target_sequence
        r2 = validator.validate_ast(
            {
                "autonomous_execution": {
                    "protocol_id": "TEST-01",
                }
            }
        )
        assert any("target_sequence" in e.message for e in r2.errors)

        # 3. Invalid non-IUPAC characters
        r3 = validator.validate_ast(
            {
                "autonomous_execution": {
                    "protocol_id": "TEST-01",
                    "target_sequence": "ACGT123$$$",
                }
            }
        )
        assert any("non-IUPAC" in e.message for e in r3.errors)

        # 4. Invalid chemistry
        r4 = validator.validate_ast(
            {
                "autonomous_execution": {
                    "protocol_id": "TEST-01",
                    "target_sequence": "ACGT",
                    "synthesizability": {
                        "chemistry": "magic_quantum_chemistry",
                    },
                }
            }
        )
        assert any("chemistry" in e.message for e in r4.errors)

        # 5. Inverted GC content bounds
        r5 = validator.validate_ast(
            {
                "autonomous_execution": {
                    "protocol_id": "TEST-01",
                    "target_sequence": "ACGT",
                    "synthesizability": {
                        "min_gc_content": 0.80,
                        "max_gc_content": 0.20,
                    },
                }
            }
        )
        assert any("GC content bounds" in e.message for e in r5.errors)

        # 6. Biosecurity failed flag
        r6 = validator.validate_ast(
            {
                "autonomous_execution": {
                    "protocol_id": "TEST-01",
                    "target_sequence": "ACGT",
                    "biosecurity": {
                        "screening_passed": False,
                    },
                }
            }
        )
        assert any("Biosecurity screening failed" in e.message for e in r6.errors)

        # 7. Empty steps list
        r7 = validator.validate_ast(
            {
                "autonomous_execution": {
                    "protocol_id": "TEST-01",
                    "target_sequence": "ACGT",
                    "steps": [],
                }
            }
        )
        assert any("at least one hardware step" in e.message for e in r7.errors)

        # 8. Invalid instrument in step
        r8 = validator.validate_ast(
            {
                "autonomous_execution": {
                    "protocol_id": "TEST-01",
                    "target_sequence": "ACGT",
                    "steps": [
                        {
                            "instrument": "microwave_oven",
                            "operation": "Cook",
                        }
                    ],
                }
            }
        )
        assert any("instrument" in e.message for e in r8.errors)

        # 9. Out of bounds concordance rate
        r9 = validator.validate_ast(
            {
                "autonomous_execution": {
                    "protocol_id": "TEST-01",
                    "target_sequence": "ACGT",
                    "telemetry": {
                        "concordance_rate": 2.5,
                    },
                }
            }
        )
        assert any("concordance_rate" in e.message for e in r9.errors)
