"""Parser for protein evidence metadata references.

This parser is intentionally local to the extension and is not wired into the
GeneForgeLang compiler or semantic engine.
"""

from __future__ import annotations

import re
from typing import Any


_CALL_PATTERN = re.compile(
    r"""
    (?P<name>PROTEIN|SEQUENCE|EMBEDDING_REF|STRUCTURE_CONFIDENCE|PLAUSIBILITY_SCORE)
    \s*\(\s*
    (?P<arg>"[^"]*"|'[^']*'|[-+]?(?:\d+(?:\.\d*)?|\.\d+))
    \s*\)
    """,
    re.VERBOSE,
)

_FORBIDDEN_SEMANTIC_PATTERNS = (
    "causes",
    "causal",
    "infer",
    "inferred",
    "pathogenic effect",
    "pathogenicity",
    "rule synthesis",
    "semantic completion",
    "complete caus",
    "rewrite rule",
)


class ProteinEvidenceSyntaxError(ValueError):
    """Raised when protein evidence extension syntax is invalid."""


def parse_protein_evidence(source: str) -> list[dict[str, Any]]:
    """Parse protein evidence references into raw metadata nodes.

    The returned nodes are syntactic records only. They do not participate in
    the GeneForgeLang semantic lattice or inference semantics.
    """

    if not isinstance(source, str):
        raise TypeError("source must be a string")
    _reject_semantic_claims(source)

    nodes: list[dict[str, Any]] = []
    position = 0
    for match in _CALL_PATTERN.finditer(source):
        gap = source[position : match.start()]
        if gap.strip():
            raise ProteinEvidenceSyntaxError(f"Unsupported protein evidence syntax: {gap.strip()}")
        nodes.append(_parse_call(match.group("name"), match.group("arg")))
        position = match.end()

    tail = source[position:]
    if tail.strip():
        raise ProteinEvidenceSyntaxError(f"Unsupported protein evidence syntax: {tail.strip()}")
    if not nodes:
        raise ProteinEvidenceSyntaxError("No protein evidence references found")
    return nodes


def _parse_call(name: str, arg: str) -> dict[str, Any]:
    if name in {"PROTEIN", "SEQUENCE", "EMBEDDING_REF"}:
        if not _is_quoted(arg):
            raise ProteinEvidenceSyntaxError(f"{name} requires a quoted string argument")
        return {"kind": name, "value": _unquote(arg)}

    if name in {"STRUCTURE_CONFIDENCE", "PLAUSIBILITY_SCORE"}:
        if _is_quoted(arg):
            raise ProteinEvidenceSyntaxError(f"{name} requires a numeric argument")
        value = float(arg)
        if not 0.0 <= value <= 1.0:
            raise ProteinEvidenceSyntaxError(f"{name} must be between 0 and 1")
        return {"kind": name, "value": value}

    raise ProteinEvidenceSyntaxError(f"Unsupported construct: {name}")


def _reject_semantic_claims(source: str) -> None:
    lowered = source.lower()
    for pattern in _FORBIDDEN_SEMANTIC_PATTERNS:
        if pattern in lowered:
            raise ProteinEvidenceSyntaxError(
                "Protein evidence extension rejects causal claims and semantic completion"
            )


def _is_quoted(value: str) -> bool:
    return (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    )


def _unquote(value: str) -> str:
    return value[1:-1]
