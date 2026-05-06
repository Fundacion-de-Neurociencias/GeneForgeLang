import pytest

from geneforgelang.ir.reasoning_loop import ReasoningLoop, MockPlannerBackend
from geneforgelang.ir.state_evaluator import StateEvaluator
from geneforgelang.ir.state import BiologicalState, Entity, EntityType
from geneforgelang.ir.strategy import Objective


def _make_state():
    state = BiologicalState()
    state.add_entity(
        Entity(
            id="TP53",
            type=EntityType.GENE,
            attrs={
                "sequence": "ATCGATCG",
                "original_sequence": "ATCGATCG",
                "status": "wildtype",
            },
        )
    )
    return state


def test_reasoning_loop_converges():
    state = _make_state()
    objective = Objective(description="Knockout TP53", target_entity="TP53")
    loop = ReasoningLoop(
        planner=MockPlannerBackend(),
        evaluator=StateEvaluator(),
        max_iterations=5,
        score_threshold=0.95,
    )
    result = loop.run(state, objective)
    assert result.iterations >= 1
    assert result.trace is not None
    assert result.score > 0.0


def test_reasoning_loop_improves_score():
    state = _make_state()
    objective = Objective(description="Knockout TP53", target_entity="TP53")
    loop = ReasoningLoop(
        planner=MockPlannerBackend(),
        evaluator=StateEvaluator(),
        max_iterations=5,
    )
    result = loop.run(state, objective)
    # Score should improve with aggressive edits
    assert result.score >= result.attempts[0][1]


def test_reasoning_loop_records_attempts():
    state = _make_state()
    objective = Objective(description="Knockout TP53", target_entity="TP53")
    loop = ReasoningLoop(
        planner=MockPlannerBackend(),
        evaluator=StateEvaluator(),
        max_iterations=3,
    )
    result = loop.run(state, objective)
    assert len(result.attempts) == result.iterations
