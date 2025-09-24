#!/usr/bin/env python3
"""
QA Service Starter for GeneForgeLang

This script starts the GFL service and waits for it to be healthy
before allowing other services to start or tests to run.
"""

import subprocess
import time
import requests
import sys
import os


def start_gfl_service():
    """Start the GFL service in the background."""
    print("Starting GFL service...")
    
    # Change to the GeneForgeLang directory
    os.chdir("c:\\Users\\usuario\\GeneForgeLang Ecosystem\\GeneForgeLang")
    
    # Check if service is already running
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("GFL service is already running and healthy!")
            return None
    except requests.exceptions.RequestException:
        pass  # Service is not running, proceed to start it
    
    # Start the service in the background
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "gfl_service:app", 
            "--host", "127.0.0.1", 
            "--port", "8000", 
            "--log-level", "info"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"GFL service started with PID {process.pid}")
        return process
    except Exception as e:
        print(f"Failed to start GFL service: {e}")
        return None


def wait_for_service_healthy(max_attempts=30, delay=1):
    """Wait for the GFL service to be healthy."""
    print("Waiting for GFL service to be healthy...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    print("✅ GFL service is healthy!")
                    return True
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1}/{max_attempts}: Service not ready yet")
        
        if attempt < max_attempts - 1:
            time.sleep(delay)
    
    print("❌ GFL service failed to become healthy within timeout")
    return False


def main():
    """Main function to start services and wait for health checks."""
    print("🚀 Starting QA services for GeneForgeLang")
    
    # Start the GFL service
    gfl_process = start_gfl_service()
    
    # If service was already running, just check health
    if gfl_process is None:
        if wait_for_service_healthy():
            print("✅ GFL service is ready for QA testing!")
            return
        else:
            print("❌ GFL service is not healthy")
            sys.exit(1)
    
    # Wait for the service to be healthy
    if not wait_for_service_healthy():
        print("Failed to start GFL service properly")
        try:
            gfl_process.terminate()
            gfl_process.wait(timeout=5)
        except:
            gfl_process.kill()
        sys.exit(1)
    
    print("✅ All services are ready for QA testing!")
    print("GFL service is running and healthy at http://localhost:8000")
    print("You can now run your QA tests or start other services")
    
    # Keep the script running to maintain the service
    try:
        gfl_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down services...")
        try:
            gfl_process.terminate()
            gfl_process.wait(timeout=5)
        except:
            gfl_process.kill()
        print("Services shut down successfully")


if __name__ == "__main__":
    main()