import re
from typing import Any, Dict, List

class GFLParseError(Exception): pass

class GFLNode:
    def __init__(self, type_: str, attrs: Dict[str, Any] | None = None):
        self.type  = type_
        self.attrs = attrs or {}
        self.children: List["GFLNode"] = []

    def to_dict(self):
        return {"type": self.type, "attrs": self.attrs,
                "children": [c.to_dict() for c in self.children]}

    def __repr__(self):
        import json; return json.dumps(self.to_dict(), indent=2)

class GFLParser:
    def __init__(self):
        self.rx = {
            "edit":     re.compile(r"^edit\(([^)]+)\)$"),
            "target":   re.compile(r"^target\(([^:]+):([^)]+)\)$"),
            "effect":   re.compile(r"^effect\(([^:]+):([^)]+)\)$"),
            "pathway":  re.compile(r"^pathway\(([^:]+):([^)]+)\)$"),
            "link":     re.compile(r"^link\(([^-]+)->([^)]+)\)$"),
            "simulate": re.compile(r"^simulate\(([^)]+)\)$")
        }

    def _parse_line(self, line: str):
        for t, r in self.rx.items():
            m = r.match(line.strip())
            if m:
                if t in ("target", "effect", "pathway"):
                    return GFLNode(t, {"key": m.group(1), "val": m.group(2)})
                if t == "link":
                    return GFLNode(t, {"from": m.group(1), "to": m.group(2)})
                return GFLNode(t, {"val": m.group(1)})
        raise GFLParseError(f"Syntax error: {line}")

    def parse(self, text: str):
        root = GFLNode("program")
        for ln in text.strip().splitlines():
            if ln.strip():
                root.children.append(self._parse_line(ln))
        return root
