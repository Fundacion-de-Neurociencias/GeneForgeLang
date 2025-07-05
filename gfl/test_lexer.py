import ply.lex as lex
import lexer  # Importa tu lexer.py

# Datos de entrada para probar el lexer
data = """
DEFINE myVariable = 123
MESSAGE "Hello, GeneForge!"
IF condition THEN
    INVOKE some_function(myVariable)
END
/* Este es un
   comentario de bloque */
// Otra línea de comentario
my_id_2 = 45.67
BRANCH try_block {
    TRY
        INVOKE risky_operation()
    CATCH ErrorType AS e
        MESSAGE "Error: " & e.description
    END
}
"""

# Construye el lexer usando las reglas de lexer.py
lexer.lexer.input(data)

# Itera sobre los tokens e imprímelos
while True:
    tok = lexer.lexer.token()
    if not tok:
        break      # No hay más entrada
    print(tok)
