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
from geneforgelang.ir.external import OpenMedConnector, HuggingScienceConnector, RetrievalService


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


def demo_openmed_connector():
    print("\n=== DEMO 7: OpenMed Connector (Fase 3) ===")
    connector = OpenMedConnector(enable_privacy_filter=True)

    # Entity embeddings and similarity
    print("\n--- Embeddings & Similarity ---")
    emb = connector.get_embedding("TP53")
    print(f"TP53 embedding dimension: {len(emb)}")

    similar = connector.find_similar_entities("TP53", top_k=3)
    print("Similar entities to TP53:")
    for s in similar:
        print(f"  - {s.entity_id}: similarity={s.similarity:.3f}")

    # NER extraction
    print("\n--- Named Entity Recognition ---")
    text = "TP53 mutations are associated with cancer progression and KRAS alterations"
    entities = connector.extract_entities(text)
    print(f"Entities in: '{text}'")
    for e in entities:
        print(f"  - {e.text} ({e.entity_type}, conf={e.confidence:.2f})")

    # Privacy filtering
    print("\n--- Privacy Filter (RFC 002) ---")
    clinical_note = "Patient: John Smith, DOB: 01/15/1980, Email: john@email.com, has TP53 mutation"
    result = connector.deidentify_clinical_note(clinical_note)
    print(f"Original length: {result['original_length']}")
    print(f"Cleaned length: {result['cleaned_length']}")
    print(f"Privacy cleared: {result['privacy_cleared']}")
    print(f"Entities found: {len(result['entities'])}")

    # Literature search
    print("\n--- Literature Retrieval ---")
    papers = connector.search_literature("TP53 AND cancer", max_results=3)
    print(f"Found {len(papers)} papers")
    for p in papers:
        print(f"  - PMID {p['pmid']}: {p['title'][:50]}... (relevance: {p['relevance']})")


def demo_huggingscience_connector():
    print("\n=== DEMO 8: HuggingScience Connector (Fase 3) ===")
    connector = HuggingScienceConnector()

    # Scientific reasoning
    print("\n--- Scientific Reasoning ---")
    hypothesis = "Knockout TP53 in cancer cells to induce apoptosis"
    result = connector.reason_about_hypothesis(hypothesis)
    print(f"Hypothesis: {hypothesis}")
    print(f"Conclusion: {result.conclusion}")
    print(f"Confidence: {result.confidence:.3f}")
    print("Reasoning chain:")
    for step in result.reasoning_chain:
        print(f"  -> {step}")

    # Biomedical QA
    print("\n--- Biomedical Question Answering ---")
    question = "What is the function of TP53?"
    answer = connector.answer_question(question)
    print(f"Q: {question}")
    print(f"A: {answer['answer']}")
    print(f"Confidence: {answer['confidence']}")

    # Evidence synthesis
    print("\n--- Evidence Synthesis ---")
    evidence = [
        {"relevance": 0.95, "source": "pubmed", "type": "experimental"},
        {"relevance": 0.88, "source": "pubmed", "type": "clinical"},
        {"relevance": 0.15, "source": "uncertain", "type": "prediction"},
    ]
    synthesis = connector.synthesize_evidence("TP53 knockout viability", evidence)
    print(f"Hypothesis: {synthesis['hypothesis']}")
    print(f"Confidence score: {synthesis['confidence_score']:.3f}")
    print(f"Supporting evidence: {len(synthesis['supporting_evidence'])}")
    print(f"Knowledge gaps: {synthesis['knowledge_gaps']}")


def demo_retrieval_service():
    print("\n=== DEMO 9: Unified Retrieval Service (Fase 3) ===")
    service = RetrievalService(enable_openmed=True, enable_huggingscience=True)

    # Retrieve for objective
    print("\n--- Retrieve for Objective ---")
    objective = Objective(description="Investigate TP53 knockout in cancer", target_entity="TP53")
    context = service.retrieve_for_objective(objective)

    print(f"Target: {context.target_entity}")
    print(f"Similar entities: {[e.entity_id for e in context.similar_entities]}")
    print(f"Literature count: {len(context.literature_evidence)}")
    if context.reasoning_result:
        print(f"Reasoning confidence: {context.reasoning_result.confidence:.3f}")
        print(f"Conclusion: {context.reasoning_result.conclusion[:60]}...")
    print(f"Combined confidence: {context.combined_confidence:.3f}")

    # Knowledge summary
    print("\n--- Knowledge Summary ---")
    for key, value in context.knowledge_summary.items():
        print(f"  {key}: {value}")


def demo_knowledge_with_retrieval():
    print("\n=== DEMO 10: KnowledgeBase + External Retrieval (Fase 3) ===")

    # Standard KnowledgeBase (local only)
    print("\n--- Local Knowledge (default) ---")
    kb_local = KnowledgeBase(enable_external=False)
    info = kb_local.query("TP53")
    print(f"TP53 function: {info.get('function')}")
    print(f"Sources: {info.get('sources', ['curated'])}")

    # Extended KnowledgeBase (with external)
    print("\n--- Extended Knowledge (OpenMed + HuggingScience) ---")
    retrieval = RetrievalService(enable_openmed=True, enable_huggingscience=True)
    kb_external = KnowledgeBase(retrieval_service=retrieval, enable_external=True)

    info = kb_external.query("TP53")
    print(f"TP53 function: {info.get('function')}")
    print(f"Sources: {info.get('sources', ['curated'])}")

    # Retrieve for objective
    objective = Objective(description="Analyze TP53 knockout viability", target_entity="TP53")
    result = kb_external.retrieve_for_objective(objective)
    print(f"\nRetrieval for objective:")
    print(f"  Enabled: {result['enabled']}")
    print(f"  Similar entities: {result['similar_entities']}")
    print(f"  Literature count: {result['literature_count']}")
    print(f"  Combined confidence: {result['combined_confidence']:.3f}")

    # State enrichment
    print("\n--- State Enrichment ---")
    state = BiologicalState()
    state.add_entity(Entity(id="TP53", type=EntityType.GENE, attrs={"sequence": "ATCG"}))
    enriched = kb_external.enrich_with_retrieval(state)
    entity = enriched.get_entity("TP53")
    knowledge = entity.get_attr("knowledge", {})
    print(f"Entity knowledge keys: {list(knowledge.keys())}")
    similar = entity.get_attr("similar_entities", [])
    print(f"Similar entities: {similar}")


if __name__ == "__main__":
    demo_parser_executor()
    demo_llm_planner()
    demo_evaluator()
    demo_knowledge()
    demo_reasoning_loop()
    demo_graph_executor()
    demo_openmed_connector()
    demo_huggingscience_connector()
    demo_retrieval_service()
    demo_knowledge_with_retrieval()
    print("\n" + "=" * 50)
    print("All demos completed successfully!")
    print("=" * 50)
