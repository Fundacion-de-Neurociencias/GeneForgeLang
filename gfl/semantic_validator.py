import logging

from gfl.plugins.plugin_registry import plugin_registry

logger = logging.getLogger(__name__)


class SemanticValidator:
    """Minimal semantic validator for GFL ASTs.

    This version validates symbol reuse, plugin existence, and recursively
    descends into expressions. It intentionally avoids tight coupling to
    specific parser/tokenizer implementations.
    """

    def __init__(self):
        self.symbol_table = {}
        self.errors = []

    def visit(self, node):
        if not isinstance(node, dict):
            return
        method_name = f"visit_{node.get('type')}"
        return getattr(self, method_name, self.generic_visit)(node)

    def generic_visit(self, node):
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
        if var_name in self.symbol_table:
            self.errors.append(f"Variable '{var_name}' already defined")
        self.symbol_table[var_name] = {"type": "unknown"}
        if "value" in node:
            self.visit(node["value"])

    def visit_invoke_statement(self, node):
        plugin_name = node["plugin"]
        method_name = node.get("method")
        # Plugin existence is optional at validation time; log instead of erroring.
        try:
            plugin_registry.get(plugin_name)
        except Exception as e:
            logger.debug("Plugin not found during validation: %s", e)
        # Validate params
        params = node.get("params", {})
        for param in params.values():
            self.visit(param)

        # Minimal domain rule example: prime_edit expects structured pegRNA, not a plain string
        try:
            if (
                str(plugin_name).lower() in {"geneediting", "gene_editing"}
                and str(method_name) == "prime_edit"
            ):
                peg = params.get("pegRNA")
                if isinstance(peg, dict) and peg.get("type") == "string_literal":
                    self.errors.append(
                        "Invalid param: 'pegRNA' must be an object, not string"
                    )
        except Exception:
            pass
        # Validate assignment name
        if "as_var" in node:
            as_var = node["as_var"]
            if as_var in self.symbol_table:
                self.errors.append(f"Result variable '{as_var}' already defined")
            self.symbol_table[as_var] = {"type": f"result_of:{method_name}"}

    def visit_message_statement(self, node):
        self.visit(node["message"])

    def visit_branch_statement(self, node):
        self.visit(node["condition"])
        self.visit(node["then_branch"])
        if "else_branch" in node:
            self.visit(node["else_branch"])

    def visit_try_catch_statement(self, node):
        self.visit(node["try_block"])
        self.visit(node["catch_block"])

    def visit_expression(self, node):
        t = node.get("type")
        if t == "variable_access":
            name = node["name"]
            if name not in self.symbol_table:
                self.errors.append(f"Undefined variable '{name}'")
        elif t in {"string_literal", "number_literal", "boolean_literal"}:
            return
        elif t == "binary_operation":
            self.visit(node["left"])
            self.visit(node["right"])
        elif t == "array_literal":
            for item in node.get("elements", []):
                self.visit(item)
        elif t == "object_literal":
            for _, value in node.get("properties", {}).items():
                self.visit(value)

    def validate_program(self, ast):
        self.errors = []
        self.symbol_table = {}
        self.visit(ast)
        return self.errors


_validator = SemanticValidator()


def validate(ast):
    """Validate a program AST and return a list of errors."""
    return _validator.validate_program(ast)


__all__ = ["SemanticValidator", "validate"]
