# GeneForgeLang Extended Syntax (syntax.md)
# ------------------------------------------

# GENOMIC EDITING BLOCKS

ENZYME(name: string, type: ["Cas9", "Cas12a", "PrimeEditor", "BaseEditor", ...], species: string, variant: string, strand: ["+", "-"], pam: string, notes: string)
OLIGO(sequence: string, type: ["ssODN", "gRNA", "pegRNA", "crRNA", ...], length: int, mod: string, notes: string)
EDIT(type: ["Base", "Prime", "Knock-in", "Knock-out", "Exon Skip", "Insertion", "Deletion", ...], target: string, pos: int|list, ref: string, alt: string, exons: list, introns: list, splice: bool, efficiency: float, byproduct: string, notes: string)
DELIVERY(vehicle: ["LNP", "AAV", "Electroporation", ...], payload: string, cells: list, tissue: string, method: string, dose: float, units: string, schedule: string, notes: string)
CONTEXT(organism: string, tissue: string, cell: string, condition: string, env: string, notes: string)

# MOLECULAR INTERACTIONS

INTERACT(partner1: string, partner2: string, type: ["binding", "cleavage", "repair", "methylation", ...], strength: float, context: string, notes: string)
POSTTRANS(type: ["Splicing", "ExonSkip", "PTM", ...], affected: list, method: string, notes: string)

# LOGIC AND SIMULATION

IF(condition) { ... } ELSE { ... }
LOOP(n) { ... }
SIMULATE(action: string, times: int, model: string, params: dict, notes: string)
BENCHMARK(ref_case: string, dataset: string, metric: string, notes: string)
TRACE(reasoning: string, result: string, confidence: float, path: list, notes: string)

# EXAMPLES

ENZYME(name="SpCas9", type="Cas9", species="Streptococcus pyogenes", variant="HiFi", strand="+", pam="NGG", notes="high-fidelity")
OLIGO(sequence="ACGTTGCAAGTT...", type="gRNA", length=20, mod="2'-O-methyl", notes="chemically stabilized")
EDIT(type="Base", target="C>T@123456", pos=123456, ref="C", alt="T", exons=[2,3], introns=[], splice=False, efficiency=0.82, byproduct="", notes="APOBEC-mediated")
DELIVERY(vehicle="LNP", payload="mRNA+gRNA", cells=["hepatocyte"], tissue="liver", method="IV", dose=1.5, units="mg/kg", schedule="1x", notes="standard protocol")
CONTEXT(organism="Homo sapiens", tissue="liver", cell="hepatocyte", condition="hypercholesterolemia", env="standard", notes="clinical trial")
INTERACT(partner1="gRNA", partner2="Cas9", type="binding", strength=0.95, context="nucleus", notes="RNP assembly")
POSTTRANS(type="ExonSkip", affected=[3], method="ASO", notes="therapeutic exon skipping")
IF(efficiency > 0.8) { APPROVED() } ELSE { OPTIMIZE() }
SIMULATE(action="EDIT", times=1000, model="GeneForgeSim-v2", params={"target":"C>T@123456"}, notes="in silico")
BENCHMARK(ref_case="edit_A", dataset="ClinVar", metric="precision", notes="comparison vs. published")
TRACE(reasoning="Selected Cas9 for NGG PAM, high activity in liver.", result="edit planned", confidence=0.92, path=["select_enzyme", "design_oligo", "plan_delivery"], notes="all parameters optimized")
