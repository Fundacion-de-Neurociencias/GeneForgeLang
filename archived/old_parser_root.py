import json
import re

with open("geneforge_grammar.json", encoding="utf-8") as f:
    grammar = json.load(f)

# Compilar patrones
regex_prefix = re.compile(r"^([~:\^\*!])([a-z]+):")
regex_entity = re.compile(
    r"(DNA|RNA|mRNA|ncRNA|miRNA|Protein|Ribozyme|Enzyme|TF|RegElement|Virus|Plasmid):([^\s]+)(\{[^}]*\})?"
)
regex_mechanism = re.compile(r"(TRANSCRIBE|SPLICE|TRANSLATE|EDIT|INHIBIT)\(([^)]+)\)")
regex_logic_block = re.compile(r"Ctrl\{([^}]+)\}")
regex_ptm = re.compile(r"([A-Z])\*([A-Za-z]+)@(\d+)")
regex_compact_ptm = re.compile(r"\*([A-Za-z]+)([A-Z])@(\d+)")
regex_mut_prov = re.compile(r"\[MUT:(PAT|MAT|SOM|GER):([A-Z])>([A-Z])@(\d+)]")
regex_mut_simple = re.compile(r"\[MUT:([A-Z])>([A-Z])@(\d+)]")
regex_del = re.compile(r"\[DEL:(\d+)-(\d+)]")
regex_ins = re.compile(r"\[INS:([A-Z]+)@(\d+)]")
regex_edit = re.compile(r"EDIT:(Base|Prime|ARCUS)\(([^)]+)\)(\{[^}]+\})?")
regex_dose = re.compile(r"DOSE\((\d+)\):EDIT:(Base|Prime|ARCUS)\(([^)]+)\)(\{[^}]+\})?")
regex_deliv = re.compile(r"DELIV\(([^@)]+)@([^\)]+)\)")
regex_conditional = re.compile(r"if\s+(.+?)\s+then\s+(.+)")
regex_effect = re.compile(r"EFFECT\((↑|↓|→)([^@)]+)(?:@(\d+[hd]))?\)(?:\{([^}]*)\})?")
regex_prob = re.compile(r"PROB\(([^)]+)\)=([0-9.]+)")
regex_fit = re.compile(r"FITNESS\(([^)]+)\)=([+-]?[0-9.]+)")
regex_epi = re.compile(r"EPISTASIS\(([^)]+)\)\{([^}]*)\}")
regex_hypothesis = re.compile(r"HYPOTHESIS:\s*if\s*(.*?)\s*then\s*(.*)")
regex_simulate = re.compile(r"SIMULATE:\s*\{(.*?)\}")
regex_time = re.compile(r"TIME\(([^)]+)\):(.+)")
regex_pathway = re.compile(r"PATHWAY:\s*(.+)")
regex_macro = re.compile(r"MACRO:([A-Za-z_0-9]+)=\{(.+?)\}")
regex_use = re.compile(r"USE:([A-Za-z_0-9]+)")
regex_localized = re.compile(r"localized\(([^)]+)\)")


def parse_metadata_block(block):
    metadata = {}
    block = block.strip("{} ")
    for pair in block.split(","):
        if "=" in pair:
            key, val = pair.strip().split("=")
            metadata[key.strip()] = val.strip()
    return metadata


