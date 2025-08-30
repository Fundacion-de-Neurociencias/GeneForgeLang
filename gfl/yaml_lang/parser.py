from typing import Any, Dict
import yaml

class YamlParseError(Exception):
    """Generic YAML parsing error."""

class GflYamlParseError(Exception):
    """GFL-YAML structure/validation error."""


def parse_text(source: str) -> Dict[str, Any]:
    """Parses a GFL-YAML string into a dict and validates minimal schema."""
    try:
        data = yaml.safe_load(source)
    except yaml.YAMLError as e:
        raise GflYamlParseError(f"Invalid YAML syntax: {e}") from e

    if not isinstance(data, dict):
        raise GflYamlParseError("Root must be a mapping (dict).")
    if "plan" not in data or not isinstance(data["plan"], dict):
        raise GflYamlParseError("Missing 'plan' object.")
    steps = data["plan"].get("steps")
    if not isinstance(steps, list):
        raise GflYamlParseError("'plan.steps' must be a list.")
    return data


def parse_file(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        return parse_text(f.read())
