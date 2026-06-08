import pytest

from geneforgelang.ir.executor import GraphExecutor, ExecutionError
from geneforgelang.ir.instruction import Substitute, Delete
from geneforgelang.ir.state import BiologicalState, Entity, EntityType
from geneforgelang.ir.strategy import Objective, PlanGraph, PlanNode


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


def test_graph_executor_unconditional():
    state = _make_state()
    root = PlanNode(action=Substitute(gene_id="TP53", position=0, ref="A", alt="G"))
    plan = PlanGraph(objective=Objective(description="Mutate TP53"), root=root)
    executor = GraphExecutor(plan)
    trace = executor.execute(state)
    assert trace.final_state().get_entity("TP53").get_attr("sequence") == "GTCGATCG"
    assert len(trace.records) == 1


def test_graph_executor_conditional_true():
    state = _make_state()
    root = PlanNode(
        condition='TP53.status == wildtype',
        action=Substitute(gene_id="TP53", position=0, ref="A", alt="G"),
    )
    plan = PlanGraph(objective=Objective(description="Mutate if wildtype"), root=root)
    executor = GraphExecutor(plan)
    trace = executor.execute(state)
    assert trace.final_state().get_entity("TP53").get_attr("sequence") == "GTCGATCG"


def test_graph_executor_conditional_false():
    state = _make_state()
    state.entities["TP53"].set_attr("status", "mutated")
    root = PlanNode(
        condition='TP53.status == wildtype',
        action=Substitute(gene_id="TP53", position=0, ref="A", alt="G"),
    )
    plan = PlanGraph(objective=Objective(description="Mutate if wildtype"), root=root)
    executor = GraphExecutor(plan)
    trace = executor.execute(state)
    # Condition false → action skipped
    assert trace.final_state().get_entity("TP53").get_attr("sequence") == "ATCGATCG"
    assert len(trace.records) == 0


def test_graph_executor_branching():
    state = _make_state()
    root = PlanNode(
        condition='TP53.status == wildtype',
        action=Substitute(gene_id="TP53", position=0, ref="A", alt="G"),
        next_nodes=[
            PlanNode(
                condition="score > 0.0",
                action=Delete(gene_id="TP53", start=1, end=3),
            )
        ],
    )
    plan = PlanGraph(
        objective=Objective(description="Branching mutation", target_entity="TP53"),
        root=root,
    )
    executor = GraphExecutor(plan)
    trace = executor.execute(state)
    final = trace.final_state().get_entity("TP53").get_attr("sequence")
    # First: ATCGATCG -> GTCGATCG
    # Second: GTCGATCG -> GGATCG (delete positions 1-3: "TCG")
    assert final == "GGATCG"
    assert len(trace.records) == 2
