
import importlib.util
import os
from BaseMCP import BaseMCP

class GestorAgentes:
    def __init__(self, ruta=".", api_key=""):
        self.ruta = ruta
        self.api_key = api_key
        self.mcp_activos = []

    def cargar_agentes(self):
        archivos = os.listdir(self.ruta)
        for archivo in archivos:
            if archivo.startswith("MCP") and archivo.endswith(".py") and archivo != "BaseMCP.py":
                nombre_modulo = archivo[:-3]
                ruta_modulo = os.path.join(self.ruta, archivo)
                print(f"🔍 Explorando: {nombre_modulo}")

                spec = importlib.util.spec_from_file_location(nombre_modulo, ruta_modulo)
                modulo = importlib.util.module_from_spec(spec)

                try:
                    spec.loader.exec_module(modulo)
                    for nombre_clase in dir(modulo):
                        clase = getattr(modulo, nombre_clase)
                        if (
                            isinstance(clase, type)
                            and issubclass(clase, BaseMCP)
                            and clase is not BaseMCP
                        ):
                            print(f"✔️ Encontrado MCP: {nombre_clase}")
                            try:
                                if "LLMThoughtAgent" in nombre_clase:
                                    instancia = clase(nombre_modulo, api_key=self.api_key)
                                else:
                                    instancia = clase(nombre_modulo)
                                self.mcp_activos.append(instancia)
                                print(f"✅ Cargado: {instancia.nombre}")
                            except Exception as init_error:
                                print(f"❌ Error al inicializar {nombre_clase}: {init_error}")
                except Exception as e:
                    print(f"⚠️ No se pudo cargar {archivo}: {e}")

    def evaluar_pensamiento(self, pensamiento):
        resultado = pensamiento
        for mcp in self.mcp_activos:
            if mcp.activo:
                resultado = mcp.evaluar(resultado)
        return resultado
