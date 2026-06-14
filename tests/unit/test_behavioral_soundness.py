from __future__ import annotations

from typing import Any

import pytest
from geneforgelang.core.api import parse
from geneforgelang.governance.equivalence_classes import (
    EQUIVALENCE_CLASSES,
    NOISE_MUTATIONS,
    SIGNAL_PAIRS,
)
from geneforgelang.governance.semantic_projection import canonical_hash, canonical_project


def _materialize(value: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, str):
        return parse(value, use_grammar=False)
    return value


@pytest.mark.parametrize("equivalence_class", EQUIVALENCE_CLASSES, ids=lambda item: item.name)
def test_canonicalization_idempotence(equivalence_class):
    for member in equivalence_class.members:
        raw_ast = _materialize(member)

        canon_once = canonical_project(raw_ast)
        canon_twice = canonical_project(canon_once)

        assert canon_once == canon_twice
        assert canonical_hash(canon_once) == canonical_hash(canon_twice)


@pytest.mark.parametrize("equivalence_class", EQUIVALENCE_CLASSES, ids=lambda item: item.name)
def test_semantic_equivalence_classes_collapse_to_same_snapshot(equivalence_class):
    hashes = {canonical_hash(_materialize(member)) for member in equivalence_class.members}

    assert len(hashes) == 1


def test_noise_resistance_for_non_semantic_parser_artifacts():
    baseline, noisy = NOISE_MUTATIONS

    assert canonical_hash(baseline) == canonical_hash(noisy)


@pytest.mark.parametrize("signal_pair", SIGNAL_PAIRS, ids=lambda item: item.name)
def test_signal_sensitivity_for_semantic_mutations(signal_pair):
    baseline = _materialize(signal_pair.baseline)
    mutated = _materialize(signal_pair.mutated)

    assert canonical_hash(baseline) != canonical_hash(mutated)
