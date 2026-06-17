from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OntologyTerm:
    id: str
    label: str
    parents: tuple[str, ...] = ()
    deprecated: bool = False


@dataclass
class SemanticOntology:
    terms: dict[str, OntologyTerm] = field(default_factory=dict)

    def add(self, term: OntologyTerm) -> None:
        self.terms[term.id] = term

    def has(self, term_id: str) -> bool:
        return term_id in self.terms and not self.terms[term_id].deprecated


@dataclass
class SemanticValidator:
    ontology: SemanticOntology
    strict: bool = False

    def validate_term(self, term_id: str) -> list[str]:
        if self.ontology.has(term_id):
            return []
        message = f"Unknown semantic term: {term_id}"
        if self.strict:
            raise ValueError(message)
        return [message]
