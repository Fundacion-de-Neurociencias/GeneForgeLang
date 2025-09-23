# SAMtools Plugin

SAMtools plugin for GeneForgeLang that enables sequence alignment manipulation and analysis directly from GFL workflows.

## Overview

This plugin provides integration with SAMtools, allowing users to manipulate and analyze sequence alignment files (SAM/BAM/CRAM) directly from GeneForgeLang workflows. It supports key SAMtools operations including sorting, indexing, filtering, and statistics generation.

## Features

- **File Manipulation**: Sort, index, and convert alignment files
- **Filtering**: Filter alignments based on various criteria
- **Statistics**: Generate alignment statistics and metrics
- **Configurable Parameters**: Set parameters for each SAMtools operation
- **Structured Output**: Returns parsed results in a clean JSON format
- **GFL Integration**: Seamlessly integrates with GeneForgeLang's plugin system

## Installation

```bash
pip install gfl-plugin-samtools
```

**Note**: This plugin requires SAMtools to be installed separately. Install SAMtools using your system's package manager or download from [the official website](http://www.htslib.org/).

## Usage

Once installed, the plugin is automatically discovered by the GeneForgeLang service through entry points.

### Example GFL Workflow

```gfl
run:
  - plugin: "samtools"
    operation: "sort"
    input_bam: "/path/to/unsorted.bam"
    output_bam: "/path/to/sorted.bam"
    as_var: "sorting_results"

  - plugin: "samtools"
    operation: "index"
    input_bam: "/path/to/sorted.bam"
    as_var: "indexing_results"

output:
  - sorted_bam: "${sorting_results.output_bam}"
  - bam_index: "${indexing_results.output_bai}"
```

### Parameters

- `operation`: The SAMtools operation to perform (sort, index, view, stats, etc.)
- `input_bam`: Path to the input BAM file
- `output_bam`: Path to the output BAM file (for operations that create new files)
- Additional operation-specific parameters

## Supported Operations

### sort

Sorts SAM/BAM/CRAM files by chromosome and genomic coordinate.

**Parameters:**
- `input_bam`: Input alignment file
- `output_bam`: Output sorted file
- `sort_order`: Sort order (coordinate, queryname, etc.)
- `memory_limit`: Memory limit for sorting

### index

Creates an index for a sorted BAM/CRAM file.

**Parameters:**
- `input_bam`: Input sorted alignment file
- `output_bai`: Output index file (optional, auto-generated if not specified)

### view

Converts between SAM/BAM/CRAM formats and filters alignments.

**Parameters:**
- `input_file`: Input alignment file
- `output_file`: Output file
- `regions`: Genomic regions to include (optional)
- `filters`: Filtering criteria (mapping quality, flags, etc.)

### stats

Generates comprehensive statistics for alignment files.

**Parameters:**
- `input_bam`: Input alignment file
- `output_stats`: Output statistics file
- `regions`: Genomic regions to analyze (optional)

### flagstat

Counts the number of alignments for each FLAG type.

**Parameters:**
- `input_bam`: Input alignment file
- `output_flagstat`: Output flagstat file

## Output Format

The plugin returns structured results containing:

- `operation`: The SAMtools operation that was performed
- `output_files`: Dictionary of output files created
- `metrics`: Performance metrics and statistics
- `status`: Execution status (success/failure)

## Requirements

- GeneForgeLang >= 1.0.0
- SAMtools >= 1.9 (separate installation required)
- pysam >= 0.15.0

## API Reference

### Class: SamtoolsPlugin

#### Methods

##### `__init__(self, config: Optional[Dict[str, Any]] = None)`
Initialize the SAMtools plugin.

**Parameters:**
- `config`: Optional configuration dictionary

##### `run(self, input_data: Any, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
Execute a SAMtools operation.

**Parameters:**
- `input_data`: Input data containing file paths and parameters
- `params`: Optional parameters for the SAMtools operation

**Returns:**
- Dictionary containing SAMtools results

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
    "samtools_path": "/path/to/samtools/binaries",  # Path to SAMtools executables
    "default_memory": "2g",  # Default memory allocation
    "temp_dir": "/tmp/samtools"  # Temporary directory for operations
}

plugin = SamtoolsPlugin(config=config)
```

## Development

### Setting Up for Development

```bash
git clone https://github.com/Fundacion-de-Neurociencias/gfl-plugin-samtools.git
cd gfl-plugin-samtools
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black gfl_plugin_samtools/
ruff check gfl_plugin_samtools/
```

## Troubleshooting

### Common Issues

1. **SAMtools Not Found**: Ensure SAMtools is installed and in your PATH
2. **File Format Errors**: Verify input file formats (SAM/BAM/CRAM)
3. **Memory Errors**: For large files, increase memory allocation
4. **Indexing Issues**: Ensure input files are properly sorted before indexing

### Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples

### Basic Sorting and Indexing Workflow

```gfl
input:
  unsorted_bam: "/data/alignments/sample1_unsorted.bam"
  output_dir: "/data/alignments"

run:
  - plugin: "samtools"
    operation: "sort"
    input_bam: "${unsorted_bam}"
    output_bam: "${output_dir}/sample1_sorted.bam"
    sort_order: "coordinate"
    as_var: "sorting_results"

  - plugin: "samtools"
    operation: "index"
    input_bam: "${sorting_results.output_bam}"
    as_var: "indexing_results"

output:
  - sorted_bam: "${sorting_results.output_bam}"
  - bam_index: "${indexing_results.output_bai}"
```

### Alignment Statistics and Filtering

```gfl
input:
  input_bam: "/data/alignments/sample1.bam"
  output_dir: "/data/stats"

run:
  - plugin: "samtools"
    operation: "stats"
    input_bam: "${input_bam}"
    output_stats: "${output_dir}/sample1_stats.txt"
    as_var: "stats_results"

  - plugin: "samtools"
    operation: "view"
    input_file: "${input_bam}"
    output_file: "${output_dir}/high_quality.bam"
    filters: [
      "-q 30",  # Minimum mapping quality
      "-F 2304"  # Exclude duplicates and secondary alignments
    ]
    as_var: "filtering_results"

  - plugin: "samtools"
    operation: "flagstat"
    input_bam: "${filtering_results.output_file}"
    output_flagstat: "${output_dir}/high_quality_flagstat.txt"
    as_var: "flagstat_results"

output:
  - alignment_stats: "${stats_results.output_stats}"
  - filtered_bam: "${filtering_results.output_file}"
  - flag_statistics: "${flagstat_results.output_flagstat}"
```

### Multi-Sample Processing Pipeline

```gfl
input:
  samples: [
    {"name": "sample1", "bam": "/data/alignments/sample1.bam"},
    {"name": "sample2", "bam": "/data/alignments/sample2.bam"},
    {"name": "sample3", "bam": "/data/alignments/sample3.bam"}
  ]
  output_dir: "/data/processed"

process:
  - name: "process_sample"
    for_each: "sample in samples"
    run:
      - plugin: "samtools"
        operation: "sort"
        input_bam: "${sample.bam}"
        output_bam: "${output_dir}/${sample.name}_sorted.bam"
        as_var: "sort_result_${sample.name}"
      
      - plugin: "samtools"
        operation: "index"
        input_bam: "${sort_result_${sample.name}.output_bam}"
        as_var: "index_result_${sample.name}"
    
    output:
      - sorted_bam_${sample.name}: "${sort_result_${sample.name}.output_bam}"
      - index_file_${sample.name}: "${index_result_${sample.name}.output_bai}"

output:
  - processed_samples: "All samples processed successfully"
```

## License

This project is licensed under the MIT License.