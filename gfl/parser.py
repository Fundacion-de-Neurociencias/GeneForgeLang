import re, json
from typing import Any, Dict, List
class GFLParseError(Exception): pass
class GFLNode:
    def __init__(self, t:str, attrs:Dict[str,Any]|None=None):
        self.type=t; self.attrs=attrs or {}; self.children:List["GFLNode"]=[]
    def to_dict(self): return {"type":self.type,"attrs":self.attrs,"children":[c.to_dict() for c in self.children]}
    def __repr__(self): return json.dumps(self.to_dict(),indent=2)

class GFLParser:
    _GEN = re.compile(r'^(\w+)\((.*)\)$')
    _LINK= re.compile(r'^link\(([^-]+)->([^)]+)\)$')
    def _split_attrs(self,s):
        if not s.strip(): return {}
        d={} ; parts=[p.strip() for p in s.split(',') if p.strip()]
        if len(parts)==1 and all(c not in parts[0] for c in ':='): return {"value":parts[0]}
        for p in parts:
            if ':' in p: k,v=p.split(':',1)
            elif '=' in p: k,v=p.split('=',1)
            else: k,v="value",p
            d[k.strip()]=v.strip()
        return d
    def _parse_line(self,l):
        l=l.strip();
        m=self._LINK.match(l)
        if m: return GFLNode('link',{'from':m.group(1),'to':m.group(2)})
        m=self._GEN.match(l)
        if m: return GFLNode(m.group(1),self._split_attrs(m.group(2)))
        if l: raise GFLParseError(f"Syntax error: {l}")
    def parse(self,text:str):
        root=GFLNode('program')
        for raw in text.strip().splitlines():
            n=self._parse_line(raw)
            if n: root.children.append(n)
        return root
