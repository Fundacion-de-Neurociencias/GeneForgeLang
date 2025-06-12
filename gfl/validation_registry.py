# gfl/validation_registry.py

# Este módulo define todos los valores válidos y reconocidos por GeneForgeLang
# para objetivos de simulación, herramientas de análisis, tipos de experimento, etc.

# --- Objetivos de Simulación Válidos ---
# Diccionario que mapea nombres de objetivos a una descripción o sugerencia.
# Esto permite dar feedback más específico al usuario.
VALID_SIMULATION_TARGETS = {
    "cell_growth": "Simula el crecimiento celular.",
    "apoptosis": "Simula la muerte celular programada.",
    "cell_division": "Simula la división celular.",
    "mutation_rate": "Simula la tasa de mutación genética.",
    # Añadir aquí futuros objetivos de simulación
}

# --- Nombres de Herramientas de Análisis Válidos ---
# Diccionario para herramientas con sus descripciones.
VALID_ANALYSIS_TOOLS = {
    "DESeq2": "Herramienta para el análisis de expresión diferencial en datos de RNA-seq.",
    "Scanpy": "Paquete para el análisis de datos de transcriptómica de células individuales (scRNA-seq).",
    "GSEA": "Análisis de Enriquecimiento de Conjuntos de Genes.",
    "CellRanger": "Herramienta para el procesamiento de datos de 10x Genomics.",
    # Añadir aquí futuras herramientas
}

# --- Tipos de Experimento Válidos ---
# Lista simple si no se necesita descripción detallada, o diccionario si sí.
VALID_EXPERIMENT_TYPES = [
    "bulkRNA",
    "scRNA",
    "proteomics",
    "genomics",
    # Añadir aquí futuros tipos de experimento
]

# --- Estrategias de Análisis Válidas ---
VALID_ANALYSIS_STRATEGIES = [
    "pathway_enrichment",
    "differential_expression",
    "clustering",
    "trajectory_inference",
    # Añadir aquí futuras estrategias
]

# Puedes añadir más categorías de validación según el crecimiento de GFL
# Por ejemplo: VALID_DATA_TYPES, VALID_PARAMETERS_FOR_TOOL, etc.
