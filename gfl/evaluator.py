# gfl/evaluator.py

import sys
from collections import deque
from .validation_registry import VALID_SIMULATION_TARGETS, VALID_ANALYSIS_TOOLS, VALID_EXPERIMENT_TYPES, VALID_ANALYSIS_STRATEGIES

class Evaluator:
    def __init__(self):
        # Aquí puedes inicializar el estado de la simulación o análisis
        self.simulation_state = {}
        self.analysis_results = []
        self.output_buffer = deque() # Usamos una cola para mensajes de output/error

    def _log_error(self, message, line=None, column=None, suggestion=None):
        """Genera un mensaje de error formateado y lo añade al buffer."""
        location = ""
        if line is not None:
            location += f" (línea {line}"
            if column is not None:
                location += f", columna {column}"
            location += ")"
        
        full_message = f"ERROR: {message}{location}."
        if suggestion:
            full_message += f" ¿Quizás quiso decir: {suggestion}?"
        self.output_buffer.append(full_message)
        # Aquí podrías decidir si el error es fatal y detener la ejecución
        # raise ValueError(full_message) # Para detener la ejecución inmediatamente

    def _log_warning(self, message, line=None, column=None, suggestion=None):
        """Genera un mensaje de advertencia formateado y lo añade al buffer."""
        location = ""
        if line is not None:
            location += f" (línea {line}"
            if column is not None:
                location += f", columna {column}"
            location += ")"
        
        full_message = f"ADVERTENCIA: {message}{location}."
        if suggestion:
            full_message += f" {suggestion}"
        self.output_buffer.append(full_message)

    def _validate_target(self, target_name, node_info):
        """Valida que el objetivo de simulación sea reconocido."""
        if target_name not in VALID_SIMULATION_TARGETS:
            valid_targets_str = ", ".join(VALID_SIMULATION_TARGETS.keys())
            suggestion = None
            if "death" in target_name.lower():
                suggestion = "'apoptosis'"
            elif "growth" in target_name.lower():
                suggestion = "'cell_growth'"
            elif "division" in target_name.lower():
                suggestion = "'cell_division'"
            
            self._log_error(
                f"El objetivo de simulación '{target_name}' no es reconocido. Los objetivos válidos son: {valid_targets_str}",
                line=node_info.get('line'),
                column=node_info.get('column'),
                suggestion=suggestion
            )
            return False
        return True

    def _validate_tool(self, tool_name, node_info):
        """Valida que la herramienta de análisis sea reconocida."""
        if tool_name not in VALID_ANALYSIS_TOOLS:
            valid_tools_str = ", ".join(VALID_ANALYSIS_TOOLS.keys())
            suggestion = None
            if "deseq" in tool_name.lower():
                suggestion = "'DESeq2'"
            elif "scan" in tool_name.lower():
                suggestion = "'Scanpy'"

            self._log_error(
                f"La herramienta de análisis '{tool_name}' no es reconocida. Las herramientas válidas son: {valid_tools_str}",
                line=node_info.get('line'),
                column=node_info.get('column'),
                suggestion=suggestion
            )
            return False
        return True

    def _validate_experiment_type(self, exp_type, node_info):
        """Valida que el tipo de experimento sea reconocido."""
        if exp_type not in VALID_EXPERIMENT_TYPES:
            valid_types_str = ", ".join(VALID_EXPERIMENT_TYPES)
            
            self._log_error(
                f"El tipo de experimento '{exp_type}' no es reconocido. Los tipos válidos son: {valid_types_str}",
                line=node_info.get('line'),
                column=node_info.get('column')
            )
            return False
        return True

    def _validate_analysis_strategy(self, strategy_name, node_info):
        """Valida que la estrategia de análisis sea reconocida."""
        if strategy_name not in VALID_ANALYSIS_STRATEGIES:
            valid_strategies_str = ", ".join(VALID_ANALYSIS_STRATEGIES)
            self._log_error(
                f"La estrategia de análisis '{strategy_name}' no es reconocida. Las estrategias válidas son: {valid_strategies_str}",
                line=node_info.get('line'),
                column=node_info.get('column')
            )
            return False
        return True

    def evaluate(self, node):
        """
        Evalúa un nodo del AST.
        Se asume que cada nodo es un diccionario con 'type' y otros campos.
        """
        node_type = node.get('type')
        node_info = {'line': node.get('line'), 'column': node.get('column')} # Para pasar info de ubicación

        if node_type == 'program':
            for statement in node.get('statements', []):
                self.evaluate(statement)
        
        elif node_type == 'simulate_statement':
            target = node.get('target')
            if self._validate_target(target, node_info):
                # Lógica para simular el objetivo (por ahora, solo lo logueamos)
                self.output_buffer.append(f"INFO: Simulación de '{target}' iniciada.")
                # Aquí iría la integración con un motor de simulación real
            else:
                self.output_buffer.append(f"ERROR: No se puede simular '{target}' debido a un objetivo inválido.")

        elif node_type == 'analyze_statement':
            tool = node.get('tool')
            params = node.get('params', {})
            strategy = node.get('strategy')

            tool_valid = self._validate_tool(tool, node_info)
            strategy_valid = True
            if strategy:
                strategy_valid = self._validate_analysis_strategy(strategy, node_info)

            if tool_valid and strategy_valid:
                self.output_buffer.append(f"INFO: Análisis usando '{tool}' con estrategia '{strategy}' y parámetros: {params}.")
                # Aquí iría la integración con la herramienta de análisis real
            else:
                self.output_buffer.append(f"ERROR: No se puede realizar el análisis debido a problemas de herramienta o estrategia.")
            # TODO: Añadir validación de parámetros (params) según la herramienta y estrategia. Esto es más avanzado.

        elif node_type == 'experiment_block':
            exp_type = node.get('type')
            block_statements = node.get('statements', [])
            
            if self._validate_experiment_type(exp_type, node_info):
                self.output_buffer.append(f"INFO: Bloque de experimento de tipo '{exp_type}' iniciado.")
                for statement in block_statements:
                    self.evaluate(statement)
                self.output_buffer.append(f"INFO: Bloque de experimento de tipo '{exp_type}' finalizado.")
            else:
                self.output_buffer.append(f"ERROR: No se puede ejecutar el bloque de experimento debido a un tipo inválido.")

        elif node_type == 'branch_statement':
            condition = node.get('condition')
            true_block = node.get('true_block', [])
            false_block = node.get('false_block', []) # Podría ser None

            self.output_buffer.append(f"INFO: Se encontró una bifurcación con condición: '{condition}'.")
            # Para la validación semántica actual, solo verificamos que la condición sea una cadena.
            # Una validación real requeriría evaluar 'condition' (ej. "genes_upregulated > 10")
            # y verificar si los nombres de variables o umbrales son válidos. Esto es un paso futuro.

            # Simulación simple de bifurcación: siempre ejecuta el true_block por ahora
            # En una implementación real, 'condition' se evaluaría a True/False
            self.output_buffer.append(f"INFO: Ejecutando el bloque 'verdadero' de la bifurcación (simulado).")
            for statement in true_block:
                self.evaluate(statement)
            # if condition_is_false and false_block:
            #    self.output_buffer.append(f"INFO: Ejecutando el bloque 'falso' de la bifurcación (simulado).")
            #    for statement in false_block:
            #        self.evaluate(statement)

        else:
            self._log_warning(f"Tipo de nodo AST no reconocido: {node_type}", line=node_info.get('line'), column=node_info.get('column'))

    def get_output(self):
        """Retorna todo el output acumulado y limpia el buffer."""
        output_list = list(self.output_buffer)
        self.output_buffer.clear()
        return "\n".join(output_list)

    def has_errors(self):
        """Verifica si el evaluador ha registrado algún error."""
        return any("ERROR:" in msg for msg in self.output_buffer)

# Ejemplo de uso (esto iría en el script principal que usa el evaluador, ej. fix_and_demo.py)
# from gfl.lexer import Lexer
# from gfl.parser import Parser
#
# if __name__ == '__main__':
#     gfl_code = """
#     simulate cell_growth
#     analyze using DESeq2 with strategy differential_expression params {threshold: 0.05}
#     experiment type bulkRNA {
#         simulate apoptosis
#         analyze using Scanpy with strategy clustering
#     }
#     simulate unknown_target
#     analyze using UnknownTool with strategy pathway_enrichment
#     experiment type invalid_type {
#         simulate cell_division
#     }
#     analyze using DESeq2 with strategy invalid_strategy
#     """
#     lexer = Lexer()
#     parser = Parser()
#     evaluator = Evaluator()
#
#     # Tokenización y parsing
#     try:
#         tokens = lexer.tokenize(gfl_code)
#         ast = parser.parse(tokens)
#
#         if ast:
#             evaluator.evaluate(ast)
#             print(evaluator.get_output())
#         else:
#             print("ERROR: No se pudo generar el AST.")
#
#     except Exception as e:
#         print(f"Error durante el procesamiento: {e}")

