"""Public API for GeneForgeLang (GFL).

This module exposes a small, stable interface intended for consumption by
third-party applications. Internals (lexer, parser variants, demos) may evolve
without breaking this layer.
"""

from __future__ import annotations

from typing import Any, Dict, List

from gfl import parser as _parser
from gfl.inference_engine import InferenceEngine as _InferenceEngine
from gfl.prob_rules import default_rules
from gfl.semantic_validator import validate as _validate


def parse(text: str) -> Dict[str, Any]:
    """Parse GFL source (YAML-style) into a Python dict AST.

    Current canonical parser expects a YAML-like DSL. This may be extended with
    grammar-based parsing in future versions, but the returned AST contract will
    remain stable.
    """
    return _parser.parse_gfl(text)


def validate(ast: Dict[str, Any]) -> List[str]:
    """Return a list of semantic errors (empty if valid)."""
    return _validate(ast)


def infer(model, ast: Dict[str, Any]) -> Dict[str, Any]:
    """Run probabilistic post-processing with a provided model.

    model must expose predict(features: Dict[str, Any]) -> Dict[str, Any].
    """
    engine = _InferenceEngine(model)
    # default_rules are wired in the engine; this import exposes them for callers
    _ = default_rules  # noqa: F401 (documented side-channel)
    return engine.predict_effect(ast)


__all__ = ["parse", "validate", "infer"]
