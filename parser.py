import re
import json

# Cargar gramática desde archivo JSON
with open("geneforge_grammar.json", "r", encoding="utf-8") as f:
    grammar = json.load(f)

# Compilar patrones
regex_prefix = re.compile(r"^([~:\^\*!])([drp]):")
regex_modules = re.compile(r"(Dom|Mot|TF|Ctrl|PTM)\(([^)]+)\)")
regex_logic_block = re.compile(r"Ctrl\{([^}]+)\}")
regex_ptm = re.compile(r"([A-Z])\*([A-Za-z]+)@(\d+)")
regex_compact_ptm = re.compile(r"\*([A-Za-z]+)([A-Z])@(\d+)")
regex_mut = re.compile(r"\[MUT:([A-Z])>([A-Z])@(\d+)]")
regex_del = re.compile(r"\[DEL:(\d+)-(\d+)]")
regex_ins = re.compile(r"\[INS:([A-Z]+)@(\d+)]")

def parse_geneforge_line(line):
    output = {
        "valid": False,
        "structure": None,
        "molecule": None,
        "modules": [],
        "ptms": [],
        "mutations": [],
        "insertions": [],
        "deletions": [],
        "logic": [],
        "errors": []
    }

    # Verificar prefijo estructural
    prefix_match = regex_prefix.match(line)
    if not prefix_match:
        output["errors"].append("❌ Prefijo estructural/molécula no válido.")
        return output

    structure_symbol, molecule_code = prefix_match.groups()
    output["structure"] = grammar["structures"].get(structure_symbol, "❓ Desconocido")
    output["molecule"] = grammar["molecules"].get(molecule_code, "❓ Desconocido")
    content = line[len(prefix_match.group(0)):]

    # Módulos funcionales
    modules_found = regex_modules.findall(content)
    output["modules"] = [{"type": m, "value": v} for m, v in modules_found]

    # Bloques lógicos Ctrl{...}
    logic_blocks = regex_logic_block.findall(content)
    output["logic"] = logic_blocks

    # PTMs estilo ProForma
    ptms1 = regex_ptm.findall(content)
    for aa, mod, pos in ptms1:
        output["ptms"].append({
            "notation": "ProForma",
            "residue": aa,
            "modification": mod,
            "position": int(pos)
        })

    # PTMs compactas estilo GeneForgeLang
    ptms2 = regex_compact_ptm.findall(content)
    for mod, aa, pos in ptms2:
        output["ptms"].append({
            "notation": "GeneForgeLang",
            "residue": aa,
            "modification": mod,
            "position": int(pos)
        })

    # Mutaciones
    mutations = regex_mut.findall(content)
    output["mutations"] = [{"from": f, "to": t, "position": int(pos)} for f, t, pos in mutations]

    # Inserciones
    insertions = regex_ins.findall(content)
    output["insertions"] = [{"sequence": s, "position": int(pos)} for s, pos in insertions]

    # Deleciones
    deletions = regex_del.findall(content)
    output["deletions"] = [{"start": int(a), "end": int(b)} for a, b in deletions]

    output["valid"] = True
    return output

# Modo CLI
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        line = sys.argv[1]
        result = parse_geneforge_line(line)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("⚠️  Introduce una frase GFL como argumento.")
