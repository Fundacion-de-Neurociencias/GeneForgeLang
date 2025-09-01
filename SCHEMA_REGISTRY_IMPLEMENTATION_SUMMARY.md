# Schema Registry Implementation Summary

This document summarizes the implementation of a Type System and Schema Registry for GeneForgeLang (GFL), which enables users and plugin developers to define custom data types and their attributes in external files, creating an extensible type system.

## Features Implemented

### 1. Schema Loader

**File Created:** `gfl/schema_loader.py`

**Enhancements:**
- Created `SchemaDefinition` class to represent schema definitions loaded from YAML files
- Created `SchemaLoader` class to parse and validate external schema definition files
- Added validation for schema structure including required fields and attribute definitions
- Implemented global schema loader instance for shared access

### 2. New Error Codes

**File Modified:** `gfl/error_handling.py`

**Enhancements:**
- Added new error codes for schema validation:
  - `SEMANTIC_INVALID_SCHEMA_FILE` - Invalid schema file structure
  - `SEMANTIC_SCHEMA_NOT_FOUND` - Referenced schema not found
  - `SEMANTIC_INVALID_SCHEMA_DEFINITION` - Invalid schema definition

### 3. Parser Extension

**File Modified:** `gfl/parser.py`

**Enhancements:**
- Extended parser to recognize `import_schemas` directive at the root level
- Added `parse_gfl_with_schema_imports` function to handle schema imports
- Maintained backward compatibility with existing parsing functionality

### 4. Schema Registry Integration

**File Modified:** `gfl/semantic_validator.py`

**Enhancements:**
- Extended `EnhancedSemanticValidator` to load schema imports during validation
- Added `_load_schema_imports()` method to process `import_schemas` directives
- Integrated schema registry into contract validation logic
- Updated `_validate_contract_definition()` to validate against schema definitions
- Added `_validate_schema_attributes()` to check required attributes and values
- Enhanced type compatibility checking to work with custom schema types
- Added `_are_base_types_compatible()` for base type compatibility rules

## Code Structure Changes

### New Files
1. `gfl/schema_loader.py` - Schema loading and validation functionality

### Updated Methods
1. `EnhancedSemanticValidator.validate_ast()` - Extended to load schema imports
2. `EnhancedSemanticValidator._load_schema_imports()` - Processes schema imports
3. `EnhancedSemanticValidator._validate_contract_definition()` - Validates against schemas
4. `EnhancedSemanticValidator._validate_schema_attributes()` - Validates schema attributes
5. `EnhancedSemanticValidator._are_contract_types_compatible()` - Enhanced type compatibility
6. `EnhancedSemanticValidator._are_base_types_compatible()` - Base type compatibility rules

## Example Usage

### Schema Definition File (my_custom_types.yml):
```yaml
schemas:
  # Definition of a paired-end FASTQ type
  FASTQ_PairedEnd:
    type: "FASTQ"
    description: "FASTQ format with paired-end layout"
    attributes:
      layout: 
        type: "string"
        required: true
        value: "paired-end"

  # Definition of a stricter BAM type
  BAM_Indexed:
    type: "BAM"
    description: "BAM format that is sorted and indexed"
    attributes:
      sorted: 
        type: "boolean"
        required: true
        value: true
      indexed: 
        type: "boolean"
        required: true
        value: true
```

### GFL Script with Schema Import:
```yaml
# Import custom schema definitions
import_schemas:
  - ./my_custom_types.yml

experiment:
  tool: "sequence_aligner"
  type: "sequencing"
  input: raw_sequences
  output: aligned_reads
  contract:
    inputs:
      raw_sequences: 
        type: "FASTQ_PairedEnd" # Uses custom type
    outputs:
      aligned_reads: 
        type: "BAM_Indexed" # Uses custom type

analyze:
  strategy: "variant"
  input: aligned_reads
  output: variants
  contract:
    inputs:
      # Validator now knows that 'BAM_Indexed' must have sorted=true and indexed=true
      aligned_reads: 
        type: "BAM_Indexed"
    outputs:
      variants: 
        type: "VCF"
```

## Benefits

1. **Extensible Type System**: Users can define custom data types beyond the built-in ones
2. **Enhanced Validation**: Contract validation now checks required attributes and values
3. **Community Sharing**: Schema files can be shared and reused across projects
4. **Backward Compatibility**: Existing GFL files continue to work without modification
5. **Improved Documentation**: Schema files serve as explicit documentation of data expectations
6. **Plugin Integration**: Plugin developers can define schemas for their tools' data types

## Backward Compatibility

All changes are backward compatible:
- Existing GFL files without schema imports continue to work without modification
- Schema validation only occurs when schemas are explicitly imported and used
- Default behavior is preserved when custom schemas are not present
- Built-in type compatibility rules remain unchanged

## Technical Implementation Details

### Schema File Format
Schema files use a simple YAML structure:
```yaml
schemas:
  <SchemaName>:
    type: <BaseType>
    description: <OptionalDescription>
    attributes:
      <AttributeName>:
        type: <AttributeType>
        required: <true|false>
        value: <ExpectedValue>
```

### Schema Loading Process
1. Parser recognizes `import_schemas` directive
2. Validator loads all referenced schema files
3. Schema definitions are stored in a global registry
4. Contract validation checks types against the registry
5. Attribute validation ensures required attributes are present with correct values

### Type Compatibility Rules
The implementation maintains and extends existing compatibility rules:
- FASTQ → FASTQ, TEXT
- FASTA → FASTA, TEXT
- BAM → BAM, SAM, BINARY
- SAM → SAM, BAM, TEXT
- VCF → VCF, TEXT
- CSV → CSV, TEXT
- JSON → JSON, TEXT
- Custom schemas are compatible if their base types are compatible