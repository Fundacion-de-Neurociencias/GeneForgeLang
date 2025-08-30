"""
GeneForgeLang public API: YAML parser and optional NL translator.
"""
import importlib.util

from .yaml_lang.parser import (
    parse_text as parse_gfl_yaml,
    parse_file as parse_gfl_yaml_file,
    GflYamlParseError,
    YamlParseError,
)

__all__ = [
    "parse_gfl_yaml",
    "parse_gfl_yaml_file",
    "GflYamlParseError",
    "YamlParseError",
]

_has_transformers = importlib.util.find_spec("transformers") is not None
if _has_transformers:
    try:
        from .nl.translator_t5 import LanguageTranslator
        __all__.append("LanguageTranslator")
    except Exception:
        pass
