"""Workflow script to configure port 5000 properly"""
import os
import sys
import time
import json

# Ensure we're using port 5000 only
def configure_workflows():
    print("Setting up single port configuration...")
    
    # We can't edit .replit directly, but we can create a wrapper script
    # that starts our application on the correct port
    
    # Create a simple server script
    server_script = """
#!/usr/bin/env python3
from app import app
import logging

logging.basicConfig(level=logging.INFO)
logging.info("Starting single port server on port 5000...")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
"""
    
    with open("single_port_server.py", "w") as f:
        f.write(server_script)
    
    os.chmod("single_port_server.py", 0o755)  # Make executable
    
    print("Created single port server script")
    print("Ready to start application on port 5000 only")

def main():
    configure_workflows()
    
    print("\nConfiguration complete. Please restart the application.")

if __name__ == "__main__":
    main()
