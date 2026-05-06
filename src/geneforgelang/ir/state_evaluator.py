from __future__ import annotations

from typing import Optional

from geneforgelang.ir.state import BiologicalState, Entity, RelationType
from geneforgelang.ir.strategy import Objective


class StateEvaluator:
    """Evaluate how close a biological state is to satisfying an objective.

    The evaluator is deliberately heuristic and extensible.  A real system
    would plug in ML models, pathway simulations, or LLM-assisted scoring here.
    What matters is that *there is a function* `evaluate(state, objective) -> score`.
    """

    def evaluate(self, state: BiologicalState, objective: Objective) -> float:
        score = 0.0
        target = objective.target_entity or self._infer_target(objective.description)

        if not target:
            return 0.0

        entity = state.get_entity(target)
        if entity is None:
            return 0.0

        desc = objective.description.lower()

        if "knockout" in desc or "loss" in desc or "disable" in desc:
            score = self._score_loss_of_function(state, entity)
        elif "activate" in desc or "gain" in desc or "overexpress" in desc:
            score = self._score_gain_of_function(state, entity)
        elif "repair" in desc or "restore" in desc:
            score = self._score_restoration(state, entity)
        else:
            score = self._score_generic_change(state, entity)

        # Down-stream effect bonus: if a target entity regulates others,
        # check whether those regulators are perturbed.
        score += self._downstream_bonus(state, target)

        return min(max(score, 0.0), 1.0)

    def _infer_target(self, description: str) -> Optional[str]:
        # Naïve keyword extraction — replaceable by NER / LLM grounding.
        tokens = description.upper().split()
        for t in tokens:
            if len(t) >= 3 and t.isalnum() and not t.isdigit():
                return t
        return None

    def _sequence_damage_ratio(self, entity: Entity) -> float:
        seq = entity.get_attr("sequence", "")
        original = entity.get_attr("original_sequence", seq)
        if not original or not seq:
            return 0.0
        if len(seq) != len(original):
            return abs(len(seq) - len(original)) / max(len(original), 1)
        mismatches = sum(1 for a, b in zip(seq, original) if a != b)
        return mismatches / len(original)

    def _score_loss_of_function(self, state: BiologicalState, entity: Entity) -> float:
        score = 0.0
        # Sequence heavily damaged or truncated → loss of function
        damage = self._sequence_damage_ratio(entity)
        if damage > 0.1:
            score += 0.3
        if damage > 0.5:
            score += 0.3
        if entity.get_attr("status") == "knocked_out":
            score += 0.4
        # If entity is a gene, check whether its transcript/protein are also broken.
        if entity.type == "GENE":
            for rel in state.relations:
                if rel.source == entity.id and rel.type == RelationType.DERIVES_FROM:
                    child = state.get_entity(rel.target)
                    if child and child.get_attr("status") in ("knocked_out", "loss_of_function"):
                        score += 0.2
        return min(score, 1.0)

    def _score_gain_of_function(self, state: BiologicalState, entity: Entity) -> float:
        score = 0.0
        if entity.get_attr("status") == "activated":
            score += 0.5
        if entity.get_attr("expression_level", 0.0) > 2.0:
            score += 0.3
        # Up-regulated downstream targets
        for rel in state.relations:
            if rel.source == entity.id and rel.type == RelationType.REGULATES:
                child = state.get_entity(rel.target)
                if child and child.get_attr("expression_level", 0.0) > 1.5:
                    score += 0.2
        return min(score, 1.0)

    def _score_restoration(self, state: BiologicalState, entity: Entity) -> float:
        score = 0.0
        if entity.get_attr("status") == "wildtype":
            score += 0.6
        damage = self._sequence_damage_ratio(entity)
        if damage == 0.0:
            score += 0.4
        return min(score, 1.0)

    def _score_generic_change(self, state: BiologicalState, entity: Entity) -> float:
        damage = self._sequence_damage_ratio(entity)
        return min(damage * 2.0, 1.0)

    def _downstream_bonus(self, state: BiologicalState, target: str) -> float:
        bonus = 0.0
        for rel in state.relations:
            if rel.source == target and rel.type == RelationType.REGULATES:
                child = state.get_entity(rel.target)
                if child and child.get_attr("status") in ("knocked_out", "loss_of_function", "activated"):
                    bonus += 0.05
        return min(bonus, 0.3)
