# Importa las clases GFLLexer y GFLParser
from gfl.lexer import GFLLexer
from gfl.parser import GFLParser

# Asegúrate de que el PYTHONPATH esté configurado correctamente para importar desde gfl
# Esto es manejado por el comando de ejecución 'PYTHONPATH=. python3 scripts/fix_and_demo.py'
# así que no necesitamos modificar sys.path aquí.


def run_demo():
    print("--- GFL Parser Demo ---")

    # Instancia el lexer y el parser
    gfl_lexer = GFLLexer()
    gfl_parser = GFLParser()

    # Define los snippets de código GFL para parsear
    snippets = {
        "gfl/gfl_example.gfl": """
analyze {
    strategy: "pathway_enrichment",
    thresholds: {
        FDR: 0.05
    }
}

experiment {
    tool: "DESeq2",
    type: "bulkRNA",
    params: {
        condition_group: "disease",
        control_group: "healthy"
    }
}

simulate cell_growth

branch {
    if: tumor_size_increased AND cell_death_rate_high
    then: {
        simulate apoptosis
        analyze {
            strategy: "clustering",
            thresholds: {
                resolution: 0.8
            }
        }
    }
    else: {
        simulate cell_division
    }
}

# Este bloque debería generar un ERROR de validación de parámetros
analyze using DESeq2 with strategy differential_expression params {
    threshold: 0.05,
    log2FC: 1.0,
    unknown_param: "esto_es_invalido"
}

# Este bloque debería generar un ERROR de validación de parámetros
analyze using Scanpy with strategy clustering params {
    resolution: 0.8,
    invalid_cluster_method: "leiden"
}

# Este bloque debería generar un ERROR de validación de parámetros
analyze using GSEA with strategy pathway_enrichment params {
    gene_set_library: "GO_BP",
    extra_option: true
}
""",
        "AI-Generated Scenario 1 (Simple Analyze)": """
analyze {
    strategy: "pathway_enrichment",
    thresholds: {
        FDR: 0.05
    }
}
""",
        "AI-Generated Scenario 2 (Complex Branch)": """
branch {
    if: tumor_size_increased AND cell_death_rate_high
    then: {
        simulate apoptosis
        analyze {
            strategy: "clustering",
            thresholds: {
                resolution: 0.8
            }
        }
    }
    else: {
        simulate cell_division
    }
}
""",
        "AI-Generated Scenario 3 (Experiment and Simulate)": """
experiment {
    tool: "CRISPR",
    type: "gene_knockout",
    params: {
        target_gene: "TP53",
        guide_RNA: "AGCTAGCTAGCTAGCT"
    }
}
simulate gene_expression
""",
        "AI-Generated Scenario 4 (Phenotype Analyze)": """
ANALYZE {
    strategy: "few_shot_diagnosis",
    tool: "SHEPHERD",
    phenotype_terms: ["ataxia", "epilepsy", "microcephaly"],
    candidate_genes: ["SCN2A", "ATM", "MECP2"]
}
""",
        "AI-Generated Scenario 5 (Analyze with new inline syntax)": """
analyze using DESeq2 with strategy differential_expression params {
    threshold: 0.05,
    log2FC: 1.0,
    condition_group: "treated",
    control_group: "untreated"
}
""",
        "AI-Generated Scenario 6 (Analyze with another new inline syntax)": """
analyze using Scanpy with strategy clustering params {
    resolution: 0.7,
    method: "leiden"
}
""",
        "AI-Generated Scenario 7 (Invalid Tool/Strategy)": """
analyze using UnknownTool with strategy invalid_strategy params {
    param1: "value1"
}
""",
        "AI-Generated Scenario 8 (Invalid Parameter for Strategy)": """
analyze using DESeq2 with strategy differential_expression params {
    threshold: 0.05,
    invalid_param: "error_value"
}
""",
    }

    for name, code_snippet in snippets.items():
        print(f"\nParsing {name} (Snippet {list(snippets.keys()).index(name) + 1}):")
        print("-" * 40)
        print(code_snippet)
        print("-" * 40)

        try:
            # Pasa la instancia del lexer al parser
            ast = gfl_parser.parse(code_snippet)
            if ast:
                print("Successfully Parsed! Generated AST (Operations):")
                # Por ahora, solo imprime la estructura del AST o partes relevantes
                for op_type, *op_details in ast:
                    print(f"  - {op_type.capitalize()} Operation:")
                    if op_type == "analyze" or op_type == "experiment":
                        for key, value in op_details[0].items():
                            print(f"    {key}: {value}")
                    elif op_type == "simulate":
                        print(f"    Target: {op_details[0]}")
                    elif op_type == "branch":
                        print(f"    If: {op_details[0]}")
                        print(f"    Then Block: {op_details[1]}")
                        print(f"    Else Block: {op_details[2]}")
                    elif op_type == "analyze_inline":
                        print(
                            f"    Tool: {op_details[0]}, Strategy: {op_details[1]}, Params: {op_details[2]}"
                        )

            else:
                print(
                    "Successfully Parsed! No operations generated (empty or only comments)."
                )

        except Exception as e:
            print(f"Error durante el parseo: {e}")

        print("\nParsing Errors/Warnings:")
        # Para esta demo, los errores de sintaxis se imprimen directamente desde el parser.
        # Las advertencias de validación de parámetros/herramientas se gestionarían en una capa posterior.
        print(
            "  - No additional warnings captured at this level in demo (see parser output above for syntax errors/warnings)."
        )


if __name__ == "__main__":
    run_demo()
