import pytest

from geneforgelang.temporal import (
    ActivationProfile,
    DissociationMode,
    TemporalCapabilityProvider,
    TemporalConstraintEngine,
    TemporalExecutionRuntime,
    TemporalPerturbationIR,
    TemporalRegimeAssessment,
    TemporalStabilityInvariant,
    TemporalStressProfile,
    activate,
    concurrent,
    facilitated_dissociation,
    parse_temporal_program,
    sequential,
)


def test_semantic_parsing_for_il2_timed_signalling():
    source = """
    entity IL2R

    perturbation cytokine_gate:
        activate
        dwell(brief)
        dissociate(facilitated)
        rebound(minimal)
    """

    temporal_ir = parse_temporal_program(source)

    assert temporal_ir.target == "IL2R"
    assert temporal_ir.perturbation_type == "cytokine_gate"
    assert temporal_ir.dwell_regime == "brief"
    assert temporal_ir.dissociation_mode == "facilitated"


def test_temporal_ir_serialization_is_deterministic():
    temporal_ir = facilitated_dissociation("IL2R", timed_release="brief")

    assert temporal_ir.to_dict() == temporal_ir.to_dict()
    assert temporal_ir.to_dict()["dissociation_mode"] == DissociationMode.FACILITATED


def test_temporal_composition_correctness():
    schedule = sequential(
        activate("IL2R", profile=ActivationProfile.GATED),
        facilitated_dissociation("IL2R", switchable_occupancy=True),
    )

    assert schedule.operator == "sequential"
    assert len(schedule.perturbations) == 2
    assert schedule.temporal_stability > 0


def test_constraint_violation_for_impossible_temporal_topology():
    temporal_ir = TemporalPerturbationIR(
        perturbation_type="invalid",
        activation_profile=ActivationProfile.GATED,
        dwell_regime="timeless",
        dissociation_mode=DissociationMode.PASSIVE,
    )

    result = TemporalConstraintEngine().validate_ir(temporal_ir)

    assert not result.valid
    assert result.violations[0].code == "impossible_temporal_topology"


def test_constraint_warning_for_antagonistic_concurrent_timing():
    composition = concurrent(activate("IL2R"), facilitated_dissociation("IL2R"))

    result = TemporalConstraintEngine().validate_composition(composition)

    assert result.valid
    assert any(violation.code == "antagonistic_timing" for violation in result.violations)


def test_temporal_runtime_is_backend_independent():
    runtime = TemporalExecutionRuntime()

    result = runtime.validate(facilitated_dissociation("IL2R"))

    assert result.valid
    assert runtime.providers == {}


def test_temporal_stability_tests_time_not_description():
    runtime = TemporalExecutionRuntime()

    report = runtime.test_temporal_stability(facilitated_dissociation("IL2R"))

    assert report.stability_score > 0
    assert report.outcomes
    assert report.max_sensitivity > 0


def test_temporal_stability_detects_invariant_failure_under_stress():
    runtime = TemporalExecutionRuntime()
    invariant = TemporalStabilityInvariant(
        name="facilitated_release_preserved",
        field="dissociation_mode",
        expected=DissociationMode.FACILITATED,
    )
    stress = TemporalStressProfile(
        name="force_passive_release",
        dissociation_shift=DissociationMode.PASSIVE,
        severity=0.2,
    )

    report = runtime.test_temporal_stability(
        facilitated_dissociation("IL2R"),
        profiles=(stress,),
        invariants=(invariant,),
    )

    assert not report.stable
    assert report.invariant_failures == ("invariant:facilitated_release_preserved",)


def test_composition_stability_includes_composition_penalty():
    runtime = TemporalExecutionRuntime()
    schedule = concurrent(activate("IL2R"), facilitated_dissociation("IL2R"))

    report = runtime.test_composition_stability(schedule)

    assert report.stability_score < 1
    assert report.outcomes


class MockTemporalProvider:
    name = "mock_temporal"
    version = "0"

    def simulate_temporal_regime(self, temporal_ir: TemporalPerturbationIR) -> TemporalRegimeAssessment:
        return TemporalRegimeAssessment(True, 0.8, temporal_ir.perturbation_type)

    def evaluate_dissociation_schedule(self, temporal_ir: TemporalPerturbationIR) -> TemporalRegimeAssessment:
        return TemporalRegimeAssessment(True, 0.8, temporal_ir.dissociation_mode)

    def estimate_rebound_topology(self, temporal_ir: TemporalPerturbationIR) -> TemporalRegimeAssessment:
        return TemporalRegimeAssessment(True, 0.7, temporal_ir.rebound_expectation)

    def assess_temporal_stability(self, composition) -> TemporalRegimeAssessment:
        return TemporalRegimeAssessment(True, composition.temporal_stability, composition.operator)


def test_temporal_capability_provider_protocol_registration():
    provider = MockTemporalProvider()
    runtime = TemporalExecutionRuntime()

    runtime.register_provider(provider)

    assert isinstance(provider, TemporalCapabilityProvider)
    assert runtime.providers["mock_temporal"] is provider


def test_cross_scale_temporal_compilation_bidirectional():
    runtime = TemporalExecutionRuntime()

    forward = runtime.compiler.compile("phenotype", "molecular_perturbation_schedule")
    reverse = runtime.compiler.compile("molecular_perturbation_schedule", "phenotype")

    assert forward[0] == "phenotype"
    assert forward[-1] == "molecular_perturbation_schedule"
    assert reverse[0] == "molecular_perturbation_schedule"


def test_parse_temporal_program_requires_entity_and_perturbation():
    with pytest.raises(ValueError, match="entity and perturbation"):
        parse_temporal_program("activate")