def parse_geneforge_line(line):
    output = {
        "valid": False,
        "structure": None,
        "molecule": None,
        "entities": [],
        "mechanisms": [],
        "ptms": [],
        "mutations": [],
        "insertions": [],
        "deletions": [],
        "edits": [],
        "doses": [],
        "delivery": None,
        "logic": [],
        "conditionals": [],
        "effects": [],
        "fitness": [],
        "probabilities": [],
        "epistasis": [],
        "hypotheses": [],
        "simulations": [],
        "timed_events": [],
        "pathways": [],
        "macros": [],
        "macro_calls": [],
        "localized": [],
        "errors": [],
    }

    prefix_match = regex_prefix.match(line)
    if not prefix_match:
        output["errors"].append("❌ Invalid structural/molecule prefix.")
        return output

    structure_symbol, molecule_code = prefix_match.groups()
    output["structure"] = grammar["structures"].get(structure_symbol, "❓ Unknown")
    output["molecule"] = grammar["molecules"].get(molecule_code, "❓ Unknown")
    content = line[len(prefix_match.group(0)) :]

    output["entities"] = [
        {"type": m, "target": t, "metadata": parse_metadata_block(md)} for m, t, md in regex_entity.findall(content)
    ]
    output["mechanisms"] = [{"type": mech, "target": tgt} for mech, tgt in regex_mechanism.findall(content)]
    output["logic"] = regex_logic_block.findall(content)

    for aa, mod, pos in regex_ptm.findall(content):
        output["ptms"].append(
            {
                "notation": "ProForma",
                "residue": aa,
                "modification": mod,
                "position": int(pos),
            }
        )
    for mod, aa, pos in regex_compact_ptm.findall(content):
        output["ptms"].append(
            {
                "notation": "GFL",
                "residue": aa,
                "modification": mod,
                "position": int(pos),
            }
        )

    for origin, f, t, pos in regex_mut_prov.findall(content):
        output["mutations"].append({"origin": origin, "from": f, "to": t, "position": int(pos)})
    for f, t, pos in regex_mut_simple.findall(content):
        output["mutations"].append({"from": f, "to": t, "position": int(pos)})

    output["insertions"] = [{"sequence": s, "position": int(pos)} for s, pos in regex_ins.findall(content)]
    output["deletions"] = [{"start": int(a), "end": int(b)} for a, b in regex_del.findall(content)]

    for kind, op, meta in regex_edit.findall(content):
        output["edits"].append(
            {
                "type": kind,
                "operation": op,
                "metadata": parse_metadata_block(meta) if meta else {},
            }
        )

    for n, kind, op, meta in regex_dose.findall(content):
        output["doses"].append(
            {
                "number": int(n),
                "edit": {
                    "type": kind,
                    "operation": op,
                    "metadata": parse_metadata_block(meta) if meta else {},
                },
            }
        )

    delivery = regex_deliv.search(content)
    if delivery:
        output["delivery"] = {"vector": delivery.group(1), "route": delivery.group(2)}

    for condition, action in regex_conditional.findall(content):
        output["conditionals"].append({"if": condition.strip(), "then": action.strip()})

    output["effects"] = [
        {
            "direction": d,
            "effect": e.strip(),
            "time": t.strip() if t else None,
            "metadata": parse_metadata_block(meta) if meta else None,
        }
        for d, e, t, meta in regex_effect.findall(content)
    ]

    output["fitness"] = [{"target": t, "value": float(v)} for t, v in regex_fit.findall(content)]
    output["probabilities"] = [{"event": ev, "value": float(p)} for ev, p in regex_prob.findall(content)]
    output["epistasis"] = [
        {"variants": v, "metadata": parse_metadata_block(meta)} for v, meta in regex_epi.findall(content)
    ]
    output["localized"] = regex_localized.findall(content)
    output["hypotheses"] = [{"if": i.strip(), "then": t.strip()} for i, t in regex_hypothesis.findall(content)]
    output["simulations"] = regex_simulate.findall(content)
    output["pathways"] = regex_pathway.findall(content)
    output["macros"] = [{"name": name, "body": body} for name, body in regex_macro.findall(content)]
    output["macro_calls"] = regex_use.findall(content)
    output["timed_events"] = [{"time": time, "event": evt.strip()} for time, evt in regex_time.findall(content)]

    output["valid"] = True
    return output


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        line = sys.argv[1]
        result = parse_geneforge_line(line)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("⚠️  Please provide a GFL line as input.")
