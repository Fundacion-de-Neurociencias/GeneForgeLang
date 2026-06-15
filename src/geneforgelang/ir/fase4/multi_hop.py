"""Multi-hop reasoning across biological entity graphs.

Enables chain-of-thought reasoning across multiple biological entities:
- Pathway traversal
- Interaction chains
- Causal reasoning across hops
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from geneforgelang.ir.external.openmed_connector import OpenMedConnector
from geneforgelang.ir.external.huggingscience_connector import HuggingScienceConnector
from geneforgelang.ir.state import BiologicalState, RelationType

logger = logging.getLogger(__name__)


@dataclass
class HopResult:
    """Result from a single reasoning hop."""

    hop_number: int
    entity_id: str
    entity_type: str = "unknown"

    # Relationships found
    outgoing_relations: list[dict[str, Any]] = field(default_factory=list)
    incoming_relations: list[dict[str, Any]] = field(default_factory=list)

    # Knowledge gathered
    knowledge: dict[str, Any] = field(default_factory=dict)

    # Reasoning at this hop
    reasoning_conclusion: str = ""
    reasoning_confidence: float = 0.0

    # Next hop candidates
    next_hop_candidates: list[str] = field(default_factory=list)


@dataclass
class MultiHopPath:
    """Complete multi-hop reasoning path."""

    start_entity: str
    end_entity: Optional[str] = None
    hops: list[HopResult] = field(default_factory=list)

    overall_confidence: float = 0.0
    path_type: str = "unknown"  # "causal", "regulatory", "physical", "unknown"

    def to_chain(self) -> list[str]:
        """Convert path to entity chain."""
        return [h.entity_id for h in self.hops]

    def explanation(self) -> str:
        """Generate human-readable explanation."""
        steps = []
        for i, hop in enumerate(self.hops):
            if i == 0:
                steps.append(f"Start: {hop.entity_id}")
            else:
                prev = self.hops[i - 1]
                # Find connecting relation
                conn = None
                for rel in hop.incoming_relations:
                    if rel.get("source") == prev.entity_id:
                        conn = rel
                        break
                if conn:
                    steps.append(f"  → {conn.get('type', 'relates to')} → {hop.entity_id}")
                else:
                    steps.append(f"  → {hop.entity_id}")

            if hop.reasoning_conclusion:
                steps.append(f"    [{hop.reasoning_conclusion[:60]}...]")

        return "\n".join(steps)


class MultiHopReasoner:
    """Multi-hop reasoning engine for biological entity graphs.

    Traverses entity graphs to find indirect relationships and
    build chain-of-thought explanations.
    """

    def __init__(
        self,
        openmed: Optional[OpenMedConnector] = None,
        huggingscience: Optional[HuggingScienceConnector] = None,
        max_hops: int = 3,
    ):
        self.openmed = openmed or OpenMedConnector()
        self.huggingscience = huggingscience or HuggingScienceConnector()
        self.max_hops = max_hops

    # ------------------------------------------------------------------
    # Core Multi-Hop Methods
    # ------------------------------------------------------------------

    def reason_across_path(
        self,
        start_entity: str,
        end_entity: Optional[str] = None,
        state: Optional[BiologicalState] = None,
        hypothesis: Optional[str] = None,
    ) -> MultiHopPath:
        """Execute multi-hop reasoning from start to end entity.

        If end_entity is None, explores all reachable entities up to max_hops.
        """
        path = MultiHopPath(start_entity=start_entity, end_entity=end_entity)
        visited = {start_entity.upper()}

        current_entity = start_entity

        for hop_num in range(self.max_hops):
            # Gather information at this hop
            hop = self._execute_hop(
                hop_num=hop_num,
                entity_id=current_entity,
                state=state,
                hypothesis=hypothesis,
            )
            path.hops.append(hop)

            # Check if we reached the target
            if end_entity and hop.entity_id.upper() == end_entity.upper():
                logger.info(f"Reached target {end_entity} at hop {hop_num}")
                break

            # Select next hop
            next_entity = self._select_next_hop(hop, visited, end_entity)
            if not next_entity:
                logger.info(f"No more hops available at step {hop_num}")
                break

            visited.add(next_entity.upper())
            current_entity = next_entity

        # Calculate overall confidence
        path.overall_confidence = self._calculate_path_confidence(path)
        path.path_type = self._classify_path(path)

        return path

    def find_paths(
        self,
        start_entity: str,
        end_entity: str,
        state: Optional[BiologicalState] = None,
        max_paths: int = 3,
    ) -> list[MultiHopPath]:
        """Find multiple paths between two entities."""
        paths = []

        # Strategy 1: Direct multi-hop
        path1 = self.reason_across_path(start_entity, end_entity, state)
        if len(path1.hops) > 1:
            paths.append(path1)

        # Strategy 2: Via common interactors
        path2 = self._find_via_interactors(start_entity, end_entity, state)
        if path2 and len(path2.hops) > 1:
            paths.append(path2)

        # Strategy 3: Via pathway membership
        path3 = self._find_via_pathway(start_entity, end_entity, state)
        if path3 and len(path3.hops) > 1:
            paths.append(path3)

        # Sort by confidence and return top paths
        paths.sort(key=lambda p: p.overall_confidence, reverse=True)
        return paths[:max_paths]

    def explain_relationship(
        self, entity_a: str, entity_b: str, state: Optional[BiologicalState] = None
    ) -> dict[str, Any]:
        """Generate explanation for relationship between two entities."""
        paths = self.find_paths(entity_a, entity_b, state, max_paths=3)

        if not paths:
            return {
                "relationship": "unknown",
                "confidence": 0.0,
                "explanation": f"No known relationship between {entity_a} and {entity_b}",
            }

        best_path = paths[0]

        # Generate explanation
        explanation = self._generate_path_explanation(best_path)

        return {
            "relationship": best_path.path_type,
            "confidence": best_path.overall_confidence,
            "path_length": len(best_path.hops),
            "path": best_path.to_chain(),
            "explanation": explanation,
            "alternative_paths": len(paths) - 1,
        }

    # ------------------------------------------------------------------
    # Hop Execution
    # ------------------------------------------------------------------

    def _execute_hop(
        self,
        hop_num: int,
        entity_id: str,
        state: Optional[BiologicalState],
        hypothesis: Optional[str],
    ) -> HopResult:
        """Execute a single hop of reasoning."""
        hop = HopResult(hop_number=hop_num, entity_id=entity_id)

        # 1. Get knowledge about entity
        hop.knowledge = self.openmed.get_entity_knowledge(entity_id)
        hop.entity_type = hop.knowledge.get("function", "unknown")

        # 2. Find relations from state if available
        if state:
            hop.outgoing_relations = self._get_outgoing_relations(state, entity_id)
            hop.incoming_relations = self._get_incoming_relations(state, entity_id)

        # 3. Get interactors from knowledge
        interactors = hop.knowledge.get("interactors", [])
        for interactor in interactors:
            if interactor not in [r.get("target") for r in hop.outgoing_relations]:
                hop.outgoing_relations.append(
                    {"source": entity_id, "target": interactor, "type": "INTERACTS_WITH"}
                )

        # 4. Reasoning at this hop
        if self.huggingscience and hypothesis:
            hop_hypothesis = f"At {entity_id}: {hypothesis}"
            result = self.huggingscience.reason_about_hypothesis(hop_hypothesis)
            hop.reasoning_conclusion = result.conclusion
            hop.reasoning_confidence = result.confidence

        # 5. Determine next hop candidates
        hop.next_hop_candidates = self._get_hop_candidates(hop)

        return hop

    def _get_outgoing_relations(self, state: BiologicalState, entity_id: str) -> list[dict]:
        """Get outgoing relations from state."""
        relations = []
        for rel in state.relations:
            if rel.source.upper() == entity_id.upper():
                relations.append(
                    {
                        "source": rel.source,
                        "target": rel.target,
                        "type": rel.type,
                    }
                )
        return relations

    def _get_incoming_relations(self, state: BiologicalState, entity_id: str) -> list[dict]:
        """Get incoming relations from state."""
        relations = []
        for rel in state.relations:
            if rel.target.upper() == entity_id.upper():
                relations.append(
                    {
                        "source": rel.source,
                        "target": rel.target,
                        "type": rel.type,
                    }
                )
        return relations

    def _get_hop_candidates(self, hop: HopResult) -> list[str]:
        """Determine candidates for next hop."""
        candidates = []

        # From outgoing relations
        for rel in hop.outgoing_relations:
            target = rel.get("target")
            if target:
                candidates.append(target)

        # From similar entities (if not enough candidates)
        if len(candidates) < 2:
            similar = self.openmed.find_similar_entities(hop.entity_id, top_k=2)
            for sim in similar:
                if sim.entity_id not in candidates:
                    candidates.append(sim.entity_id)

        # From pathways
        pathways = hop.knowledge.get("pathways", [])
        # Could query pathway membership for more candidates

        return candidates[:5]  # Limit candidates

    def _select_next_hop(
        self, current_hop: HopResult, visited: set[str], target: Optional[str]
    ) -> Optional[str]:
        """Select best next hop candidate."""
        candidates = [
            c for c in current_hop.next_hop_candidates if c.upper() not in visited
        ]

        if not candidates:
            return None

        # If we have a target, prioritize candidates closer to it
        if target:
            # Simple heuristic: check if candidate is target or interacts with target
            for candidate in candidates:
                if candidate.upper() == target.upper():
                    return candidate

            # Could use embedding similarity here
            target_emb = self.openmed.get_embedding(target)
            if target_emb:
                best_sim = 0
                best_candidate = None
                for candidate in candidates:
                    cand_emb = self.openmed.get_embedding(candidate)
                    if cand_emb:
                        sim = self._cosine_sim(target_emb, cand_emb)
                        if sim > best_sim:
                            best_sim = sim
                            best_candidate = candidate
                if best_candidate:
                    return best_candidate

        # Default: return first candidate
        return candidates[0]

    # ------------------------------------------------------------------
    # Path Finding Strategies
    # ------------------------------------------------------------------

    def _find_via_interactors(
        self, start: str, end: str, state: Optional[BiologicalState]
    ) -> Optional[MultiHopPath]:
        """Find path via common interactors."""
        start_knowledge = self.openmed.get_entity_knowledge(start)
        end_knowledge = self.openmed.get_entity_knowledge(end)

        start_interactors = set(start_knowledge.get("interactors", []))
        end_interactors = set(end_knowledge.get("interactors", []))

        common = start_interactors & end_interactors
        if not common:
            return None

        # Build path through first common interactor
        bridge = list(common)[0]
        path = MultiHopPath(start_entity=start, end_entity=end)

        # Hop 1: start -> bridge
        hop1 = HopResult(
            hop_number=0,
            entity_id=start,
            outgoing_relations=[{"source": start, "target": bridge, "type": "INTERACTS_WITH"}],
        )
        path.hops.append(hop1)

        # Hop 2: bridge
        hop2 = HopResult(
            hop_number=1,
            entity_id=bridge,
            incoming_relations=[{"source": start, "target": bridge, "type": "INTERACTS_WITH"}],
            outgoing_relations=[{"source": bridge, "target": end, "type": "INTERACTS_WITH"}],
        )
        path.hops.append(hop2)

        # Hop 3: end
        hop3 = HopResult(
            hop_number=2,
            entity_id=end,
            incoming_relations=[{"source": bridge, "target": end, "type": "INTERACTS_WITH"}],
        )
        path.hops.append(hop3)

        path.overall_confidence = 0.7  # Heuristic for interactor-based paths
        path.path_type = "physical"

        return path

    def _find_via_pathway(
        self, start: str, end: str, state: Optional[BiologicalState]
    ) -> Optional[MultiHopPath]:
        """Find path via common pathway membership."""
        start_knowledge = self.openmed.get_entity_knowledge(start)
        end_knowledge = self.openmed.get_entity_knowledge(end)

        start_pathways = set(start_knowledge.get("pathways", []))
        end_pathways = set(end_knowledge.get("pathways", []))

        common = start_pathways & end_pathways
        if not common:
            return None

        # Build path through pathway
        pathway = list(common)[0]
        path = MultiHopPath(start_entity=start, end_entity=end)

        hop1 = HopResult(hop_number=0, entity_id=start)
        path.hops.append(hop1)

        hop2 = HopResult(
            hop_number=1,
            entity_id=f"pathway:{pathway}",
            knowledge={"pathway": pathway},
        )
        path.hops.append(hop2)

        hop3 = HopResult(hop_number=2, entity_id=end)
        path.hops.append(hop3)

        path.overall_confidence = 0.6
        path.path_type = "regulatory"

        return path

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _calculate_path_confidence(self, path: MultiHopPath) -> float:
        """Calculate overall path confidence."""
        if not path.hops:
            return 0.0

        confidences = [h.reasoning_confidence for h in path.hops if h.reasoning_confidence > 0]
        if not confidences:
            return 0.5  # Default if no reasoning

        return sum(confidences) / len(confidences)

    def _classify_path(self, path: MultiHopPath) -> str:
        """Classify the type of biological relationship."""
        # Analyze relations
        has_regulatory = any(
            "REGULATES" in str(r.get("type", "")) for h in path.hops for r in h.outgoing_relations
        )
        has_physical = any(
            "INTERACTS_WITH" in str(r.get("type", ""))
            for h in path.hops
            for r in h.outgoing_relations
        )

        if has_regulatory:
            return "regulatory"
        if has_physical:
            return "physical"

        return "unknown"

    def _generate_path_explanation(self, path: MultiHopPath) -> str:
        """Generate natural language explanation."""
        return path.explanation()

    def _cosine_sim(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity."""
        import math

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
