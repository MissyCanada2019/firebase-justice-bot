#!/usr/bin/env python3
"""
Production web server for SmartDispute.ai on port 8080
Ensures Replit web interface accessibility
"""

import subprocess
import sys
import time
import signal
import os

def start_gunicorn_server():
    """Start gunicorn server on port 8080"""
    cmd = [
        'gunicorn',
        '--bind', '0.0.0.0:8080',
        '--workers', '1',
        '--timeout', '300',
        '--keep-alive', '60',
        '--max-requests', '1000',
        '--max-requests-jitter', '100',
        '--worker-class', 'sync',
        '--worker-connections', '1000',
        '--preload',
        'main:app'
    ]
    
    print("Starting SmartDispute.ai on port 8080...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Print output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        return process.returncode
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
        process.terminate()
        process.wait()
        return 0
    except Exception as e:
        print(f"Error starting server: {e}")
        return 1

def main():
    """Main entry point"""
    exit_code = start_gunicorn_server()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()