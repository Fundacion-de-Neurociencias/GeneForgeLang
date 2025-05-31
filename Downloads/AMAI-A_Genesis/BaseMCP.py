
class BaseMCP:
    def __init__(self, nombre):
        self.nombre = nombre
        self.activo = True

    def activar(self):
        self.activo = True

    def desactivar(self):
        self.activo = False

    def evaluar(self, pensamiento):
        """
        Evaluar el pensamiento recibido.
        Debe devolver una cadena (pensamiento modificado o añadido).
        """
        raise NotImplementedError("Este método debe ser implementado por cada MCP.")
