#!/usr/bin/env python3
"""
Port 8080 Workflow Creator for SmartDispute.ai

This script creates or updates a workflow that runs the application 
directly on port 8080 for Replit compatibility.
"""
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('workflow_setup')

# Path to .replit file
REPLIT_CONFIG_PATH = '.replit'

# Workflow name
WORKFLOW_NAME = 'Direct Port 8080'

# Command to run
COMMAND = 'python main_8080.py'

def read_replit_config():
    """Read the .replit configuration file"""
    try:
        if os.path.exists(REPLIT_CONFIG_PATH):
            with open(REPLIT_CONFIG_PATH, 'r') as file:
                content = file.read()
                # Parse as TOML (simplified approach since we don't want to add a dependency)
                return content
        else:
            logger.warning(f"No {REPLIT_CONFIG_PATH} file found")
            return None
    except Exception as e:
        logger.error(f"Error reading .replit file: {str(e)}")
        return None

def print_workflow_info():
    """Print information about how to use the workflow"""
    logger.info("\n=====================================================\n")
    logger.info("SmartDispute.ai Port 8080 Workflow Setup")
    logger.info("-----------------------------------------------------")
    logger.info("To run the application directly on port 8080:")
    logger.info(f"1. Run: python {os.path.basename(__file__)}")
    logger.info(f"2. In the Replit shell, run: python main_8080.py")
    logger.info("\nThis will start the application directly on port 8080,\n" \
               "which is required for proper Replit web access.")
    logger.info("\nAlternatively, you can also run: python run_direct_port8080.py")
    logger.info("=====================================================\n")

def main():
    """Main function to run the workflow setup"""
    try:
        # Read existing config
        config_content = read_replit_config()
        
        # Since we can't modify .replit directly (as per restrictions),
        # we'll provide instructions instead
        print_workflow_info()
        
        # Create a workflow file that can be run directly
        workflow_file = 'run_port8080.sh'
        with open(workflow_file, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("# Direct Port 8080 Runner for SmartDispute.ai\n\n")
            f.write("echo \"Starting SmartDispute.ai on port 8080...\"\n")
            f.write(f"python main_8080.py\n")
        
        # Make the file executable
        os.chmod(workflow_file, 0o755)
        
        logger.info(f"Created executable workflow file: {workflow_file}")
        logger.info(f"You can run it directly with: ./{workflow_file}")
        
        return True
    except Exception as e:
        logger.error(f"Error setting up workflow: {str(e)}")
        return False

if __name__ == "__main__":
    main()
