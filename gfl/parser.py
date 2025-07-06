# gfl/parser.py

import ply.yacc as yacc
from .lexer import lexer # Importa la instancia del lexer desde lexer.py

# Helper function to get line number and column from token
def _get_line_col(p, idx=1):
    if hasattr(p[idx], 'lineno') and hasattr(p[idx], 'lexpos') and hasattr(p.lexer, 'lexdata'):
        # Calculate column based on lexpos and the start of the line
        line_start = p.lexer.lexdata.rfind('\n', 0, p[idx].lexpos)
        if line_start == -1: # If no newline before, it's the first line (column starts from 1)
            line_start = 0
        column = (p[idx].lexpos - line_start) + 1 # +1 for 1-based column number
        return p[idx].lineno, column
    return 'N/A', 'N/N' # Fallback for tokens without lineno or lexpos

# Precedencia de operadores (de menor a mayor)
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('left', 'EQUALS_EQUALS', 'NOT_EQUALS', 'GREATER_THAN', 'LESS_THAN', 'LTE', 'GTE'), # Comparaciones
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

# --- Parser Definition ---

class GFLParser:
    """
    GFL (GeneForge Language) Parser using PLY.
    """
    # Define tokens directamente dentro de la clase del parser
    # PLY los encontrará automáticamente cuando uses yacc.yacc(module=self)
    tokens = [
        'DEFINE', 'INVOKE', 'MESSAGE', 'IF', 'THEN', 'ELSE', 'END', 'BRANCH',
        'TRY', 'CATCH', 'AS', 'BASED_ON', 'NOT',
        'EQUALS_EQUALS', 'NOT_EQUALS', 'LTE', 'GTE', 'GREATER_THAN', 'LESS_THAN', # Operadores de comparación
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'EQUALS', 'DOT', 'AMPERSAND',
        'LPAREN', 'RPAREN', 'COMMA', 'COLON',
        'LBRACKET', 'RBRACKET', 'LCURLY', 'RCURLY',
        'AND', 'OR',
        'TRUE', 'FALSE',
        'ANALYZE', 'USING', 'WITH', 'STRATEGY', 'PARAMS', # New tokens for analyze statement
        'EXPERIMENT', 'SIMULATE',
        'LINE_COMMENT',
        'BLOCK_COMMENT',
        'ID', 'STRING', 'NUMBER' # ID, STRING, NUMBER deben ser los últimos
    ]

    def __init__(self, lexer_instance):
        self.lexer = lexer_instance
        # PLY ahora encontrará GFLParser.tokens automáticamente
        self.parser = yacc.yacc(module=self, start='program', debug=True)
        self.operations = [] # Stores the parsed operations/AST
        self.errors = []     # Stores parsing errors

        # Basic validation data (can be expanded)
        self.valid_sim_targets = ["cell_growth", "apoptosis", "cell_division", "mutation_rate", "gene_expression"]
        self.valid_analyze_strategies = {
            "pathway_enrichment": ["FDR", "threshold"],
            "clustering": ["resolution"],
            "differential_expression": ["threshold", "log2FC", "condition_group", "control_group"],
            "few_shot_diagnosis": ["phenotype_terms", "candidate_genes", "tool"]
        }
        self.valid_analyze_tools = ["DESeq2", "Scanpy", "SHEPHERD"] # New valid tools

    def parse(self, code):
        """
        Parses the given GFL code.
        """
        self.operations = []
        self.errors = []
        self.lexer.lineno = 1
        self.lexer.lexpos = 0 # Reset lex position as well
        # Construye el parser cada vez para un estado fresco (opcional, para robustez)
        # PLY buscará 'self.tokens' para la lista de tokens
        self.parser = yacc.yacc(module=self, start='program', debug=True)
        return self.parser.parse(code, lexer=self.lexer)

    # --- GFL Grammar Rules ---

    def p_program(self, p):
        '''
        program : statements
        '''
        self.operations = p[1]

    def p_statements(self, p):
        '''
        statements : statement
                   | statements statement
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_statement(self, p):
        '''
        statement : analyze_statement
                  | experiment_statement
                  | simulate_statement
                  | branch_statement
                  | phenotype_analyze_statement
                  | analyze_statement_inline
        '''
        p[0] = p[1]


    # New rule for inline analyze statement
    def p_analyze_statement_inline(self, p):
        '''
        analyze_statement_inline : ANALYZE USING ID WITH STRATEGY ID PARAMS LCURLY properties RCURLY
        '''
        tool = p[3]
        strategy = p[6]
        params = p[9] # <-- ¡CORREGIDO! Antes era p[8]

        lineno, column = _get_line_col(p, 1)

        # Validation for tool and strategy
        if tool not in self.valid_analyze_tools:
            self.errors.append(f"Warning: Unknown analysis tool '{tool}' at line {lineno}, column {column}. Valid tools are: {', '.join(self.valid_analyze_tools)}")
        if strategy not in self.valid_analyze_strategies:
            self.errors.append(f"Warning: Unknown analysis strategy '{strategy}' at line {lineno}, column {column}. Valid strategies are: {', '.join(self.valid_analyze_strategies.keys())}")
        else:
            for param_key in params.keys():
                if param_key not in self.valid_analyze_strategies[strategy]:
                    self.errors.append(f"Warning: Unknown parameter '{param_key}' for strategy '{strategy}' at line {lineno}, column {column}. Valid parameters for '{strategy}' are: {', '.join(self.valid_analyze_strategies[strategy])}")

        p[0] = {
            'type': 'analyze_inline',
            'tool': tool,
            'strategy': strategy,
            'params': params,
            'location': {'line': lineno, 'column': column}
        }


    def p_analyze_statement(self, p):
        '''
        analyze_statement : ANALYZE LCURLY properties RCURLY
        '''
        lineno, column = _get_line_col(p, 1)
        p[0] = {'type': 'analyze', 'properties': p[3], 'location': {'line': lineno, 'column': column}}

        # Basic validation for analyze statement properties
        strategy = p[3].get('strategy')
        if strategy and strategy not in self.valid_analyze_strategies:
            self.errors.append(f"Warning: Unknown analysis strategy '{strategy}' at line {lineno}, column {column}. Valid strategies are: {', '.join(self.valid_analyze_strategies.keys())}")
        elif strategy:
            # Validate parameters within the strategy
            strategy_params = self.valid_analyze_strategies.get(strategy, [])
            for prop_key, prop_value in p[3].items():
                if prop_key == 'thresholds' and isinstance(prop_value, dict):
                    for threshold_key in prop_value.keys():
                        if threshold_key not in strategy_params:
                            self.errors.append(f"Warning: Unknown threshold parameter '{threshold_key}' for strategy '{strategy}' at line {lineno}, column {column}. Valid parameters for '{strategy}' are: {', '.join(strategy_params)}")
                elif prop_key != 'strategy' and prop_key not in strategy_params:
                     self.errors.append(f"Warning: Unknown parameter '{prop_key}' for strategy '{strategy}' at line {lineno}, column {column}. Valid parameters for '{strategy}' are: {', '.join(strategy_params)}")


    def p_experiment_statement(self, p):
        '''
        experiment_statement : EXPERIMENT LCURLY properties RCURLY
        '''
        lineno, column = _get_line_col(p, 1)
        p[0] = {'type': 'experiment', 'properties': p[3], 'location': {'line': lineno, 'column': column}}

    def p_simulate_statement(self, p):
        '''
        simulate_statement : SIMULATE ID
        '''
        lineno, column = _get_line_col(p, 1)
        p[0] = {'type': 'simulate', 'target': p[2], 'location': {'line': lineno, 'column': column}}

    def p_branch_statement(self, p):
        '''
        branch_statement : BRANCH LCURLY IF COLON expression THEN COLON LCURLY statements RBRACKET
                         | BRANCH LCURLY IF COLON expression THEN COLON LCURLY statements RBRACKET ELSE COLON LCURLY statements RBRACKET
        '''
        lineno, column = _get_line_col(p, 1)
        branch_info = {
            'type': 'branch',
            'condition': p[5],
            'then_block': p[9],
            'location': {'line': lineno, 'column': column}
        }
        if len(p) > 10: # Check for ELSE block
            branch_info['else_block'] = p[13]
        p[0] = branch_info

    def p_phenotype_analyze_statement(self, p):
        '''
        phenotype_analyze_statement : ANALYZE LCURLY properties RCURLY
        '''
        lineno, column = _get_line_col(p, 1)
        p[0] = {'type': 'phenotype_analyze', 'properties': p[3], 'location': {'line': lineno, 'column': column}}


    def p_expression(self, p):
        '''
        expression : ID
                   | expression AND expression
                   | expression OR expression
                   | NOT expression
                   | LPAREN expression RPAREN
        '''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            p[0] = {'operator': p[2], 'left': p[1], 'right': p[3]}
        elif len(p) == 3: # NOT expression
            p[0] = {'operator': p[1], 'operand': p[2]}

    def p_properties(self, p):
        '''
        properties : property
                   | properties COMMA property
        '''
        if len(p) == 2:
            p[0] = {p[1]['key']: p[1]['value']}
        else:
            p[0] = p[1]
            p[0][p[3]['key']] = p[3]['value']

    def p_property(self, p):
        '''
        property : ID COLON value
        '''
        p[0] = {'key': p[1], 'value': p[3]}

    def p_value(self, p):
        '''
        value : ID
              | STRING
              | NUMBER
              | boolean_value
              | LCURLY properties RCURLY
              | list_value
        '''
        if p[1] == '{': # For nested properties
            p[0] = p[2]
        else:
            p[0] = p[1]

    def p_list_value(self, p):
        '''
        list_value : LBRACKET RBRACKET
                   | LBRACKET elements RBRACKET
        '''
        if len(p) == 3:
            p[0] = []
        else:
            p[0] = p[2]

    def p_elements(self, p):
        '''
        elements : value
                 | elements COMMA value
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_boolean_value(self, p):
        '''
        boolean_value : TRUE
                      | FALSE
        '''
        p[0] = True if p[1].lower() == 'true' else False

    # Manejo de errores
    def p_error(self, p):
        if p:
            # Calculate column manually as p.lexer.find_column does not exist
            line_start = self.lexer.lexdata.rfind('\n', 0, p.lexpos)
            if line_start == -1:
                line_start = 0
            column = (p.lexpos - line_start) + 1

            print(f"Error de sintaxis en el token '{p.value}' en la línea {p.lineno} en la posición {column}.")
        else:
            print("Error de sintaxis al final del archivo (posiblemente un archivo vacío o un error de sintaxis incompleto).")


