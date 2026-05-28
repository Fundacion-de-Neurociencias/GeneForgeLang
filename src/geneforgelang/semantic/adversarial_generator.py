from __future__ import annotations

import random
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from geneforgelang.semantic.lattice import (
    ContradictionLoad,
    EcologicalScope,
    EpistemicState,
    ObservationalResolution,
    TemporalStability,
    TruthSupport,
)
from geneforgelang.semantic.state_space import SemanticStateSpaceAudit


@dataclass(frozen=True)
class OperationTrace:
    operation: str
    operands: tuple[EpistemicState, ...]
    result: EpistemicState


class RepresentationalAdversarialGenerator:
    """Generate adversarial lattice states and compositions from parameters."""

    def __init__(self, seed: int):
        self.random = random.Random(seed)
        self.space = SemanticStateSpaceAudit()
        self.valid_states = tuple(sorted(self.space.valid_states, key=_state_sort_key))
        self.all_states = tuple(sorted(self.space.all_states, key=_state_sort_key))

    def tier_a_states(self, enabled: bool = True) -> tuple[EpistemicState, ...]:
        return self.all_states if enabled else ()

    def tier_b_operation_traces(
        self,
        sequence_lengths: Sequence[int],
        samples: int,
    ) -> tuple[OperationTrace, ...]:
        traces: list[OperationTrace] = []
        if not sequence_lengths or samples <= 0:
            return ()

        for _ in range(samples):
            length = self.random.choice(tuple(sequence_lengths))
            current = self.random.choice(self.valid_states)
            for _step in range(length):
                other = self.random.choice(self.valid_states)
                operation = self.random.choice(("meet", "join"))
                result = current.meet(other) if operation == "meet" else current.join(other)
                traces.append(OperationTrace(operation=operation, operands=(current, other), result=result))
                current = result
        return tuple(traces)

    def tier_c_mutations(self, mutations: int) -> tuple[OperationTrace, ...]:
        traces: list[OperationTrace] = []
        dimensions = (
            tuple(TruthSupport),
            tuple(TemporalStability),
            tuple(ObservationalResolution),
            tuple(EcologicalScope),
            tuple(ContradictionLoad),
        )
        for _ in range(max(0, mutations)):
            source = self.random.choice(self.all_states)
            values = [
                source.truth_support,
                source.temporal_stability,
                source.observational_resolution,
                source.ecological_scope,
                source.contradiction_load,
            ]
            dimension_index = self.random.randrange(len(dimensions))
            values[dimension_index] = self.random.choice(dimensions[dimension_index])
            mutated = EpistemicState(*values)
            operation = self.random.choice(("meet", "join"))
            boundary = self.random.choice((EpistemicState.get_null_state(), EpistemicState.get_ideal_state()))
            result = mutated.meet(boundary) if operation == "meet" else mutated.join(boundary)
            traces.append(
                OperationTrace(operation=f"mutation_{operation}", operands=(mutated, boundary), result=result)
            )
        return tuple(traces)


def flatten_trace_states(traces: Iterable[OperationTrace]) -> tuple[EpistemicState, ...]:
    states: list[EpistemicState] = []
    for trace in traces:
        states.extend(trace.operands)
        states.append(trace.result)
    return tuple(states)


def _state_sort_key(state: EpistemicState) -> tuple[int, int, int, int, int]:
    return (
        state.truth_support.value,
        state.temporal_stability.value,
        state.observational_resolution.value,
        state.ecological_scope.value,
        state.contradiction_load.value,
    )
