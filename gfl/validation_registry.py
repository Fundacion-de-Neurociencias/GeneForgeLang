# gfl/validation_registry.py

# Este módulo define todos los valores válidos y reconocidos por GeneForgeLang
# para objetivos de simulación, herramientas de análisis, tipos de experimento, parameters, etc.

# --- Objetivos de Simulación Válidos ---
VALID_SIMULATION_TARGETS = {
    "cell_growth": "Simula el crecimiento celular.",
    "apoptosis": "Simula la muerte celular programada.",
    "cell_division": "Simula la división celular.",
    "mutation_rate": "Simula la tasa de mutación genética.",
}

# --- Nombres de Herramientas de Análisis Válidos ---
VALID_ANALYSIS_TOOLS = {
    "DESeq2": "Herramienta para el análisis de expresión diferencial en datos de RNA-seq.",
    "Scanpy": "Paquete para el análisis de datos de transcriptómica de células individuales (scRNA-seq).",
    "GSEA": "Análisis de Enriquecimiento de Conjuntos de Genes.",
    "CellRanger": "Herramienta para el procesamiento de datos de 10x Genomics.",
}

# --- Tipos de Experimento Válidos ---
VALID_EXPERIMENT_TYPES = [
    "bulkRNA",
    "scRNA",
    "proteomics",
    "genomics",
]

# --- Estrategias de Análisis Válidas ---
VALID_ANALYSIS_STRATEGIES = [
    "pathway_enrichment",
    "differential_expression",
    "clustering",
    "trajectory_inference",
]

# --- Parámetros Válidos por Herramienta y Estrategia ---
# Define un mapeo de herramienta -> estrategia -> {parametro: descripcion_tipo}
# Esto nos permite validar que solo se usen parameters relevantes para cada combinación.
VALID_PARAMS_BY_TOOL_STRATEGY = {
    "DESeq2": {
        "differential_expression": {
            "threshold": "float (umbral de p-valor ajustado, ej. 0.05)",
            "log2FC": "float (umbral de cambio de expresión en log2, ej. 1.0)",
            "conditions": "lista de strings (ej. ['treated', 'untreated'])",
        },
        # Puedes añadir otras estrategias para DESeq2 aquí
    },
    "Scanpy": {
        "clustering": {
            "resolution": "float (resolución para el algoritmo de clustering, ej. 0.5)",
            "n_neighbors": "int (número de vecinos para la construcción del grafo, ej. 15)",
        },
        "differential_expression": {  # Scanpy también puede hacer esto
            "method": "string (ej. 'wilcoxon', 't-test')",
            "groupby": "string (columna para agrupar, ej. 'cell_type')",
        },
        "trajectory_inference": {
            "root_cells": "lista de strings (ID de células raíz)",
            "method": "string (ej. 'diffusion_map', 'paga')",
        },
    },
    "GSEA": {
        "pathway_enrichment": {
            "gene_set_library": "string (ej. 'GO_BP', 'KEGG_2019')",
            "permutation_type": "string (ej. 'phenotype', 'gene_set')",
        },
    },
    # Añadir más herramientas y sus parameters válidos aquí
}
