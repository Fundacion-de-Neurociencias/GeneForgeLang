# Locityper Haplotyping Conformance Tests v1.5.0

## Overview

These conformance tests validate that a GFL execution engine correctly implements support for genomic haplotyping using Locityper, including:
- Haplotype panel references in loci definitions
- Locityper tool invocation in analyze blocks
- LocusGenotypeResult schema validation
- Genotype reasoning predicates

## Test Cases

### 01_loci_with_haplotype_panel.gfl
**Purpose**: Validates parsing of `haplotype_panel` field in loci blocks

**Requirements:**
- Parser must accept `haplotype_panel` as optional locus field
- Field value must be stored and accessible
- Multiple loci with haplotype panels should be supported

**Expected Behavior:**
- No parsing errors
- Haplotype panel paths correctly associated with loci
- Loci remain valid without haplotype_panel (optional field)

### 02_locityper_analyze_block.gfl
**Purpose**: Validates analyze blocks using Locityper tool

**Requirements:**
- Engine must recognize `tool: "locityper"` in analyze blocks
- `target: locus(...)` references must resolve correctly
- Contract with LocusGenotypeResult type must validate
- Input/output contracts must be enforced

**Expected Behavior:**
- Analyze block parses without errors
- Locus reference resolves to defined locus with haplotype panel
- Output contract validates against LocusGenotypeResult schema
- BAM input requirements are checked

### 03_genotype_result_schema.gfl
**Purpose**: Validates LocusGenotypeResult schema structure and validation

**Requirements:**
- Schema must define required fields (haplotype1_id, haplotype2_id, quality_value)
- Schema must define optional fields correctly
- Type constraints must be enforced (strings, numbers)
- Contract validation must check attribute constraints

**Expected Behavior:**
- LocusGenotypeResult schema loads correctly
- Required field validation works
- Type checking enforces correct data types
- Attribute constraints (min values) are validated

## Schema Import

All tests require the Locityper types schema:
```yaml
import_schemas:
  - ./schema/locityper_types.yml
```

## Expected Engine Capabilities

A conformant engine should:
1. Parse loci blocks with optional `haplotype_panel` field
2. Validate haplotype_panel is a string (file path)
3. Support analyze blocks with `tool: "locityper"`
4. Resolve `locus(...)` references and access haplotype_panel
5. Validate contracts using LocusGenotypeResult type
6. (Future) Implement genotype predicates for rules

## Usage

To validate a GFL execution engine:

```bash
# Run conformance tests
gfl validate conformance_suite/v1.5.0/locityper_haplotyping/01_loci_with_haplotype_panel.gfl
gfl validate conformance_suite/v1.5.0/locityper_haplotyping/02_locityper_analyze_block.gfl
gfl validate conformance_suite/v1.5.0/locityper_haplotyping/03_genotype_result_schema.gfl
```

All tests should parse without errors and validate successfully.

## Notes

- These tests validate **syntax and structure**, not actual Locityper execution
- Haplotype panel files referenced may not exist (testing references only)
- Actual genotyping would require Locityper plugin implementation
- Predicate evaluation (genotype_contains, etc.) is reserved for future versions

