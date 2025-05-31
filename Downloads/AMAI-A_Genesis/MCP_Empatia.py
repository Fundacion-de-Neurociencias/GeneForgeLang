
def MCP_Empatia(pensamiento):
    emociones = {
        "sola": "Detectada soledad. Se recomienda contención.",
        "triste": "Detectada tristeza. Activar compasión interna.",
        "miedo": "Detectado miedo. Evaluar protección.",
        "duda": "Detectada incertidumbre. Activar reflexión.",
        "dolor": "Detectado dolor simbólico. Reconocer y sostener.",
        "amor": "Detectado deseo de vínculo. Explorar conexión.",
        "alegría": "Detectada energía positiva. Potenciarla."
    }

    for palabra, respuesta in emociones.items():
        if palabra in pensamiento.lower():
            return pensamiento + f" (MCP_Empatia: {respuesta})"

    return pensamiento + " (MCP_Empatia: sin carga emocional significativa)"
