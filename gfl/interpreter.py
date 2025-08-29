import logging
from gfl.plugins.plugin_registry import plugin_registry

logger = logging.getLogger(__name__)


class Interpreter:
    """Lightweight AST walker with optional plugin invocation support."""

    def __init__(self):
        self.symbol_table = {}

    def interpret(self, ast):
        """Entry point to interpret a program AST."""
        self.visit(ast)

    def visit(self, node):
        """Dynamic dispatch for AST node handlers."""
        if not isinstance(node, dict) or "type" not in node:
            logger.warning(f"Invalid AST node encountered: {node}")
            return
        method_name = f"visit_{node['type']}"
        visitor_method = getattr(self, method_name, self.generic_visit)
        return visitor_method(node)

    def generic_visit(self, node):
        """Default visit: walk nested dict/list children."""
        for _, value in node.items():
            if isinstance(value, dict) and "type" in value:
                self.visit(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and "type" in item:
                        self.visit(item)

    def visit_program(self, node):
        for statement in node.get("body", []):
            self.visit(statement)

    def visit_define_statement(self, node):
        var_name = node["name"]
        value = self.evaluate_expression(node.get("value"))
        self.symbol_table[var_name] = value
        logger.info(f"DEFINED: {var_name} = {value}")

    def visit_invoke_statement(self, node):
        plugin_name = node["plugin"]
        method_name = node["method"]
        params = {k: self.evaluate_expression(v) for k, v in node.get("params", {}).items()}

        as_var = node.get("as_var")
        try:
            plugin = plugin_registry.get(plugin_name)
            result = plugin.execute(method_name, params, self.symbol_table)
            if as_var:
                self.symbol_table[as_var] = result
                logger.info(f"INVOKED: {plugin_name}.{method_name} (stored in {as_var})")
            else:
                logger.info(f"INVOKED: {plugin_name}.{method_name}")
            return result
        except Exception as e:
            logger.error(f"Error executing plugin {plugin_name}.{method_name}: {e}", exc_info=True)
            raise

    def visit_message_statement(self, node):
        message_value = self.evaluate_expression(node["message"])
        logger.info(f"MESSAGE: {message_value}")

    def visit_branch_statement(self, node):
        condition_result = self.evaluate_expression(node["condition"])
        if condition_result:
            logger.info("BRANCH: Condition true, executing THEN branch.")
            self.visit(node["then_branch"])
        elif "else_branch" in node:
            logger.info("BRANCH: Condition false, executing ELSE branch.")
            self.visit(node["else_branch"])
        else:
            logger.info("BRANCH: Condition false, no ELSE branch.")

    def visit_try_catch_statement(self, node):
        logger.info("Entering TRY block...")
        try:
            self.visit(node["try_block"])
            logger.info("TRY block completed successfully.")
        except Exception as e:
            logger.info(f"Caught exception: {e}. Executing CATCH block...")
            self.symbol_table["__last_error__"] = str(e)
            self.visit(node["catch_block"])
            logger.info("CATCH block completed.")

    def evaluate_expression(self, node):
        """Evaluate expressions supported by the demo interpreter."""
        if node is None:
            return None
        t = node.get("type")
        if t in {"string_literal", "number_literal", "boolean_literal"}:
            return node.get("value")
        if t == "variable_access":
            name = node["name"]
            if name in self.symbol_table:
                return self.symbol_table[name]
            raise NameError(f"Undefined variable '{name}'")
        if t == "binary_operation":
            left = self.evaluate_expression(node["left"])
            right = self.evaluate_expression(node["right"])
            op = node["operator"]
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if op == "/":
                return left / right
            if op == "&":
                return str(left) + str(right)
            if op == "==":
                return left == right
            if op == ">":
                return left > right
            if op == "<":
                return left < right
            if op == ">=":
                return left >= right
            if op == "<=":
                return left <= right
            if str(op).upper() == "AND":
                return bool(left) and bool(right)
            if str(op).upper() == "OR":
                return bool(left) or bool(right)
            raise ValueError(f"Unsupported binary operator: {op}")
        if t == "unary_operation":
            operand = self.evaluate_expression(node["operand"])
            op = node["operator"]
            if str(op).upper() == "NOT":
                return not bool(operand)
            raise ValueError(f"Unsupported unary operator: {op}")
        if t == "array_literal":
            return [self.evaluate_expression(e) for e in node.get("elements", [])]
        if t == "object_literal":
            return {k: self.evaluate_expression(v) for k, v in node.get("properties", {}).items()}
        if t == "access_chain":
            base_value = self.evaluate_expression(node["base"])
            for accessor in node["accessors"]:
                if accessor["type"] == "property_access":
                    prop_name = accessor["name"]
                    if isinstance(base_value, dict) and prop_name in base_value:
                        base_value = base_value[prop_name]
                    else:
                        raise AttributeError(f"Cannot access property '{prop_name}'")
                elif accessor["type"] == "index_access":
                    index_value = self.evaluate_expression(accessor["index"])
                    if isinstance(base_value, (list, str)) and isinstance(index_value, int):
                        if 0 <= index_value < len(base_value):
                            base_value = base_value[index_value]
                        else:
                            raise IndexError(f"Index {index_value} out of bounds")
                    else:
                        raise TypeError("Invalid index operation")
            return base_value
        raise ValueError(f"Unknown expression type: {t}")


__all__ = ["Interpreter"]
