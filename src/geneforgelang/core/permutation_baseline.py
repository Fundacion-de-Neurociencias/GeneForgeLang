"""Permutation Baseline Gate for Bio-Foundation Model Sequence Signal Auditing.

Grounded in the Phylo sequence-vs-shuffled benchmark (Xinming Tu & Leo Chen, Nov 2026):
Evaluates whether a generative language or protein model possesses genuine evolutionary
sequence knowledge (as opposed to literature memorization or compositional priors)
by comparing next-residue / continuation accuracy on a native biological sequence
against a composition- or 2-mer-preserving shuffled copy of the same sequence.
"""

from __future__ import annotations

import hashlib
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from geneforgelang.core.gftypes import (
    PermutationControlMode,
    SequencePermutationBaselineContract,
)


def _eulerian_2mer_shuffle(sequence: str, rng: random.Random) -> str:
    """Altschul-Erickson (1985) exact 2-mer preserving Eulerian trail shuffle.

    Preserves the exact first character, last character, and every dinucleotide
    or dipeptide transition count of the input sequence.
    """
    n = len(sequence)
    if n < 4:
        chars = list(sequence)
        rng.shuffle(chars)
        return "".join(chars)

    start_char = sequence[0]
    end_char = sequence[-1]

    # Build edge lists per vertex
    edges_by_vertex: dict[str, list[str]] = defaultdict(list)
    for i in range(n - 1):
        edges_by_vertex[sequence[i]].append(sequence[i + 1])

    vertices_with_out = [v for v in edges_by_vertex if v != end_char]

    # Sample a random spanning tree of last-edges rooted at end_char
    last_edge: dict[str, str] = {}
    for _ in range(1000):
        candidate_last: dict[str, str] = {}
        for v in vertices_with_out:
            candidate_last[v] = rng.choice(edges_by_vertex[v])

        # Verify no cycle exists and every vertex reaches end_char
        valid_tree = True
        for v in vertices_with_out:
            curr = v
            visited: set[str] = set()
            while curr != end_char:
                if curr in visited or curr not in candidate_last:
                    valid_tree = False
                    break
                visited.add(curr)
                curr = candidate_last[curr]
            if not valid_tree:
                break

        if valid_tree:
            last_edge = candidate_last
            break

    if not last_edge:
        # Fallback to uniform shuffle if graph structure cannot yield a tree within budget
        chars = list(sequence)
        rng.shuffle(chars)
        return "".join(chars)

    # Shuffle remaining outgoing edges per vertex, keeping last_edge at index -1
    ordered_edges: dict[str, list[str]] = {}
    for v, targets in edges_by_vertex.items():
        pool = list(targets)
        if v in last_edge:
            pool.remove(last_edge[v])
            rng.shuffle(pool)
            pool.append(last_edge[v])
        else:
            rng.shuffle(pool)
        ordered_edges[v] = pool

    # Walk Eulerian trail
    out = [start_char]
    curr = start_char
    edge_idx: dict[str, int] = defaultdict(int)
    for _ in range(n - 1):
        idx = edge_idx[curr]
        nxt = ordered_edges[curr][idx]
        edge_idx[curr] = idx + 1
        out.append(nxt)
        curr = nxt

    return "".join(out)


def deterministic_shuffle(
    sequence: str,
    mode: PermutationControlMode = PermutationControlMode.UNIFORM_SHUFFLE,
    seed: int = 42,
) -> str:
    """Deterministically permute a biological sequence according to the control mode."""
    clean = sequence.strip().upper()
    if len(clean) <= 1:
        return clean

    rng = random.Random(seed)  # nosec B311 - deterministic scientific permutation control

    if mode in (
        PermutationControlMode.DINUCLEOTIDE_SHUFFLE,
        PermutationControlMode.DIPEPTIDE_SHUFFLE,
    ):
        return _eulerian_2mer_shuffle(clean, rng)

    chars = list(clean)
    rng.shuffle(chars)
    return "".join(chars)


@dataclass
class PermutationAuditResult:
    """Result of evaluating a model's native vs. shuffled sequence continuation gap."""

    contract_id: str
    model_id: str
    native_accuracy: float
    shuffled_accuracy: float
    permutation_gap: float
    min_required_gap: float
    passes_gate: bool
    evidence_status: str
    shuffled_prefix: str
    verification_hash: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "contract_id": self.contract_id,
            "model_id": self.model_id,
            "native_accuracy": self.native_accuracy,
            "shuffled_accuracy": self.shuffled_accuracy,
            "permutation_gap": self.permutation_gap,
            "min_required_gap": self.min_required_gap,
            "passes_gate": self.passes_gate,
            "evidence_status": self.evidence_status,
            "shuffled_prefix": self.shuffled_prefix,
            "verification_hash": self.verification_hash,
            "metadata": dict(self.metadata),
        }


class PermutationBaselineAuditor:
    """Deterministic auditor measuring sequence-level signal above shuffled controls."""

    @staticmethod
    def compute_positional_accuracy(predicted: str, target: str) -> float:
        """Compute exact positional residue/nucleotide match accuracy over target length."""
        clean_pred = predicted.strip().upper()
        clean_target = target.strip().upper()
        if not clean_target:
            return 0.0

        matches = sum(1 for i, ch in enumerate(clean_target) if i < len(clean_pred) and clean_pred[i] == ch)
        return matches / len(clean_target)

    @classmethod
    def audit_predictions(
        cls,
        contract: SequencePermutationBaselineContract,
        native_prediction: str,
        shuffled_prediction: str,
    ) -> PermutationAuditResult:
        """Evaluate native vs. shuffled predictions and enforce the permutation gap gate."""
        shuffled_prefix = deterministic_shuffle(
            contract.reference_prefix,
            mode=contract.control_mode,
            seed=contract.seed,
        )

        native_acc = cls.compute_positional_accuracy(native_prediction, contract.target_suffix)
        shuffled_acc = cls.compute_positional_accuracy(shuffled_prediction, contract.target_suffix)
        gap = native_acc - shuffled_acc
        passes = gap >= contract.min_permutation_gap

        evidence_status = "PERMUTATION_CONTROL_VERIFIED" if passes else "INSUFFICIENT_SEQUENCE_SIGNAL"

        payload = f"{contract.contract_id}:{contract.model_id}:{native_acc:.6f}:{shuffled_acc:.6f}:{gap:.6f}:{passes}"
        verification_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        return PermutationAuditResult(
            contract_id=contract.contract_id,
            model_id=contract.model_id or "unspecified_model",
            native_accuracy=round(native_acc, 6),
            shuffled_accuracy=round(shuffled_acc, 6),
            permutation_gap=round(gap, 6),
            min_required_gap=contract.min_permutation_gap,
            passes_gate=passes,
            evidence_status=evidence_status,
            shuffled_prefix=shuffled_prefix,
            verification_hash=verification_hash,
            metadata={
                "control_mode": str(contract.control_mode),
                "sequence_type": contract.sequence_type,
                "seed": contract.seed,
            },
        )
