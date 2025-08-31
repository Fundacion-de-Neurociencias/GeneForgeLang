axioms = set()
rules = []


def add_axiom(expr):
    axioms.add(expr)


def add_rule(premise, conclusion):
    rules.append((premise, conclusion))


def infer():
    new_inferences = True
    while new_inferences:
        new_inferences = False
        for premise, conclusion in rules:
            if premise in axioms and conclusion not in axioms:
                axioms.add(conclusion)
                new_inferences = True


def explain():
    print("=== 🔍 Axiomas conocidos ===")
    for ax in sorted(axioms):
        print(f"• {ax}")
    print("\n=== 📐 Reglas activas ===")
    for prem, concl in rules:
        print(f"• Si {prem} → entonces {concl}")
