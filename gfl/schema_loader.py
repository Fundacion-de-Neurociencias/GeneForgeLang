"""Schema loader for GeneForgeLang type definitions.

This module provides functionality to load and parse external schema definition
files that define custom data types and their attributes for use in IO contracts.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from gfl.error_handling import (
    EnhancedValidationResult,
    ErrorCodes,
    ErrorSeverity,
)

logger = logging.getLogger(__name__)


class SchemaDefinition:
    """Represents a schema definition loaded from a YAML file."""

    def __init__(self, name: str, type_info: Dict[str, Any]):
        """Initialize a schema definition.

        Args:
            name: The name of the schema type
            type_info: Dictionary containing type and attributes information
        """
        self.name = name
        self.base_type = type_info.get("type")
        self.attributes = type_info.get("attributes", {})
        self.description = type_info.get("description", "")

    def validate_definition(self, result: EnhancedValidationResult) -> bool:
        """Validate the schema definition structure.

        Args:
            result: Validation result to add errors to

        Returns:
            True if valid, False otherwise
        """
        is_valid = True

        if not self.base_type:
            error = result.add_error(
                f"Schema '{self.name}' missing required 'type' field",
                ErrorCodes.SCHEMA_MISSING_PROPERTY,
                ErrorSeverity.ERROR,
            )
            error.add_fix(f"Add 'type: <base_type>' to schema '{self.name}'")
            is_valid = False

        if not isinstance(self.base_type, str):
            error = result.add_error(
                f"Schema '{self.name}' type must be a string",
                ErrorCodes.TYPE_INVALID_TYPE,
                ErrorSeverity.ERROR,
            )
            error.add_fix(f"Change type to a string value in schema '{self.name}'")
            is_valid = False

        if not isinstance(self.attributes, dict):
            error = result.add_error(
                f"Schema '{self.name}' attributes must be a dictionary",
                ErrorCodes.SCHEMA_INVALID_FORMAT,
                ErrorSeverity.ERROR,
            )
            error.add_fix(f"Format attributes as a dictionary in schema '{self.name}'")
            is_valid = False

        # Validate each attribute definition
        for attr_name, attr_def in self.attributes.items():
            if not isinstance(attr_def, dict):
                error = result.add_error(
                    f"Attribute '{attr_name}' in schema '{self.name}' must be a dictionary",
                    ErrorCodes.SCHEMA_INVALID_FORMAT,
                    ErrorSeverity.ERROR,
                )
                error.add_fix(f"Format attribute '{attr_name}' as a dictionary with type and required fields")
                is_valid = False
                continue

            # Check required fields in attribute definition
            if "type" not in attr_def:
                error = result.add_error(
                    f"Attribute '{attr_name}' in schema '{self.name}' missing required 'type' field",
                    ErrorCodes.SCHEMA_MISSING_PROPERTY,
                    ErrorSeverity.ERROR,
                )
                error.add_fix(f"Add 'type: <attr_type>' to attribute '{attr_name}' in schema '{self.name}'")
                is_valid = False

        return is_valid


class SchemaLoader:
    """Loader for external schema definition files."""

    def __init__(self):
        """Initialize the schema loader."""
        self.schemas: Dict[str, SchemaDefinition] = {}
        self.loaded_files: List[str] = []

    def load_schema_file(self, file_path: Union[str, Path], result: EnhancedValidationResult) -> bool:
        """Load and parse a schema definition file.

        Args:
            file_path: Path to the schema definition file
            result: Validation result to add errors to

        Returns:
            True if loaded successfully, False otherwise
        """
        file_path = Path(file_path)

        # Check if file exists
        if not file_path.exists():
            error = result.add_error(
                f"Schema file not found: {file_path}",
                ErrorCodes.SCHEMA_VALIDATION_FAILED,
                ErrorSeverity.ERROR,
            )
            error.add_fix(f"Ensure schema file exists at {file_path}")
            return False

        # Check if already loaded
        if str(file_path) in self.loaded_files:
            logger.debug(f"Schema file already loaded: {file_path}")
            return True

        try:
            # Load YAML content
            with open(file_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)

            if not isinstance(content, dict):
                error = result.add_error(
                    f"Schema file {file_path} must contain a dictionary at root level",
                    ErrorCodes.SCHEMA_INVALID_FORMAT,
                    ErrorSeverity.ERROR,
                )
                error.add_fix("Format the schema file as a YAML dictionary with 'schemas' key")
                return False

            # Check for schemas key
            if "schemas" not in content:
                error = result.add_error(
                    f"Schema file {file_path} missing required 'schemas' key",
                    ErrorCodes.SCHEMA_MISSING_PROPERTY,
                    ErrorSeverity.ERROR,
                )
                error.add_fix("Add 'schemas:' at the root of the schema file")
                return False

            schemas_section = content["schemas"]
            if not isinstance(schemas_section, dict):
                error = result.add_error(
                    f"Schema file {file_path} 'schemas' section must be a dictionary",
                    ErrorCodes.SCHEMA_INVALID_FORMAT,
                    ErrorSeverity.ERROR,
                )
                error.add_fix("Format the 'schemas' section as a dictionary of schema definitions")
                return False

            # Process each schema definition
            for schema_name, schema_info in schemas_section.items():
                if not isinstance(schema_info, dict):
                    error = result.add_error(
                        f"Schema '{schema_name}' in {file_path} must be a dictionary",
                        ErrorCodes.SCHEMA_INVALID_FORMAT,
                        ErrorSeverity.ERROR,
                    )
                    error.add_fix(f"Format schema '{schema_name}' as a dictionary with type and attributes")
                    continue

                # Create schema definition
                schema_def = SchemaDefinition(schema_name, schema_info)

                # Validate the schema definition
                if schema_def.validate_definition(result):
                    self.schemas[schema_name] = schema_def

            # Mark file as loaded
            self.loaded_files.append(str(file_path))
            logger.info(f"Successfully loaded schema file: {file_path}")
            return True

        except yaml.YAMLError as e:
            error = result.add_error(
                f"Error parsing schema file {file_path}: {e}",
                ErrorCodes.SYNTAX_INVALID_YAML,
                ErrorSeverity.CRITICAL,
            )
            error.add_fix("Fix YAML syntax errors in the schema file")
            return False
        except Exception as e:
            error = result.add_error(
                f"Error loading schema file {file_path}: {e}",
                ErrorCodes.SCHEMA_VALIDATION_FAILED,
                ErrorSeverity.ERROR,
            )
            error.add_fix("Check file permissions and format")
            return False

    def get_schema(self, schema_name: str) -> Optional[SchemaDefinition]:
        """Get a schema definition by name.

        Args:
            schema_name: Name of the schema to retrieve

        Returns:
            SchemaDefinition if found, None otherwise
        """
        return self.schemas.get(schema_name)

    def get_all_schemas(self) -> Dict[str, SchemaDefinition]:
        """Get all loaded schema definitions.

        Returns:
            Dictionary of all schema definitions
        """
        return self.schemas.copy()

    def clear(self) -> None:
        """Clear all loaded schemas."""
        self.schemas.clear()
        self.loaded_files.clear()


# Global schema loader instance
_schema_loader = SchemaLoader()


def get_global_schema_loader() -> SchemaLoader:
    """Get the global schema loader instance.

    Returns:
        Global SchemaLoader instance
    """
    return _schema_loader


def load_schemas_from_files(file_paths: List[Union[str, Path]], result: EnhancedValidationResult) -> bool:
    """Load schemas from multiple files.

    Args:
        file_paths: List of paths to schema files
        result: Validation result to add errors to

    Returns:
        True if all files loaded successfully, False otherwise
    """
    loader = get_global_schema_loader()
    all_success = True

    for file_path in file_paths:
        if not loader.load_schema_file(file_path, result):
            all_success = False

    return all_success


__all__ = [
    "SchemaDefinition",
    "SchemaLoader",
    "get_global_schema_loader",
    "load_schemas_from_files",
]
