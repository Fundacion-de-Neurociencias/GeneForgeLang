import re
import json

# Load grammar
with open("geneforge_grammar.json", "r") as f:
    grammar = json.load(f)

regex_prefix = re.compile(r"^([~:\^\*!])([drp]):")
regex_modules = re.compile(r"(Dom|Mot|TF|Ctrl|PTM)\(([^)]+)\)")
regex_ptm = re.compile(r"([A-Z])\*([A-Za-z]+)@(\d+)")
regex_compact_ptm = re.compile(r"\*([A-Za-z]+)([A-Z])@(\d+)")
regex_mut = re.compile(r"\[MUT:([A-Z])>([A-Z])@(\d+)]")

def parse_geneforge_line(line):
    output = {
        "valid": False,
        "structure": None,
        "molecule": None,
        "modules": [],
        "ptms": [],
        "mutations": [],
        "errors": []
    }

    prefix_match = regex_prefix.match(line)
    if not prefix_match:
        output["errors"].append("Invalid or missing structural/molecular prefix.")
        return output

    structure_symbol, molecule_code = prefix_match.groups()
    output["structure"] = grammar["structures"].get(structure_symbol)
    output["molecule"] = grammar["molecules"].get(molecule_code)

    modules_found = regex_modules.findall(line)
    output["modules"] = [{"type": m, "value": v} for m, v in modules_found]

    ptms_proforma = regex_ptm.findall(line)
    for r, t, pos in ptms_proforma:
        output["ptms"].append({
            "notation": "ProForma",
            "residue": r,
            "modification": t,
            "position": int(pos)
        })

    ptms_compact = regex_compact_ptm.findall(line)
    for t, r, pos in ptms_compact:
        output["ptms"].append({
            "notation": "GeneForgeLang",
            "residue": r,
            "modification": t,
            "position": int(pos)
        })

    mutations = regex_mut.findall(line)
    output["mutations"] = [{"from": f, "to": t, "position": int(pos)} for f, t, pos in mutations]

    output["valid"] = True
    return output

if __name__ == "__main__":
    import sys
    line = sys.argv[1] if len(sys.argv) > 1 else ""
    result = parse_geneforge_line(line)
    print(json.dumps(result, indent=2))