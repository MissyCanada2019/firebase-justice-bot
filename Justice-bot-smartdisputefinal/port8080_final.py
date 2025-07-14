#!/usr/bin/env python3
"""
Final port 8080 solution for Replit web interface
Uses gunicorn to run the main application on port 8080
"""

import subprocess
import sys
import os

def main():
    """Run the main application on port 8080 using gunicorn"""
    try:
        # Set environment variables
        os.environ['PORT'] = '8080'
        
        # Run gunicorn on port 8080
        cmd = [
            'gunicorn',
            '--bind', '0.0.0.0:8080',
            '--workers', '1',
            '--timeout', '120',
            '--reload',
            'main:app'
        ]
        
        print("Starting SmartDispute.ai on port 8080 for Replit web interface...")
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\nShutting down port 8080 server")
    except Exception as e:
        print(f"Error starting port 8080 server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()