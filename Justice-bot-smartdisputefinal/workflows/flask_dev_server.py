"""
Flask Development Server Workflow
This workflow starts the Flask application using its built-in development server
instead of gunicorn, matching the configuration that was working on Railway.
"""
import os
import sys
import signal
import subprocess
import time

def signal_handler(sig, frame):
    """Handle signals for graceful shutdown"""
    print("Received signal to shut down...")
    cleanup()
    sys.exit(0)

def cleanup():
    """Clean up processes on exit"""
    print("Cleaning up processes...")
    # Add cleanup code if needed

def main():
    """Start Flask development server"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("\n===== Starting Flask Development Server Workflow =====")
    
    # Start the Flask development server
    flask_cmd = ["python", "flask_dev_server.py"]
    flask_proc = subprocess.Popen(flask_cmd)
    
    try:
        # Keep the workflow running
        while True:
            time.sleep(1)
            if flask_proc.poll() is not None:
                print("Flask server has stopped. Restarting...")
                flask_proc = subprocess.Popen(flask_cmd)
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Shutting down...")
    finally:
        # Cleanup on exit
        if flask_proc.poll() is None:
            flask_proc.terminate()
            flask_proc.wait(timeout=5)
        cleanup()

if __name__ == "__main__":
    main()
