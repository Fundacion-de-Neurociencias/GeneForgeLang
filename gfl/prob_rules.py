# gfl/prob_rules.py
"""
Probabilistic rule engine for GeneForgeLang ASTs.
Each rule has a likelihood-ratio (LR).  Posterior confidence is computed
with Bayes' log-odds update.
"""
from __future__ import annotations
import math
from typing import Callable, Dict, Any, List

class ProbRule:
    def __init__(self, name: str, lr: float,
                 condition: Callable[[Dict[str, Any]], bool]):
        self.name = name
        self.lr = lr
        self.condition = condition          # function(node_dict) -> bool

    def applies(self, node: Dict[str, Any]) -> bool:
        return self.condition(node)

class ProbReasoner:
    def __init__(self, rules: List[ProbRule], prior: float = 0.5):
        self.rules = rules
        self.prior = prior                  # 0–1

    def posterior(self, ast_dict: Dict[str, Any]) -> Dict[str, Any]:
        log_odds = math.log(self.prior / (1 - self.prior))
        fired: list[str] = []
        for node in ast_dict["children"]:
            for rule in self.rules:
                if rule.applies(node):
                    log_odds += math.log(rule.lr)
                    fired.append(rule.name)
        post = 1 / (1 + math.exp(-log_odds))
        return {"confidence": round(post, 2),
                "fired_rules": fired or None}

# ---------- default demo rules ------------------------------------------
def default_rules() -> List[ProbRule]:
    return [
        # Vector tropism matches target tissue → LR 3
        ProbRule("vector_tropism_match", 3.0,
                 lambda n: n["type"] == "vector"
                 and "tropism=retina" in n["attrs"]["val"]),
        # Governance value not in core list → LR 0.5 (penalty)
        ProbRule("non_equity_governance", 0.5,
                 lambda n: n["type"] == "governance"
                 and not any(k in n["attrs"]["val"] for k in
                             ("equity", "transparency", "stewardship"))),
        # High off-target risk (>0.6) → LR 0.4
        ProbRule("high_offtarget", 0.4,
                 lambda n: n["type"] == "risk"
                 and float(n["attrs"]["val"].split(':')[1]) > 0.6),
    ]
