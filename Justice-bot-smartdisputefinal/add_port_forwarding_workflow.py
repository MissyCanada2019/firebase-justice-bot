#!/usr/bin/env python3
# Creates a Replit workflow configuration file for the port forwarding service

import os
import json

def create_workflow_config():
    # Define the workflow configuration
    workflow = {
        "name": "Port 8080 Forwarder",
        "command": "python simple_port_8080.py",
        "restart": "always",
        "restartAt": "always",
        "restartDelayMs": 2000,
        "runOnBoot": True
    }
    
    # Create the .replit/workflows folder if it doesn't exist
    os.makedirs(".replit/workflows", exist_ok=True)
    
    # Save the workflow configuration
    with open(".replit/workflows/port_forwarder.toml", "w") as f:
        f.write(f"[deployment]\
run = \"{workflow['command']}\"\
restartPolicyType = \"{workflow['restart']}\"\
restartPolicyDelaySeconds = {workflow['restartDelayMs'] / 1000}")
    
    # Also create a shell script to run the forwarder directly
    with open("run_port_forwarder.sh", "w") as f:
        f.write(f"#!/bin/bash\n# Run the port forwarder service\n\npython simple_port_8080.py\n")
    os.chmod("run_port_forwarder.sh", 0o755)
    
    print("Workflow configuration created successfully!")
    print("You can now start the port forwarder with: restart_workflow 'Port 8080 Forwarder'")
    print("Or manually with: ./run_port_forwarder.sh")

if __name__ == "__main__":
    create_workflow_config()
