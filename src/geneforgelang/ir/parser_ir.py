from __future__ import annotations

from typing import List, Tuple

from geneforgelang.ir.instruction import (
    Delete,
    Insert,
    Instruction,
    Invert,
    Substitute,
)
from geneforgelang.ir.state import BiologicalState, Entity, Relation


class ParseError(Exception):
    pass


def _parse_attrs(parts: List[str]) -> dict:
    attrs = {}
    for part in parts:
        if "=" in part:
            key, val = part.split("=", 1)
            low = val.lower()
            if low == "true":
                val = True
            elif low == "false":
                val = False
            else:
                try:
                    val = int(val)
                except ValueError:
                    try:
                        val = float(val)
                    except ValueError:
                        pass
            attrs[key] = val
    return attrs


def parse_text(text: str) -> Tuple[BiologicalState, List[Instruction]]:
    state = BiologicalState()
    instructions: List[Instruction] = []

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if not parts:
            continue

        cmd = parts[0].lower()

        if cmd == "entity":
            if len(parts) < 3:
                raise ParseError(f"Invalid entity line: {line}")
            eid = parts[1]
            etype = parts[2]
            attrs = _parse_attrs(parts[3:])
            state.add_entity(Entity(id=eid, type=etype, attrs=attrs))

        elif cmd == "relation":
            if len(parts) < 4:
                raise ParseError(f"Invalid relation line: {line}")
            source = parts[1]
            rel_type = parts[2]
            target = parts[3]
            attrs = _parse_attrs(parts[4:])
            state.add_relation(
                Relation(source=source, target=target, type=rel_type, metadata=attrs)
            )

        elif cmd == "substitute":
            if len(parts) < 5:
                raise ParseError(f"Invalid substitute line: {line}")
            instructions.append(
                Substitute(
                    gene_id=parts[1],
                    position=int(parts[2]),
                    ref=parts[3],
                    alt=parts[4],
                )
            )

        elif cmd == "insert":
            if len(parts) < 4:
                raise ParseError(f"Invalid insert line: {line}")
            instructions.append(
                Insert(
                    gene_id=parts[1],
                    position=int(parts[2]),
                    sequence=parts[3],
                )
            )

        elif cmd == "delete":
            if len(parts) < 4:
                raise ParseError(f"Invalid delete line: {line}")
            instructions.append(
                Delete(
                    gene_id=parts[1],
                    start=int(parts[2]),
                    end=int(parts[3]),
                )
            )

        elif cmd == "invert":
            if len(parts) < 4:
                raise ParseError(f"Invalid invert line: {line}")
            instructions.append(
                Invert(
                    gene_id=parts[1],
                    start=int(parts[2]),
                    end=int(parts[3]),
                )
            )

        else:
            raise ParseError(f"Unknown command: {cmd}")

    return state, instructions
