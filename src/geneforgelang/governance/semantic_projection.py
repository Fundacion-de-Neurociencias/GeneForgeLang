from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

JsonLike = dict[str, Any] | list[Any] | str | int | float | bool | None


@dataclass(frozen=True)
class ProjectionPolicy:
    ignored_keys: frozenset[str]
    case_insensitive_value_keys: frozenset[str]
    unordered_list_keys: frozenset[str]


DEFAULT_POLICY = ProjectionPolicy(
    ignored_keys=frozenset(
        {
            "__file__",
            "__line__",
            "__parser__",
            "__trace__",
            "_meta",
            "metadata",
            "normalization_path",
            "parser_fallback",
            "source_loc",
            "source_location",
            "span",
        }
    ),
    case_insensitive_value_keys=frozenset(
        {
            "entity",
            "gene",
            "model",
            "target",
            "target_gene",
            "tool",
            "type",
        }
    ),
    unordered_list_keys=frozenset(
        {
            "annotations",
            "constraints",
            "evidence",
            "params",
            "tags",
        }
    ),
)


class SemanticProjection:
    """Canonical semantic projection used for behavioral soundness checks.

    The projection intentionally separates observable semantic content from
    incidental parser shape. Hashes must be computed from this projection, never
    from raw AST serialization.
    """

    def __init__(self, policy: ProjectionPolicy = DEFAULT_POLICY) -> None:
        self.policy = policy

    def project(self, value: Any, *, key_context: str | None = None) -> JsonLike:
        if key_context == "interacts_with":
            value = _normalize_interaction_sugar(value)
        elif key_context in {"effect", "effects"}:
            value = _normalize_effect_sugar(value)
        if isinstance(value, dict):
            return self._project_dict(value)
        if isinstance(value, list):
            projected = [self.project(item, key_context=key_context) for item in value]
            if key_context in self.policy.unordered_list_keys:
                return sorted(projected, key=_canonical_json)
            return projected
        if isinstance(value, tuple):
            return self.project(list(value), key_context=key_context)
        if isinstance(value, str):
            normalized = " ".join(value.strip().split())
            if key_context in self.policy.case_insensitive_value_keys:
                return normalized.lower()
            return normalized
        if isinstance(value, (int, float, bool)) or value is None:
            return value
        return str(value)

    def canonical_hash(self, value: Any) -> str:
        projected = self.project(value)
        return hashlib.sha256(_canonical_json(projected).encode("utf-8")).hexdigest()

    def _project_dict(self, value: dict[str, Any]) -> dict[str, JsonLike]:
        projected: dict[str, JsonLike] = {}
        for raw_key, raw_value in value.items():
            key = raw_key.strip().lower()
            if key in self.policy.ignored_keys:
                continue
            projected[key] = self.project(raw_value, key_context=key)
        return {key: projected[key] for key in sorted(projected)}


def canonical_project(ast: Any) -> JsonLike:
    return SemanticProjection().project(ast)


def canonical_hash(ast: Any) -> str:
    return SemanticProjection().canonical_hash(ast)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _normalize_interaction_sugar(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    parts = value.strip().split(maxsplit=1)
    if len(parts) == 2:
        return {"role": parts[0], "target": parts[1]}
    return {"role": "interactor", "target": value.strip()}


def _normalize_effect_sugar(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    if "(" not in stripped:
        return value
    kind, rest = stripped.split("(", 1)
    return {"type": kind.strip(), "target": rest.rsplit(")", 1)[0].strip()}
