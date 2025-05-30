import re
from typing import Any, Dict, List

class GFLParseError(Exception): pass

class GFLNode:
    def __init__(self, type_: str, attrs: Dict[str, Any] | None = None):
        self.type  = type_
        self.attrs = attrs or {}
        self.children: List["GFLNode"] = []

    def to_dict(self): return {
        "type": self.type, "attrs": self.attrs,
        "children": [c.to_dict() for c in self.children]
    }

    def __repr__(self):
        import json; return json.dumps(self.to_dict(), indent=2)

class GFLParser:
    """Parser with Vector, Region, Governance, Risk and Repeat-Edit support."""
    def __init__(self):
        self.rx = {
            "edit":     re.compile(r"^edit\\(([^)]+)\\)$"),
            "target":   re.compile(r"^target\\(([^:]+):([^)]+)\\)$"),
            "effect":   re.compile(r"^effect\\(([^:]+):([^)]+)\\)$"),
            "pathway":  re.compile(r"^pathway\\(([^:]+):([^)]+)\\)$"),
            "link":     re.compile(r"^link\\(([^-]+)->([^)]+)\\)$"),
            "simulate": re.compile(r"^simulate\\(([^)]+)\\)$"),
            # extensions
            "vector":      re.compile(r"^vector\\((.+)\\)$"),
            "region":      re.compile(r"^region\\((.+)\\)$"),
            "governance":  re.compile(r"^governance\\((.+)\\)$"),
            "risk":        re.compile(r"^risk\\((.+)\\)$"),
            "repeat_edit": re.compile(r"^repeat_edit\\((.+)\\)$"),
        }

    def _parse_line(self, line: str):
        for typ, rx in self.rx.items():
            m = rx.match(line.strip())
            if not m: continue
            if typ in ("target", "effect", "pathway"):
                return GFLNode(typ, {"key": m.group(1), "val": m.group(2)})
            if typ == "link":
                return GFLNode(typ, {"from": m.group(1), "to": m.group(2)})
            return GFLNode(typ, {"val": m.group(1)})
        raise GFLParseError(f"Syntax error: {line}")

    def parse(self, text: str):
        root = GFLNode("program")
        for ln in text.strip().splitlines():
            if ln.strip():
                root.children.append(self._parse_line(ln))
        return root
