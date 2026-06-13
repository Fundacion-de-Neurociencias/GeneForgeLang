from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any


class ProteinEvidenceSyntaxError(ValueError):
    """Raised when protein evidence extension syntax is invalid."""


_CALL_PATTERN = re.compile(
    r"""
    (?P<name>[A-Z_][A-Z0-9_]*)      # extension construct
    \s*\(\s*
    (?P<arg>
        "(?:[^"\\]|\\.)*"          # quoted string
        |
        '(?:[^'\\]|\\.)*'          # quoted string
        |
        [+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?  # number
    )
    \s*\)
    """,
    re.VERBOSE,
)

_ALLOWED_CONSTRUCTS = {
    "PROTEIN",
    "SEQUENCE",
    "EMBEDDING_REF",
    "MODEL_STRUCTURE_CONFIDENCE",
    "EMBEDDING_SCORE",
}


@dataclass(frozen=True)
class ProteinEvidenceCall:
    name: str
    argument: str | float


def parse_protein_evidence(source: str) -> list[ProteinEvidenceCall]:
    """Parse protein evidence extension calls without invoking core semantics."""

    calls: list[ProteinEvidenceCall] = []
    consumed_spans: list[tuple[int, int]] = []

    for match in _CALL_PATTERN.finditer(source):
        name = match.group("name")
        if name not in _ALLOWED_CONSTRUCTS:
            raise ProteinEvidenceSyntaxError(f"Unsupported protein evidence construct: {name}")

        argument = _coerce_argument(name, match.group("arg"))
        calls.append(ProteinEvidenceCall(name=name, argument=argument))
        consumed_spans.append(match.span())

    remainder = _remove_spans(source, consumed_spans).strip()
    if remainder:
        raise ProteinEvidenceSyntaxError(f"Invalid protein evidence syntax: {remainder}")
    if not calls:
        raise ProteinEvidenceSyntaxError("No protein evidence constructs found")

    return calls


def _coerce_argument(name: str, raw: str) -> str | float:
    if raw.startswith(('"', "'")):
        value = bytes(raw[1:-1], "utf-8").decode("unicode_escape")
        if name in {"MODEL_STRUCTURE_CONFIDENCE", "EMBEDDING_SCORE"}:
            raise ProteinEvidenceSyntaxError(f"{name} expects a numeric argument")
        return value

    if name not in {"MODEL_STRUCTURE_CONFIDENCE", "EMBEDDING_SCORE"}:
        raise ProteinEvidenceSyntaxError(f"{name} expects a string argument")
    value = float(raw)
    if not 0.0 <= value <= 1.0:
        raise ProteinEvidenceSyntaxError(f"{name} must be between 0.0 and 1.0")
    return value


def _remove_spans(source: str, spans: list[tuple[int, int]]) -> str:
    chars = list(source)
    for start, end in spans:
        for index in range(start, end):
            chars[index] = " "
    return "".join(chars).replace(",", " ").replace("\n", " ")
