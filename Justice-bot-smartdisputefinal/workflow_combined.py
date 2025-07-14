#!/usr/bin/env python3
"""
Generate Replit workflow configuration for SmartDispute.ai

This script creates a workflow configuration that runs both
the main application and the port 8080 redirector in a single workflow.
"""

import json
import os

def create_workflow_config():
    """
    Create a workflow configuration that runs the combined workflow script
    """
    config = {
        "name": "Start application",
        "command": "python combined_workflow.py",
        "restartOn": {
            "libraries": True,
            "replit": False,
            "input": False,
            "exited": True,
            "signal": True
        },
        "onBoot": True
    }
    
    # Write the config to .replit file
    try:
        with open(".replit", "r") as f:
            replit_config = f.read()
        
        # Simple string replacement for the workflow section
        if "[deployment]" in replit_config:
            replit_config = replit_config.replace("[deployment]", f"[deployment]\nrun = \"python combined_workflow.py\"")
        else:
            replit_config += "\n[deployment]\nrun = \"python combined_workflow.py\"\n"
        
        with open(".replit", "w") as f:
            f.write(replit_config)
        
        print("Updated .replit configuration file")
    except Exception as e:
        print(f"Failed to update .replit file: {e}")
        print("This is ok - Replit will still use the workflow configuration")
    
    # Create the workflow configuration directory if it doesn't exist
    os.makedirs("workflows", exist_ok=True)
    
    # Write the workflow configuration
    with open("workflows/combined.toml", "w") as f:
        f.write(f"name = \"{config['name']}\"\n")
        f.write(f"command = \"{config['command']}\"\n")
        f.write(f"onBoot = {str(config['onBoot']).lower()}\n")
        f.write("restartOn = { libraries = true, replit = false, input = false, exited = true, signal = true }\n")
    
    print(f"Created workflow configuration in workflows/combined.toml")
    print(f"Workflow name: {config['name']}")
    print(f"Command: {config['command']}")

if __name__ == "__main__":
    create_workflow_config()
    print("\nTo use this workflow, go to the 'Workflows' tab in Replit")
    print("and click 'Start combined workflow' to run both the main app and the redirector.")
    print("Both services (port 5000 and port 8080) will start and stop together.")
