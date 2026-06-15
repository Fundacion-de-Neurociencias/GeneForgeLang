import pytest

from geneforgelang.ir.executor import (
    StrategyExecutor,
    ExecutionError,
    apply,
)
from geneforgelang.ir.instruction import Substitute, Insert
from geneforgelang.ir.state import BiologicalState, Entity, EntityType
from geneforgelang.ir.strategy import Strategy, Objective, Constraint


def _make_state():
    return BiologicalState(
        entities={
            "TP53": Entity(
                id="TP53",
                type=EntityType.GENE,
                attrs={"sequence": "AAA", "status": "wildtype"},
            )
        }
    )


def test_apply_single_instruction():
    state = _make_state()
    inst = Substitute(gene_id="TP53", position=0, ref="A", alt="T")
    new_state = apply(state, inst)
    assert new_state.get_entity("TP53").get_attr("sequence") == "TAA"
    assert state.get_entity("TP53").get_attr("sequence") == "AAA"


def test_executor_trace():
    state = _make_state()
    strategy = Strategy(
        objective=Objective(description="Mutate TP53"),
        steps=[
            Substitute(gene_id="TP53", position=0, ref="A", alt="T"),
            Substitute(gene_id="TP53", position=1, ref="A", alt="G"),
        ],
    )
    executor = StrategyExecutor(strategy)
    trace = executor.execute(state)
    final = trace.final_state()
    assert final.get_entity("TP53").get_attr("sequence") == "TGA"
    assert len(trace.records) == 2
    assert trace.records[0].state_after.get_entity("TP53").get_attr("sequence") == "TAA"
    assert trace.initial_state == state  # original intact


def test_executor_failure_halts():
    state = _make_state()
    strategy = Strategy(
        objective=Objective(description="Fail"),
        steps=[
            Substitute(gene_id="TP53", position=0, ref="A", alt="T"),
            Substitute(gene_id="TP53", position=0, ref="G", alt="C"),
        ],
    )
    executor = StrategyExecutor(strategy)
    with pytest.raises(ExecutionError):
        executor.execute(state)


def test_executor_with_constraints():
    state = _make_state()
    strategy = Strategy(
        objective=Objective(description="Insert with constraints"),
        constraints=[Constraint(expression="length < 10")],
        steps=[Insert(gene_id="TP53", position=1, sequence="GG")],
    )
    executor = StrategyExecutor(strategy)
    trace = executor.execute(state)
    assert trace.final_state().get_entity("TP53").get_attr("sequence") == "AGGAA"


def test_empty_strategy():
    state = _make_state()
    strategy = Strategy(objective=Objective(description="No-op"))
    executor = StrategyExecutor(strategy)
    trace = executor.execute(state)
    assert trace.final_state() == state
    assert len(trace.records) == 0
