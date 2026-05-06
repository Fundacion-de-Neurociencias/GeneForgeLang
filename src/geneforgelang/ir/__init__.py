from geneforgelang.ir.executor import (
    ExecutionError,
    GraphExecutor,
    StateTrace,
    StepRecord,
    StrategyExecutor,
    apply,
)
from geneforgelang.ir.external import (
    HuggingScienceConnector,
    OpenMedConnector,
    RetrievedEvidence,
    RetrievalService,
)
from geneforgelang.ir.instruction import (
    Delete,
    EntityNotFoundError,
    Insert,
    Instruction,
    InstructionError,
    InvalidSequenceError,
    Invert,
    ReferenceMismatchError,
    Substitute,
)
from geneforgelang.ir.knowledge_grounding import KnowledgeBase
from geneforgelang.ir.llm_planner import LLMBackend, LLMPlanner, MockLLMBackend
from geneforgelang.ir.parser_ir import ParseError, parse_text
from geneforgelang.ir.reasoning_loop import (
    MockPlannerBackend,
    PlannerBackend,
    ReasoningLoop,
    ReasoningResult,
)
from geneforgelang.ir.state import BiologicalState, Entity, EntityType, Relation, RelationType
from geneforgelang.ir.state_evaluator import StateEvaluator
from geneforgelang.ir.strategy import Constraint, Objective, PlanGraph, PlanNode, Strategy

__all__ = [
    # Core state
    "BiologicalState",
    "Entity",
    "EntityType",
    "Relation",
    "RelationType",
    # Instructions
    "Instruction",
    "Substitute",
    "Insert",
    "Delete",
    "Invert",
    "InstructionError",
    "EntityNotFoundError",
    "ReferenceMismatchError",
    "InvalidSequenceError",
    # Strategy
    "Strategy",
    "Objective",
    "Constraint",
    "PlanNode",
    "PlanGraph",
    # Execution
    "StrategyExecutor",
    "GraphExecutor",
    "StateTrace",
    "StepRecord",
    "ExecutionError",
    "apply",
    # Parsing
    "parse_text",
    "ParseError",
    # Planning
    "LLMPlanner",
    "LLMBackend",
    "MockLLMBackend",
    # Evaluation
    "StateEvaluator",
    "KnowledgeBase",
    # Reasoning
    "ReasoningLoop",
    "ReasoningResult",
    "PlannerBackend",
    "MockPlannerBackend",
    # Fase 3: External Knowledge
    "OpenMedConnector",
    "HuggingScienceConnector",
    "RetrievalService",
    "RetrievedEvidence",
]
