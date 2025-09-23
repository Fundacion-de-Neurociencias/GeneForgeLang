# Uso de la Plantilla CookieCutter para Plugins GFL

## Instalación de CookieCutter

```bash
pip install cookiecutter
```

## Generar un Nuevo Plugin

```bash
cookiecutter cookiecutter-gfl-plugin/
```

CookieCutter te pedirá los siguientes valores:

- `plugin_name`: Nombre del plugin (ej: `gfl-plugin-blast`)
- `version`: Versión inicial (ej: `0.1.0`)
- `description`: Descripción del plugin
- `author_name`: Tu nombre
- `author_email`: Tu email

## Ejemplo de Uso

```bash
$ cookiecutter cookiecutter-gfl-plugin/
plugin_name [gfl-plugin-example]: gfl-plugin-blast
version [0.1.0]: 0.1.0
description [A new plugin for GeneForgeLang.]: BLAST sequence analysis plugin for GFL
author_name [Your Name]: Dr. Smith
author_email [your.email@example.com]: dr.smith@example.com
```

Esto creará un directorio `gfl-plugin-blast/` con toda la estructura necesaria.

## Estructura Generada

```
gfl-plugin-blast/
├── pyproject.toml          # Configuración del paquete
├── README.md               # Documentación
└── gfl_plugin_blast/       # Módulo Python
    ├── __init__.py
    └── plugin.py           # Implementación del plugin
```

## Desarrollo del Plugin

1. **Editar `plugin.py`**: Implementar la lógica específica del plugin
2. **Añadir dependencias**: Actualizar `pyproject.toml` con las dependencias necesarias
3. **Escribir tests**: Añadir tests en el directorio del plugin
4. **Documentar**: Actualizar README.md con instrucciones específicas

## Instalación del Plugin

```bash
cd gfl-plugin-blast
pip install -e .
```

## Integración con GFL

El plugin se puede usar en workflows GFL:

```python
from gfl_plugin_blast import BlastPlugin

plugin = BlastPlugin()
result = plugin.run(sequence_data, params={"database": "nt"})
```
