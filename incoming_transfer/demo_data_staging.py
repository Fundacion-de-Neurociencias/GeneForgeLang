#!/usr/bin/env python3
"""
Demo script showing the complete DataStagingManager workflow.
"""

import sys
import os
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

# Add the GeneForge directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from geneforge_app.execution_components.data_staging_manager import DataStagingManager


def demo_data_staging_workflow():
    """Demonstrate the complete data staging workflow."""
    print("=== DataStagingManager Workflow Demo ===\n")
    
    # 1. Simulate receiving a workflow request with project context
    print("1. Workflow Request Received")
    workflow_request = {
        "prompt": "Run samtools alignment on my sample",
        "project_id": 123
    }
    print(json.dumps(workflow_request, indent=2))
    print()
    
    # 2. Simulate GFL script generation
    print("2. GFL Script Generated")
    gfl_script = '''
experiment:
  tool: samtools
  type: alignment
  params:
    input_file: "sample.sam"
    reference_file: "hg38.fasta"
    output_file: "aligned.bam"
    threads: 4
    
analyze:
  strategy: "variant_calling"
  params:
    input_bam: "aligned.bam"
    reference: "hg38.fasta"
    output_vcf: "variants.vcf"
'''
    print(gfl_script)
    print()
    
    # 3. Simulate data context preparation (from GF-165.1)
    print("3. Data Context Prepared")
    data_context = {
        "sample.sam": "https://storage.googleapis.com/geneforge-data-bucket/projects/123/files/456/sample.sam?X-Goog-Signature=abc123...",
        "hg38.fasta": "https://storage.googleapis.com/geneforge-data-bucket/projects/123/files/789/hg38.fasta?X-Goog-Signature=def456...",
        "variants.vcf": "https://storage.googleapis.com/geneforge-data-bucket/projects/123/files/101/variants.vcf?X-Goog-Signature=ghi789..."
    }
    print("Data Manifest:")
    print(json.dumps(data_context, indent=2))
    print()
    
    # 4. Create and use DataStagingManager
    print("4. Data Staging Process")
    
    # Create DataStagingManager instance
    data_staging_manager = DataStagingManager()
    print(f"   Created temporary directory: {data_staging_manager.temp_dir}")
    
    # Simulate plugin execution - first plugin (samtools alignment)
    print("\n   Executing Plugin: samtools alignment")
    samtools_params = {
        "input_file": "sample.sam",
        "reference_file": "hg38.fasta", 
        "output_file": "aligned.bam",
        "threads": 4
    }
    print(f"   Original parameters: {samtools_params}")
    
    # In a real implementation, we would download from signed URLs
    # For demo purposes, we'll create mock files
    _create_mock_files(data_staging_manager.temp_dir, ["sample.sam", "hg38.fasta"])
    
    # Stage files for this plugin
    staged_samtools_params = data_staging_manager.stage_files(samtools_params, data_context)
    print(f"   Staged parameters: {staged_samtools_params}")
    print(f"   Files staged: {list(data_staging_manager.staged_files.keys())}")
    
    # Simulate plugin execution (in reality, this would call the GFL service)
    print("   Plugin execution would now use local file paths...")
    
    # Simulate second plugin execution (variant calling)
    print("\n   Executing Plugin: variant calling")
    variant_params = {
        "input_bam": "aligned.bam",  # This would be created by previous step
        "reference": "hg38.fasta",   # This should use the already staged file
        "output_vcf": "variants.vcf"
    }
    print(f"   Original parameters: {variant_params}")
    
    # Stage files for this plugin (hg38.fasta should already be staged)
    _create_mock_files(data_staging_manager.temp_dir, ["aligned.bam"])  # Simulate output from previous step
    staged_variant_params = data_staging_manager.stage_files(variant_params, data_context)
    print(f"   Staged parameters: {staged_variant_params}")
    
    # 5. Cleanup
    print(f"\n5. Cleanup Process")
    print(f"   Cleaning up temporary directory: {data_staging_manager.temp_dir}")
    data_staging_manager.cleanup()
    print(f"   Cleanup completed. Directory exists: {data_staging_manager.temp_dir.exists()}")
    
    print("\n=== Workflow Demo Complete ===")


