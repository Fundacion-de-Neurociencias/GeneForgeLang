# GATK Plugin

Genomic Analysis Toolkit (GATK) plugin for GeneForgeLang that enables variant calling, genotyping, and other genomic analysis workflows directly from GFL.

## Overview

This plugin provides integration with the Genomic Analysis Toolkit (GATK), allowing users to perform variant calling, genotyping, and other genomic analysis tasks directly from GeneForgeLang workflows. It supports key GATK tools including HaplotypeCaller, GenotypeGVCFs, and VariantFiltration.

## Features

- **Variant Calling**: HaplotypeCaller for SNP and indel detection
- **Genotyping**: GenotypeGVCFs for joint genotyping
- **Variant Filtering**: VariantFiltration for quality control
- **Configurable Parameters**: Set parameters for each GATK tool
- **Structured Output**: Returns parsed results in a clean JSON format
- **GFL Integration**: Seamlessly integrates with GeneForgeLang's plugin system

## Installation

```bash
pip install gfl-plugin-gatk
```

**Note**: This plugin requires GATK to be installed separately. Download GATK from [the Broad Institute website](https://gatk.broadinstitute.org/hc/en-us).

## Usage

Once installed, the plugin is automatically discovered by the GeneForgeLang service through entry points.

### Example GFL Workflow

```gfl
run:
  - plugin: "gatk"
    tool: "HaplotypeCaller"
    reference: "/path/to/reference.fasta"
    input_bam: "/path/to/sample.bam"
    output_vcf: "/path/to/output.vcf"
    as_var: "variant_calling_results"

output:
  - vcf_file: "${variant_calling_results.output_vcf}"
```

### Parameters

- `tool`: The GATK tool to run (HaplotypeCaller, GenotypeGVCFs, VariantFiltration, etc.)
- `reference`: Path to the reference genome FASTA file
- `input_bam`: Path to the input BAM file
- `output_vcf`: Path to the output VCF file
- Additional tool-specific parameters

## Supported Tools

### HaplotypeCaller

Calls germline SNPs and indels via local re-assembly of haplotypes.

**Parameters:**
- `input_bam`: Input BAM file
- `reference`: Reference genome FASTA
- `output_vcf`: Output VCF file
- `intervals`: Genomic intervals to process (optional)
- `stand_call_conf`: Minimum phred-scaled confidence threshold (default: 30)

### GenotypeGVCFs

Performs joint genotyping on one or more samples pre-called with HaplotypeCaller.

**Parameters:**
- `input_gvcfs`: List of input GVCF files
- `reference`: Reference genome FASTA
- `output_vcf`: Output VCF file
- `intervals`: Genomic intervals to process (optional)

### VariantFiltration

Filters variant calls based on INFO and/or FORMAT annotations.

**Parameters:**
- `input_vcf`: Input VCF file
- `output_vcf`: Output VCF file
- `filter_expressions`: List of filter expressions
- `filter_names`: Names for the filters

## Output Format

The plugin returns structured results containing:

- `tool`: The GATK tool that was run
- `output_files`: Dictionary of output files created
- `metrics`: Performance metrics and statistics
- `status`: Execution status (success/failure)

## Requirements

- GeneForgeLang >= 1.0.0
- GATK >= 4.0.0 (separate installation required)
- Java >= 8

## API Reference

### Class: GatkPlugin

#### Methods

##### `__init__(self, config: Optional[Dict[str, Any]] = None)`
Initialize the GATK plugin.

**Parameters:**
- `config`: Optional configuration dictionary

##### `run(self, input_data: Any, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
Execute a GATK tool.

**Parameters:**
- `input_data`: Input data containing file paths and parameters
- `params`: Optional parameters for the GATK tool

**Returns:**
- Dictionary containing GATK results

##### `validate_input(self, input_data: Any) -> bool`
Validate input data for the plugin.

**Parameters:**
- `input_data`: Input data to validate

**Returns:**
- True if input is valid, False otherwise

## Configuration

The plugin accepts optional configuration parameters:

```python
config = {
    "gatk_path": "/path/to/gatk/binaries",  # Path to GATK executables
    "java_path": "/path/to/java",  # Path to Java executable
    "default_memory": "4g",  # Default memory allocation
    "temp_dir": "/tmp/gatk"  # Temporary directory for GATK operations
}

plugin = GatkPlugin(config=config)
```

## Development

### Setting Up for Development

```bash
git clone https://github.com/Fundacion-de-Neurociencias/gfl-plugin-gatk.git
cd gfl-plugin-gatk
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black gfl_plugin_gatk/
ruff check gfl_plugin_gatk/
```

## Troubleshooting

### Common Issues

1. **GATK Not Found**: Ensure GATK is installed and in your PATH
2. **Java Issues**: Verify Java installation and version compatibility
3. **Memory Errors**: For large datasets, increase memory allocation
4. **File Permissions**: Check read/write permissions for input/output files

### Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples

### Basic Variant Calling

```gfl
input:
  reference_genome: "/data/reference/hg38.fasta"
  sample_bam: "/data/samples/sample1.bam"
  output_dir: "/data/results"

run:
  - plugin: "gatk"
    tool: "HaplotypeCaller"
    reference: "${reference_genome}"
    input_bam: "${sample_bam}"
    output_vcf: "${output_dir}/sample1.vcf"
    stand_call_conf: 30
    as_var: "haplotypecaller_results"

output:
  - variant_calls: "${haplotypecaller_results.output_vcf}"
```

### Joint Genotyping Workflow

```gfl
input:
  reference_genome: "/data/reference/hg38.fasta"
  sample_gvcfs: [
    "/data/gvcfs/sample1.g.vcf",
    "/data/gvcfs/sample2.g.vcf",
    "/data/gvcfs/sample3.g.vcf"
  ]
  output_dir: "/data/results"

run:
  - plugin: "gatk"
    tool: "GenotypeGVCFs"
    reference: "${reference_genome}"
    input_gvcfs: "${sample_gvcfs}"
    output_vcf: "${output_dir}/joint_genotyped.vcf"
    as_var: "genotyping_results"

process:
  - name: "filter_variants"
    plugin: "gatk"
    tool: "VariantFiltration"
    input_vcf: "${genotyping_results.output_vcf}"
    output_vcf: "${output_dir}/filtered_variants.vcf"
    filter_expressions: [
      "QD < 2.0",
      "MQ < 40.0",
      "FS > 60.0"
    ]
    filter_names: [
      "LowQualityDepth",
      "LowMappingQuality",
      "HighStrandBias"
    ]
    as_var: "filtered_results"

output:
  - final_variants: "${filtered_results.output_vcf}"
```

## License

This project is licensed under the MIT License.