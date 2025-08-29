from __future__ import annotations
import math
from typing import Callable, Dict, Any, List


class ProbRule:
    """Simple likelihood-ratio rule used by the probabilistic reasoner."""

    def __init__(self, name: str, lr: float, condition: Callable[[Dict[str, Any]], bool]):
        self.name = name
        self.lr = lr
        self.condition = condition

    def applies(self, node: Dict[str, Any]) -> bool:
        return bool(self.condition(node))


class ProbReasoner:
    """Naive-Bayes style post-processing over an AST using LR rules."""

    def __init__(self, rules: List[ProbRule], prior: float = 0.5):
        self.rules = rules
        self.prior = prior

    def posterior(self, ast: Dict[str, Any]) -> Dict[str, Any]:
        log_odds = math.log(self.prior / (1 - self.prior))
        fired: List[str] = []
        for n in ast.get("children", []):
            for r in self.rules:
                try:
                    if r.applies(n):
                        log_odds += math.log(r.lr)
                        fired.append(r.name)
                except Exception:
                    # Guard against malformed nodes
                    continue
        post = 1 / (1 + math.exp(-log_odds))
        return {"confidence": round(post, 2), "fired_rules": fired or None}


def default_rules() -> List[ProbRule]:
    """Reference set of lightweight heuristic rules.

    These are intentionally simple and operate on a minimal AST shape:
    nodes with fields: {"type": str, "attrs": {"val": str}}.
    """
    return [
        ProbRule(
            "vector_tropism_match",
            3.0,
            lambda n: n.get("type") == "vector" and "tropism=retina" in str(n.get("attrs", {}).get("val", "")),
        ),
        ProbRule(
            "non_equity_governance",
            0.5,
            lambda n: n.get("type") == "governance"
            and not any(k in str(n.get("attrs", {}).get("val", "")) for k in ("equity", "transparency", "stewardship")),
        ),
        ProbRule(
            "high_offtarget",
            0.4,
            lambda n: n.get("type") == "risk"
            and _parse_float_after_colon(str(n.get("attrs", {}).get("val", "0:0"))) > 0.6,
        ),
        ProbRule("repeat_interruption", 4.0, lambda n: n.get("type") == "repeat_edit"),
    ]


def _parse_float_after_colon(val: str) -> float:
    try:
        return float(val.split(":")[1])
    except Exception:
        return 0.0


__all__ = ["ProbRule", "ProbReasoner", "default_rules"]