# Bloque de código para probar el parser
if __name__ == '__main__':
    test_code = r"""
DEFINE myAge = 30
MESSAGE "Mi edad es: " & myAge
IF myAge > 25 THEN
    MESSAGE "Eres mayor que 25."
ELSE
    MESSAGE "Eres 25 o menor."
END

BRANCH validate_input {
    INVOKE process_data()
}
TRY
    INVOKE process_data()
CATCH InvalidInput AS err
    MESSAGE "Error de entrada: " & err
END
ANALYZE security_log BASED_ON user_activity
ANALYZE USING DESeq2 WITH STRATEGY differential_expression PARAMS {
    threshold: 0.05,
    log2FC: 1.0,
    condition_group: "treated",
    control_group: "untreated"
}
    """
    # Instanciar el parser con el lexer
    gfl_parser = GFLParser(lexer)
    parsed_ast = gfl_parser.parse(test_code)

    print("\n--- GFL Parser Demo ---")
    print(f"\nParsing gfl/gfl_example.gfl (Snippet 1):\n----------------------------------------\n{test_code}\n----------------------------------------")


    print("\nÁrbol de Sintaxis Abstracta (AST) generado:")
    if parsed_ast:
        import json
        print(json.dumps(parsed_ast, indent=2))
        if gfl_parser.errors:
            print("\nErrores/Advertencias detectadas durante el parseo:")
            for error in gfl_parser.errors:
                print(f"- {error}")
    else:
        print("No se pudo generar el AST (puede haber errores de sintaxis o que el archivo de prueba esté vacío).")
