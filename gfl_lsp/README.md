# GFL Language Server Protocol

Este es el servidor LSP (Language Server Protocol) para GeneForgeLang (GFL). Proporciona diagnósticos de errores en tiempo real, validación semántica y análisis de código GFL.

## Instalación

El servidor LSP ya está instalado en el sistema. Puedes verificarlo ejecutando:

```bash
gfl-lsp-server --help
```

## Uso

### Con VS Code

1. Abre VS Code en el directorio del proyecto
2. El servidor LSP se configurará automáticamente usando el archivo `.vscode/settings.json`
3. Abre cualquier archivo `.gfl` para ver los diagnósticos en tiempo real

### Con otros editores

El servidor LSP es compatible con cualquier editor que soporte LSP. Configura tu editor para usar el comando:

```
gfl-lsp-server
```

## Características

- **Validación en tiempo real**: Detecta errores de sintaxis y semántica mientras escribes
- **Diagnósticos detallados**: Muestra errores con códigos específicos y sugerencias de corrección
- **Soporte completo de GFL**: Reconoce todos los bloques de GFL (experiment, analyze, simulate, etc.)
- **Validación semántica**: Verifica que los parámetros y herramientas sean válidos

## Archivo de prueba

Se incluye un archivo `test_example.gfl` que demuestra las capacidades del servidor LSP.

## Estructura del proyecto

```
gfl_lsp/
├── pyproject.toml          # Configuración del paquete
├── gfl_lsp/
│   ├── __init__.py
│   └── server/
│       ├── __init__.py
│       └── main.py         # Implementación del servidor LSP
├── test_example.gfl        # Archivo de prueba
├── .vscode/
│   └── settings.json       # Configuración para VS Code
└── README.md              # Este archivo
```

## Desarrollo

Para modificar el servidor LSP:

1. Edita `gfl_lsp/server/main.py`
2. Reinstala el paquete: `pip install -e .`
3. Reinicia tu editor

El servidor utiliza la librería GFL existente para el parsing y validación, proporcionando una interfaz LSP estándar.
