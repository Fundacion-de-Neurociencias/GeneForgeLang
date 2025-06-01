import re, json
from typing import Any, Dict, List

class GFLParseError(Exception):
    pass

class GFLNode:
    def __init__(self, type_: str, attrs: Dict[str, Any] | None = None):
        self.type = type_
        self.attrs = attrs or {}
        self.children: List["GFLNode"] = []

    def to_dict(self):
        return {
            "type": self.type,
            "attrs": self.attrs,
            "children": [c.to_dict() for c in self.children]
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)

class GFLParser:
    """Parser that combines multi-line statements based on balanced parentheses and strips BOM."""

    _LINK_RX = re.compile(r"^link\(([^-]+)->([^)]+)\)$")
    _GEN_RX  = re.compile(r"^(\w+)\((.*)\)$")

    def _split_attrs(self, body: str) -> Dict[str, Any]:
        if not body.strip():
            return {}
        # Split on commas not inside brackets
        items = [p.strip() for p in re.split(r',(?=(?:[^\[\]]*\[[^\[\]]*\])*[^\[\]]*$)', body) if p.strip()]
        if len(items) == 1 and all(c not in items[0] for c in (":","=")):
            return {"value": items[0]}
        out: Dict[str, Any] = {}
        for it in items:
            if ":" in it:
                k, v = it.split(":", 1)
            elif "=" in it:
                k, v = it.split("=", 1)
            else:
                k, v = "value", it
            out[k.strip()] = v.strip()
        return out

    def _parse_line(self, line: str):
        line = line.lstrip("\ufeff").strip()
        if not line:
            return None
        m_link = self._LINK_RX.match(line)
        if m_link:
            return GFLNode("link", {"from": m_link.group(1), "to": m_link.group(2)})
        m_gen = self._GEN_RX.match(line)
        if m_gen:
            typ, body = m_gen.group(1), m_gen.group(2)
            return GFLNode(typ, self._split_attrs(body))
        raise GFLParseError(f"Syntax error: {line}")

    def parse(self, text: str):
        root = GFLNode("program")
        buffer = ""
        depth = 0
        for raw in text.splitlines():
            line = raw.lstrip("\ufeff")
            depth += line.count("(") - line.count(")")
            buffer += " " + line.strip()
            if depth == 0 and buffer.strip():
                node = self._parse_line(buffer.strip())
                if node:
                    root.children.append(node)
                buffer = ""
        if depth != 0:
            raise GFLParseError("Unbalanced parentheses in GFL code.")
        return root
