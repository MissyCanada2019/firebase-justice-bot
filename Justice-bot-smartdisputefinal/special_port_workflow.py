#!/usr/bin/env python3
"""
Script to create a workflow file for running the app directly on port 8080
"""
import os
import sys
import json

# The workflow configuration for direct port 8080
workflow_config = {
    "workflows": {
        "Port8080": {
            "name": "Port 8080 Server",
            "onBoot": True,
            "restartPolicyType": "ALWAYS",
            "restartPolicyMaxRetries": 10,
            "command": "python run_port8080.py"
        }
    }
}

def create_workflow_file():
    """Create the workflow file"""
    try:
        # Write the workflow configuration to a file
        with open('.replit.workflow', 'w') as f:
            json.dump(workflow_config, f, indent=2)
        
        print("Workflow configuration created in .replit.workflow")
        print("Ready to run server directly on port 8080")
        return True
    except Exception as e:
        print(f"Error creating workflow file: {e}")
        return False

if __name__ == "__main__":
    if create_workflow_file():
        print("Run the workflow with: python run_port8080.py")
        # Try to execute the port 8080 server directly
        os.system("python run_port8080.py")
    else:
        sys.exit(1)