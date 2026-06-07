import json
from typing import Any

from .equivalence_classes import DEFAULT_POLICY, filter_non_semantic_annotations

JsonLike = dict[str, Any] | list[Any] | str | int | float | bool | None


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


class SemanticProjection:
    def __init__(self, policy=DEFAULT_POLICY):
        self.policy = policy

    def project(self, value: Any, *, key_context: str | None = None) -> JsonLike:
        if isinstance(value, dict):
            new_val = dict(value)
            filter_non_semantic_annotations(new_val)
            return self._project_dict(new_val)
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

    def _project_dict(self, value: dict[str, Any]) -> dict[str, JsonLike]:
        projected: dict[str, JsonLike] = {}
        for raw_key, raw_value in value.items():
            key = raw_key.strip().lower()
            if key in self.policy.ignored_keys:
                continue
            projected[key] = self.project(raw_value, key_context=key)
        return {key: projected[key] for key in sorted(projected)}


def project(ast: Any) -> JsonLike:
    """Canonical Semantic Projection mapping."""
    return SemanticProjection().project(ast)
