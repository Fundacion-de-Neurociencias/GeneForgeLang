import os
import random


def generate_simulate():
    targets = [
        "cell_growth",
        "inflammation",
        "apoptosis",
        "tissue_repair",
        "gene_expression",
        "protein_synthesis",
        "metabolic_pathway",
        "cell_division",
        "immune_response",
        "drug_effect",
    ]
    return f"simulate {random.choice(targets)}"


def generate_experiment():
    tools = ["scanpy", "DESeq2", "seurat", "flowjo", "qiime2"]
    types = {
        "scanpy": ["scRNA", "ATACseq", "spatial_transcriptomics"],
        "DESeq2": ["bulkRNA", "ChIPseq"],
        "seurat": ["scRNA", "spatial_transcriptomics"],
        "flowjo": ["flow_cytometry"],
        "qiime2": ["metagenomics"],
    }

    selected_tool = random.choice(tools)
    selected_type = random.choice(types[selected_tool])

    params = []
    if selected_tool == "scanpy":
        if random.random() < 0.7:
            params.append(f"normalize: {str(random.choice(['true', 'false'])).lower()}")
        if random.random() < 0.7:
            params.append(f"min_cells: {random.randint(1, 10)}")
        if random.random() < 0.7:
            params.append(f"min_genes: {random.randint(100, 500)}")
        if random.random() < 0.5:
            params.append(f"pca_dims: {random.choice([20, 30, 50])}")
        if random.random() < 0.3:
            params.append(f"target_cluster_count: {random.randint(3, 15)}")
        if random.random() < 0.2:
            params.append(f"imputation: {str(random.choice(['true', 'false'])).lower()}")
    elif selected_tool == "DESeq2":
        if random.random() < 0.9:
            params.append(f'condition_group: "{random.choice(["treated", "disease", "mutant"])}"')
        if random.random() < 0.9:
            params.append(f'control_group: "{random.choice(["untreated", "healthy", "wildtype"])}"')
        if random.random() < 0.3:
            params.append(f"batch_correction: {str(random.choice(['true', 'false'])).lower()}")
    elif selected_tool == "seurat":
        if random.random() < 0.7:
            params.append(f"resolution: {round(random.uniform(0.1, 1.5), 2)}")
        if random.random() < 0.5:
            params.append(f"integrate_datasets: {str(random.choice(['true', 'false'])).lower()}")
    elif selected_tool == "flowjo":
        if random.random() < 0.8:
            params.append(f"gating_strategy: \"{random.choice(['T_cells', 'B_cells', 'Macrophages'])}\"")
    elif selected_tool == "qiime2":
        if random.random() < 0.8:
            params.append(f"alpha_diversity_metric: \"{random.choice(['shannon', 'simpson'])}\"")
        if random.random() < 0.5:
            params.append(f"beta_diversity_metric: \"{random.choice(['bray_curtis', 'unifrac'])}")

    params_str = ",\n    ".join(params)
    if params_str:
        params_block = f"\n  params: {{\n    {params_str}\n  }}"
    else:
        params_block = ""

    return f"experiment {{\n  tool: {selected_tool}\n  type: {selected_type}{params_block}\n}}"


def generate_analyze():
    strategies = [
        "differential_expression",
        "pathway_enrichment",
        "clustering",
        "gene_set_enrichment",
        "survival_analysis",
    ]
    selected_strategy = random.choice(strategies)

    thresholds = []
    if selected_strategy == "differential_expression":
        if random.random() < 0.9:
            thresholds.append(f"log2FC: {round(random.uniform(0.5, 3.0), 2)}")
        if random.random() < 0.9:
            thresholds.append(f"pval: {random.choice([0.001, 0.01, 0.05])}")
    elif selected_strategy == "pathway_enrichment":
        if random.random() < 0.9:
            thresholds.append(f"FDR: {random.choice([0.01, 0.05, 0.1])}")
    elif selected_strategy == "clustering":
        if random.random() < 0.9:
            thresholds.append(f"resolution: {round(random.uniform(0.1, 1.5), 2)}")
    elif selected_strategy == "survival_analysis":
        if random.random() < 0.9:
            thresholds.append(f"hazard_ratio_threshold: {round(random.uniform(1.0, 3.0), 1)}")

    thresholds_str = ",\n    ".join(thresholds)
    if thresholds_str:
        thresholds_block = f"\n  thresholds: {{\n    {thresholds_str}\n  }}"
    else:
        thresholds_block = ""

    return f"analyze {{\n  strategy: {selected_strategy}{thresholds_block}\n}}"


def generate_branch():
    conditions = [
        "inflammation_high",
        "cell_death_rate_high",
        "tumor_size_increased",
        "gene_mutation_detected",
        "immune_cells_activated",
    ]

    then_block = "\n    " + "\n    ".join(
        [
            random.choice([generate_simulate(), generate_experiment(), generate_analyze()])
            for _ in range(random.randint(1, 2))
        ]
    )
    else_block = "\n    " + "\n    ".join(
        [
            random.choice([generate_simulate(), generate_experiment(), generate_analyze()])
            for _ in range(random.randint(1, 2))
        ]
    )

    return (
        f"branch {{\n  if: {random.choice(conditions)}\n  then: {{{then_block}\n  }}\n  else: {{{else_block}\n  }}\n}}"
    )


def generate_random_gfl_block():
    block_type = random.choice(["simulate", "experiment", "analyze", "branch"])
    if block_type == "simulate":
        return generate_simulate()
    elif block_type == "experiment":
        return generate_experiment()
    elif block_type == "analyze":
        return generate_analyze()
    elif block_type == "branch":
        return generate_branch()


def main(num_blocks=500):
    output_dir = "examples"
    output_file = os.path.join(output_dir, "gfl_training_data.txt")

    # Asegúrate de que el directorio exista
    os.makedirs(output_dir, exist_ok=True)

    print(f"Generando {num_blocks} bloques de GFL en {output_file}...")

    with open(output_file, "w") as f:
        for _ in range(num_blocks):
            gfl_block = generate_random_gfl_block()
            f.write(gfl_block)
            f.write("\n\n")  # Doble salto de línea para separar bloques lógicamente

    print(f"Generación completada. {num_blocks} bloques de GFL escritos.")


if __name__ == "__main__":
    main(num_blocks=1000)  # Generar 1000 bloques de GFL
