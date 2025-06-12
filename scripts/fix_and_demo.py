import os
import sys
import logging
import inspect
import re

# Configuración básica del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Asegura que el directorio padre del paquete 'gfl' esté en sys.path.
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from gfl.parser import parse_gfl_code

def post_process_gfl_output(gfl_code):
    """
    Realiza un post-procesamiento básico para corregir errores comunes de formato
    en la salida GFL generada por la IA, antes de pasarla al parser.
    """
    lines = gfl_code.splitlines()
    processed_lines = []
    in_block = 0  # Contador para detectar la profundidad del bloque {}
    
    # Patrón para identificar una propiedad: IDENTIFIER: value
    property_pattern = re.compile(r'^\s*([a-zA-Z_][a-zA-Z_0-9]*)\s*:\s*(.*)')

    for i, line in enumerate(lines):
        stripped_line = line.strip()
        original_line_indent = len(line) - len(line.lstrip())

        # Eliminar comas extra al inicio de una línea o después de ':'
        stripped_line = re.sub(r'^\s*,\s*', '', stripped_line) # Eliminar coma al inicio
        stripped_line = re.sub(r':\s*,', ':', stripped_line) # Eliminar coma después de ':'

        # Normalizar True/False sin comillas si la IA las añade
        stripped_line = stripped_line.replace('"true"', 'true').replace('"false"', 'false')
        
        # Ajustar espacios después de ':' y ','
        stripped_line = re.sub(r':\s*', ':', stripped_line)
        stripped_line = re.sub(r',\s*', ',', stripped_line)

        # Insertar comas entre propiedades si faltan, solo si estamos en un bloque
        if in_block > 0 and processed_lines:
            last_processed_line = processed_lines[-1].strip()
            current_is_property = property_pattern.match(stripped_line)
            
            # Heurística: Si la línea anterior es una propiedad completa (no solo el inicio de un bloque)
            # y no termina en '{' o '}', y la línea actual es otra propiedad,
            # y no hay una coma explícita ya en la línea anterior.
            if not last_processed_line.endswith('{') and \
               not last_processed_line.endswith('}') and \
               not last_processed_line.endswith(',') and \
               current_is_property and \
               property_pattern.match(last_processed_line): # Asegurarse que la línea anterior también era una propiedad
                
                # Añadir la coma solo si la línea anterior realmente contiene un valor (no solo "key:")
                if re.search(r':\s*(\S+)', last_processed_line): # Busca un valor después de ':'
                    processed_lines[-1] += ','
                    logger.debug(f"Added missing comma after '{last_processed_line}'")

        # Actualizar contador de bloques
        if '{' in stripped_line:
            in_block += 1
        if '}' in stripped_line:
            in_block -= 1

        # Añadir la línea (o la línea modificada)
        processed_lines.append(stripped_line)

    cleaned_code = "\n".join(processed_lines)
    
    # Limpiar comas al final de una línea si la siguiente es un cierre de bloque
    cleaned_code = re.sub(r',\s*\}', '}', cleaned_code)
    
    # Eliminar múltiples saltos de línea extra
    cleaned_code = re.sub(r'\n{2,}', '\n\n', cleaned_code)

    # Asegurar un único espacio después de ':'
    cleaned_code = re.sub(r':', ': ', cleaned_code)
    
    # Asegurar un único espacio después de ','
    cleaned_code = re.sub(r',', ', ', cleaned_code)

    # Limpiar espacios antes de comas o dos puntos
    cleaned_code = re.sub(r'\s+([:,])', r'\1', cleaned_code)

    # Asegurar que las comillas no estén pegadas a los valores si se insertaron espacios
    cleaned_code = re.sub(r'\" (.*?) \"', r'"\1"', cleaned_code)


    return cleaned_code

