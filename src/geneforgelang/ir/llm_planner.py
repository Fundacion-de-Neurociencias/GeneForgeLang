from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from geneforgelang.ir.instruction import Insert, Instruction, Substitute
from geneforgelang.ir.strategy import Constraint, Objective, Strategy


class LLMBackend(ABC):
    @abstractmethod
    def generate(
        self, prompt: str, context: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        raise NotImplementedError


class MockLLMBackend(LLMBackend):
    """A mock backend that returns a canned strategy based on keyword matching."""

    def generate(
        self, prompt: str, context: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        if "knockout" in prompt_lower and "tp53" in prompt_lower:
            return {
                "objective": {
                    "description": "Knockout TP53",
                    "target_entity": "TP53",
                    "desired_outcome": "loss_of_function",
                },
                "constraints": ["KRAS_mutation == True"],
                "steps": [
                    {
                        "op": "SUBSTITUTE",
                        "gene_id": "TP53",
                        "position": 100,
                        "ref": "A",
                        "alt": "T",
                    },
                ],
            }
        return {
            "objective": {
                "description": "Generic strategy",
                "target_entity": "",
                "desired_outcome": "",
            },
            "constraints": [],
            "steps": [],
        }


class LLMPlanner:
    """Planner that turns a natural-language prompt into a typed GFL Strategy.

    The planner is backend-agnostic: swap the LLMBackend for a real model
    (OpenAI, local Llama, etc.) without touching the IR layer.
    """

    def __init__(self, backend: LLMBackend | None = None):
        self.backend = backend or MockLLMBackend()

    def generate_strategy(
        self, prompt: str, context: Dict[str, Any] | None = None
    ) -> Strategy:
        raw = self.backend.generate(prompt, context)
        obj = raw.get("objective", {})
        objective = Objective(
            description=obj.get("description", ""),
            target_entity=obj.get("target_entity", ""),
            desired_outcome=obj.get("desired_outcome", ""),
        )
        constraints = [
            Constraint(expression=c) for c in raw.get("constraints", [])
        ]
        steps: List[Instruction] = []
        for step in raw.get("steps", []):
            op = step.get("op", "").upper()
            if op == "SUBSTITUTE":
                steps.append(
                    Substitute(
                        gene_id=step["gene_id"],
                        position=step["position"],
                        ref=step["ref"],
                        alt=step["alt"],
                    )
                )
            elif op == "INSERT":
                steps.append(
                    Insert(
                        gene_id=step["gene_id"],
                        position=step["position"],
                        sequence=step["sequence"],
                    )
                )
            else:
                raise ValueError(f"Unsupported step op: {op}")
        return Strategy(
            objective=objective, constraints=constraints, steps=steps
        )
