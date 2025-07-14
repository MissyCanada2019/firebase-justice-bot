#!/usr/bin/env python3
"""
Update the Replit workflow configuration for SmartDispute.ai

This script updates the workflow configuration to use our deployment solution.
"""

import os
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_workflow_config():
    """Create workflow configuration for SmartDispute.ai deployment"""
    
    workflow_config = {
        "workflows": [
            {
                "name": "Start SmartDispute.ai",
                "command": "./deploy.sh",
                "restartable": True,
                "restart": "on-watchfile-change"
            }
        ]
    }
    
    # Write the configuration file
    config_file = ".replit.workflow"
    try:
        with open(config_file, "w") as f:
            json.dump(workflow_config, f, indent=2)
        logger.info(f"Created workflow configuration at {config_file}")
        logger.info("Use 'Start SmartDispute.ai' workflow to deploy the application")
    except Exception as e:
        logger.error(f"Error creating workflow configuration: {e}")

if __name__ == "__main__":
    create_workflow_config()
