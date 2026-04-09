# GF-163.1 - Implement Container-Based Plugin Execution

## Summary

Successfully implemented container-based plugin execution for GFL to ensure reproducibility and eliminate dependency on locally installed tools. This feature allows plugins to specify Docker container images that contain all necessary dependencies for execution.

## Changes Made

### 1. Plugin Registry Updates
- Modified [gfl/plugins/plugin_registry.py](file:///C:/Users/usuario/GeneForgeLang/gfl/plugins/plugin_registry.py) to discover container images through `gfl.plugin_containers` entry points
- Added `_container_images` dictionary to store plugin-to-container mappings
- Implemented `get_container_image()` method to retrieve container images for plugins
- Updated `_discover_plugins()` to use `entry_points().select()` for proper entry point discovery

### 2. Container Executor Implementation
- Created [gfl/container_executor.py](file:///C:/Users/usuario/GeneForgeLang/gfl/container_executor.py) with `ContainerExecutor` class
- Implemented Docker integration using `docker-py` library
- Added automatic volume mounting for file I/O operations
- Implemented error handling for container execution failures
- Added fallback mechanism when Docker is not available

### 3. Execution Engine Updates
- Modified [gfl/execution_engine.py](file:///C:/Users/usuario/GeneForgeLang/gfl/execution_engine.py) to check for container images before execution
- Implemented automatic switching between container and local execution
- Added `ContainerExecutor` integration with proper error handling

### 4. Dependency Management
- Added `docker>=7.0.0` as optional dependency in [pyproject.toml](file:///C:/Users/usuario/GeneForgeLang/pyproject.toml) under `containers` extra
- Updated `all` extra to include `containers` dependency

### 5. Plugin Example Updates
- Updated [gfl-plugin-samtools/pyproject.toml](file:///C:/Users/usuario/GeneForgeLang/gfl-plugin-samtools/pyproject.toml) to include container entry point example
- Added `[project.entry-points."gfl.plugin_containers"]` section with `biocontainers/samtools:v1.15.1_cv4`

### 6. Documentation
- Created [docs/container_execution.md](file:///C:/Users/usuario/GeneForgeLang/docs/container_execution.md) with comprehensive documentation
- Added container execution example in [examples/container_execution_example.gfl](file:///C:/Users/usuario/GeneForgeLang/examples/container_execution_example.gfl)
- Updated [README.md](file:///C:/Users/usuario/GeneForgeLang/README.md) to mention container execution feature
- Updated [CHANGELOG.md](file:///C:/Users/usuario/GeneForgeLang/CHANGELOG.md) to document the new feature

### 7. Testing
- Created [tests/test_container_execution.py](file:///C:/Users/usuario/GeneForgeLang/tests/test_container_execution.py) with unit tests for container execution functionality

## How It Works

1. Plugins can optionally specify container images through the `gfl.plugin_containers` entry point group in their `pyproject.toml`
2. The plugin registry automatically discovers these container images during initialization
3. When executing a plugin method, the execution engine first checks if a container image is associated with the plugin
4. If a container image is found and Docker is available, the method is executed within the container with automatic volume mounting
5. If no container image is found or Docker is not available, the method falls back to local execution

## Backward Compatibility

This implementation maintains full backward compatibility:
- Plugins without container images continue to work exactly as before
- Systems without Docker continue to work exactly as before
- All existing workflows continue to function unchanged
- No breaking changes to existing APIs

## Usage

To use container execution:

1. Install with container support:
   ```bash
   pip install geneforgelang[containers]
   ```

2. Plugins can specify container images in their `pyproject.toml`:
   ```toml
   [project.entry-points."gfl.plugins"]
   samtools = "gfl_plugin_samtools.plugin:SamtoolsPlugin"

   [project.entry-points."gfl.plugin_containers"]
   samtools = "biocontainers/samtools:v1.15.1_cv4"
   ```

3. Workflows will automatically execute in containers when available:
   ```gfl
   design:
     model: samtools
     entity: AlignmentFile
     count: 5
   ```

This implementation fulfills all requirements from Epic GF-163 and Task GF-163.1, providing a robust, reproducible execution environment for GFL workflows.
