# Container-Based Plugin Execution

## Overview

GFL now supports container-based plugin execution to ensure reproducibility and eliminate dependency on locally installed tools. This feature allows plugins to specify Docker container images that contain all necessary dependencies for execution.

## How It Works

1. Plugins can optionally specify a container image through the `gfl.plugin_containers` entry point group
2. The execution engine automatically detects container images for plugins
3. If a container image is available and Docker is installed, the plugin is executed within the container
4. If no container image is available or Docker is not available, the plugin falls back to local execution

## Plugin Definition with Container Support

Plugins can specify container images in their `pyproject.toml` file:

```toml
[project.entry-points."gfl.plugins"]
samtools = "gfl_plugin_samtools.plugin:SamtoolsPlugin"

[project.entry-points."gfl.plugin_containers"]
samtools = "biocontainers/samtools:v1.15.1_cv4"
```

## Dependencies

To use container execution, install the `containers` extra:

```bash
pip install geneforgelang[containers]
```

This installs the `docker` Python package required for container interaction.

## Execution Flow

1. When executing a plugin method, the execution engine first checks if a container image is associated with the plugin
2. If a container image is found and Docker is available, the method is executed within the container
3. If no container image is found or Docker is not available, the method is executed locally as before

## Volume Mounting

When executing in containers, the system automatically:
- Creates temporary directories for file I/O
- Mounts these directories into the container
- Handles input file copying and output file retrieval
- Cleans up temporary directories after execution

## Backward Compatibility

This feature maintains full backward compatibility:
- Plugins without container images continue to work as before
- Systems without Docker continue to work as before
- All existing workflows continue to function unchanged

## Example Workflow

A GFL workflow using a containerized plugin:

```gfl
design:
  model: samtools
  entity: AlignmentFile
  count: 10
  objective:
    quality: high
```

When executed, if the `samtools` plugin has a container image specified, it will run within that container rather than requiring `samtools` to be installed locally.