def _create_mock_files(temp_dir: Path, filenames: list):
    """Create mock files for demonstration purposes."""
    for filename in filenames:
        file_path = temp_dir / filename
        file_path.write_text(f"Mock content for {filename}")
        print(f"     Created mock file: {filename}")


def demo_context_enhancement():
    """Demonstrate how the execution context is enhanced with staging information."""
    print("\n=== Context Enhancement Demo ===\n")
    
    # Original context from data preparation
    original_context = {
        "data_files": {
            "sample.sam": "https://storage.googleapis.com/geneforge-data-bucket/projects/123/files/456/sample.sam?X-Goog-Signature=abc123...",
            "reference.fasta": "https://storage.googleapis.com/geneforge-data-bucket/projects/123/files/789/reference.fasta?X-Goog-Signature=def456..."
        }
    }
    
    print("1. Original Execution Context:")
    print(json.dumps(original_context, indent=2))
    
    # Enhanced context with staging information
    enhanced_context = original_context.copy()
    enhanced_context["staged_files"] = {
        "sample.sam": "/tmp/gfl_run_xyz123/sample.sam",
        "reference.fasta": "/tmp/gfl_run_xyz123/reference.fasta"
    }
    
    print("\n2. Enhanced Execution Context (with staging):")
    print(json.dumps(enhanced_context, indent=2))
    
    print("\n3. How GFL Service Would Use This:")
    print("   - Check if 'staged_files' exists in context")
    print("   - If a parameter value matches a key in 'staged_files', use the local path")
    print("   - Otherwise, use the original value or download from 'data_files'")
    print("   - This provides transparent access to staged files")


def demo_error_handling():
    """Demonstrate error handling in the DataStagingManager."""
    print("\n=== Error Handling Demo ===\n")
    
    data_staging_manager = DataStagingManager()
    
    # Simulate a case where a file cannot be downloaded
    print("1. Handling Download Failure:")
    problematic_manifest = {
        "missing_file.txt": "https://example.com/missing_file.txt"  # This URL doesn't exist
    }
    
    params = {
        "input": "missing_file.txt",
        "output": "result.txt"
    }
    
    print(f"   Parameters: {params}")
    print(f"   Manifest contains invalid URL for 'missing_file.txt'")
    print("   DataStagingManager will:")
    print("   - Log the error")
    print("   - Keep the original parameter value")
    print("   - Continue execution")
    
    # In a real scenario, this would fail to download
    # For demo, we'll show what happens
    try:
        result = data_staging_manager.stage_files(params, problematic_manifest)
        print(f"   Result: {result}")
        print("   ✓ Original parameter preserved despite download failure")
    except Exception as e:
        print(f"   Error (this shouldn't happen in production): {e}")
    
    # Cleanup
    data_staging_manager.cleanup()
    
    print("\n2. Handling Cleanup Failures:")
    print("   - DataStagingManager uses try/finally blocks")
    print("   - Even if cleanup fails, the system continues")
    print("   - Errors are logged but don't stop workflow execution")


if __name__ == "__main__":
    demo_data_staging_workflow()
    demo_context_enhancement()
    demo_error_handling()
    
    print("\n" + "="*60)
    print("DataStagingManager Implementation Summary:")
    print("="*60)
    print("✓ Creates unique temporary directories for each workflow")
    print("✓ Downloads files from signed URLs to local storage")
    print("✓ Updates plugin parameters with local file paths")
    print("✓ Handles download failures gracefully")
    print("✓ Ensures cleanup of temporary files")
    print("✓ Integrates with existing GeneForge workflow engine")
    print("✓ Maintains compatibility with GFL service")
    print("\nThe DataStagingManager provides a robust, secure, and")
    print("efficient way to handle file access in GFL workflows.")