def evaluate_gfl_ast(ast_node, indent=0, operations=None):
    """
    Recorre el AST, realiza una evaluación/interpretación básica con validaciones semánticas,
    y acumula una lista de operaciones estructuradas.
    """
    if operations is None:
        operations = []

    prefix = "  " * indent
    
    if not ast_node:
        logger.debug(f"{prefix}Nodo AST vacío o nulo.")
        return operations

    node_type = ast_node.get('node_type')

    if node_type == 'program':
        logger.info(f"{prefix}Programa GFL detectado. Iniciando validación y ejecución simulada:")
        for statement in ast_node.get('statements', []):
            evaluate_gfl_ast(statement, indent + 1, operations)
    
    elif node_type == 'analyze':
        logger.info(f"{prefix}  --> Acción: Realizando análisis.")
        current_op = {'type': 'analyze'}
        strategy = None
        thresholds = {}

        for prop in ast_node.get('properties', []):
            for key, value in prop.items():
                if key == 'strategy':
                    strategy = value.strip('"') # Eliminar comillas
                    current_op['strategy'] = strategy
                    valid_strategies = ["pathway_enrichment", "clustering", "differential_expression"]
                    if strategy not in valid_strategies:
                        logger.error(f"{prefix}    ERROR: Estrategia de análisis '{strategy}' no válida. Las válidas son: {', '.join(valid_strategies)}")
                    else:
                        logger.info(f"{prefix}    Estrategia de análisis: {strategy}")
                elif key == 'thresholds':
                    logger.info(f"{prefix}    Umbrales:")
                    for threshold_prop in value:
                        for t_key, t_val in threshold_prop.items():
                            thresholds[t_key] = t_val
                            logger.info(f"{prefix}      - {t_key}: {t_val}")
                            # Validaciones específicas de umbrales
                            if t_key == 'FDR':
                                if not isinstance(t_val, (int, float)) or not (0 <= t_val <= 1):
                                    logger.error(f"{prefix}        ERROR: FDR debe ser un valor numérico entre 0 y 1. Valor actual: {t_val}")
                            elif t_key == 'resolution':
                                if not isinstance(t_val, (int, float)) or not (0 < t_val <= 2): # Ejemplo de rango para resolución
                                    logger.error(f"{prefix}        ERROR: Resolution debe ser un valor numérico positivo (típicamente entre 0 y 2). Valor actual: {t_val}")
                            elif t_key in ['log2FC', 'pval']: # Para differential_expression
                                if not isinstance(t_val, (int, float)):
                                    logger.error(f"{prefix}        ERROR: {t_key} debe ser un valor numérico. Valor actual: {t_val}")
                    current_op['thresholds'] = thresholds        
                else:
                    logger.warning(f"{prefix}    Advertencia: Propiedad de análisis desconocida: {key}: {value}")
        operations.append(current_op)

    elif node_type == 'experiment':
        logger.info(f"{prefix}  --> Acción: Configurando experimento.")
        current_op = {'type': 'experiment'}
        tool = None
        exp_type = None
        params = {}

        for prop in ast_node.get('properties', []):
            for key, value in prop.items():
                if key == 'tool':
                    tool = value.strip('"')
                    current_op['tool'] = tool
                    valid_tools = ["DESeq2", "scanpy", "STAR"] # Ejemplo de herramientas
                    if tool not in valid_tools:
                        logger.error(f"{prefix}    ERROR: Herramienta '{tool}' no válida. Las válidas son: {', '.join(valid_tools)}")
                    else:
                        logger.info(f"{prefix}    Herramienta: {tool}")
                elif key == 'type':
                    exp_type = value.strip('"') if isinstance(value, str) else value
                    current_op['exp_type'] = exp_type
                    valid_types = ["bulkRNA", "scRNA", "WGS"] # Ejemplo de tipos
                    if exp_type not in valid_types:
                        logger.error(f"{prefix}    ERROR: El tipo de experimento '{exp_type}' no es reconocido. Los tipos permitidos son: {', '.join(valid_types)}. Por favor, corrija la definición del experimento.")
                    else:
                        logger.info(f"{prefix}    Tipo de experimento: {exp_type}")
                elif key == 'params':
                    logger.info(f"{prefix}    Parámetros:")
                    for param_prop in value:
                        for p_key, p_val in param_prop.items():
                            params[p_key] = p_val
                            logger.info(f"{prefix}      - {p_key}: {p_val}")
                            # Validaciones específicas de parámetros
                            if p_key in ["normalize", "qc_filter"] and not isinstance(p_val, bool):
                                logger.error(f"{prefix}        ERROR: El parámetro '{p_key}' debe ser un valor booleano (true/false). Valor actual: {p_val}")
                            elif p_key in ["min_cells", "min_genes"] and (not isinstance(p_val, (int, float)) or p_val < 0):
                                logger.error(f"{prefix}        ERROR: El parámetro '{p_key}' debe ser un número positivo. Valor actual: {p_val}")
                    current_op['params'] = params
                else:
                    logger.warning(f"{prefix}    Advertencia: Propiedad de experimento desconocida: {key}: {value}")
            
            # Validación de compatibilidad herramienta-tipo (ejemplo)
            if tool == "DESeq2" and exp_type != "bulkRNA":
                logger.warning(f"{prefix}    Advertencia: La herramienta DESeq2 es compatible con bulkRNA, pero la configuración sugiere otro tipo ({exp_type}). Asegúrese de que su uso sea intencionado y adecuado para {exp_type}.")
            elif tool == "scanpy" and exp_type != "scRNA":
                logger.warning(f"{prefix}    Advertencia: La herramienta Scanpy es compatible con scRNA, pero la configuración sugiere otro tipo ({exp_type}). Asegúrese de que su uso sea intencionado y adecuado para {exp_type}.")
        operations.append(current_op)

    elif node_type == 'simulate':
        target = ast_node.get('target')
        valid_targets = ["cell_growth", "apoptosis", "cell_division", "mutation_rate"] # Ejemplos de simulaciones
        if target not in valid_targets:
            logger.error(f"{prefix}  ERROR: El objetivo de simulación '{target}' no es reconocido. Los objetivos válidos son: {', '.join(valid_targets)}. ¿Quizás quiso usar 'apoptosis' para la muerte celular?")
        else:
            logger.info(f"{prefix}  --> Acción: Simulando: {target}")
            operations.append({'type': 'simulate', 'target': target})

    elif node_type == 'branch':
        logger.info(f"{prefix}  --> Bloque Condicional (Branch):")
        condition = ast_node.get('if')
        
        # Una función real evaluaría la condición. Aquí solo la simulamos.
        # Podrías pasar un "estado" o "contexto" al evaluador.
        condition_evaluated_result = True # Por ahora, siempre True para ver el 'then' block
        
        logger.info(f"{prefix}    Condición 'if': {condition}")
        current_op = {'type': 'branch', 'condition': condition}

        # VALIDACIÓN DE LA CONDICIÓN (ejemplo básico)
        if condition and 'op' in condition: # Si es una operación (AND, OR)
            left_val = condition.get('left', {}).get('value')
            right_val = condition.get('right', {}).get('value')
            if left_val and right_val:
                logger.info(f"{prefix}    Validando condición compuesta: '{left_val}' {condition['op']} '{right_val}'")
            else:
                logger.error(f"{prefix}    ERROR: Condición compuesta incompleta o mal formada: {condition}")
        elif condition and 'type' in condition and condition['type'] == 'boolean_literal': # Si es un literal booleano
            bool_val = condition.get('value')
            # Aquí podrías tener una lista de booleanos válidos o variables de estado
            # if bool_val not in ["tumor_size_increased", "cell_death_rate_high"]:
            #     logger.warning(f"{prefix}    Advertencia: La variable booleana '{bool_val}' no está en la lista de variables de estado conocidas.")
            logger.info(f"{prefix}    Validando condición simple: '{bool_val}'")
        else:
            logger.error(f"{prefix}    ERROR: Formato de condición desconocido o vacío: {condition}")


        if condition_evaluated_result:
            logger.info(f"{prefix}    Condición evaluada como verdadera. Ejecutando bloque 'then':")
            then_ops = []
            for statement in ast_node.get('then', []):
                evaluate_gfl_ast(statement, indent + 2, then_ops)
            current_op['then'] = then_ops
        else:
            else_block = ast_node.get('else')
            if else_block:
                logger.info(f"{prefix}    Condición evaluada como falsa. Ejecutando bloque 'else':")
                else_ops = []
                for statement in else_block:
                    evaluate_gfl_ast(statement, indent + 2, else_ops)
                current_op['else'] = else_ops
            else:
                logger.info(f"{prefix}    Condición evaluada como falsa, pero no hay bloque 'else'.")
        operations.append(current_op)
    
    # boolean_literal y comparison no necesitan una rama de evaluación directa aquí
    # porque son manejados como parte del nodo 'branch'
    elif node_type in ['boolean_literal', 'comparison']:
        pass
    
    else:
        logger.warning(f"{prefix}Tipo de nodo AST desconocido: {node_type} - {ast_node}")
    
    return operations # La función ahora retorna las operaciones acumuladas

