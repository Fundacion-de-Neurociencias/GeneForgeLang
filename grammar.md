{
  "structures": {
    "~": "Linear",
    ":": "Secondary",
    "^": "Tertiary",
    "*": "Quaternary",
    "!": "Unknown"
  },
  "molecules": {
    "d": "DNA",
    "r": "RNA",
    "p": "Protein"
  },
  "tokens": {
    "EX": "Exon",
    "IN": "Intron",
    "UTR5": "5' Untranslated Region",
    "UTR3": "3' Untranslated Region",
    "TATA": "TATA box",
    "TSS": "Transcription Start Site"
  },
  "modules": [
    "Dom", "Mot", "TF", "Ctrl"
  ],
  "operations": {
    "EDIT": ["Base", "Prime", "ARCUS", "RNA_Transport"],
    "DELIV": true,
    "DOSE": true,
    "TIME": true,
    "TRANSCRIBE": true,
    "SPLICE": true,
    "TRANSLATE": true,
    "INHIBIT": true,
    "MODULATE_ALLOSTERIC": true,
    "BIND": true,
    "HIERARCHY": true,
    "EFFECT": true,
    "SIMULATE": true,
    "DIAGNOSE": true,
    "ASSERT": true,
    "MAP": true,
    "TYPE": true,
    "HYPOTHESIS": true,
    "PATHWAY": true,
    "MACRO": true,
    "USE": true
  },
  "modifiers": {
    "*": "PTM",
    "'": "High conservation",
    "^": "Epigenetic mark",
    "@": "Position index",
    "[]": "Annotation",
    "{}": "Metadata block",
    "=": "Assignment / Logic",
    "/": "Co-occurrence or composite",
    "-": "Sequential linkage",
    "#": "Comment"
  },
  "logic": {
    "PROB": true,
    "FITNESS": true,
    "EPISTASIS": true,
    "KINETIC": true,
    "DYNAMICS": true,
    "CURVE": true
  },
  "examples": {
    "EDIT": "EDIT:Base(G→A@Q335X){efficacy=partial, cells=liver}",
    "DELIV": "DELIV(mRNA+LNP@IV)",
    "HYPOTHESIS": "HYPOTHESIS: if MUT(Q335X) → Loss(CPS1)",
    "SIMULATE": "SIMULATE: {EDIT:Base(...), OUTCOME:↓ammonia}",
    "DIAGNOSE": "DIAGNOSE:{if ↓ATP7B_mRNA & ↑serum_copper then Wilson_Disease}",
    "EFFECT": "EFFECT(↑neurite_growth@24h)",
    "PATHWAY": "PATHWAY: ARG+NH3 → CPS1 → Carbamoyl-P → OTC",
    "BIND": "BIND(MAPK:MEK){Kd=2.5nM, reversible=true}",
    "ASSERT": "ASSERT: TRANSCRIBE(p:) ❌ Invalid",
    "TYPE": "TYPE: BACE1 → [Gene, Enzyme]",
    "MAP": "MAP: Dom(Kin) → Pfam:PF00069"
  }
}
