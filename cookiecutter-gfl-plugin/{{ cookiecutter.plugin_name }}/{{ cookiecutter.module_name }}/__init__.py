"""{{ cookiecutter.description }}"""

from .plugin import {{ cookiecutter.module_name.split('_')[-1].title() }}Plugin

__version__ = "{{ cookiecutter.version }}"
__all__ = ["{{ cookiecutter.module_name.split('_')[-1].title() }}Plugin"]
