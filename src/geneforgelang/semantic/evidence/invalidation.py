"""
Evidence Invalidation Bridge

This module handles the operational propagation of semantic state changes
(such as retractions, supersessions, or invalidations) through the
epistemic dependency graph.

It guarantees that when an upstream EvidenceContract mutates its truth value,
downstream dependents undergo mandatory epistemic recalibration in accordance
with the ContractStateTransitionMatrix.
"""

from typing import Dict, List, Set

from geneforgelang.semantic.evidence.contract import ContractStateTransitionMatrix, ContradictionState, EvidenceContract


class SourceMutationEvent:
    def __init__(self, contract_id: str, new_state: ContradictionState, trigger: str):
        self.contract_id = contract_id
        self.new_state = new_state
        self.trigger = trigger


class InvalidationCascadeResult:
    def __init__(self):
        self.invalidated_contracts: set[str] = set()
        self.recalibrated_contracts: set[str] = set()
        self.failed_transitions: list[str] = []


class EvidenceGraph:
    """
    A minimal topological representation of epistemic dependencies.
    In the full runtime, this interfaces with the core HVL StructuralGraph.
    """

    def __init__(self):
        # Maps contract_id -> EvidenceContract
        self._nodes: dict[str, EvidenceContract] = {}
        # Maps upstream_contract_id -> List[downstream_contract_ids]
        self._downstream_edges: dict[str, list[str]] = {}

    def add_contract(self, contract: EvidenceContract):
        self._nodes[contract.contract_id] = contract
        # Register in downstream edges for all its dependencies
        for upstream_id in contract.invalidation_dependencies.upstream_contract_ids:
            if upstream_id not in self._downstream_edges:
                self._downstream_edges[upstream_id] = []
            self._downstream_edges[upstream_id].append(contract.contract_id)

    def get_contract(self, contract_id: str) -> EvidenceContract:
        return self._nodes.get(contract_id)

    def get_downstream(self, contract_id: str) -> list[EvidenceContract]:
        downstream_ids = self._downstream_edges.get(contract_id, [])
        return [self._nodes[did] for did in downstream_ids if did in self._nodes]

    def update_contract_state(self, contract_id: str, new_state: ContradictionState):
        if contract_id in self._nodes:
            old_contract = self._nodes[contract_id]

            temp_validity = old_contract.temporal_validity
            if new_state in {ContradictionState.INVALIDATED, ContradictionState.RETRACTED}:
                import datetime as dt

                from geneforgelang.semantic.evidence.contract import TemporalValidity

                now = dt.datetime.now()
                v_from = temp_validity.valid_from
                if v_from > now:
                    now = v_from
                temp_validity = TemporalValidity(
                    valid_from=v_from,
                    valid_until=now,
                    stability_expectation=temp_validity.stability_expectation,
                    decay_model=temp_validity.decay_model,
                )

            # In a truly immutable functional system, we replace the node.
            # Here we hack it by modifying __dict__ for prototype propagation,
            # or creating a deep copy. We will create a fresh instance.
            new_contract = EvidenceContract(
                contract_id=old_contract.contract_id,
                claim=old_contract.claim,
                scale_anchor=old_contract.scale_anchor,
                observability=old_contract.observability,
                compressibility=old_contract.compressibility,
                temporal_validity=temp_validity,
                contradiction_state=new_state,
                uncertainty=old_contract.uncertainty,
                provenance=old_contract.provenance,
                invalidation_dependencies=old_contract.invalidation_dependencies,
            )
            self._nodes[contract_id] = new_contract


class EvidenceInvalidationBridge:
    """
    Propagates causal mutations through the epistemic graph.
    """

    def __init__(self, graph: EvidenceGraph):
        self.graph = graph

    def propagate_mutation(self, event: SourceMutationEvent) -> InvalidationCascadeResult:
        result = InvalidationCascadeResult()

        # 1. Mutate the source node if legal
        source_contract = self.graph.get_contract(event.contract_id)
        if not source_contract:
            result.failed_transitions.append(f"Source {event.contract_id} not found.")
            return result

        if not ContractStateTransitionMatrix.is_valid_transition(
            source_contract.contradiction_state, event.new_state, event.trigger
        ):
            result.failed_transitions.append(
                f"Illegal transition for {event.contract_id}: {source_contract.contradiction_state.name} -> {event.new_state.name}"
            )
            return result

        self.graph.update_contract_state(event.contract_id, event.new_state)
        result.recalibrated_contracts.add(event.contract_id)

        # 2. Propagate cascade via BFS
        queue = self.graph.get_downstream(event.contract_id)

        while queue:
            current = queue.pop(0)

            # If the upstream died (INVALIDATED or RETRACTED), dependent contracts default to INVALIDATED
            # unless they have alternative active provenance (handled by ConflictResolver in Phase 5).
            if current.contradiction_state not in {ContradictionState.INVALIDATED, ContradictionState.RETRACTED}:
                if ContractStateTransitionMatrix.is_valid_transition(
                    current.contradiction_state, ContradictionState.INVALIDATED, "invalidation_propagation"
                ):
                    self.graph.update_contract_state(current.contract_id, ContradictionState.INVALIDATED)
                    result.invalidated_contracts.add(current.contract_id)
                    result.recalibrated_contracts.add(current.contract_id)

                    # Cascade further downstream
                    queue.extend(self.graph.get_downstream(current.contract_id))
                else:
                    result.failed_transitions.append(
                        f"Downstream transition failed for {current.contract_id} during cascade."
                    )

        return result
