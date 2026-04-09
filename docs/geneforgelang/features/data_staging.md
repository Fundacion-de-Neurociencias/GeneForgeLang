# Data Staging Feature

## Overview

The Data Staging feature enables GeneForgeLang workflows to work with remote data files by automatically downloading them to local temporary directories before plugin execution. This ensures that plugins receive local file paths while maintaining security through signed URLs.

## Architecture

The data staging system consists of:

- **DataStagingManager**: Core class that handles file downloads and parameter resolution
- **GFL Service Integration**: Modified execution endpoint that uses data staging
- **Automatic Cleanup**: Temporary files are cleaned up after workflow completion

## Usage

### Basic Workflow

1. **Workflow Request**: GeneForge sends a GFL AST with file references and a data manifest
2. **Data Staging**: DataStagingManager downloads referenced files to local temporary directory
3. **Parameter Resolution**: File parameters are updated with local paths
4. **Plugin Execution**: Plugins receive local file paths instead of remote URLs
5. **Cleanup**: Temporary files are automatically removed after execution

### API Integration

The GFL service `/api/v2/execute` endpoint now accepts a `data_manifest` parameter:

```json
{
  "ast": {
    "experiment": {
      "tool": "samtools",
      "params": {
        "input_file": "sample.sam",
        "reference_file": "hg38.fasta"
      }
    }
  },
  "data_manifest": {
    "sample.sam": "https://storage.googleapis.com/bucket/sample.sam?signature=abc123",
    "hg38.fasta": "https://storage.googleapis.com/bucket/hg38.fasta?signature=def456"
  }
}
```

### Response Format

The execution response includes staging information:

```json
{
  "success": true,
  "result": {
    "status": "success",
    "staged_files": ["sample.sam", "hg38.fasta"],
    "plugin_params": {
      "input_file": "/tmp/gfl_run_123/sample.sam",
      "reference_file": "/tmp/gfl_run_123/hg38.fasta"
    }
  }
}
```

## Implementation Details

### DataStagingManager Class

```python
from gfl.staging import DataStagingManager

# Initialize manager
manager = DataStagingManager()

# Stage files
staged_params = manager.stage_files(plugin_params, data_manifest)

# Cleanup (automatic in GFL service)
manager.cleanup()
```

### Key Features

- **Unique Temporary Directories**: Each workflow execution gets its own temporary directory
- **Graceful Error Handling**: Download failures don't stop workflow execution
- **Parameter Preservation**: Non-file parameters remain unchanged
- **Automatic Cleanup**: Temporary files are removed after execution
- **Logging**: Comprehensive logging for debugging and monitoring

### Security Considerations

- **Signed URLs**: All remote file access uses signed URLs for security
- **Temporary Storage**: Files are stored in temporary directories that are cleaned up
- **No Persistent Storage**: No files are permanently stored on the GFL service
- **Error Isolation**: Download failures are logged but don't affect other files

## Configuration

### Dependencies

The data staging feature requires:

```toml
dependencies = [
    "requests>=2.25.0",
]

[project.optional-dependencies]
staging = [
    "google-cloud-storage>=2.0.0",
]
```

### Installation

```bash
# Basic installation (includes requests)
pip install geneforgelang

# With Google Cloud Storage support
pip install geneforgelang[staging]
```

## Testing

The data staging feature includes comprehensive tests:

- **Unit Tests**: Test individual DataStagingManager methods
- **Integration Tests**: Test complete workflow with GFL service
- **Error Handling Tests**: Test various failure scenarios
- **Mock Tests**: Test without actual file downloads

Run tests with:

```bash
pytest tests/test_data_staging.py
pytest tests/test_data_staging_integration.py
```

## Error Handling

The data staging system handles various error scenarios:

- **Download Failures**: Individual file download failures are logged but don't stop execution
- **Network Issues**: Temporary network issues are handled gracefully
- **Cleanup Failures**: Cleanup failures are logged but don't affect workflow results
- **Invalid URLs**: Invalid or expired signed URLs are handled gracefully

## Monitoring

The system provides comprehensive logging:

- **Info Level**: Normal staging operations and cleanup
- **Debug Level**: Detailed parameter processing information
- **Error Level**: Download failures and cleanup issues
- **Warning Level**: Non-critical issues and fallbacks

## Future Enhancements

Potential future improvements:

- **Caching**: Cache frequently used files to avoid re-downloading
- **Parallel Downloads**: Download multiple files in parallel for better performance
- **Progress Tracking**: Real-time progress updates for large file downloads
- **Retry Logic**: Automatic retry for failed downloads
- **Compression**: Support for compressed file formats
