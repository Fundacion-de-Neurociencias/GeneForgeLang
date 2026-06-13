from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from geneforgelang.adapters.chai import InteractionSpec
from geneforgelang.core.parser import parse_gfl
from geneforgelang.eig.ir import (
    BiologicalEntity,
    BiologicalEvidence,
    BiologicalRelation,
    BiologicalScale,
    EvidenceGraph,
    RelationType,
)
from geneforgelang.eig.perturbation import PerturbationSet
from geneforgelang.semantic.capabilities import VariantSpec


@dataclass(frozen=True)
class CrossScaleCompilation:
    source_scale: BiologicalScale
    target_scale: BiologicalScale
    steps: tuple[BiologicalScale, ...]
    confidence: float


class CrossScaleCompiler:
    _order = (
        BiologicalScale.VARIANT,
        BiologicalScale.GENE,
        BiologicalScale.TRANSCRIPT,
        BiologicalScale.PROTEIN,
        BiologicalScale.DOMAIN,
        BiologicalScale.PATHWAY,
        BiologicalScale.CELL,
        BiologicalScale.TISSUE,
        BiologicalScale.PHENOTYPE,
        BiologicalScale.DISEASE,
    )

    def compile(
        self, source_scale: BiologicalScale | str, target_scale: BiologicalScale | str
    ) -> CrossScaleCompilation:
        source = BiologicalScale(source_scale)
        target = BiologicalScale(target_scale)
        source_index = self._order.index(source)
        target_index = self._order.index(target)
        if source_index <= target_index:
            steps = self._order[source_index : target_index + 1]
        else:
            steps = tuple(reversed(self._order[target_index : source_index + 1]))
        distance = abs(target_index - source_index)
        return CrossScaleCompilation(source, target, tuple(steps), max(0.05, 1.0 - 0.1 * distance))

    def phenotype_to_variant(self) -> CrossScaleCompilation:
        return self.compile(BiologicalScale.PHENOTYPE, BiologicalScale.VARIANT)

    def variant_to_phenotype(self) -> CrossScaleCompilation:
        return self.compile(BiologicalScale.VARIANT, BiologicalScale.PHENOTYPE)


