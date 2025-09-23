"""Data staging module for GFL workflows.

This module provides functionality for staging data files from remote sources
to local temporary directories before plugin execution.
"""

from .manager import DataStagingManager

__all__ = ["DataStagingManager"]

