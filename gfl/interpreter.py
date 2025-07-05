import logging
from gfl.plugins import plugin_registry # Importa el registro de plugins

logger = logging.getLogger(__name__)

class Interpreter:
    def __init__(self):
        self.symbol_table = {} # Para almacenar variables y sus valores

    def interpret(self, ast):
        """
        Interpreta el Abstract Syntax Tree (AST).
        """
        self.visit(ast)

    def visit(self, node):
        """
        Método genérico para visitar nodos del AST.
        """
        if not isinstance(node, dict) or 'type' not in node:
            logger.warning(f"Invalid AST node encountered: {node}")
            return

        method_name = f"visit_{node['type']}"
        visitor_method = getattr(self, method_name, self.generic_visit)
        return visitor_method(node)

    def generic_visit(self, node):
        """
        Visita recursivamente los hijos de un nodo.
        """
        for key, value in node.items():
            if isinstance(value, dict) and 'type' in value:
                self.visit(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and 'type' in item:
                        self.visit(item)

    def visit_program(self, node):
        """
        Visita el nodo raíz del programa.
        """
        for statement in node.get('body', []):
            self.visit(statement)

    def visit_define_statement(self, node):
        """
        Interpreta una declaración DEFINE.
        """
        var_name = node['name']
        value = self.evaluate_expression(node.get('value'))
        self.symbol_table[var_name] = value
        logger.info(f"DEFINED: {var_name} = {value}")

    def visit_invoke_statement(self, node):
        """
        Interpreta una declaración INVOKE.
        """
        plugin_name = node['plugin']
        method_name = node['method']
        params = {}
        for param_name, param_node in node.get('params', {}).items():
            params[param_name] = self.evaluate_expression(param_node)

        as_var = node.get('as_var')

        try:
            plugin = plugin_registry.get(plugin_name)
            result = plugin.execute(method_name, params, self.symbol_table)
            if as_var:
                self.symbol_table[as_var] = result
                logger.info(f"INVOKED: {plugin_name}.{method_name} (result stored in {as_var})")
            else:
                logger.info(f"INVOKED: {plugin_name}.{method_name}")
            return result # Devuelve el resultado por si se necesita encadenar llamadas
        except ValueError as e:
            logger.error(f"Plugin Error: {e}")
            raise # Re-lanza para que el TRY/CATCH de GFL pueda capturarlo
        except NotImplementedError as e:
            logger.error(f"Plugin method not implemented: {e}")
            raise
        except Exception as e:
            logger.error(f"Error executing plugin {plugin_name}.{method_name}: {e}", exc_info=True)
            raise

    def visit_message_statement(self, node):
        """
        Interpreta una declaración MESSAGE (actualmente solo para mensajes simples).
        """
        message_value = self.evaluate_expression(node['message'])
        logger.info(f"MESSAGE: {message_value}")

    def visit_branch_statement(self, node):
        """
        Interpreta una declaración BRANCH (IF/THEN/ELSE).
        """
        condition_result = self.evaluate_expression(node['condition'])
        if condition_result:
            logger.info("BRANCH: Condition true, executing THEN branch.")
            self.visit(node['then_branch'])
        elif 'else_branch' in node:
            logger.info("BRANCH: Condition false, executing ELSE branch.")
            self.visit(node['else_branch'])
        else:
            logger.info("BRANCH: Condition false, no ELSE branch to execute.")

    def visit_try_catch_statement(self, node):
        """
        Interpreta una declaración TRY/CATCH.
        """
        logger.info("Entering TRY block...")
        try:
            self.visit(node['try_block'])
            logger.info("TRY block completed successfully.")
        except Exception as e:
            logger.info(f"Caught exception in TRY block: {e}. Executing CATCH block...")
            # Aquí podrías pasar la excepción al bloque catch si GFL lo soportara explícitamente
            self.symbol_table['__last_error__'] = str(e) # Opcional: almacenar el error
            self.visit(node['catch_block'])
            logger.info("CATCH block completed.")

    def evaluate_expression(self, node):
        """
        Evalúa y retorna el valor de una expresión.
        """
        if node['type'] == 'string_literal':
            return node['value']
        elif node['type'] == 'number_literal':
            return node['value']
        elif node['type'] == 'boolean_literal':
            return node['value']
        elif node['type'] == 'variable_access':
            var_name = node['name']
            if var_name in self.symbol_table:
                return self.symbol_table[var_name]
            else:
                logger.error(f"Runtime Error: Undefined variable '{var_name}'.")
                raise NameError(f"Undefined variable '{var_name}'")
        elif node['type'] == 'binary_operation':
            left = self.evaluate_expression(node['left'])
            right = self.evaluate_expression(node['right'])
            op = node['operator']
            
            if op == '+': # Esto ya no se usa, ahora es para números
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                return left / right
            elif op == '&': # Concatenación de cadenas
                return str(left) + str(right)
            elif op == '==':
                return left == right
            elif op == '>':
                return left > right
            elif op == '<':
                return left < right
            elif op == '>=':
                return left >= right
            elif op == '<=':
                return left <= right
            elif op.upper() == 'AND':
                return bool(left) and bool(right)
            elif op.upper() == 'OR':
                return bool(left) or bool(right)
            else:
                logger.error(f"Unsupported binary operator: {op}")
                raise ValueError(f"Unsupported binary operator: {op}")
        elif node['type'] == 'unary_operation':
            operand = self.evaluate_expression(node['operand'])
            op = node['operator']
            if op.upper() == 'NOT':
                return not bool(operand)
            else:
                logger.error(f"Unsupported unary operator: {op}")
                raise ValueError(f"Unsupported unary operator: {op}")
        elif node['type'] == 'array_literal':
            return [self.evaluate_expression(elem) for elem in node.get('elements', [])]
        elif node['type'] == 'object_literal':
            return {key: self.evaluate_expression(value) for key, value in node.get('properties', {}).items()}
        elif node['type'] == 'access_chain':
            # Manejar cadenas de acceso como 'object.property' o 'array[index]'
            base_value = self.evaluate_expression(node['base'])
            for accessor in node['accessors']:
                if accessor['type'] == 'property_access':
                    prop_name = accessor['name']
                    if isinstance(base_value, dict) and prop_name in base_value:
                        base_value = base_value[prop_name]
                    else:
                        logger.error(f"Runtime Error: Cannot access property '{prop_name}' in {base_value}")
                        raise AttributeError(f"Cannot access property '{prop_name}'")
                elif accessor['type'] == 'index_access':
                    index_value = self.evaluate_expression(accessor['index'])
                    if isinstance(base_value, (list, str)) and isinstance(index_value, int):
                        if 0 <= index_value < len(base_value):
                            base_value = base_value[index_value]
                        else:
                            logger.error(f"Runtime Error: Index {index_value} out of bounds for {base_value}")
                            raise IndexError(f"Index {index_value} out of bounds")
                    else:
                        logger.error(f"Runtime Error: Cannot index {type(base_value)} with {type(index_value)}")
                        raise TypeError(f"Cannot index {type(base_value)} with {type(index_value)}")
            return base_value

        logger.error(f"Unknown expression type: {node['type']}")
        raise ValueError(f"Unknown expression type: {node['type']}")
