# Start the port 8080 adapter as a permanent process

import subprocess
import os
import time
import signal
import sys
import atexit

# Configuration
PORT_ADAPTER_SCRIPT = 'replit_port_8080.py'

# Global variables
adapter_process = None

def start_adapter():
    """Start the port adapter process"""
    global adapter_process
    
    print(f"Starting port 8080 adapter using {PORT_ADAPTER_SCRIPT}...")
    
    try:
        # Start the port adapter as a subprocess
        adapter_process = subprocess.Popen(
            ["python", PORT_ADAPTER_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Save process ID to file
        with open('port_8080.pid', 'w') as f:
            f.write(str(os.getpid()))
            
        print(f"Port adapter started with PID {adapter_process.pid}")
        
        # Wait for process to complete
        adapter_process.wait()
        
    except Exception as e:
        print(f"Error starting port adapter: {e}")

def cleanup(signum=None, frame=None):
    """Clean up function for exit"""
    global adapter_process
    
    if adapter_process:
        print("Stopping port adapter...")
        try:
            adapter_process.terminate()
            try:
                adapter_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                adapter_process.kill()
        except:
            pass
    
    # Remove PID file
    try:
        if os.path.exists('port_8080.pid'):
            os.remove('port_8080.pid')
    except:
        pass
    
    if signum is not None:
        sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Register cleanup function
    atexit.register(cleanup)
    
    print("===== SmartDispute.ai Port 8080 Adapter =====")
    print("Starting persistent port 8080 adapter process")
    
    # Start the adapter
    start_adapter()