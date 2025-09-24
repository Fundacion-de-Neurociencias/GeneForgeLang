#!/usr/bin/env python3
"""
Test script to check if the GFL service can be imported and started.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    print("Attempting to import gfl_service...")
    import gfl_service

    print("Successfully imported gfl_service")
    print("Health check endpoint is available at: /health")
    print("Service title:", gfl_service.app.title)
    print("Service description:", gfl_service.app.description)
    print("\nService routes:")
    for route in gfl_service.app.routes:
        print(f"  {route.methods} {route.path}")
except Exception as e:
    print(f"Error importing gfl_service: {e}")
    import traceback

    traceback.print_exc()