def main():
    example_gfl_file = os.path.join(parent_dir, 'gfl', 'gfl_example.gfl')

    # --- Parte 1: Parsear el archivo de ejemplo GFL ---
    logger.info(f"Intentando parsear el archivo de ejemplo: {example_gfl_file}")
    if os.path.exists(example_gfl_file):
        with open(example_gfl_file, 'r') as f:
            gfl_content = f.read()
        logger.info(f"Contenido de '{example_gfl_file}':\n---{gfl_content}\n---")
        
        logger.info("Iniciando parseo de código GFL...")
        ast = parse_gfl_code(gfl_content)
        
        if ast:
            logger.info("Parseo completado con éxito. AST generado.")
            logger.info(f"✅ AST válido generado para '{example_gfl_file}':\n{ast}")
            
            logger.info("\n--- Iniciando evaluación básica del AST para el archivo de ejemplo ---")
            collected_operations = evaluate_gfl_ast(ast)
            logger.info(f"\n--- Operaciones recolectadas para el archivo de ejemplo: ---\n{collected_operations}")
        else:
            logger.error(f"❌ El archivo '{example_gfl_file}' no produjo un AST válido o el AST está vacío.")
    else:
        logger.error(f"El archivo de ejemplo '{example_gfl_file}' no se encontró.")

    logger.info("\n--- Simulando la salida de la IA afinada y post-procesando ---")

    # --- Parte 2: Simular y post-procesar la salida de la IA afinada ---
    # Ejemplos de salida de la IA (simulados)
    ai_generated_texts = [
        """simulate cell_growth analyze {
strategy: "differential_expression" thresholds: {
    log2FC: 0.5, pval: 0.01
}
}
experiment {
tool: "scanpy" type: "scRNA" params: {
normalize: true, min_cells: 3, min_genes: 200
}
}""",
        """experiment {
tool: "DESeq2" type: bulkRNA params: {
condition_group: "treated", control_group: "untreated"
}
}
analyze {
strategy: "clustering" thresholds: {
resolution: 0.8
}
}""",
        """simulate cell_death simulate apoptosis branch { if: "tumor_size_increased"
then: {
simulate apoptosis
}
else: {
simulate cell_division
}
}"""
    ]

    for i, text in enumerate(ai_generated_texts):
        logger.info(f"\n--- Prompt para la IA afinada ({i+1}/{len(ai_generated_texts)}): ---")
        logger.info(text)
        logger.info("---")
        
        logger.info("Texto generado por la IA afinada (candidato GFL ANTES de post-procesar):")
        logger.info(f"---\n{text}\n---")

        processed_text = post_process_gfl_output(text)
        logger.info("Texto generado por la IA afinada (candidato GFL DESPUÉS de post-procesar):")
        logger.info(f"---\n{processed_text}\n---")
        
        logger.info("Iniciando parseo de código GFL...")
        ast = parse_gfl_code(processed_text)
        
        if ast:
            logger.info(f"✅ AST válido generado por el texto post-procesado ({i+1}/{len(ai_generated_texts)}).")
            # Opcional: logger.debug(f"AST: {ast}") # Descomentar para ver el AST completo
            
            logger.info(f"--- Iniciando evaluación básica del AST para el ejemplo ({i+1}/{len(ai_generated_texts)}) ---")
            collected_operations = evaluate_gfl_ast(ast)
            logger.info(f"\n--- Operaciones recolectadas para el ejemplo ({i+1}/{len(ai_generated_texts)}): ---\n{collected_operations}")
        else:
            logger.error(f"❌ El texto generado por la IA afinada ({i+1}/{len(ai_generated_texts)}) no produjo un AST válido o el AST está vacío.")
    
    logger.info("\nProceso de parsing y post-procesamiento completado.")

if __name__ == "__main__":
    main()
