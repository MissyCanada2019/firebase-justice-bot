#!/usr/bin/env python3

"""
Start both the main application and port 8080 forwarder
"""

import os
import subprocess
import time
import sys

def restart_workflow(name):
    """
    Restart a workflow using the Replit workflow system
    """
    print(f"Restarting workflow: {name}")
    try:
        # Use the replit workflow command to restart the workflow
        subprocess.run(["workflows", "restart", name], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error restarting workflow '{name}': {e}")
        return False
    except Exception as e:
        print(f"Unexpected error restarting workflow '{name}': {e}")
        return False

def main():
    """Main function"""
    print("Starting both servers...")
    
    # First, start the main application
    main_app_success = restart_workflow("Start application")
    if not main_app_success:
        print("Failed to start the main application workflow")
        sys.exit(1)
    
    print("Waiting for main application to initialize...")
    time.sleep(5)  # Give the main app some time to start
    
    # Then start the port 8080 forwarder
    forwarder_success = restart_workflow("Port 8080 Forwarder")
    if not forwarder_success:
        print("Failed to start the port 8080 forwarder workflow")
        sys.exit(1)
    
    print("Both workflows started successfully!")
    print("Main application running on port 5000")
    print("Port 8080 forwarder is running")

if __name__ == "__main__":
    main()
