# gfl/evaluator.py

from collections import deque

from .validation_registry import (
    VALID_ANALYSIS_STRATEGIES,
    VALID_ANALYSIS_TOOLS,
    VALID_EXPERIMENT_TYPES,
    VALID_PARAMS_BY_TOOL_STRATEGY,
    VALID_SIMULATION_TARGETS,
)


class Evaluator:
    def __init__(self):
        self.simulation_state = {}
        self.analysis_results = []
        self.output_buffer = deque()

    def _log_error(self, message, line=None, column=None, suggestion=None):
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

    def _log_warning(self, message, line=None, column=None, suggestion=None):
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
                line=node_info.get("line"),
                column=node_info.get("column"),
                suggestion=suggestion,
            )
            return False
        return True

    def _validate_tool(self, tool_name, node_info):
        if tool_name not in VALID_ANALYSIS_TOOLS:
            valid_tools_str = ", ".join(VALID_ANALYSIS_TOOLS.keys())
            suggestion = None
            if "deseq" in tool_name.lower():
                suggestion = "'DESeq2'"
            elif "scan" in tool_name.lower():
                suggestion = "'Scanpy'"

            self._log_error(
                f"La herramienta de análisis '{tool_name}' no es reconocida. Las herramientas válidas son: {valid_tools_str}",
                line=node_info.get("line"),
                column=node_info.get("column"),
                suggestion=suggestion,
            )
            return False
        return True

    def _validate_experiment_type(self, exp_type, node_info):
        if exp_type not in VALID_EXPERIMENT_TYPES:
            valid_types_str = ", ".join(VALID_EXPERIMENT_TYPES)

            self._log_error(
                f"El tipo de experimento '{exp_type}' no es reconocido. Los tipos válidos son: {valid_types_str}",
                line=node_info.get("line"),
                column=node_info.get("column"),
            )
            return False
        return True

    def _validate_analysis_strategy(self, strategy_name, node_info):
        if strategy_name not in VALID_ANALYSIS_STRATEGIES:
            valid_strategies_str = ", ".join(VALID_ANALYSIS_STRATEGIES)
            self._log_error(
                f"La estrategia de análisis '{strategy_name}' no es reconocida. Las estrategias válidas son: {valid_strategies_str}",
                line=node_info.get("line"),
                column=node_info.get("column"),
            )
            return False
        return True

    def _validate_analysis_params(self, tool, strategy, params, node_info):
        """
        Valida que los parámetros proporcionados sean válidos para la herramienta y estrategia dadas.
        """
        tool_params = VALID_PARAMS_BY_TOOL_STRATEGY.get(tool)
        if not tool_params:
            # Si la herramienta no tiene parámetros definidos en el registro,
            # no podemos validar, pero ya se debería haber generado un error de herramienta.
            # Podríamos loguear una advertencia si se proporcionaron params inesperadamente.
            if params:
                self._log_warning(
                    f"No hay parámetros definidos para la herramienta '{tool}'. Los parámetros proporcionados serán ignorados o podrían causar errores posteriores.",
                    line=node_info.get("line"),
                    column=node_info.get("column"),
                )
            return True  # No hay definición de params, así que no podemos validar más estrictamente

        strategy_params = tool_params.get(strategy)
        if not strategy_params:
            # Si la estrategia no tiene parámetros definidos para la herramienta,
            # lo mismo que arriba.
            if params:
                self._log_warning(
                    f"No hay parámetros definidos para la estrategia '{strategy}' bajo la herramienta '{tool}'. Los parámetros proporcionados serán ignorados o podrían causar errores posteriores.",
                    line=node_info.get("line"),
                    column=node_info.get("column"),
                )
            return True

        all_params_valid = True
        for param_name, param_value in params.items():
            if param_name not in strategy_params:
                valid_param_keys = ", ".join(strategy_params.keys())
                self._log_error(
                    f"El parámetro '{param_name}' no es válido para la herramienta '{tool}' con estrategia '{strategy}'.",
                    line=node_info.get("line"),
                    column=node_info.get("column"),
                    suggestion=f"Los parámetros válidos son: {valid_param_keys}"
                    if valid_param_keys
                    else "No hay parámetros válidos definidos.",
                )
                all_params_valid = False
            # TODO: Aquí se podría añadir validación de tipo/rango para param_value
            # For example:
            # expected_type_desc = strategy_params.get(param_name)
            # if expected_type_desc and not self._is_param_value_of_expected_type(param_value, expected_type_desc):
            #     self._log_error(f"El valor '{param_value}' para el parámetro '{param_name}' no coincide con el tipo esperado: {expected_type_desc}.")

        return all_params_valid

    def evaluate(self, node):
        node_type = node.get("type")
        node_info = {"line": node.get("line"), "column": node.get("column")}

        if node_type == "program":
            for statement in node.get("statements", []):
                self.evaluate(statement)

        elif node_type == "simulate_statement":
            target = node.get("target")
            if self._validate_target(target, node_info):
                self.output_buffer.append(f"INFO: Simulación de '{target}' iniciada.")
            else:
                self.output_buffer.append("ERROR: Simulación no válida debido a objetivo inválido.")

        elif node_type == "analyze_statement":
            tool = node.get("tool")
            params = node.get("params", {})
            strategy = node.get("strategy")

            tool_valid = self._validate_tool(tool, node_info)
            strategy_valid = True
            if strategy:
                strategy_valid = self._validate_analysis_strategy(strategy, node_info)

            params_valid = self._validate_analysis_params(tool, strategy, params, node_info)

            if tool_valid and strategy_valid and params_valid:
                self.output_buffer.append(
                    f"INFO: Análisis usando '{tool}' con estrategia '{strategy}' y parámetros: {params}."
                )
            else:
                self.output_buffer.append(
                    "ERROR: No se puede realizar el análisis debido a problemas de herramienta, estrategia o parámetros."
                )

        elif node_type == "experiment_block":
            exp_type = node.get("type")
            block_statements = node.get("statements", [])

            if self._validate_experiment_type(exp_type, node_info):
                self.output_buffer.append(f"INFO: Bloque de experimento de tipo '{exp_type}' iniciado.")
                for statement in block_statements:
                    self.evaluate(statement)
                self.output_buffer.append(f"INFO: Bloque de experimento de tipo '{exp_type}' finalizado.")
            else:
                self.output_buffer.append(
                    "ERROR: No se puede ejecutar el bloque de experimento debido a un tipo inválido."
                )

        elif node_type == "branch_statement":
            condition = node.get("condition")
            true_block = node.get("true_block", [])
            node.get("false_block", [])

            self.output_buffer.append(f"INFO: Se encontró una bifurcación con condición: '{condition}'.")

            self.output_buffer.append("INFO: Ejecutando el bloque 'verdadero' de la bifurcación (simulado).")
            for statement in true_block:
                self.evaluate(statement)

        else:
            self._log_warning(
                f"Tipo de nodo AST no reconocido: {node_type}",
                line=node_info.get("line"),
                column=node_info.get("column"),
            )

    def get_output(self):
        output_list = list(self.output_buffer)
        self.output_buffer.clear()
        return "\n".join(output_list)

    def has_errors(self):
        return any("ERROR:" in msg for msg in self.output_buffer)
