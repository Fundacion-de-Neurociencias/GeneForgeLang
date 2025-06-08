# GeneForgeLang Extended Syntax (v2)

## GENOMIC EDITING BLOCKS

- **ENZYME**: Describe the nuclease/protein used for editing.
  - Parameters: name, type, species, variant, strand, pam, notes

- **OLIGO**: Oligonucleotide (e.g., guide RNA, donor DNA).
  - Parameters: sequence, type, length, mod, notes

- **EDIT**: Defines the genetic change.
  - Parameters: type, target, pos, ref, alt, exons, introns, splice, efficiency, byproduct, notes

- **DELIVERY**: Vehicle and protocol for molecular delivery.
  - Parameters: vehicle, payload, cells, tissue, method, dose, units, schedule, notes

- **CONTEXT**: Biological context for the experiment.
  - Parameters: organism, tissue, cell, condition, env, notes

## MOLECULAR INTERACTIONS

- **INTERACT**: Interaction between molecules.
  - Parameters: partner1, partner2, type, strength, context, notes

- **POSTTRANS**: Post-transcriptional/translational processes.
  - Parameters: type, affected, method, notes

## LOGIC AND SIMULATION

- **IF ( ... ) { ... } ELSE { ... }**: Conditional execution
- **LOOP ( n ) { ... }**: Repeated operations
- **SIMULATE**: In-silico simulation of molecular or cellular event
  - Parameters: action, times, model, params, notes

- **BENCHMARK**: Compare outcomes to reference datasets/cases
  - Parameters: ref_case, dataset, metric, notes

- **TRACE**: Reasoning trace for AI, includes hypothesis, evidence, alternatives, confidence, path, notes

---

### **EXAMPLES**

ENZYME(name="SpCas9", type="Cas9", species="Streptococcus pyogenes", variant="HiFi", strand="+", pam="NGG", notes="high-fidelity")
OLIGO(sequence="ACGTTGCAAGTT...", type="gRNA", length=20, mod="2'-O-methyl", notes="chemically stabilized")
EDIT(type="Base", target="C>T@123456", pos=123456, ref="C", alt="T", exons=[2,3], introns=[], splice=False, efficiency=0.82, byproduct="", notes="APOBEC-mediated")
DELIVERY(vehicle="LNP", payload="mRNA+gRNA", cells=["hepatocyte"], tissue="liver", method="IV", dose=1.5, units="mg/kg", schedule="1x", notes="standard protocol")
CONTEXT(organism="Homo sapiens", tissue="liver", cell="hepatocyte", condition="hypercholesterolemia", env="normal", notes="")

INTERACT(partner1="Cas9", partner2="DNA", type="binding", strength=0.98, context="nucleus", notes="PAM required")
POSTTRANS(type="Splicing", affected=["exon3"], method="exon skip", notes="therapeutic strategy")
IF(efficiency > 0.8) { USE:EDIT } ELSE { SIMULATE(alternative_strategy) }
SIMULATE(action="edit", times=1000, model="MonteCarlo", params={"enzyme": "Cas9"}, notes="in silico batch")
BENCHMARK(ref_case="Nature2023_BaseEdit", dataset="ClinVar", metric="repair_rate", notes="")
TRACE(reasoning="Base editor expected to correct C>T mutation at 123456", result="Predicted repair", confidence=0.93, alternatives=["prime edit"], path=["bind", "cut", "repair"], notes="AI-assisted")
