from __future__ import annotations
import math
from typing import Callable, Dict, Any, List

class ProbRule:
    def __init__(self, name: str, lr: float,
                 condition: Callable[[Dict[str, Any]], bool]):
        self.name = name; self.lr = lr; self.condition = condition
    def applies(self, node: Dict[str, Any]) -> bool: return self.condition(node)

class ProbReasoner:
    def __init__(self, rules: List[ProbRule], prior: float = 0.5):
        self.rules = rules; self.prior = prior
    def posterior(self, ast: Dict[str, Any]) -> Dict[str, Any]:
        log_odds = math.log(self.prior / (1 - self.prior)); fired=[]
        for n in ast["children"]:
            for r in self.rules:
                if r.applies(n): log_odds += math.log(r.lr); fired.append(r.name)
        post = 1 / (1 + math.exp(-log_odds))
        return {"confidence": round(post, 2), "fired_rules": fired or None}

def default_rules() -> List[ProbRule]:
    return [
        ProbRule("vector_tropism_match", 3.0,
                 lambda n: n["type"]=="vector" and "tropism=retina" in n["attrs"]["val"]),
        ProbRule("non_equity_governance", 0.5,
                 lambda n: n["type"]=="governance" and
                           not any(k in n["attrs"]["val"] for k in ("equity","transparency","stewardship"))),
        ProbRule("high_offtarget", 0.4,
                 lambda n: n["type"]=="risk" and
                           float(n["attrs"]["val"].split(':')[1]) > 0.6),
        # NEW: repeat interruption boosts odds (LR 4)
        ProbRule("repeat_interruption", 4.0,
                 lambda n: n["type"]=="repeat_edit")
    ]
