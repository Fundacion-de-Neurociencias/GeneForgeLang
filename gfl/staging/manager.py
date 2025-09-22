"""DataStagingManager for handling file downloads and parameter resolution before plugin execution.

This module provides the DataStagingManager class that handles downloading files from signed URLs
to local temporary directories and resolving parameter references before plugin execution.
"""

import os
import logging
import shutil
import tempfile
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class DataStagingManager:
    """
    Manages the staging of data files for GFL workflow execution.
    
    This component handles downloading files from signed URLs to local temporary directories
    and resolving parameter references before plugin execution.
    """
    
    def __init__(self):
        """Initialize the DataStagingManager."""
        # Create a unique temporary directory for this workflow execution
        self.temp_dir = Path(tempfile.mkdtemp(prefix="gfl_run_"))
        self.staged_files: Dict[str, Path] = {}
        logger.info(f"Created temporary directory for data staging: {self.temp_dir}")
    
    def stage_files(self, params: Dict[str, Any], data_manifest: Dict[str, str]) -> Dict[str, Any]:
        """
        Stage files referenced in plugin parameters and update parameter values with local paths.
        
        Args:
            params: Dictionary of plugin parameters
            data_manifest: Dictionary mapping filenames to signed URLs
            
        Returns:
            Modified parameters dictionary with local file paths
        """
        # Make a copy of the parameters to avoid modifying the original
        modified_params = params.copy()
        
        # Iterate through each parameter
        for key, value in params.items():
            # Check if the parameter value exists as a key in the data manifest
            if isinstance(value, str) and value in data_manifest:
                try:
                    # Get the signed URL from the manifest
                    signed_url = data_manifest[value]
                    logger.info(f"Found file reference '{value}' in data manifest, staging file...")
                    
                    # Construct local destination path
                    local_path = self.temp_dir / value
                    logger.info(f"Downloading {value} to {local_path}")
                    
                    # Download the file from the signed URL
                    self._download_file_from_signed_url(signed_url, local_path)
                    
                    # Update the parameter value to point to the local path
                    modified_params[key] = str(local_path)
                    self.staged_files[value] = local_path
                    
                    logger.info(f"Successfully staged file '{value}' to '{local_path}'")
                except Exception as e:
                    logger.error(f"Failed to stage file '{value}': {e}")
                    # Keep the original value if staging fails
                    # This allows the plugin to handle the error appropriately
            else:
                # Parameter value is not a file reference, leave it unchanged
                logger.debug(f"Parameter '{key}' with value '{value}' is not a file reference, leaving unchanged")
        
        return modified_params
    
    def _download_file_from_signed_url(self, signed_url: str, destination: Path) -> None:
        """
        Download a file from a signed URL to a local destination using requests.
        
        Args:
            signed_url: Signed URL to download from
            destination: Local path to save the file to
        """
        try:
            # Create the destination directory if it doesn't exist
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Use requests to download from the signed URL
            import requests  # type: ignore
            with requests.get(signed_url, stream=True) as response:
                response.raise_for_status()
                with open(destination, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            logger.info(f"Downloaded file to {destination}")
        except Exception as e:
            logger.error(f"Failed to download file from {signed_url}: {e}")
            raise
    
    def cleanup(self) -> None:
        """
        Clean up the temporary directory and all staged files.
        """
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                logger.error(f"Failed to clean up temporary directory {self.temp_dir}: {e}")
        else:
            logger.info("No temporary directory to clean up")