class EvidenceGraphCompiler:
    def __init__(self, capability_provider: Any | None = None) -> None:
        self.capability_provider = capability_provider
        self.scale_compiler = CrossScaleCompiler()

    def compile(self, program: str | dict[str, Any]) -> EvidenceGraph:
        ast = self._parse_program(program)
        entity_label = str(ast.get("entity", ast.get("gene", "unknown")))
        root = BiologicalEntity(
            id=f"gene:{entity_label}",
            label=entity_label,
            scale=BiologicalScale.GENE,
            namespace="HGNC",
        )
        graph = EvidenceGraph(nodes=[root], metadata={"compiler": "EvidenceGraphCompiler"})

        perturbation_specs = self._extract_perturbations(ast)
        perturbations = PerturbationSet.from_specs(root.id, perturbation_specs).to_eig()
        graph.perturbations.extend(perturbations)

        for perturbation in perturbations:
            perturbation_evidence = self._score_perturbation(root.label, perturbation.description)
            graph.evidence.append(perturbation_evidence)
            graph.edges.append(
                BiologicalRelation(
                    id=f"edge:{perturbation.id}:perturbs:{root.id}",
                    source=perturbation.id,
                    target=root.id,
                    relation=RelationType.PERTURBS,
                    confidence=perturbation_evidence.confidence,
                    evidence=(perturbation_evidence.id,),
                    uncertainty=round(1.0 - perturbation_evidence.confidence, 6),
                )
            )

        self._compile_interactions(graph, root, ast)

        if self._requests_downstream(ast):
            self._compile_downstream_effects(graph, root, perturbations)

        graph.metadata["exportable_to"] = ("PharmaOracle", "Neurodiagnoses")
        return graph

    def export_evidence_graph(self, program: str | dict[str, Any]) -> dict[str, Any]:
        return self.compile(program).to_dict()

    def _compile_downstream_effects(
        self,
        graph: EvidenceGraph,
        root: BiologicalEntity,
        perturbations: tuple[Any, ...],
    ) -> None:
        pathway = BiologicalEntity(
            id=f"pathway:{root.label}:downstream",
            label=f"{root.label} downstream pathway",
            scale=BiologicalScale.PATHWAY,
        )
        phenotype = BiologicalEntity(
            id=f"phenotype:{root.label}:downstream_effects",
            label=f"{root.label} downstream effects",
            scale=BiologicalScale.PHENOTYPE,
        )
        graph.nodes.extend([pathway, phenotype])

        route = self.scale_compiler.compile(BiologicalScale.GENE, BiologicalScale.PHENOTYPE)
        route_evidence = BiologicalEvidence(
            id=f"evidence:{root.label}:cross_scale",
            claim=f"{root.label} effects compile across {' > '.join(step.value for step in route.steps)}",
            source="gfl.cross_scale_compiler",
            confidence=route.confidence,
            method="scale_path_prior",
        )
        graph.evidence.append(route_evidence)
        graph.edges.extend(
            [
                BiologicalRelation(
                    id=f"edge:{root.id}:modulates:{pathway.id}",
                    source=root.id,
                    target=pathway.id,
                    relation=RelationType.MODULATES,
                    confidence=route.confidence,
                    evidence=(route_evidence.id,),
                    uncertainty=round(1.0 - route.confidence, 6),
                ),
                BiologicalRelation(
                    id=f"edge:{pathway.id}:associated_with:{phenotype.id}",
                    source=pathway.id,
                    target=phenotype.id,
                    relation=RelationType.ASSOCIATED_WITH,
                    confidence=max(0.05, route.confidence - 0.1),
                    evidence=(route_evidence.id,),
                    uncertainty=round(1.0 - max(0.05, route.confidence - 0.1), 6),
                ),
            ]
        )
        graph.add_evidence_first_claim(
            claim=f"{root.label} perturbation may alter downstream phenotype",
            confidence=max(0.05, route.confidence - 0.1),
            evidence=(route_evidence.id, *(evidence.id for evidence in graph.evidence if root.label in evidence.claim)),
            counter_evidence=(),
            inferred_entities=(pathway.id, phenotype.id, *(item.id for item in perturbations)),
        )

    def _score_perturbation(self, entity_label: str, perturbation: str) -> BiologicalEvidence:
        if self.capability_provider is not None and hasattr(self.capability_provider, "score_variant"):
            result = self.capability_provider.score_variant(VariantSpec(entity_label, perturbation))
            return BiologicalEvidence(
                id=f"evidence:{entity_label}:{perturbation}",
                claim=f"{perturbation} has variant impact on {entity_label}",
                source=result.source,
                confidence=result.confidence,
                method=result.method,
                provenance={"score": result.value, **result.metadata},
            )
        return BiologicalEvidence(
            id=f"evidence:{entity_label}:{perturbation}",
            claim=f"{perturbation} has unscored perturbation effect on {entity_label}",
            source="gfl.eig.compiler",
            confidence=0.5,
            method="default_prior",
        )

    def _compile_interactions(self, graph: EvidenceGraph, root: BiologicalEntity, ast: dict[str, Any]) -> None:
        for interaction in self._extract_interactions(ast):
            target_label = interaction["target"]
            target = BiologicalEntity(
                id=f"entity:{target_label}",
                label=target_label,
                scale=BiologicalScale.PROTEIN,
                attributes={"role": interaction.get("role", "interactor")},
            )
            complex_entity = BiologicalEntity(
                id=f"complex:{root.label}:{target_label}",
                label=f"{root.label}-{target_label} complex",
                scale=BiologicalScale.PROTEIN,
                attributes={"kind": "complex"},
            )
            graph.nodes.extend([target, complex_entity])
            evidence = self._score_interaction(root.label, target_label)
            graph.evidence.append(evidence)
            graph.edges.extend(
                [
                    BiologicalRelation(
                        id=f"edge:{root.id}:interacts_with:{target.id}",
                        source=root.id,
                        target=target.id,
                        relation=RelationType.INTERACTS_WITH,
                        confidence=evidence.confidence,
                        evidence=(evidence.id,),
                        uncertainty=round(1.0 - evidence.confidence, 6),
                        attributes={"primitive": "interaction"},
                    ),
                    BiologicalRelation(
                        id=f"edge:{root.id}:forms_complex:{complex_entity.id}",
                        source=root.id,
                        target=complex_entity.id,
                        relation=RelationType.FORMS_COMPLEX,
                        confidence=float(evidence.provenance.get("complex_formation", evidence.confidence)),
                        evidence=(evidence.id,),
                        uncertainty=round(
                            1.0 - float(evidence.provenance.get("complex_formation", evidence.confidence)), 6
                        ),
                    ),
                    BiologicalRelation(
                        id=f"edge:{target.id}:forms_complex:{complex_entity.id}",
                        source=target.id,
                        target=complex_entity.id,
                        relation=RelationType.FORMS_COMPLEX,
                        confidence=float(evidence.provenance.get("complex_formation", evidence.confidence)),
                        evidence=(evidence.id,),
                        uncertainty=round(
                            1.0 - float(evidence.provenance.get("complex_formation", evidence.confidence)), 6
                        ),
                    ),
                ]
            )
            self._compile_effects(graph, complex_entity, ast, evidence.id)

    def _compile_effects(
        self, graph: EvidenceGraph, source: BiologicalEntity, ast: dict[str, Any], evidence_id: str
    ) -> None:
        for effect in self._extract_effects(ast):
            kind = effect["kind"]
            target_label = effect["target"]
            scale = BiologicalScale.PATHWAY if kind in {"activation", "inhibition"} else BiologicalScale.PHENOTYPE
            target = BiologicalEntity(
                id=f"{scale.value}:{target_label}",
                label=target_label,
                scale=scale,
            )
            graph.nodes.append(target)
            relation = RelationType.ACTIVATES if kind == "activation" else RelationType.INHIBITS
            graph.edges.append(
                BiologicalRelation(
                    id=f"edge:{source.id}:{relation.value}:{target.id}",
                    source=source.id,
                    target=target.id,
                    relation=relation,
                    confidence=0.7,
                    evidence=(evidence_id,),
                    uncertainty=0.3,
                    attributes={"effect": kind},
                )
            )
            graph.add_evidence_first_claim(
                claim=f"{source.label} {kind} affects {target_label}",
                confidence=0.7,
                evidence=(evidence_id,),
                inferred_entities=(source.id, target.id),
            )

    def _score_interaction(self, source: str, target: str) -> BiologicalEvidence:
        if self.capability_provider is not None and hasattr(self.capability_provider, "score_interaction"):
            result = self.capability_provider.score_interaction(InteractionSpec(source, target))
            return BiologicalEvidence(
                id=f"evidence:{source}:{target}:chai_interaction_score",
                claim=f"{source} interacts with {target}",
                source=result.source,
                confidence=result.interaction_score,
                method=result.method,
                provenance={
                    "chai_interaction_score": result.interaction_score,
                    "affinity": result.affinity,
                    "specificity": result.specificity,
                    "complex_formation": result.complex_formation,
                    **result.metadata,
                },
            )
        return BiologicalEvidence(
            id=f"evidence:{source}:{target}:interaction_prior",
            claim=f"{source} interacts with {target}",
            source="gfl.eig.compiler",
            confidence=0.5,
            method="default_interaction_prior",
        )

    def _parse_program(self, program: str | dict[str, Any]) -> dict[str, Any]:
        if isinstance(program, dict):
            return program
        try:
            parsed = parse_gfl(program)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
        return self._parse_line_program(program)

    def _parse_line_program(self, program: str) -> dict[str, Any]:
        ast: dict[str, Any] = {}
        perturbations: list[str] = []
        inferences: list[str] = []
        for raw_line in program.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("entity "):
                ast["entity"] = line.removeprefix("entity ").strip()
            elif line.startswith("perturbation "):
                perturbations.append(line.removeprefix("perturbation ").strip())
            elif line.startswith("infer "):
                inferences.append(line.removeprefix("infer ").strip())
            elif line.startswith("interacts_with "):
                ast["interacts_with"] = line.removeprefix("interacts_with ").strip()
            elif line.startswith("effect:"):
                value = line.removeprefix("effect:").strip()
                if value:
                    ast["effect"] = value
            elif line.startswith("confidence:"):
                ast["confidence"] = line.removeprefix("confidence:").strip()
            elif line.startswith("activation(") or line.startswith("inhibition("):
                ast["effect"] = line
        ast["perturbations"] = perturbations
        ast["infer"] = inferences
        return ast

    def _extract_perturbations(self, ast: dict[str, Any]) -> list[Any]:
        value = ast.get("perturbations", ast.get("perturbation", []))
        if isinstance(value, (str, dict)):
            return [value]
        return list(value)

    def _extract_interactions(self, ast: dict[str, Any]) -> list[dict[str, str]]:
        value = ast.get("interacts_with", ast.get("interaction", []))
        if not value:
            return []
        values = [value] if isinstance(value, (str, dict)) else list(value)
        interactions: list[dict[str, str]] = []
        for item in values:
            if isinstance(item, dict):
                target = str(item.get("target", item.get("entity", "")))
                role = str(item.get("role", "interactor"))
            else:
                text = str(item).strip()
                parts = text.split(maxsplit=1)
                role = parts[0] if len(parts) == 2 else "interactor"
                target = parts[1] if len(parts) == 2 else text
            if target:
                interactions.append({"role": role, "target": target})
        return interactions

    def _extract_effects(self, ast: dict[str, Any]) -> list[dict[str, str]]:
        value = ast.get("effect", ast.get("effects", []))
        if not value:
            return []
        values = [value] if isinstance(value, (str, dict)) else list(value)
        effects: list[dict[str, str]] = []
        for item in values:
            if isinstance(item, dict):
                kind = str(item.get("type", item.get("kind", "")))
                target = str(item.get("target", ""))
            else:
                kind, target = self._parse_effect_call(str(item))
            if kind and target:
                effects.append({"kind": kind, "target": target})
        return effects

    def _parse_effect_call(self, value: str) -> tuple[str, str]:
        stripped = value.strip()
        if "(" not in stripped:
            return stripped, ""
        kind, rest = stripped.split("(", 1)
        return kind.strip(), rest.rsplit(")", 1)[0].strip()

    def _requests_downstream(self, ast: dict[str, Any]) -> bool:
        value = ast.get("infer", ast.get("inference", ""))
        if isinstance(value, str):
            return "downstream" in value.lower()
        return any("downstream" in str(item).lower() for item in value)
