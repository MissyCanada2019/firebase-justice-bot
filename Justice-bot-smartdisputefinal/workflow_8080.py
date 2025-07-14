#!/usr/bin/env python3
"""
Workflow Configuration Generator for SmartDispute.ai

This script creates a workflow configuration that runs the application on port 8080
for Replit compatibility.
"""

import os
import json

def create_workflow_config():
    """Create workflow configuration file for port 8080"""
    
    workflow_config = {
        "workflows": [
            {
                "name": "Start Direct 8080 Application",
                "command": "python main_8080.py",
                "restartable": True,
                "restart": "always"
            }
        ]
    }
    
    # Write the configuration file
    with open(".replit.workflow", "w") as f:
        json.dump(workflow_config, f, indent=2)
    
    print("Created workflow configuration for port 8080 application")
    print("Run the application with: python main_8080.py")

if __name__ == "__main__":
    create_workflow_config()
