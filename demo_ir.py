#!/usr/bin/env python3
"""
Demo script for GeneForgeLang IR Core.

Shows the new pipeline:
    Text -> Parser -> State + Instructions -> Executor -> Trace
    Prompt -> LLM Planner -> Strategy -> Executor -> Trace
"""

import sys
from pathlib import Path

# Ensure src is on path when run directly
sys.path.insert(0, str(Path(__file__).parent / "src"))

from geneforgelang.ir.parser_ir import parse_text
from geneforgelang.ir.executor import StrategyExecutor, GraphExecutor
from geneforgelang.ir.strategy import Strategy, Objective, PlanNode, PlanGraph
from geneforgelang.ir.llm_planner import LLMPlanner
from geneforgelang.ir.state_evaluator import StateEvaluator
from geneforgelang.ir.knowledge_grounding import KnowledgeBase
from geneforgelang.ir.reasoning_loop import ReasoningLoop, MockPlannerBackend
from geneforgelang.ir.state import BiologicalState, Entity, EntityType


def demo_parser_executor():
    print("=== DEMO 1: Parser + Executor ===")
    text = """
    # Define biological state
    entity TP53 GENE sequence=ATCGATCG status=wildtype
    entity KRAS GENE sequence=GGCGGCGGC status=wildtype

    relation TP53 REGULATES KRAS

    # Plan: mutate TP53
    substitute TP53 0 A G
    insert TP53 2 AA
    """
    state, instructions = parse_text(text)
    print("Entities:", list(state.entities.keys()))
    print("Relations:", state.relations)

    strategy = Strategy(
        objective=Objective(description="Demo mutation"), steps=instructions
    )
    executor = StrategyExecutor(strategy)
    trace = executor.execute(state)

    print(
        "Final TP53 sequence:",
        trace.final_state().get_entity("TP53").get_attr("sequence"),
    )
    print("Trace steps:", len(trace.records))
    for rec in trace.records:
        print(" -", rec.instruction)


def demo_llm_planner():
    print("\n=== DEMO 2: LLM Planner ===")
    planner = LLMPlanner()
    strategy = planner.generate_strategy("Knockout TP53 in KRAS-mutated cells")
    print("Objective:", strategy.objective.description)
    print("Target:", strategy.objective.target_entity)
    print("Constraints:", [c.expression for c in strategy.constraints])
    print("Steps:")
    for step in strategy.steps:
        print(" -", step)


def demo_evaluator():
    print("\n=== DEMO 3: State Evaluation ===")
    state = BiologicalState()
    state.add_entity(
        Entity(
            id="TP53",
            type=EntityType.GENE,
            attrs={
                "sequence": "NNNNNNNN",
                "original_sequence": "ATCGATCG",
                "status": "knocked_out",
            },
        )
    )
    obj = Objective(description="Knockout TP53", target_entity="TP53")
    ev = StateEvaluator()
    score = ev.evaluate(state, obj)
    print("Score for knocked-out TP53:", score)


def demo_knowledge():
    print("\n=== DEMO 4: Knowledge Grounding ===")
    kb = KnowledgeBase()
    info = kb.query("TP53")
    print("TP53 function:", info.get("function"))
    print("TP53 interactors:", info.get("interactors"))
    print("Viability knockout:", kb.is_viable_edit("TP53", "knockout"))


def demo_reasoning_loop():
    print("\n=== DEMO 5: Reasoning Loop ===")
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
    objective = Objective(description="Knockout TP53", target_entity="TP53")
    loop = ReasoningLoop(
        planner=MockPlannerBackend(),
        evaluator=StateEvaluator(),
        max_iterations=5,
        score_threshold=0.95,
    )
    result = loop.run(state, objective)
    print("Iterations:", result.iterations)
    print("Final score:", result.score)
    if result.trace:
        print("Final TP53 sequence:", result.trace.final_state().get_entity("TP53").get_attr("sequence"))


def demo_graph_executor():
    print("\n=== DEMO 6: Conditional Plan Graph ===")
    state = BiologicalState()
    state.add_entity(
        Entity(
            id="TP53",
            type=EntityType.GENE,
            attrs={"sequence": "ATCGATCG", "status": "wildtype"},
        )
    )
    from geneforgelang.ir.instruction import Substitute, Delete
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
        objective=Objective(description="Branching knockout", target_entity="TP53"),
        root=root,
    )
    executor = GraphExecutor(plan)
    trace = executor.execute(state)
    print("Final sequence:", trace.final_state().get_entity("TP53").get_attr("sequence"))
    print("Steps executed:", len(trace.records))


if __name__ == "__main__":
    demo_parser_executor()
    demo_llm_planner()
    demo_evaluator()
    demo_knowledge()
    demo_reasoning_loop()
    demo_graph_executor()
