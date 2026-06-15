from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from geneforgelang.ir.state import BiologicalState, Entity

IUPAC_NUCLEOTIDES = set("ACGTN")


class InstructionError(Exception):
    pass


class EntityNotFoundError(InstructionError):
    pass


class ReferenceMismatchError(InstructionError):
    pass


class InvalidSequenceError(InstructionError):
    pass


def _validate_iupac(seq: str) -> None:
    invalid = set(seq.upper()) - IUPAC_NUCLEOTIDES
    if invalid:
        raise InvalidSequenceError(f"Invalid IUPAC characters: {invalid}")


class Instruction(ABC):
    @abstractmethod
    def apply(self, state: BiologicalState) -> BiologicalState:
        raise NotImplementedError

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError


class Substitute(Instruction):
    def __init__(self, gene_id: str, position: int, ref: str, alt: str):
        if position < 0:
            raise ValueError("position must be non-negative")
        if len(ref) != 1 or len(alt) != 1:
            raise ValueError("ref and alt must be single nucleotides for Substitute")
        _validate_iupac(ref)
        _validate_iupac(alt)
        self.gene_id = gene_id
        self.position = position
        self.ref = ref.upper()
        self.alt = alt.upper()

    def apply(self, state: BiologicalState) -> BiologicalState:
        new_state = state.fork()
        gene = new_state.get_entity(self.gene_id)
        if gene is None:
            raise EntityNotFoundError(f"Entity {self.gene_id} not found in state")

        seq = gene.get_attr("sequence")
        if seq is None:
            raise ReferenceMismatchError(f"Entity {self.gene_id} has no sequence")

        seq = str(seq)
        if self.position >= len(seq):
            raise ReferenceMismatchError(f"Position {self.position} out of bounds for sequence of length {len(seq)}")

        actual = seq[self.position].upper()
        if actual != self.ref:
            raise ReferenceMismatchError(f"Reference mismatch at {self.position}: expected {self.ref}, found {actual}")

        new_seq = seq[: self.position] + self.alt + seq[self.position + 1 :]
        if gene.get_attr("original_sequence") is None:
            gene.set_attr("original_sequence", seq)
        gene.set_attr("sequence", new_seq)
        gene.set_attr("status", "mutated")
        new_state.propagate_mutation_effects(self.gene_id)
        return new_state

    def to_dict(self) -> dict[str, Any]:
        return {
            "op": "SUBSTITUTE",
            "gene_id": self.gene_id,
            "position": self.position,
            "ref": self.ref,
            "alt": self.alt,
        }

    def __repr__(self) -> str:
        return f"Substitute({self.gene_id}, pos={self.position}, {self.ref}->{self.alt})"


class Insert(Instruction):
    def __init__(self, gene_id: str, position: int, sequence: str):
        if position < 0:
            raise ValueError("position must be non-negative")
        _validate_iupac(sequence)
        self.gene_id = gene_id
        self.position = position
        self.sequence = sequence.upper()

    def apply(self, state: BiologicalState) -> BiologicalState:
        new_state = state.fork()
        gene = new_state.get_entity(self.gene_id)
        if gene is None:
            raise EntityNotFoundError(f"Entity {self.gene_id} not found in state")

        seq = gene.get_attr("sequence")
        if seq is None:
            raise ReferenceMismatchError(f"Entity {self.gene_id} has no sequence")

        seq = str(seq)
        if self.position > len(seq):
            raise ReferenceMismatchError(f"Position {self.position} out of bounds for sequence of length {len(seq)}")

        new_seq = seq[: self.position] + self.sequence + seq[self.position :]
        if gene.get_attr("original_sequence") is None:
            gene.set_attr("original_sequence", seq)
        gene.set_attr("sequence", new_seq)
        gene.set_attr("status", "mutated")
        new_state.propagate_mutation_effects(self.gene_id)
        return new_state

    def to_dict(self) -> dict[str, Any]:
        return {
            "op": "INSERT",
            "gene_id": self.gene_id,
            "position": self.position,
            "sequence": self.sequence,
        }

    def __repr__(self) -> str:
        return f"Insert({self.gene_id}, pos={self.position}, len={len(self.sequence)})"


class Delete(Instruction):
    def __init__(self, gene_id: str, start: int, end: int):
        if start < 0 or end < 0 or start >= end:
            raise ValueError("start must be non-negative and less than end")
        self.gene_id = gene_id
        self.start = start
        self.end = end

    def apply(self, state: BiologicalState) -> BiologicalState:
        new_state = state.fork()
        gene = new_state.get_entity(self.gene_id)
        if gene is None:
            raise EntityNotFoundError(f"Entity {self.gene_id} not found in state")

        seq = gene.get_attr("sequence")
        if seq is None:
            raise ReferenceMismatchError(f"Entity {self.gene_id} has no sequence")

        seq = str(seq)
        if self.end > len(seq):
            raise ReferenceMismatchError(f"End {self.end} out of bounds for sequence of length {len(seq)}")

        new_seq = seq[: self.start] + seq[self.end :]
        if gene.get_attr("original_sequence") is None:
            gene.set_attr("original_sequence", seq)
        gene.set_attr("sequence", new_seq)
        gene.set_attr("status", "mutated")
        new_state.propagate_mutation_effects(self.gene_id)
        return new_state

    def to_dict(self) -> dict[str, Any]:
        return {
            "op": "DELETE",
            "gene_id": self.gene_id,
            "start": self.start,
            "end": self.end,
        }

    def __repr__(self) -> str:
        return f"Delete({self.gene_id}, {self.start}:{self.end})"


class Invert(Instruction):
    def __init__(self, gene_id: str, start: int, end: int):
        if start < 0 or end < 0 or start >= end:
            raise ValueError("start must be non-negative and less than end")
        self.gene_id = gene_id
        self.start = start
        self.end = end

    def apply(self, state: BiologicalState) -> BiologicalState:
        new_state = state.fork()
        gene = new_state.get_entity(self.gene_id)
        if gene is None:
            raise EntityNotFoundError(f"Entity {self.gene_id} not found in state")

        seq = gene.get_attr("sequence")
        if seq is None:
            raise ReferenceMismatchError(f"Entity {self.gene_id} has no sequence")

        seq = str(seq)
        if self.end > len(seq):
            raise ReferenceMismatchError(f"End {self.end} out of bounds for sequence of length {len(seq)}")

        segment = seq[self.start : self.end]
        inverted = segment.translate(str.maketrans("ACGTUN", "TGCAAN"))[::-1]
        new_seq = seq[: self.start] + inverted + seq[self.end :]
        if gene.get_attr("original_sequence") is None:
            gene.set_attr("original_sequence", seq)
        gene.set_attr("sequence", new_seq)
        gene.set_attr("status", "mutated")
        new_state.propagate_mutation_effects(self.gene_id)
        return new_state

    def to_dict(self) -> dict[str, Any]:
        return {
            "op": "INVERT",
            "gene_id": self.gene_id,
            "start": self.start,
            "end": self.end,
        }

    def __repr__(self) -> str:
        return f"Invert({self.gene_id}, {self.start}:{self.end})"
