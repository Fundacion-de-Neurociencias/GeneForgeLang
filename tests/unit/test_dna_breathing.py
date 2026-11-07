"""Unit test suite for Mesoscopic DNA Breathing & Shape Engine in GeneForgeLang (GFL).

Grounded in Chiu et al., Bioinformatics Advances, 2026 (Rohs Lab / USC).
Asserts physical opening dynamics, DNA shape coupling, and TF binding bifurcation.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from geneforgelang.core.dna_breathing_engine import DNABreathingEngine
from geneforgelang.core.gftypes import (
    GFLAST,
    DNABreathingModel,
    DNABreathingProfile,
    DNADynamicsContract,
    TFBindingCouplingMode,
    TFBreathingCouplingContract,
)
from geneforgelang.core.parser import parse_gfl
from geneforgelang.core.validator import EnhancedSemanticValidator


class TestDNABreathingTypes:
    """Test enums, dataclasses, and GFLAST serialization for DNA breathing."""

    def test_enums_and_dataclasses(self) -> None:
        assert DNABreathingModel.PBD_MESOSCOPIC.value == "pbd_mesoscopic"
        assert DNABreathingModel.EPBD_STOCHASTIC.value == "epbd_stochastic"
        assert TFBindingCouplingMode.RIGID_SHAPE_DOMINATED.value == "rigid_shape_dominated"
        assert TFBindingCouplingMode.BREATHING_ASSISTED.value == "breathing_assisted"
        assert TFBindingCouplingMode.BIFUNCTIONAL_BALANCED.value == "bifunctional_balanced"

        prof = DNABreathingProfile(
            sequence="TATAAA",
            temperature_kelvin=310.15,
            displacement_threshold_angstrom=1.5,
            mean_displacements=[0.5, 0.6, 0.6, 0.5, 0.5, 0.5],
            opening_probabilities=[0.12, 0.14, 0.14, 0.12, 0.09, 0.09],
            local_melting_energies=[1.3, 1.2, 1.2, 1.3, 1.5, 1.5],
            bubble_prone_regions=[(0, 6)],
            static_shape_mgw=[3.2, 3.1, 3.1, 3.2, 3.3, 3.3],
            static_shape_roll=[0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
            static_shape_helt=[35.8, 35.8, 35.8, 35.8, 35.8, 35.8],
            static_shape_prot=[-14.5, -14.5, -14.5, -14.5, -14.5, -14.5],
        )
        p_dict = prof.to_dict()
        assert p_dict["sequence"] == "TATAAA"
        assert len(p_dict["mean_displacements"]) == 6
        assert p_dict["evidence_status"] == "analytical_mesoscopic"

        p_recovered = DNABreathingProfile.from_dict(p_dict)
        assert p_recovered.sequence == "TATAAA"
        assert p_recovered.bubble_prone_regions == [(0, 6)]

        tf = TFBreathingCouplingContract(
            tf_name="TBP",
            coupling_mode=TFBindingCouplingMode.BREATHING_ASSISTED,
            shape_weight=0.3,
            breathing_weight=0.7,
            target_motif="TATAAA",
        )
        tf_dict = tf.to_dict()
        assert tf_dict["coupling_mode"] == "breathing_assisted"
        tf_rec = TFBreathingCouplingContract.from_dict(tf_dict)
        assert tf_rec.coupling_mode == TFBindingCouplingMode.BREATHING_ASSISTED

        contract = DNADynamicsContract(
            contract_id="dyn_test",
            sequence="TATAAAGCG",
            temperature_kelvin=310.15,
            model=DNABreathingModel.PBD_MESOSCOPIC,
            target_tf_coupling=tf,
            verified_profile=prof,
        )
        c_dict = contract.to_dict()
        assert c_dict["contract_id"] == "dyn_test"
        assert c_dict["model"] == "pbd_mesoscopic"
        c_rec = DNADynamicsContract.from_dict(c_dict)
        assert c_rec.contract_id == "dyn_test"
        assert c_rec.target_tf_coupling is not None
        assert c_rec.target_tf_coupling.tf_name == "TBP"

    def test_gflast_roundtrip(self) -> None:
        contract = DNADynamicsContract(
            contract_id="dyn_ast_test",
            sequence="ATGCATGC",
            temperature_kelvin=310.15,
        )
        ast = GFLAST(dna_dynamics=contract)
        d = ast.to_dict()
        assert "dna_dynamics" in d
        assert d["dna_dynamics"]["contract_id"] == "dyn_ast_test"

        recovered = GFLAST.from_dict(d)
        assert recovered.dna_dynamics is not None
        assert recovered.dna_dynamics.contract_id == "dyn_ast_test"

        # Test alias 'breathing'
        alias_dict = {"breathing": contract.to_dict()}
        alias_recovered = GFLAST.from_dict(alias_dict)
        assert alias_recovered.dna_dynamics is not None
        assert alias_recovered.dna_dynamics.contract_id == "dyn_ast_test"


class TestDNABreathingEngine:
    """Test physical mesoscopic calculations, temperature scaling, and variant deltas."""

    def test_at_rich_vs_gc_rich_thermal_opening(self) -> None:
        tata_box = "TATAAAGCG"
        gc_box = "GGGCGGCCG"

        prof_tata = DNABreathingEngine.compute_breathing_profile(tata_box)
        prof_gc = DNABreathingEngine.compute_breathing_profile(gc_box)

        # AT-rich regions have lower dissociation energy and higher thermal opening
        avg_p_tata = sum(prof_tata.opening_probabilities) / len(prof_tata.opening_probabilities)
        avg_p_gc = sum(prof_gc.opening_probabilities) / len(prof_gc.opening_probabilities)
        assert avg_p_tata > avg_p_gc * 3.0, f"Expected TATA breathing > 3x GC breathing, got {avg_p_tata} vs {avg_p_gc}"

        avg_y_tata = sum(prof_tata.mean_displacements) / len(prof_tata.mean_displacements)
        avg_y_gc = sum(prof_gc.mean_displacements) / len(prof_gc.mean_displacements)
        assert avg_y_tata > avg_y_gc * 1.5

    def test_temperature_monotonicity(self) -> None:
        seq = "ATATATAT"
        p_298 = DNABreathingEngine.compute_breathing_profile(seq, temperature_kelvin=298.15)
        p_310 = DNABreathingEngine.compute_breathing_profile(seq, temperature_kelvin=310.15)
        p_330 = DNABreathingEngine.compute_breathing_profile(seq, temperature_kelvin=330.15)

        sum_298 = sum(p_298.opening_probabilities)
        sum_310 = sum(p_310.opening_probabilities)
        sum_330 = sum(p_330.opening_probabilities)

        assert sum_330 > sum_310 > sum_298, "Breathing probabilities must increase with temperature"

    def test_dna_shape_profiles(self) -> None:
        a_tract = "AAAAAA"
        gc_tract = "CGCGCG"

        shape_a = DNABreathingEngine.compute_static_shape_profile(a_tract)
        shape_gc = DNABreathingEngine.compute_static_shape_profile(gc_tract)

        # A-tract minor groove width narrows significantly (< 3.5 A)
        assert all(mgw < 3.5 for mgw in shape_a["mgw"])
        # GC tract minor groove is wider (> 5.0 A)
        assert all(mgw > 5.0 for mgw in shape_gc["mgw"])
        # GC roll is higher than A-tract roll
        assert sum(shape_gc["roll"]) > sum(shape_a["roll"])

    def test_tf_binding_mode_bifurcation(self) -> None:
        seq = "CGTATAAAGC"  # pos 2 is T in TATA box
        tf_tbp = TFBreathingCouplingContract(
            tf_name="TBP",
            coupling_mode=TFBindingCouplingMode.BREATHING_ASSISTED,
        )
        tf_rigid = TFBreathingCouplingContract(
            tf_name="HOXA9",
            coupling_mode=TFBindingCouplingMode.RIGID_SHAPE_DOMINATED,
        )

        # Mutate T to G at pos 2 (decreases breathing)
        delta_tbp = DNABreathingEngine.evaluate_variant_breathing_delta(
            wildtype_sequence=seq,
            variant_ref="T",
            variant_alt="G",
            variant_pos=2,
            tf_coupling=tf_tbp,
        )
        delta_rigid = DNABreathingEngine.evaluate_variant_breathing_delta(
            wildtype_sequence=seq,
            variant_ref="T",
            variant_alt="G",
            variant_pos=2,
            tf_coupling=tf_rigid,
        )

        # Decreased breathing impairs TBP (positive Delta Delta G penalizes binding)
        assert delta_tbp["delta_opening_probability"] < 0.0
        assert delta_tbp["predicted_binding_delta_ddg_kcal_mol"] > 0.0
        assert "inhibiting TF binding" in delta_tbp["consequence_explanation"]

        # Rigid TF responds differently
        assert "rigid shape" in delta_rigid["consequence_explanation"]

    def test_contract_execution(self) -> None:
        tf = TFBreathingCouplingContract(
            tf_name="TBP",
            coupling_mode=TFBindingCouplingMode.BREATHING_ASSISTED,
        )
        contract = DNADynamicsContract(
            contract_id="dyn_exec_test",
            sequence="TATAAAGCG",
            temperature_kelvin=310.15,
            target_tf_coupling=tf,
            variant_delta={"ref": "T", "alt": "G", "pos": 0},
        )
        prof = DNABreathingEngine.execute_contract(contract)
        assert contract.verified_profile is not None
        assert contract.verified_profile == prof
        assert "variant_impact" in contract.metadata
        assert contract.target_tf_coupling.binding_affinity_delta_kcal is not None


class TestDNABreathingValidator:
    """Test EnhancedSemanticValidator checks and rejections for dna_dynamics."""

    def test_validate_exemplar_gfl_file(self) -> None:
        exemplar_path = (
            Path(__file__).resolve().parent.parent.parent / "examples" / "dna_breathing_tata_box_dynamics.gfl"
        )
        assert exemplar_path.exists()
        raw = parse_gfl(exemplar_path.read_text(encoding="utf-8"))
        assert raw is not None

        validator = EnhancedSemanticValidator(file_path=str(exemplar_path))
        res = validator.validate_ast(raw)
        assert res.is_valid is True
        assert len(res.errors) == 0

    def test_validator_rejections(self) -> None:
        v = EnhancedSemanticValidator()

        # 1. Missing sequence
        res1 = v.validate_ast({"dna_dynamics": {"temperature_kelvin": 310.15}})
        assert res1.is_valid is False
        assert any("missing required 'sequence'" in e.message for e in res1.errors)

        # 2. Invalid DNA characters
        res2 = v.validate_ast({"dna_dynamics": {"sequence": "ATGXYZ"}})
        assert res2.is_valid is False
        assert any("Invalid nucleotide characters" in e.message for e in res2.errors)

        # 3. Temperature out of biophysical range
        res3 = v.validate_ast({"dna_dynamics": {"sequence": "ATGC", "temperature_kelvin": 600.0}})
        assert res3.is_valid is False
        assert any("temperature_kelvin" in e.message for e in res3.errors)

        # 4. Variant delta out of bounds
        res4 = v.validate_ast(
            {
                "dna_dynamics": {
                    "sequence": "ATGC",
                    "variant_delta": {"pos": 10, "ref": "A", "alt": "G"},
                }
            }
        )
        assert res4.is_valid is False
        assert any("out of sequence bounds" in e.message for e in res4.errors)

        # 5. Variant delta reference mismatch
        res5 = v.validate_ast(
            {
                "dna_dynamics": {
                    "sequence": "ATGC",
                    "variant_delta": {"pos": 0, "ref": "C", "alt": "G"},
                }
            }
        )
        assert res5.is_valid is False
        assert any("does not match sequence base" in e.message for e in res5.errors)
