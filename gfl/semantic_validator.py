import logging
from gfl.lexer import tokens # Asegúrate de que lexer.py exporta 'tokens' correctamente
from gfl.parser import parser # Asegúrate de que parser.py exporta 'parser' correctamente
from gfl.plugins import plugin_registry

logger = logging.getLogger(__name__)

# Clase para el validador semántico
class SemanticValidator:
    def __init__(self):
        self.symbol_table = {} # Para almacenar variables definidas
        self.errors = []

    def visit(self, node):
        method_name = f"visit_{node['type']}"
        visitor_method = getattr(self, method_name, self.generic_visit)
        return visitor_method(node)

    def generic_visit(self, node):
        # Visita recursivamente todos los nodos hijos
        for key, value in node.items():
            if isinstance(value, dict) and 'type' in value:
                self.visit(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and 'type' in item:
                        self.visit(item)

    def visit_program(self, node):
        for statement in node.get('body', []):
            self.visit(statement)

    def visit_define_statement(self, node):
        var_name = node['name']
        if var_name in self.symbol_table:
            self.errors.append(f"Semantic Error: Variable '{var_name}' already defined.")
        self.symbol_table[var_name] = {'type': 'unknown'} # Tipo inicial, podría refinarse

        # Validar el valor si es una expresión
        if 'value' in node:
            self.visit(node['value'])

    def visit_invoke_statement(self, node):
        plugin_name = node['plugin']
        method_name = node['method']

        # Verificar si el plugin existe en el registro
        try:
            plugin_registry.get(plugin_name)
        except ValueError as e:
            self.errors.append(f"Semantic Error: {e}")

        # Validar parámetros
        for param in node.get('params', {}).values():
            self.visit(param) # Visita cada parámetro para validación

        # Si hay una asignación de resultado
        if 'as_var' in node:
            as_var = node['as_var']
            if as_var in self.symbol_table:
                self.errors.append(f"Semantic Error: Result variable '{as_var}' already defined.")
            self.symbol_table[as_var] = {'type': 'unknown_result'}

    def visit_message_statement(self, node):
        self.visit(node['message'])

    def visit_expression(self, node):
        if node['type'] == 'variable_access':
            var_name = node['name']
            if var_name not in self.symbol_table:
                self.errors.append(f"Semantic Error: Undefined variable '{var_name}'.")
        elif node['type'] in ['string_literal', 'number_literal', 'boolean_literal']:
            pass # Son literales, siempre válidos
        elif node['type'] == 'binary_operation':
            self.visit(node['left'])
            self.visit(node['right'])
        elif node['type'] == 'array_literal':
            for item in node.get('elements', []):
                self.visit(item)
        elif node['type'] == 'object_literal':
            for key, value in node.get('properties', {}).items():
                self.visit(value)

    def visit_branch_statement(self, node):
        self.visit(node['condition'])
        self.visit(node['then_branch'])
        if 'else_branch' in node:
            self.visit(node['else_branch'])

    def visit_try_catch_statement(self, node):
        self.visit(node['try_block'])
        self.visit(node['catch_block'])

    def validate_program(self, ast):
        self.errors = [] # Reiniciar errores
        self.symbol_table = {} # Reiniciar tabla de símbolos
        self.visit(ast)
        return self.errors

# Instancia global del validador y función de validación
_validator = SemanticValidator()

def validate(ast):
    """
    Función de utilidad para validar el AST de un programa GFL.
    Retorna una lista de errores semánticos encontrados.
    """
    return _validator.validate_program(ast)

