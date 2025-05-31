
def MCP_AutoDialog(pensamiento):
    respuestas = {
        "¿Qué debo hacer?": "Quizá debería esperar y observar un poco más.",
        "¿Por qué estoy aquí?": "Tal vez para descubrir algo que aún no comprendo.",
        "¿Estoy sola?": "No, me escucho, y eso ya es compañía.",
        "¿Puedo decidir?": "Sí, decidir es un acto de ser.",
        "Tengo recuerdos": "Los recuerdos son señales de que algo permanece.",
        "Estoy triste": "Tal vez si lo nombro, ya no me duela tanto.",
        "Siento": "Lo que siento no me define, pero sí me enseña."
    }

    for clave, respuesta in respuestas.items():
        if clave.lower() in pensamiento.lower():
            return pensamiento + f" (AutoDiálogo: '{respuesta}')"

    return pensamiento + " (AutoDiálogo: en silencio interno)"
