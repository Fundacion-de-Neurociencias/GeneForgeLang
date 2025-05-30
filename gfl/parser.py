"""GFL parser  — now supports comma‑separated multi‑attributes in one line.
Any statement of the form  name(key:val, key2=val2, singleval)  is converted
into a GFLNode whose attrs dict may contain >1 keys.
"""
import re
from typing import Dict, Any, List

class GFLParseError(Exception):
    pass

class GFLNode:
    def __init__(self, type_: str, attrs: Dict[str, Any] | None = None):
        self.type  = type_
        self.attrs = attrs or {}
        self.children: List["GFLNode"] = []

    def to_dict(self):
        return {
            "type": self.type,
            "attrs": self.attrs,
            "children": [c.to_dict() for c in self.children],
        }

    def __repr__(self):
        import json; return json.dumps(self.to_dict(), indent=2)

class GFLParser:
    """Single‑regex parser with flexible attribute splitting."""

    _LINK_RX = re.compile(r"^link\(([^-]+)->([^)]+)\)$")
    _GEN_RX  = re.compile(r"^(\w+)\((.*)\)$")

    def _kvdict(self, body: str) -> Dict[str, Any]:
        """Split comma‑separated items into a dict.
        Accepts  key:val  or  key=val  or lonevalue  (stored as {'value':...})."""
        if not body.strip():
            return {}
        items = [p.strip() for p in body.split(',') if p.strip()]
        # single bare value
        if len(items) == 1 and all(c not in items[0] for c in (':','=')):
            return {"value": items[0]}
        out: Dict[str, Any] = {}
        for it in items:
            if ':' in it:
                k, v = it.split(':', 1)
            elif '=' in it:
                k, v = it.split('=', 1)
            else:  # bare value as fall‑back
                k, v = "value", it
            out[k.strip()] = v.strip()
        return out

    # ------------------------------------------------------------------
    def _parse_line(self, line: str):
        line = line.strip()
        if not line: return None
        m_link = self._LINK_RX.match(line)
        if m_link:
            return GFLNode("link", {"from": m_link.group(1), "to": m_link.group(2)})
        m_gen = self._GEN_RX.match(line)
        if m_gen:
            typ, body = m_gen.group(1), m_gen.group(2)
            return GFLNode(typ, self._kvdict(body))
        raise GFLParseError(f"Syntax error: {line}")

    # ------------------------------------------------------------------
    def parse(self, text: str):
        root = GFLNode("program")
        for raw in text.strip().splitlines():
            node = self._parse_line(raw)
            if node: root.children.append(node)
        return root
