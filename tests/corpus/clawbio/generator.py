import random
import uuid
from pathlib import Path

# Base templates derived from the 10 real fixtures.
# We will perturb these to generate 90 variations.

TEMPLATES = [
    {
        "name": "pharmgx_reporter",
        "domain": "pharmacogenomics",
        "template": """# GFL Stress Test Fixture
metadata:
  experiment_id: CB_STRESS_{idx:03d}
  source_skill: clawbio/pharmgx-reporter
  domain: pharmacogenomics

experiment:
  tool: {tool}
  type: {type}
  contract:
    inputs:
      raw_genome:
        type: TEXT
        attributes:
          format: "{format}"
    outputs:
      pharmacogenomic_report:
        type: JSON
  params:
    genes: {genes}
    cpic_level_filter: {cpic}
""",
    },
    {
        "name": "rnaseq_de",
        "domain": "transcriptomics",
        "template": """# GFL Stress Test Fixture
metadata:
  experiment_id: CB_STRESS_{idx:03d}
  source_skill: clawbio/rnaseq-de
  domain: transcriptomics

analyze:
  strategy: {strategy}
  data:
    counts: "mock_counts.csv"
    metadata: "mock_metadata.csv"
  thresholds:
    significance: {alpha}
    fold_change: {lfc}
  params:
    design_formula: "{formula}"
    contrast: {contrast}
""",
    },
    {
        "name": "gwas_lookup",
        "domain": "population-genomics",
        "template": """# GFL Stress Test Fixture
metadata:
  experiment_id: CB_STRESS_{idx:03d}
  source_skill: clawbio/gwas-lookup
  domain: population-genomics

experiment:
  tool: {tool}
  type: analysis
  contract:
    inputs:
      variants:
        type: TEXT
        attributes:
          format: "rsid_list"
    outputs:
      gwas_report:
        type: JSON
  params:
    rsids: {rsids}
    databases: {databases}
    p_value_threshold: {pvalue}
""",
    },
    {
        "name": "pathway_enricher",
        "domain": "functional-genomics",
        "template": """# GFL Stress Test Fixture
metadata:
  experiment_id: CB_STRESS_{idx:03d}
  source_skill: clawbio/pathway-enricher
  domain: functional-genomics

analyze:
  strategy: {strategy}
  data:
    genes: "de_genes.txt"
  params:
    databases: {databases}
    organism: "{organism}"
    fdr_threshold: {fdr}
""",
    },
    {
        "name": "scrnaseq_orchestrator",
        "domain": "single-cell",
        "template": """# GFL Stress Test Fixture
metadata:
  experiment_id: CB_STRESS_{idx:03d}
  source_skill: clawbio/scrna-orchestrator
  domain: single-cell

guided_discovery:
  data: "cells.h5ad"
  design_params:
    space: "continuous"
    candidates_per_cycle: 5
  active_learning_params:
    strategy: "uncertainty"
  budget:
    max_cycles: 100
  output: "results"
  agents:
    - role: "qc_analyst"
      prompt: "Filter cells with > {mt_pct}% mitochondrial reads and < {min_genes} genes."
    - role: "clustering_analyst"
      prompt: "Perform {clustering_method} clustering with resolution {res}."
""",
    },
]


def generate_fixtures(start_idx: int = 11, count: int = 90):
    output_dir = Path(__file__).parent

    # Perturbation domains
    pharmgx_tools = ["clawbio_pharmgx", "pharmacogenomics_pipeline"]
    pharmgx_formats = ["23andme_v5", "vcf", "ancestrydna", "myheritage"]
    rnaseq_formulas = ["~condition", "~treatment + batch", "~disease_state", "~time_point"]
    clustering_methods = ["leiden", "louvain", "kmeans"]
    organisms = ["human", "mouse", "rat", "zebrafish"]
    strategies = ["differential", "pathway", "functional", "variant", "population_genetics", "metagenomics_analysis"]
    exp_types = ["analysis", "sequencing", "metagenomics", "simulation"]

    genes_pool = ["CYP2D6", "TPMT", "DPYD", "BRCA1", "BRCA2", "APOE", "EGFR", "KRAS", "BRAF"]
    rsids_pool = ["rs123", "rs456", "rs789", "rs111", "rs222", "rs333"]
    db_pool = ["KEGG", "Reactome", "GO_Biological_Process", "WikiPathways", "GWAS_Catalog", "ClinVar"]

    for i in range(start_idx, start_idx + count):
        base = random.choice(TEMPLATES)

        # Build kwargs for formatting
        kwargs = {
            "idx": i,
            "tool": random.choice(pharmgx_tools + ["clawbio_gwas_lookup", "clawbio_metagenomics_profiler"]),
            "type": random.choice(exp_types),
            "format": random.choice(pharmgx_formats),
            "genes": str(random.sample(genes_pool, random.randint(2, 5))),
            "cpic": str(random.sample(["A", "B", "C", "D"], random.randint(1, 3))),
            "strategy": random.choice(strategies),
            "alpha": round(random.uniform(0.001, 0.1), 3),
            "lfc": round(random.uniform(0.5, 3.0), 2),
            "formula": random.choice(rnaseq_formulas),
            "contrast": "['condition', 'treated', 'control']",
            "rsids": str(random.sample(rsids_pool, random.randint(2, 4))),
            "databases": str(random.sample(db_pool, random.randint(1, 3))),
            "pvalue": f"{random.uniform(1e-8, 1e-4):.1e}",
            "organism": random.choice(organisms),
            "fdr": round(random.uniform(0.01, 0.2), 3),
            "mt_pct": random.randint(5, 20),
            "min_genes": random.randint(200, 1000),
            "clustering_method": random.choice(clustering_methods),
            "res": round(random.uniform(0.1, 1.5), 2),
        }

        content = base["template"].format(**kwargs)

        # Replace python repr of lists with yaml-like
        content = content.replace("'", '"')

        filename = f"CB_{i:03d}_synth_{base['name']}.gfl"
        out_path = output_dir / filename
        out_path.write_text(content, encoding="utf-8")

    print(f"Generated {count} synthetic ClawBio workflows in {output_dir}")


if __name__ == "__main__":
    generate_fixtures()
