"""Enhanced semantic validator for GeneForgeLang ASTs.

This module provides comprehensive semantic validation with enhanced error
reporting, including location tracking, error codes, and suggested fixes.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union

from gfl.error_handling import (
    EnhancedValidationResult,
    ErrorCodes,
    ErrorSeverity,
    SourceLocation,
)
from gfl.schema_loader import get_global_schema_loader, load_schemas_from_files

logger = logging.getLogger(__name__)


class EnhancedSemanticValidator:
    """Enhanced semantic validator for GFL ASTs.

    Provides comprehensive semantic validation with rich error reporting,
    including location tracking, error codes, and suggested fixes.
    """

    def __init__(self, file_path: Optional[str] = None):
        """Initialize validator.

        Args:
            file_path: Optional path to the file being validated for error reporting.
        """
        self.symbol_table: dict[str, dict[str, Any]] = {}
        self.result = EnhancedValidationResult(file_path=file_path)
        self.current_block: Optional[str] = None
        self.nested_level = 0
        self.schema_loader = get_global_schema_loader()

    def validate_ast(self, ast: dict[str, Any]) -> EnhancedValidationResult:
        """Validate a GFL AST and return enhanced validation result.

        Args:
            ast: The AST dictionary to validate.

        Returns:
            EnhancedValidationResult with detailed error information.
        """
        self.symbol_table.clear()
        self.result = EnhancedValidationResult(file_path=self.result.file_path)
        self.nested_level = 0
        self.schema_loader.clear()

        try:
            # Load schema imports first
            self._load_schema_imports(ast)

            self._validate_root_structure(ast)
            self._validate_blocks(ast)
        except Exception as e:
            error = self.result.add_error(
                f"Internal validation error: {e}",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
                ErrorSeverity.CRITICAL,
            )
            error.add_context("exception_type", type(e).__name__)

        return self.result

    def _load_schema_imports(self, ast: dict[str, Any]) -> None:
        """Load schema imports from the AST.

        Args:
            ast: The AST dictionary to process.
        """
        if "import_schemas" not in ast:
            return

        import_schemas = ast["import_schemas"]
        if not isinstance(import_schemas, list):
            error = self.result.add_error(
                "import_schemas must be a list of file paths",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            )
            error.add_fix("Format import_schemas as a list of schema file paths")
            return

        # Resolve file paths relative to the GFL file location
        base_path = os.path.dirname(self.result.file_path) if self.result.file_path else "."

        schema_files = []
        for schema_path in import_schemas:
            if not isinstance(schema_path, str):
                error = self.result.add_error(
                    f"Schema path must be a string, got {type(schema_path).__name__}",
                    ErrorCodes.TYPE_INVALID_TYPE,
                )
                error.add_fix("Use string values for schema file paths")
                continue

            # Resolve relative paths
            resolved_path = os.path.join(base_path, schema_path) if not os.path.isabs(schema_path) else schema_path

            schema_files.append(resolved_path)

        # Load all schema files
        load_schemas_from_files(schema_files, self.result)

    def _validate_root_structure(self, ast: dict[str, Any]) -> None:
        """Validate the root structure of the AST."""
        if not isinstance(ast, dict):
            self.result.add_error(
                "AST must be a dictionary",
                ErrorCodes.SYNTAX_INVALID_STRUCTURE,
                ErrorSeverity.CRITICAL,
            )
            return

        # Check for at least one main block
        main_blocks = {
            "experiment",
            "analyze",
            "simulate",
            "branch",
            "design",
            "optimize",
            "refine_data",
            "guided_discovery",
            "rules",
            "hypothesis",
            "timeline",
            "pathways",
            "complexes",
        }
        found_blocks = set(ast.keys()) & main_blocks

        if not found_blocks:
            error = self.result.add_error(
                "GFL document must contain at least one main block",
                ErrorCodes.SEMANTIC_MISSING_EXPERIMENT_BLOCK,
                ErrorSeverity.ERROR,
            )
            error.add_fix(
                "Add an 'experiment', 'analyze', 'simulate', 'design', 'optimize', 'refine_data', 'guided_discovery', 'rules', 'hypothesis', 'timeline', 'pathways', or 'complexes' block"
            )
            error.add_context("available_blocks", list(main_blocks))

        # Check for unknown top-level keys
        valid_top_level = main_blocks | {"metadata", "imports", "exports"}
        unknown_keys = set(ast.keys()) - valid_top_level

        for key in unknown_keys:
            error = self.result.add_error(
                f"Unknown top-level block '{key}'",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
                ErrorSeverity.WARNING,
            )
            error.add_fix(f"Remove '{key}' or move it to the metadata block")
            error.add_context("valid_blocks", list(valid_top_level))

    def _validate_blocks(self, ast: dict[str, Any]) -> None:
        """Validate individual blocks in the AST."""
        # First, collect entity definitions for reference validation
        self._collect_entity_definitions(ast)

        # Collect hypothesis definitions for reference validation
        self._collect_hypothesis_definitions(ast)

        for block_name, block_content in ast.items():
            self.current_block = block_name

            if block_name == "experiment":
                self._validate_experiment_block(block_content)
                # Store contract for compatibility checking
                if isinstance(block_content, dict) and "contract" in block_content:
                    self._store_block_contract(block_name, block_content["contract"])
            elif block_name == "analyze":
                self._validate_analysis_block(block_content)
                # Store contract for compatibility checking
                if isinstance(block_content, dict) and "contract" in block_content:
                    self._store_block_contract(block_name, block_content["contract"])
            elif block_name == "design":
                self._validate_design_block(block_content)
            elif block_name == "optimize":
                self._validate_optimize_block(block_content)
            elif block_name == "simulate":
                self._validate_simulate_block(block_content)
            elif block_name == "branch":
                self._validate_branch_block(block_content)
            elif block_name == "refine_data":
                self._validate_refine_data_block(block_content)
            elif block_name == "guided_discovery":
                self._validate_guided_discovery_block(block_content)
            elif block_name == "metadata":
                self._validate_metadata_block(block_content)
            elif block_name == "rules":
                self._validate_rules_block(block_content)
            elif block_name == "hypothesis":
                self._validate_hypothesis_block(block_content)
            elif block_name == "timeline":
                self._validate_timeline_block(block_content)
            elif block_name == "pathways":
                # Pathways are validated during collection
                pass
            elif block_name == "complexes":
                # Complexes are validated during collection
                pass

    def _collect_entity_definitions(self, ast: dict[str, Any]) -> None:
        """Collect pathway and complex definitions for reference validation."""
        self.entity_registry = {}

        # Debug: Print AST
        print(f"AST keys: {list(ast.keys())}")

        # Collect pathways
        if "pathways" in ast:
            print("Found pathways in AST")
            pathways = ast["pathways"]
            if not isinstance(pathways, dict):
                self.result.add_error(
                    "Pathways block must be a dictionary",
                    ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
                ).add_fix("Format pathways as a dictionary mapping names to pathway definitions")
            else:
                self.entity_registry["pathways"] = pathways
                # Validate pathway structure
                for pathway_name, pathway_def in pathways.items():
                    if not isinstance(pathway_def, dict):
                        self.result.add_error(
                            f"Pathway '{pathway_name}' must be a dictionary",
                            ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
                        ).add_fix(f"Format pathway '{pathway_name}' as a dictionary")

        # Collect complexes
        if "complexes" in ast:
            print("Found complexes in AST")
            complexes = ast["complexes"]
            if not isinstance(complexes, dict):
                self.result.add_error(
                    "Complexes block must be a dictionary",
                    ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
                ).add_fix("Format complexes as a dictionary mapping names to complex definitions")
            else:
                self.entity_registry["complexes"] = complexes
                # Validate complex structure
                for complex_name, complex_def in complexes.items():
                    if not isinstance(complex_def, dict):
                        self.result.add_error(
                            f"Complex '{complex_name}' must be a dictionary",
                            ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
                        ).add_fix(f"Format complex '{complex_name}' as a dictionary")

        # Debug: Print entity registry contents
        print(f"Collected entity registry: {self.entity_registry}")

    def _validate_entity_reference(self, entity_ref: str) -> None:
        """Validate entity reference in parameter values."""
        import re

        # Extract entity type and name
        match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\(([a-zA-Z_][a-zA-Z0-9_]*)\)$", entity_ref)
        if not match:
            self.result.add_error(
                f"Invalid entity reference format: {entity_ref}",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            ).add_fix("Use format 'entity_type(entity_name)' for entity references")
            return

        entity_type, entity_name = match.groups()

        # Check if entity type is supported
        supported_entity_types = {"pathway", "complex"}
        if entity_type not in supported_entity_types:
            self.result.add_error(
                f"Unsupported entity type '{entity_type}' in reference: {entity_ref}",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            ).add_fix(f"Use one of the supported entity types: {', '.join(supported_entity_types)}")
            return

        # Check if entity is defined
        if hasattr(self, "entity_registry"):
            # Debug: Print entity registry contents
            print(f"Entity registry: {self.entity_registry}")
            print(f"Looking for entity type: {entity_type}")
            print(f"Looking for entity name: {entity_name}")

            registry_key = entity_type + "s"  # "pathway" -> "pathways", "complex" -> "complexes"
            # Fix for complex -> complexes
            if entity_type == "complex":
                registry_key = "complexes"
            print(f"Registry key: {registry_key}")
            if registry_key in self.entity_registry:
                print(f"Found registry key: {registry_key}")
                print(f"Available entities: {list(self.entity_registry[registry_key].keys())}")
                if entity_name in self.entity_registry[registry_key]:
                    print(f"Found entity: {entity_name}")
                    return  # Valid reference
                else:
                    self.result.add_error(
                        f"Referenced {entity_type} '{entity_name}' is not defined",
                        ErrorCodes.SEMANTIC_UNDEFINED_ENTITY_REFERENCE,
                    ).add_fix(f"Define a {entity_type} with name '{entity_name}' or reference an existing one")
            else:
                # Entity type registry doesn't exist
                self.result.add_error(
                    f"Referenced {entity_type} '{entity_name}' is not defined (no {entity_type} definitions found)",
                    ErrorCodes.SEMANTIC_UNDEFINED_ENTITY_REFERENCE,
                ).add_fix(f"Add a {entity_type} definition section or reference an existing one")
        else:
            self.result.add_error(
                f"Referenced {entity_type} '{entity_name}' is not defined (no entity definitions found)",
                ErrorCodes.SEMANTIC_UNDEFINED_ENTITY_REFERENCE,
            ).add_fix("Add entity definitions or reference an existing one")

    def _collect_hypothesis_definitions(self, ast: dict[str, Any]) -> None:
        """Collect hypothesis definitions for reference validation."""
        self.hypothesis_registry = {}

        if "hypothesis" in ast:
            hypothesis = ast["hypothesis"]
            if isinstance(hypothesis, dict) and "id" in hypothesis:
                self.hypothesis_registry[hypothesis["id"]] = hypothesis

    def _validate_rules_block(self, rules_block: Any) -> None:
        """Validate the rules block structure."""
        if not isinstance(rules_block, list):
            self.result.add_error(
                "Rules block must be a list of rule definitions",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix("Format rules as a list of dictionaries, e.g., rules: [{id: 'rule1', ...}]")
            return

        for i, rule in enumerate(rules_block):
            if not isinstance(rule, dict):
                self.result.add_error(
                    f"Rule {i} must be a dictionary",
                    ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
                ).add_fix(f"Format rule {i} as a dictionary with id, if, and then fields")
                continue

            # Validate required fields
            if "id" not in rule:
                self.result.add_error(
                    f"Rule {i} missing required 'id' field",
                    ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
                ).add_fix(f"Add 'id: <rule_id>' to rule {i}")

            if "if" not in rule:
                self.result.add_error(
                    f"Rule {i} missing required 'if' field",
                    ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
                ).add_fix(f"Add 'if: <condition>' to rule {i}")
            elif not isinstance(rule["if"], dict):
                self.result.add_error(
                    f"Rule {i} 'if' field must be a dictionary",
                    ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
                ).add_fix(f"Format 'if' field as a dictionary in rule {i}")

            if "then" not in rule:
                self.result.add_error(
                    f"Rule {i} missing required 'then' field",
                    ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
                ).add_fix(f"Add 'then: <consequence>' to rule {i}")
            elif not isinstance(rule["then"], dict):
                self.result.add_error(
                    f"Rule {i} 'then' field must be a dictionary",
                    ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
                ).add_fix(f"Format 'then' field as a dictionary in rule {i}")

    def _validate_hypothesis_block(self, hypothesis_block: Any) -> None:
        """Validate the hypothesis block structure."""
        if not isinstance(hypothesis_block, dict):
            self.result.add_error(
                "Hypothesis block must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix("Format hypothesis as a dictionary with id, description, if, and then fields")
            return

        # Validate required fields
        if "id" not in hypothesis_block:
            self.result.add_error(
                "Hypothesis missing required 'id' field",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            ).add_fix("Add 'id: <hypothesis_id>' to hypothesis")

        if "description" not in hypothesis_block:
            self.result.add_error(
                "Hypothesis missing required 'description' field",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            ).add_fix("Add 'description: <hypothesis_description>' to hypothesis")
        elif not isinstance(hypothesis_block["description"], str):
            self.result.add_error(
                "Hypothesis 'description' field must be a string",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix("Format 'description' field as a string in hypothesis")

        if "if" not in hypothesis_block:
            self.result.add_error(
                "Hypothesis missing required 'if' field",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            ).add_fix("Add 'if: <conditions>' to hypothesis")
        elif not isinstance(hypothesis_block["if"], list):
            self.result.add_error(
                "Hypothesis 'if' field must be a list",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix("Format 'if' field as a list in hypothesis")

        if "then" not in hypothesis_block:
            self.result.add_error(
                "Hypothesis missing required 'then' field",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            ).add_fix("Add 'then: <consequences>' to hypothesis")
        elif not isinstance(hypothesis_block["then"], list):
            self.result.add_error(
                "Hypothesis 'then' field must be a list",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix("Format 'then' field as a list in hypothesis")

    def _validate_timeline_block(self, timeline_block: Any) -> None:
        """Validate the timeline block structure."""
        if not isinstance(timeline_block, dict):
            self.result.add_error(
                "Timeline block must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix("Format timeline as a dictionary with events field")
            return

        # Validate required events field
        if "events" not in timeline_block:
            self.result.add_error(
                "Timeline missing required 'events' field",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            ).add_fix("Add 'events: []' to timeline")
            return

        events = timeline_block["events"]
        if not isinstance(events, list):
            self.result.add_error(
                "Timeline 'events' field must be a list",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix("Format 'events' field as a list in timeline")
            return

        # Validate each event
        for i, event in enumerate(events):
            if not isinstance(event, dict):
                self.result.add_error(
                    f"Timeline event {i} must be a dictionary",
                    ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
                ).add_fix(f"Format timeline event {i} as a dictionary with at and actions fields")
                continue

            # Validate required fields
            if "at" not in event:
                self.result.add_error(
                    f"Timeline event {i} missing required 'at' field",
                    ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
                ).add_fix(f"Add 'at: <time>' to timeline event {i}")
            elif not isinstance(event["at"], str):
                self.result.add_error(
                    f"Timeline event {i} 'at' field must be a string",
                    ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
                ).add_fix(f"Format 'at' field as a string in timeline event {i}")

            if "actions" not in event:
                self.result.add_error(
                    f"Timeline event {i} missing required 'actions' field",
                    ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
                ).add_fix(f"Add 'actions: []' to timeline event {i}")
            elif not isinstance(event["actions"], list):
                self.result.add_error(
                    f"Timeline event {i} 'actions' field must be a list",
                    ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
                ).add_fix(f"Format 'actions' field as a list in timeline event {i}")

            # Validate optional expectations field
            if "expectations" in event and not isinstance(event["expectations"], list):
                self.result.add_error(
                    f"Timeline event {i} 'expectations' field must be a list",
                    ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
                ).add_fix(f"Format 'expectations' field as a list in timeline event {i}")

    def _store_block_contract(self, block_name: str, contract: dict[str, Any]) -> None:
        """Store block contract in symbol table for compatibility checking."""
        self.symbol_table[block_name] = {"contract": contract}

    def _check_contract_compatibility(self, producer_block: str, consumer_block: str) -> None:
        """Check compatibility between producer and consumer block contracts."""
        # Get producer contract
        if producer_block not in self.symbol_table:
            return  # No contract to check

        producer_info = self.symbol_table[producer_block]
        if "contract" not in producer_info or "outputs" not in producer_info["contract"]:
            return  # No output contract to check

        producer_outputs = producer_info["contract"]["outputs"]

        # Get consumer contract
        if consumer_block not in self.symbol_table:
            return  # No contract to check

        consumer_info = self.symbol_table[consumer_block]
        if "contract" not in consumer_info or "inputs" not in consumer_info["contract"]:
            return  # No input contract to check

        consumer_inputs = consumer_info["contract"]["inputs"]

        # Check compatibility for each input
        for input_name, input_contract in consumer_inputs.items():
            # Check if there's a matching output
            if input_name in producer_outputs:
                output_contract = producer_outputs[input_name]
                # Check type compatibility
                if not self._are_contract_types_compatible(output_contract.get("type"), input_contract.get("type")):
                    error = self.result.add_error(
                        f"Contract type mismatch: {producer_block} output '{input_name}' "
                        f"(type: {output_contract.get('type')}) is incompatible with "
                        f"{consumer_block} input '{input_name}' (type: {input_contract.get('type')})",
                        ErrorCodes.SEMANTIC_CONTRACT_MISMATCH,
                    )
                    error.add_fix(
                        f"Ensure {producer_block} output '{input_name}' and "
                        f"{consumer_block} input '{input_name}' have compatible types"
                    )

                # Check attribute compatibility
                self._check_contract_attributes_compatibility(
                    output_contract.get("attributes", {}),
                    input_contract.get("attributes", {}),
                    producer_block,
                    consumer_block,
                    input_name,
                )

    def _validate_contract_definition(self, definition: Any, name: str, section_name: str) -> None:
        """Validate a single contract definition."""
        if not isinstance(definition, dict):
            self.result.add_error(
                f"Contract {section_name} '{name}' must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix(f"Format {section_name} '{name}' as a dictionary with 'type' and optional 'attributes'")
            return

        # Validate type field
        if "type" not in definition:
            error = self.result.add_error(
                f"Missing required 'type' field in contract {section_name} '{name}'",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix(f"Add 'type: <data_type>' to contract {section_name} '{name}'")
        elif not isinstance(definition["type"], str):
            self.result.add_error(
                f"Contract {section_name} '{name}' type must be a string",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix(f"Use a string for the type in contract {section_name} '{name}'")
        else:
            # Validate against schema registry if type is a custom schema
            contract_type = definition["type"]
            schema_def = self.schema_loader.get_schema(contract_type)
            if schema_def:
                # Validate attributes against schema definition
                self._validate_schema_attributes(definition, schema_def, name, section_name)

        # Validate attributes field if present
        if "attributes" in definition and not isinstance(definition["attributes"], dict):
            self.result.add_error(
                f"Contract {section_name} '{name}' attributes must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix(f"Format attributes as a dictionary in contract {section_name} '{name}'")

    def _validate_schema_attributes(
        self, definition: dict[str, Any], schema_def: Any, name: str, section_name: str
    ) -> None:
        """Validate contract attributes against schema definition."""
        attributes = definition.get("attributes", {})

        # Check required attributes
        for attr_name, attr_def in schema_def.attributes.items():
            is_required = attr_def.get("required", False)
            expected_value = attr_def.get("value")

            if is_required and attr_name not in attributes:
                error = self.result.add_error(
                    f"Required attribute '{attr_name}' missing in contract {section_name} '{name}' "
                    f"for schema type '{schema_def.name}'",
                    ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
                )
                error.add_fix(f"Add '{attr_name}: {expected_value}' to contract {section_name} '{name}' attributes")
            elif attr_name in attributes and expected_value is not None:
                actual_value = attributes[attr_name]
                if actual_value != expected_value:
                    error = self.result.add_error(
                        f"Attribute '{attr_name}' in contract {section_name} '{name}' "
                        f"must have value '{expected_value}' for schema type '{schema_def.name}', got '{actual_value}'",
                        ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                    )
                    error.add_fix(
                        f"Change '{attr_name}' to '{expected_value}' in contract {section_name} '{name}' attributes"
                    )

    def _are_contract_types_compatible(self, output_type: Any, input_type: Any) -> bool:
        """Check if two contract types are compatible."""
        if output_type is None or input_type is None:
            return True  # No type specified, assume compatible

        if not isinstance(output_type, str) or not isinstance(input_type, str):
            return False

        # Exact match
        if output_type == input_type:
            return True

        # Check if both types are defined in schema registry
        output_schema = self.schema_loader.get_schema(output_type)
        input_schema = self.schema_loader.get_schema(input_type)

        # If both are custom schemas, check base type compatibility
        if output_schema and input_schema:
            output_base = output_schema.base_type or output_type
            input_base = input_schema.base_type or input_type
            return self._are_base_types_compatible(output_base, input_base)
        elif output_schema:
            # Output is custom schema, input is primitive
            output_base = output_schema.base_type or output_type
            return self._are_base_types_compatible(output_base, input_type)
        elif input_schema:
            # Input is custom schema, output is primitive
            input_base = input_schema.base_type or input_type
            return self._are_base_types_compatible(output_type, input_base)

        # Use existing compatibility rules for primitive types
        return self._are_base_types_compatible(output_type, input_type)

    def _are_base_types_compatible(self, output_base_type: str, input_base_type: str) -> bool:
        """Check if two base types are compatible."""
        # Exact match
        if output_base_type == input_base_type:
            return True

        # Special compatibility rules
        compatibility_rules = {
            "FASTQ": ["FASTQ", "TEXT"],
            "FASTA": ["FASTA", "TEXT"],
            "BAM": ["BAM", "SAM", "BINARY"],
            "SAM": ["SAM", "BAM", "TEXT"],
            "VCF": ["VCF", "TEXT"],
            "CSV": ["CSV", "TEXT"],
            "JSON": ["JSON", "TEXT"],
        }

        if output_base_type in compatibility_rules:
            return input_base_type in compatibility_rules[output_base_type]

        # Default: assume custom types are compatible if they match exactly
        return output_base_type == input_base_type

    def _check_contract_attributes_compatibility(
        self,
        output_attributes: dict[str, Any],
        input_attributes: dict[str, Any],
        producer_block: str,
        consumer_block: str,
        data_name: str,
    ) -> None:
        """Check compatibility of contract attributes."""
        # Check that all required input attributes are satisfied by output attributes
        for attr_name, attr_value in input_attributes.items():
            if attr_name in output_attributes:
                output_value = output_attributes[attr_name]
                # For boolean attributes, output must be True if input requires True
                if isinstance(attr_value, bool) and attr_value is True:
                    if not isinstance(output_value, bool) or output_value is False:
                        error = self.result.add_error(
                            f"Contract attribute mismatch: {producer_block} output '{data_name}' "
                            f"does not satisfy {consumer_block} input requirement for '{attr_name}'",
                            ErrorCodes.SEMANTIC_CONTRACT_MISMATCH,
                        )
                        error.add_fix(
                            f"Ensure {producer_block} output '{data_name}' has '{attr_name}: true' "
                            f"to satisfy {consumer_block} input requirements"
                        )
                # For other attributes, we could implement more specific checks
                # For now, we'll just check for exact matches
                elif attr_value != output_value:
                    # This is a warning, not an error, as attributes might be flexible
                    pass  # We could add a warning here if needed

    def _validate_experiment_block(self, experiment: Any) -> None:
        """Validate experiment block structure and content."""
        if not isinstance(experiment, dict):
            self.result.add_error(
                "Experiment block must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
                location=SourceLocation(line=0, column=0),  # Would be filled by parser
            ).add_fix("Format the experiment block as a YAML dictionary")
            return

        # Required fields
        required_fields = ["tool", "type"]
        for field in required_fields:
            if field not in experiment:
                error = self.result.add_error(
                    f"Missing required field '{field}' in experiment block",
                    ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
                )
                error.add_fix(f"Add '{field}: <value>' to the experiment block")
                error.add_context("block", "experiment")
                error.add_context("required_fields", required_fields)

        # Validate tool
        if "tool" in experiment:
            self._validate_tool_field(experiment["tool"])

        # Validate type
        if "type" in experiment:
            self._validate_experiment_type(experiment["type"])

        # Validate params if present
        if "params" in experiment:
            self._validate_experiment_params(experiment["params"])

        # Check tool-type compatibility
        if "tool" in experiment and "type" in experiment:
            self._validate_tool_type_compatibility(experiment["tool"], experiment["type"])

        # Validate IO contract if present
        if "contract" in experiment:
            self._validate_io_contract(experiment["contract"])

        # Validate hypothesis reference if present
        if "validates_hypothesis" in experiment:
            self._validate_hypothesis_reference(experiment["validates_hypothesis"])

    def _validate_hypothesis_reference(self, hypothesis_id: Any) -> None:
        """Validate hypothesis reference in experiment or analysis blocks."""
        if not isinstance(hypothesis_id, str):
            self.result.add_error(
                f"Hypothesis reference must be a string, got {type(hypothesis_id).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Use a string for the hypothesis reference")
            return

        # Check if hypothesis is defined
        if hasattr(self, "hypothesis_registry") and hypothesis_id not in self.hypothesis_registry:
            self.result.add_error(
                f"Referenced hypothesis '{hypothesis_id}' is not defined",
                ErrorCodes.SEMANTIC_UNDEFINED_HYPOTHESIS,
            ).add_fix(f"Define a hypothesis with id '{hypothesis_id}' or reference an existing one")

    def _validate_io_contract(self, contract: Any) -> None:
        """Validate IO contract structure."""
        if not isinstance(contract, dict):
            self.result.add_error(
                "Contract must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix("Format contract as a dictionary with 'inputs' and/or 'outputs' keys")
            return

        # Validate inputs section
        if "inputs" in contract:
            self._validate_contract_section(contract["inputs"], "inputs")

        # Validate outputs section
        if "outputs" in contract:
            self._validate_contract_section(contract["outputs"], "outputs")

    def _validate_contract_section(self, section: Any, section_name: str) -> None:
        """Validate a contract section (inputs or outputs)."""
        if not isinstance(section, dict):
            self.result.add_error(
                f"Contract {section_name} must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix(f"Format {section_name} as a dictionary mapping names to contract definitions")
            return

        # Validate each contract definition
        for name, definition in section.items():
            self._validate_contract_definition(definition, name, section_name)

    def _validate_tool_field(self, tool: Any) -> None:
        """Validate the tool field."""
        if not isinstance(tool, str):
            error = self.result.add_error(
                f"Tool must be a string, got {type(tool).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            )
            error.add_fix("Change tool to a string value like 'CRISPR_cas9'")
            return

        # Known tools (could be extended with a registry)
        known_tools = {
            "CRISPR_cas9",
            "CRISPR_cas12",
            "CRISPR_base_editor",
            "CRISPR_prime_editor",
            "RNAseq",
            "ChIPseq",
            "ATACseq",
            "WGS",
            "WES",
            "targeted_seq",
        }

        if tool not in known_tools:
            error = self.result.add_error(
                f"Unknown tool '{tool}'",
                ErrorCodes.SEMANTIC_UNKNOWN_TOOL,
                ErrorSeverity.WARNING,
            )
            error.add_fix(f"Use a known tool or ensure '{tool}' plugin is available")
            error.add_context("suggested_tools", list(known_tools))

    def _validate_experiment_type(self, exp_type: Any) -> None:
        """Validate the experiment type."""
        if not isinstance(exp_type, str):
            error = self.result.add_error(
                f"Experiment type must be a string, got {type(exp_type).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            )
            error.add_fix("Change type to a string like 'gene_editing'")
            return

        valid_types = {
            "gene_editing",
            "sequencing",
            "analysis",
            "simulation",
            "validation",
        }

        if exp_type not in valid_types:
            error = self.result.add_error(
                f"Unknown experiment type '{exp_type}'",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                ErrorSeverity.WARNING,
            )
            error.add_fix(f"Use one of: {', '.join(valid_types)}")
            error.add_context("valid_types", list(valid_types))

    def _validate_experiment_params(self, params: Any) -> None:
        """Validate experiment parameters."""
        if not isinstance(params, dict):
            self.result.add_error(
                f"Experiment params must be a dictionary, got {type(params).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format params as a YAML dictionary with key-value pairs")
            return

        # Validate specific parameter types
        type_validations = {
            "concentration": (float, int),
            "temperature": (float, int),
            "replicates": int,
            "target_gene": str,
            "guide_rna": str,
        }

        for param_name, param_value in params.items():
            # Skip validation for parameter injection (${...} syntax)
            if isinstance(param_value, str) and param_value.startswith("${") and param_value.endswith("}"):
                continue

            # Check for entity references (e.g., pathway(UreaCycle))
            if isinstance(param_value, str) and self._is_entity_reference(param_value):
                self._validate_entity_reference(param_value)
                continue

            if param_name in type_validations:
                expected_types = type_validations[param_name]
                if not isinstance(expected_types, tuple):
                    expected_types = (expected_types,)

                if not isinstance(param_value, expected_types):
                    type_names = " or ".join(t.__name__ for t in expected_types)
                    error = self.result.add_error(
                        f"Parameter '{param_name}' should be {type_names}, got {type(param_value).__name__}",
                        ErrorCodes.TYPE_INVALID_TYPE,
                    )
                    error.add_fix(f"Change '{param_name}' to a {type_names} value")
                    error.add_context("parameter", param_name)
                    error.add_context("expected_type", type_names)

    def _is_entity_reference(self, value: str) -> bool:
        """Check if a string value is an entity reference (e.g., pathway(UreaCycle))."""
        import re

        # Pattern for entity references: entity_type(entity_name)
        pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*\([a-zA-Z_][a-zA-Z0-9_]*\)$"
        return bool(re.match(pattern, value))

    def _validate_entity_reference(self, entity_ref: str) -> None:
        """Validate entity reference in parameter values."""
        import re

        # Extract entity type and name
        match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\(([a-zA-Z_][a-zA-Z0-9_]*)\)$", entity_ref)
        if not match:
            self.result.add_error(
                f"Invalid entity reference format: {entity_ref}",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            ).add_fix("Use format 'entity_type(entity_name)' for entity references")
            return

        entity_type, entity_name = match.groups()

        # Check if entity type is supported
        supported_entity_types = {"pathway", "complex"}
        if entity_type not in supported_entity_types:
            self.result.add_error(
                f"Unsupported entity type '{entity_type}' in reference: {entity_ref}",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            ).add_fix(f"Use one of the supported entity types: {', '.join(supported_entity_types)}")
            return

        # Check if entity is defined
        if hasattr(self, "entity_registry"):
            # Debug: Print entity registry contents
            print(f"Entity registry: {self.entity_registry}")
            print(f"Looking for entity type: {entity_type}")
            print(f"Looking for entity name: {entity_name}")

            registry_key = entity_type + "s"  # "pathway" -> "pathways", "complex" -> "complexes"
            # Fix for complex -> complexes
            if entity_type == "complex":
                registry_key = "complexes"
            print(f"Registry key: {registry_key}")
            if registry_key in self.entity_registry:
                print(f"Found registry key: {registry_key}")
                print(f"Available entities: {list(self.entity_registry[registry_key].keys())}")
                if entity_name in self.entity_registry[registry_key]:
                    print(f"Found entity: {entity_name}")
                    return  # Valid reference
                else:
                    self.result.add_error(
                        f"Referenced {entity_type} '{entity_name}' is not defined",
                        ErrorCodes.SEMANTIC_UNDEFINED_ENTITY_REFERENCE,
                    ).add_fix(f"Define a {entity_type} with name '{entity_name}' or reference an existing one")
            else:
                # Entity type registry doesn't exist
                self.result.add_error(
                    f"Referenced {entity_type} '{entity_name}' is not defined (no {entity_type} definitions found)",
                    ErrorCodes.SEMANTIC_UNDEFINED_ENTITY_REFERENCE,
                ).add_fix(f"Add a {entity_type} definition section or reference an existing one")
        else:
            self.result.add_error(
                f"Referenced {entity_type} '{entity_name}' is not defined (no entity definitions found)",
                ErrorCodes.SEMANTIC_UNDEFINED_ENTITY_REFERENCE,
            ).add_fix("Add entity definitions or reference an existing one")

    def _validate_tool_type_compatibility(self, tool: str, exp_type: str) -> None:
        """Validate tool and type compatibility."""
        compatibility_matrix = {
            "CRISPR_cas9": ["gene_editing"],
            "CRISPR_cas12": ["gene_editing"],
            "CRISPR_base_editor": ["gene_editing"],
            "RNAseq": ["sequencing", "analysis"],
            "ChIPseq": ["sequencing", "analysis"],
            "ATACseq": ["sequencing", "analysis"],
        }

        if tool in compatibility_matrix:
            compatible_types = compatibility_matrix[tool]
            if exp_type not in compatible_types:
                error = self.result.add_error(
                    f"Tool '{tool}' is not compatible with type '{exp_type}'",
                    ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                    ErrorSeverity.WARNING,
                )
                error.add_fix(f"Use type: {' or '.join(compatible_types)}")
                error.add_context("tool", tool)
                error.add_context("compatible_types", compatible_types)

    def _validate_analysis_block(self, analysis: Any) -> None:
        """Validate analysis block."""
        if not isinstance(analysis, dict):
            self.result.add_error(
                "Analysis block must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix("Format the analysis block as a YAML dictionary")
            return

        # Required strategy field
        if "strategy" not in analysis:
            error = self.result.add_error(
                "Missing required field 'strategy' in analysis block",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix("Add 'strategy: <analysis_type>' to the analysis block")
        else:
            self._validate_analysis_strategy(analysis["strategy"])

        # Validate IO contract if present
        if "contract" in analysis:
            self._validate_io_contract(analysis["contract"])

        # Validate hypothesis reference if present
        if "validates_hypothesis" in analysis:
            self._validate_hypothesis_reference(analysis["validates_hypothesis"])

    def _validate_analysis_strategy(self, strategy: Any) -> None:
        """Validate analysis strategy."""
        if not isinstance(strategy, str):
            self.result.add_error(
                f"Analysis strategy must be a string, got {type(strategy).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Use a string like 'differential' for the strategy")
            return

        valid_strategies = {
            "differential",
            "pathway",
            "variant",
            "expression",
            "structural",
            "functional",
            "comparative",
            "longitudinal",
        }

        if strategy not in valid_strategies:
            error = self.result.add_error(
                f"Unknown analysis strategy '{strategy}'",
                ErrorCodes.SEMANTIC_UNKNOWN_STRATEGY,
                ErrorSeverity.WARNING,
            )
            error.add_fix(f"Use one of: {', '.join(sorted(valid_strategies))}")
            error.add_context("valid_strategies", list(valid_strategies))

    def _validate_design_block(self, design: Any) -> None:
        """Validate design block structure and content."""
        if not isinstance(design, dict):
            self.result.add_error(
                "Design block must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix("Format the design block as a YAML dictionary")
            return

        # Check for design_type field
        design_type = design.get("design_type", "standard")  # Default to standard design

        # Required fields (standard design)
        required_fields = ["entity", "model", "objective", "count", "output"]

        # For inverse_design, we may have different requirements
        if design_type == "inverse_design":
            # For inverse_design, we still need most standard fields but also need inverse_design config
            pass  # We'll validate inverse_design specific requirements separately

        for field in required_fields:
            if field not in design:
                error = self.result.add_error(
                    f"Missing required field '{field}' in design block",
                    ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
                )
                error.add_fix(f"Add '{field}: <value>' to the design block")
                error.add_context("block", "design")
                error.add_context("required_fields", required_fields)

        # Validate entity field
        if "entity" in design:
            self._validate_design_entity(design["entity"])

        # Validate model field
        if "model" in design:
            self._validate_design_model(design["model"])

        # Validate objective field
        if "objective" in design:
            self._validate_design_objective(design["objective"])

        # Validate count field
        if "count" in design:
            self._validate_design_count(design["count"])

        # Validate output field
        if "output" in design:
            self._validate_design_output(design["output"])

        # Validate constraints field if present
        if "constraints" in design:
            self._validate_design_constraints(design["constraints"])

        # Validate design_type specific requirements
        if design_type == "inverse_design":
            self._validate_inverse_design(design)

    def _validate_inverse_design(self, design: dict[str, Any]) -> None:
        """Validate inverse_design configuration."""
        # Check for required inverse_design dictionary
        if "inverse_design" not in design:
            error = self.result.add_error(
                "Design block with design_type 'inverse_design' requires 'inverse_design' configuration",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix("Add 'inverse_design: {...}' with target_properties and foundation_model")
            return

        inverse_design_config = design["inverse_design"]
        if not isinstance(inverse_design_config, dict):
            self.result.add_error(
                "inverse_design configuration must be a dictionary",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format inverse_design as a dictionary with required keys")
            return

        # Required keys in inverse_design dictionary
        required_keys = ["target_properties", "foundation_model"]

        for key in required_keys:
            if key not in inverse_design_config:
                error = self.result.add_error(
                    f"Missing required key '{key}' in inverse_design configuration",
                    ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
                )
                error.add_fix(f"Add '{key}: <value>' to inverse_design configuration")
            else:
                value = inverse_design_config[key]
                if key == "target_properties":
                    if not isinstance(value, dict):
                        self.result.add_error(
                            f"target_properties must be a dictionary, got {type(value).__name__}",
                            ErrorCodes.TYPE_INVALID_TYPE,
                        ).add_fix("Format target_properties as a dictionary with property specifications")
                elif key == "foundation_model" and not isinstance(value, str):
                    self.result.add_error(
                        f"foundation_model must be a string, got {type(value).__name__}",
                        ErrorCodes.TYPE_INVALID_TYPE,
                    ).add_fix("Use a string for foundation_model")

    def _validate_design_entity(self, entity: Any) -> None:
        """Validate the entity field in design block."""
        if not isinstance(entity, str):
            self.result.add_error(
                f"Design entity must be a string, got {type(entity).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Use a string like 'ProteinSequence' for the entity")
            return

        valid_entities = {
            "ProteinSequence",
            "DNASequence",
            "RNASequence",
            "SmallMolecule",
            "Peptide",
            "Antibody",
        }

        if entity not in valid_entities:
            error = self.result.add_error(
                f"Unknown design entity '{entity}'",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                ErrorSeverity.WARNING,
            )
            error.add_fix(f"Use one of: {', '.join(sorted(valid_entities))}")
            error.add_context("valid_entities", list(valid_entities))

    def _validate_design_model(self, model: Any) -> None:
        """Validate the model field in design block."""
        if not isinstance(model, str):
            self.result.add_error(
                f"Design model must be a string, got {type(model).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Use a string like 'ProteinGeneratorVAE' for the model")
            return

        # Known generative models (could be extended with a registry)
        known_models = {
            "ProteinGeneratorVAE",
            "DNADesignerGAN",
            "MoleculeTransformer",
            "SequenceOptimizer",
            "StructurePredictor",
        }

        if model not in known_models:
            error = self.result.add_error(
                f"Unknown generative model '{model}'",
                ErrorCodes.SEMANTIC_UNKNOWN_TOOL,
                ErrorSeverity.WARNING,
            )
            error.add_fix(f"Ensure '{model}' plugin is available or use a known model")
            error.add_context("suggested_models", list(known_models))

    def _validate_design_objective(self, objective: Any) -> None:
        """Validate the objective field in design block."""
        if not isinstance(objective, dict):
            self.result.add_error(
                f"Design objective must be a dictionary, got {type(objective).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format objective as '{maximize: metric}' or '{minimize: metric}'")
            return

        # Must have exactly one of maximize or minimize
        has_maximize = "maximize" in objective
        has_minimize = "minimize" in objective

        if not (has_maximize or has_minimize):
            error = self.result.add_error(
                "Objective must contain either 'maximize' or 'minimize' key",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix("Add 'maximize: binding_affinity' or 'minimize: toxicity'")

        if has_maximize and has_minimize:
            error = self.result.add_error(
                "Objective cannot have both 'maximize' and 'minimize' keys",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            )
            error.add_fix("Choose either 'maximize' or 'minimize', not both")

        # Validate metric names
        if has_maximize:
            self._validate_objective_metric(objective["maximize"], "maximize")
        if has_minimize:
            self._validate_objective_metric(objective["minimize"], "minimize")

    def _validate_objective_metric(self, metric: Any, direction: str) -> None:
        """Validate an objective metric."""
        if not isinstance(metric, str):
            self.result.add_error(
                f"Objective metric must be a string, got {type(metric).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix(f"Use a string like 'binding_affinity' for {direction}")
            return

        # Common metrics for different entity types
        valid_metrics = {
            "binding_affinity",
            "stability",
            "solubility",
            "toxicity",
            "activity",
            "selectivity",
            "permeability",
            "expression_level",
        }

        if metric not in valid_metrics:
            error = self.result.add_error(
                f"Unknown objective metric '{metric}'",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                ErrorSeverity.WARNING,
            )
            error.add_fix(f"Use one of: {', '.join(sorted(valid_metrics))}")
            error.add_context("valid_metrics", list(valid_metrics))

    def _validate_design_count(self, count: Any) -> None:
        """Validate the count field in design block."""
        if not isinstance(count, int):
            self.result.add_error(
                f"Design count must be an integer, got {type(count).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Use an integer like 10 for the count")
            return

        if count <= 0:
            error = self.result.add_error(
                f"Design count must be positive, got {count}",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            )
            error.add_fix("Use a positive integer like 10 for the count")

        if count > 1000:
            error = self.result.add_error(
                f"Design count {count} seems very high, consider reducing",
                "HINT002",
                ErrorSeverity.HINT,
            )
            error.add_fix("Consider using a smaller count for faster generation")

    def _validate_design_output(self, output: Any) -> None:
        """Validate the output field in design block."""
        if not isinstance(output, str):
            self.result.add_error(
                f"Design output must be a string, got {type(output).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Use a string identifier like 'designed_candidates'")
            return

        # Validate identifier format
        import re

        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", output):
            error = self.result.add_error(
                f"Invalid output identifier '{output}'",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            )
            error.add_fix("Use a valid identifier like 'designed_candidates' or 'output_seqs'")

    def _validate_design_constraints(self, constraints: Any) -> None:
        """Validate the constraints field in design block."""
        if not isinstance(constraints, list):
            self.result.add_error(
                f"Design constraints must be a list, got {type(constraints).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format constraints as a list of constraint expressions")
            return

        for i, constraint in enumerate(constraints):
            if not isinstance(constraint, str):
                error = self.result.add_error(
                    f"Constraint {i + 1} must be a string, got {type(constraint).__name__}",
                    ErrorCodes.TYPE_INVALID_TYPE,
                )
                error.add_fix(f"Convert constraint {i + 1} to a string expression")

    def _validate_optimize_block(self, optimize: Any) -> None:
        """Validate optimize block structure and content."""
        if not isinstance(optimize, dict):
            self.result.add_error(
                "Optimize block must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix("Format the optimize block as a YAML dictionary")
            return

        # Required fields
        required_fields = ["search_space", "strategy", "objective", "budget", "run"]
        for field in required_fields:
            if field not in optimize:
                error = self.result.add_error(
                    f"Missing required field '{field}' in optimize block",
                    ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
                )
                error.add_fix(f"Add '{field}: <value>' to the optimize block")
                error.add_context("block", "optimize")
                error.add_context("required_fields", required_fields)

        # Special validation for ActiveLearning strategy
        if "strategy" in optimize:
            strategy = optimize["strategy"]
            if isinstance(strategy, dict) and strategy.get("name") == "ActiveLearning":
                # Check for surrogate_model requirement
                if "surrogate_model" not in optimize:
                    error = self.result.add_error(
                        "Optimize block with ActiveLearning strategy requires 'surrogate_model'",
                        ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
                    )
                    error.add_fix("Add 'surrogate_model: <model_name>' to the optimize block")

        # Validate individual fields
        if "search_space" in optimize:
            self._validate_optimize_search_space(optimize["search_space"])

        if "strategy" in optimize:
            self._validate_optimize_strategy(optimize["strategy"])

        if "objective" in optimize:
            self._validate_optimize_objective(optimize["objective"])

        if "budget" in optimize:
            self._validate_optimize_budget(optimize["budget"])

        if "run" in optimize:
            self._validate_optimize_run(optimize["run"])

        # Validate surrogate_model if present
        if "surrogate_model" in optimize:
            self._validate_surrogate_model(optimize["surrogate_model"])

    def _validate_surrogate_model(self, surrogate_model: Any) -> None:
        """Validate the surrogate_model field."""
        if not isinstance(surrogate_model, str):
            self.result.add_error(
                f"surrogate_model must be a string, got {type(surrogate_model).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Use a string like 'GaussianProcess' for surrogate_model")
            return

    def _validate_optimize_search_space(self, search_space: Any) -> None:
        """Validate the search_space field in optimize block."""
        if not isinstance(search_space, dict):
            self.result.add_error(
                f"Search space must be a dictionary, got {type(search_space).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format search_space as parameter_name: range() or choice() expressions")
            return

        if not search_space:
            self.result.add_error(
                "Search space cannot be empty",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            ).add_fix("Add at least one parameter with range() or choice() syntax")
            return

        # Validate each parameter definition
        for param_name, param_def in search_space.items():
            self._validate_search_space_parameter(param_name, param_def)

    def _validate_search_space_parameter(self, param_name: str, param_def: Any) -> None:
        """Validate a single parameter in search space."""
        if not isinstance(param_def, str):
            self.result.add_error(
                f"Parameter '{param_name}' definition must be a string, got {type(param_def).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix(f"Use 'range(min, max)' or 'choice([...])' for '{param_name}'")
            return

        # Validate parameter name format
        import re

        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", param_name):
            error = self.result.add_error(
                f"Invalid parameter name '{param_name}'",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            )
            error.add_fix("Use valid identifier like 'promoter_strength' or 'temperature'")

        # Validate parameter definition syntax
        if param_def.startswith("range(") and param_def.endswith(")"):
            self._validate_range_syntax(param_name, param_def)
        elif param_def.startswith("choice([") and param_def.endswith("])"):
            self._validate_choice_syntax(param_name, param_def)
        else:
            error = self.result.add_error(
                f"Invalid syntax for parameter '{param_name}': {param_def}",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            )
            error.add_fix("Use 'range(min, max)' or 'choice([val1, val2, ...])' syntax")

    def _validate_range_syntax(self, param_name: str, range_def: str) -> None:
        """Validate range(min, max) syntax."""
        try:
            # Extract content between parentheses
            content = range_def[6:-1].strip()  # Remove 'range(' and ')'
            parts = [p.strip() for p in content.split(",")]

            if len(parts) != 2:
                error = self.result.add_error(
                    f"Range for '{param_name}' must have exactly 2 values: range(min, max)",
                    ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                )
                error.add_fix(f"Use 'range(0.1, 1.0)' format for '{param_name}'")
                return

            # Try to parse as numbers
            try:
                min_val = float(parts[0])
                max_val = float(parts[1])

                if min_val >= max_val:
                    error = self.result.add_error(
                        f"Range minimum ({min_val}) must be less than maximum ({max_val}) for '{param_name}'",
                        ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                    )
                    error.add_fix(f"Ensure min < max in range() for '{param_name}'")
            except ValueError:
                error = self.result.add_error(
                    f"Range values for '{param_name}' must be numbers",
                    ErrorCodes.TYPE_INVALID_TYPE,
                )
                error.add_fix(f"Use numeric values like 'range(0.1, 1.0)' for '{param_name}'")

        except Exception:
            error = self.result.add_error(
                f"Invalid range syntax for '{param_name}': {range_def}",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            )
            error.add_fix(f"Use correct format: 'range(min, max)' for '{param_name}'")

    def _validate_choice_syntax(self, param_name: str, choice_def: str) -> None:
        """Validate choice([...]) syntax."""
        try:
            # Extract content between square brackets inside choice([...])
            # Find the opening [ and closing ]
            start_bracket = choice_def.find("[")
            end_bracket = choice_def.rfind("]")

            if start_bracket == -1 or end_bracket == -1 or start_bracket >= end_bracket:
                error = self.result.add_error(
                    f"Invalid choice syntax for '{param_name}': {choice_def}",
                    ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                )
                error.add_fix(f"Use correct format: 'choice([val1, val2, ...])' for '{param_name}'")
                return

            content = choice_def[start_bracket + 1 : end_bracket].strip()

            if not content:
                error = self.result.add_error(
                    f"Choice for '{param_name}' cannot be empty",
                    ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                )
                error.add_fix(f"Add at least one choice value for '{param_name}'")
                return

            # Simple validation - should contain comma-separated values
            choices = [c.strip() for c in content.split(",") if c.strip()]

            if len(choices) < 2:
                error = self.result.add_error(
                    f"Choice for '{param_name}' should have at least 2 options",
                    ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                    ErrorSeverity.WARNING,
                )
                error.add_fix(f"Add more choice options for '{param_name}'")

        except Exception:
            error = self.result.add_error(
                f"Invalid choice syntax for '{param_name}': {choice_def}",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            )
            error.add_fix(f"Use correct format: 'choice([val1, val2, ...])' for '{param_name}'")

    def _validate_optimize_strategy(self, strategy: Any) -> None:
        """Validate the strategy field in optimize block."""
        if not isinstance(strategy, dict):
            self.result.add_error(
                f"Strategy must be a dictionary, got {type(strategy).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format strategy as '{name: StrategyName, ...}'")
            return

        # Must have a name field
        if "name" not in strategy:
            error = self.result.add_error(
                "Strategy must have a 'name' field",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix("Add 'name: ActiveLearning' to strategy")
            return

        strategy_name = strategy["name"]
        if not isinstance(strategy_name, str):
            self.result.add_error(
                f"Strategy name must be a string, got {type(strategy_name).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Use a string like 'ActiveLearning' for strategy name")
            return

        # Known optimization strategies
        known_strategies = {
            "ActiveLearning",
            "BayesianOptimization",
            "GeneticAlgorithm",
            "SimulatedAnnealing",
            "RandomSearch",
            "GridSearch",
        }

        if strategy_name not in known_strategies:
            error = self.result.add_error(
                f"Unknown optimization strategy '{strategy_name}'",
                ErrorCodes.SEMANTIC_UNKNOWN_TOOL,
                ErrorSeverity.WARNING,
            )
            error.add_fix(f"Use one of: {', '.join(sorted(known_strategies))}")
            error.add_context("available_strategies", list(known_strategies))

        # Special validation for ActiveLearning strategy
        if strategy_name == "ActiveLearning":
            self._validate_active_learning_strategy(strategy)

    def _validate_active_learning_strategy(self, strategy: dict[str, Any]) -> None:
        """Validate ActiveLearning strategy with required nested keys."""
        # Check for required active_learning dictionary
        if "active_learning" not in strategy:
            error = self.result.add_error(
                "ActiveLearning strategy requires 'active_learning' configuration",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix(
                "Add 'active_learning: {...}' with acquisition_function, initial_experiments, max_uncertainty, convergence_threshold"
            )
            return

        active_learning_config = strategy["active_learning"]
        if not isinstance(active_learning_config, dict):
            self.result.add_error(
                "ActiveLearning configuration must be a dictionary",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format active_learning as a dictionary with required keys")
            return

        # Required keys in active_learning dictionary
        required_keys = {
            "acquisition_function": str,
            "initial_experiments": int,
            "max_uncertainty": float,
            "convergence_threshold": (int, float),
        }

        for key, expected_type in required_keys.items():
            if key not in active_learning_config:
                error = self.result.add_error(
                    f"Missing required key '{key}' in active_learning configuration",
                    ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
                )
                error.add_fix(f"Add '{key}: <value>' to active_learning configuration")
            else:
                value = active_learning_config[key]
                if not isinstance(value, expected_type if isinstance(expected_type, tuple) else (expected_type,)):
                    type_names = " or ".join(
                        t.__name__ for t in (expected_type if isinstance(expected_type, tuple) else (expected_type,))
                    )
                    error = self.result.add_error(
                        f"'{key}' must be {type_names}, got {type(value).__name__}",
                        ErrorCodes.TYPE_INVALID_TYPE,
                    )
                    error.add_fix(f"Change '{key}' to a {type_names} value")

        # Validate initial_experiments is positive
        if "initial_experiments" in active_learning_config:
            initial_experiments = active_learning_config["initial_experiments"]
            if isinstance(initial_experiments, int) and initial_experiments <= 0:
                error = self.result.add_error(
                    f"initial_experiments must be positive, got {initial_experiments}",
                    ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                )
                error.add_fix("Use a positive integer for initial_experiments")

        # Validate convergence_threshold is positive
        if "convergence_threshold" in active_learning_config:
            threshold = active_learning_config["convergence_threshold"]
            if isinstance(threshold, (int, float)) and threshold <= 0:
                error = self.result.add_error(
                    f"convergence_threshold must be positive, got {threshold}",
                    ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                )
                error.add_fix("Use a positive number for convergence_threshold")

    def _validate_optimize_objective(self, objective: Any) -> None:
        """Validate the objective field in optimize block."""
        if not isinstance(objective, dict):
            self.result.add_error(
                f"Objective must be a dictionary, got {type(objective).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format objective as '{maximize: metric}' or '{minimize: metric}'")
            return

        # Must have exactly one of maximize or minimize
        has_maximize = "maximize" in objective
        has_minimize = "minimize" in objective

        if not (has_maximize or has_minimize):
            error = self.result.add_error(
                "Objective must contain either 'maximize' or 'minimize' key",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix("Add 'maximize: gene_expression_level' or 'minimize: cost'")

        if has_maximize and has_minimize:
            error = self.result.add_error(
                "Objective cannot have both 'maximize' and 'minimize' keys",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            )
            error.add_fix("Choose either 'maximize' or 'minimize', not both")

        # Validate metric names
        if has_maximize:
            self._validate_objective_metric(objective["maximize"], "maximize")
        if has_minimize:
            self._validate_objective_metric(objective["minimize"], "minimize")

    def _validate_optimize_budget(self, budget: Any) -> None:
        """Validate the budget field in optimize block."""
        if not isinstance(budget, dict):
            self.result.add_error(
                f"Budget must be a dictionary, got {type(budget).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format budget as '{max_experiments: 50}' or similar")
            return

        if not budget:
            self.result.add_error(
                "Budget cannot be empty",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            ).add_fix("Add at least one budget constraint like 'max_experiments: 50'")
            return

        # Validate budget constraints
        valid_constraints = {
            "max_experiments",
            "max_time",
            "max_cost",
            "convergence_threshold",
        }

        for constraint, value in budget.items():
            if constraint not in valid_constraints:
                error = self.result.add_error(
                    f"Unknown budget constraint '{constraint}'",
                    ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                    ErrorSeverity.WARNING,
                )
                error.add_fix(f"Use one of: {', '.join(sorted(valid_constraints))}")
                error.add_context("valid_constraints", list(valid_constraints))

            # Validate constraint values
            if constraint == "max_experiments":
                if not isinstance(value, int) or value <= 0:
                    error = self.result.add_error(
                        f"Budget constraint '{constraint}' must be a positive integer, got {value}",
                        ErrorCodes.TYPE_INVALID_TYPE,
                    )
                    error.add_fix(f"Use a positive integer for '{constraint}'")
            elif constraint == "max_time":
                if not isinstance(value, str):
                    error = self.result.add_error(
                        f"Budget constraint '{constraint}' must be a string with time format, got {type(value).__name__}",
                        ErrorCodes.TYPE_INVALID_TYPE,
                    )
                    error.add_fix(f"Use time format like '24h', '7d' for '{constraint}'")
                else:
                    # Validate time format
                    import re

                    if not re.match(r"^\d+[smhd]$", value):
                        error = self.result.add_error(
                            f"Budget constraint '{constraint}' has invalid time format: {value}",
                            ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                        )
                        error.add_fix(f"Use format like '24h', '7d', '30m' for '{constraint}'")
            elif constraint in ["max_cost", "convergence_threshold"]:
                if not isinstance(value, (int, float)) or value <= 0:
                    error = self.result.add_error(
                        f"Budget constraint '{constraint}' must be a positive number, got {value}",
                        ErrorCodes.TYPE_INVALID_TYPE,
                    )
                    error.add_fix(f"Use a positive number for '{constraint}'")

    def _validate_optimize_run(self, run: Any) -> None:
        """Validate the run field in optimize block."""
        if not isinstance(run, dict):
            self.result.add_error(
                f"Run block must be a dictionary, got {type(run).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format run as a nested experiment or analyze block")
            return

        # Must contain exactly one of: experiment, analyze
        valid_nested_blocks = {"experiment", "analyze"}
        found_blocks = set(run.keys()) & valid_nested_blocks

        if not found_blocks:
            error = self.result.add_error(
                "Run block must contain an 'experiment' or 'analyze' block",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix("Add 'experiment: {...}' or 'analyze: {...}' to the run block")
            error.add_context("valid_nested_blocks", list(valid_nested_blocks))

        if len(found_blocks) > 1:
            error = self.result.add_error(
                "Run block can only contain one nested block",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            )
            error.add_fix("Use either 'experiment' or 'analyze', not both")

        # Validate the nested block
        if "experiment" in run:
            self._validate_experiment_block(run["experiment"])
            self._validate_parameter_injection(run["experiment"])
        elif "analyze" in run:
            self._validate_analysis_block(run["analyze"])
            self._validate_parameter_injection(run["analyze"])

    def _validate_parameter_injection(self, block: dict) -> None:
        """Validate ${...} parameter injection syntax in nested blocks."""
        # Recursively check all values in the block for parameter injection
        self._check_parameter_injection_recursive(block, "")

    def _check_parameter_injection_recursive(self, obj: Any, path: str) -> None:
        """Recursively check for parameter injection patterns."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                self._check_parameter_injection_recursive(value, new_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                self._check_parameter_injection_recursive(item, new_path)
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            # This is a parameter injection - validate the parameter name
            param_name = obj[2:-1]  # Remove ${}
            if not param_name:
                error = self.result.add_error(
                    f"Empty parameter injection at {path}",
                    ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                )
                error.add_fix("Specify a parameter name like ${parameter_name}")
            else:
                # Validate parameter name format
                import re

                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", param_name):
                    error = self.result.add_error(
                        f"Invalid parameter name '{param_name}' in injection at {path}",
                        ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                    )
                    error.add_fix("Use valid identifier like ${valid_param_name}")

    def _validate_simulate_block(self, simulate: Any) -> None:
        """Validate simulate block."""
        if not isinstance(simulate, bool):
            error = self.result.add_error(
                f"Simulate must be a boolean, got {type(simulate).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            )
            error.add_fix("Use 'true' or 'false' for the simulate value")

    def _validate_branch_block(self, branch: Any) -> None:
        """Validate branch block."""
        if not isinstance(branch, dict):
            self.result.add_error(
                "Branch block must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix("Format the branch block as a YAML dictionary with 'if' and 'then'")
            return

        # Branch blocks need 'if' and 'then'
        if "if" not in branch:
            error = self.result.add_error(
                "Missing 'if' condition in branch block",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix("Add 'if: <condition>' to the branch block")

        if "then" not in branch:
            error = self.result.add_error(
                "Missing 'then' clause in branch block",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix("Add 'then: <actions>' to the branch block")

    def _validate_metadata_block(self, metadata: Any) -> None:
        """Validate metadata block."""
        if not isinstance(metadata, dict):
            self.result.add_error(
                "Metadata block must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
                ErrorSeverity.WARNING,
            ).add_fix("Format metadata as key-value pairs")
            return

        # Suggest useful metadata fields if missing
        useful_fields = {"experiment_id", "researcher", "date", "description"}
        present_fields = set(metadata.keys())
        missing_useful = useful_fields - present_fields

        if missing_useful and len(present_fields) < 2:
            error = self.result.add_error(
                "Consider adding more descriptive metadata",
                "HINT001",
                ErrorSeverity.HINT,
            )
            error.add_fix(f"Consider adding: {', '.join(missing_useful)}")
            error.add_context("suggested_fields", list(missing_useful))

    def _validate_refine_data_block(self, refine_data: Any) -> None:
        """Validate refine_data block structure and content."""
        if not isinstance(refine_data, dict):
            self.result.add_error(
                "refine_data block must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix("Format the refine_data block as a YAML dictionary")
            return

        # Check for required refinement_config dictionary
        if "refinement_config" not in refine_data:
            error = self.result.add_error(
                "refine_data block requires 'refinement_config' configuration",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix("Add 'refinement_config: {...}' with refinement_type, noise_level, and target_resolution")
            return

        refinement_config = refine_data["refinement_config"]
        if not isinstance(refinement_config, dict):
            self.result.add_error(
                "refinement_config must be a dictionary",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format refinement_config as a dictionary with required keys")
            return

        # Required keys in refinement_config dictionary
        required_keys = {"refinement_type": str, "noise_level": float, "target_resolution": str}

        for key, expected_type in required_keys.items():
            if key not in refinement_config:
                error = self.result.add_error(
                    f"Missing required key '{key}' in refinement_config",
                    ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
                )
                error.add_fix(f"Add '{key}: <value>' to refinement_config")
            else:
                value = refinement_config[key]
                if not isinstance(value, expected_type):
                    error = self.result.add_error(
                        f"'{key}' must be {expected_type.__name__}, got {type(value).__name__}",
                        ErrorCodes.TYPE_INVALID_TYPE,
                    )
                    error.add_fix(f"Change '{key}' to a {expected_type.__name__} value")

    def _validate_guided_discovery_block(self, guided_discovery: Any) -> None:
        """Validate guided_discovery block structure and content."""
        if not isinstance(guided_discovery, dict):
            self.result.add_error(
                "guided_discovery block must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix("Format the guided_discovery block as a YAML dictionary")
            return

        # Required keys in guided_discovery block
        required_keys = ["design_params", "active_learning_params", "budget", "output"]

        for key in required_keys:
            if key not in guided_discovery:
                error = self.result.add_error(
                    f"Missing required key '{key}' in guided_discovery block",
                    ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
                )
                error.add_fix(f"Add '{key}: <value>' to guided_discovery block")
            else:
                # Validate each section
                value = guided_discovery[key]
                if key == "design_params":
                    self._validate_guided_discovery_design_params(value)
                elif key == "active_learning_params":
                    self._validate_guided_discovery_active_learning_params(value)
                elif key == "budget":
                    self._validate_guided_discovery_budget(value)
                elif key == "output":
                    self._validate_guided_discovery_output(value)

    def _validate_guided_discovery_design_params(self, design_params: Any) -> None:
        """Validate design_params in guided_discovery block."""
        if not isinstance(design_params, dict):
            self.result.add_error(
                "design_params must be a dictionary",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format design_params as a dictionary with design block structure")
            return

        # Reuse design block validation logic
        # Save current block context and temporarily set to design
        original_block = self.current_block
        self.current_block = "design"

        # Validate as a design block first
        self._validate_design_block(design_params)

        # Additional validation for guided discovery specific requirements
        if "candidates_per_cycle" not in design_params:
            error = self.result.add_error(
                "design_params in guided_discovery requires 'candidates_per_cycle'",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix("Add 'candidates_per_cycle: <positive_integer>' to design_params")
        else:
            candidates_per_cycle = design_params["candidates_per_cycle"]
            if not isinstance(candidates_per_cycle, int) or candidates_per_cycle <= 0:
                error = self.result.add_error(
                    f"candidates_per_cycle must be a positive integer, got {candidates_per_cycle}",
                    ErrorCodes.TYPE_INVALID_TYPE,
                )
                error.add_fix("Use a positive integer for candidates_per_cycle")

        # Restore original block context
        self.current_block = original_block

    def _validate_guided_discovery_active_learning_params(self, active_learning_params: Any) -> None:
        """Validate active_learning_params in guided_discovery block."""
        if not isinstance(active_learning_params, dict):
            self.result.add_error(
                "active_learning_params must be a dictionary",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format active_learning_params as a dictionary with optimize block structure")
            return

        # Reuse optimize block validation logic
        # Save current block context and temporarily set to optimize
        original_block = self.current_block
        self.current_block = "optimize"

        # Validate as an optimize block first
        self._validate_optimize_block(active_learning_params)

        # Additional validation for guided discovery specific requirements
        if "experiments_per_cycle" not in active_learning_params:
            error = self.result.add_error(
                "active_learning_params in guided_discovery requires 'experiments_per_cycle'",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix("Add 'experiments_per_cycle: <positive_integer>' to active_learning_params")
        else:
            experiments_per_cycle = active_learning_params["experiments_per_cycle"]
            if not isinstance(experiments_per_cycle, int) or experiments_per_cycle <= 0:
                error = self.result.add_error(
                    f"experiments_per_cycle must be a positive integer, got {experiments_per_cycle}",
                    ErrorCodes.TYPE_INVALID_TYPE,
                )
                error.add_fix("Use a positive integer for experiments_per_cycle")

        # Restore original block context
        self.current_block = original_block

    def _validate_guided_discovery_budget(self, budget: Any) -> None:
        """Validate budget in guided_discovery block."""
        if not isinstance(budget, dict):
            self.result.add_error(
                "budget must be a dictionary",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format budget as a dictionary with at least one budget constraint")
            return

        # Must contain at least one of the specified keys
        valid_budget_keys = {"max_cycles", "convergence_threshold", "target_objective_value"}
        present_keys = set(budget.keys()) & valid_budget_keys

        if not present_keys:
            error = self.result.add_error(
                "budget must contain at least one of: max_cycles, convergence_threshold, target_objective_value",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix("Add at least one budget constraint like 'max_cycles: 10'")
            error.add_context("valid_budget_keys", list(valid_budget_keys))
            return

        # Validate each present key
        for key, value in budget.items():
            if key == "max_cycles":
                if not isinstance(value, int) or value <= 0:
                    error = self.result.add_error(
                        f"max_cycles must be a positive integer, got {value}",
                        ErrorCodes.TYPE_INVALID_TYPE,
                    )
                    error.add_fix("Use a positive integer for max_cycles")
            elif key == "convergence_threshold":
                if not isinstance(value, (int, float)) or value <= 0:
                    error = self.result.add_error(
                        f"convergence_threshold must be a positive number, got {value}",
                        ErrorCodes.TYPE_INVALID_TYPE,
                    )
                    error.add_fix("Use a positive number for convergence_threshold")
            elif key == "target_objective_value" and not isinstance(value, (int, float)):
                self.result.add_error(
                    f"target_objective_value must be a number, got {type(value).__name__}",
                    ErrorCodes.TYPE_INVALID_TYPE,
                ).add_fix("Use a number for target_objective_value")

    def _validate_guided_discovery_output(self, output: Any) -> None:
        """Validate output in guided_discovery block."""
        if not isinstance(output, str):
            self.result.add_error(
                f"output must be a string, got {type(output).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Use a string identifier for output")
            return

        # Validate identifier format
        import re

        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", output):
            error = self.result.add_error(
                f"Invalid output identifier '{output}'",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            )
            error.add_fix("Use a valid identifier like 'discovered_candidates' or 'output_results'")


# Legacy validator for backward compatibility
class SemanticValidator:
    """Legacy semantic validator for backward compatibility.

    Maintains the original API while delegating to the enhanced validator.
    """

    def __init__(self):
        self.symbol_table = {}
        self.errors = []
        self._enhanced_validator = EnhancedSemanticValidator()

    def validate_program(self, ast):
        """Validate a program AST and return a list of error strings."""
        result = self._enhanced_validator.validate_ast(ast)
        return result.to_legacy_format()


# Global validator instances
_validator = SemanticValidator()
_enhanced_validator = EnhancedSemanticValidator()


def validate(ast: dict[str, Any], enhanced: bool = False) -> Union[list[str], EnhancedValidationResult]:
    """Validate a GFL AST and return validation results.

    Args:
        ast: The AST dictionary to validate.
        enhanced: If True, return EnhancedValidationResult. If False, return legacy string list.

    Returns:
        List of error strings (legacy) or EnhancedValidationResult (enhanced).
    """
    if enhanced:
        return _enhanced_validator.validate_ast(ast)
    else:
        return _validator.validate_program(ast)


__all__ = ["SemanticValidator", "EnhancedSemanticValidator", "validate"]
