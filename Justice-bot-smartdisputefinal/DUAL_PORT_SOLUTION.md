# SmartDispute.ai Dual-Port Solution

## Overview

This document explains the native dual-port solution implemented for SmartDispute.ai. The application now runs simultaneously on both port 5000 and port 8080 as two independent but synchronized instances of the same application, sharing the same database and resources.

## Architecture

The dual-port solution consists of:

1. **Main Application (Port 5000)**: The original application using `main.py`
2. **Secondary Application (Port 8080)**: A duplicate of the application using `main_8080.py`
3. **Dual-Port Launcher Script**: A shell script that starts both instances
4. **Automatic Startup**: Configuration in `.bash_profile` to launch at environment startup

## Benefits of This Approach

1. **Maximum Compatibility**: Works with both Replit's web interface and custom domain access
2. **Reliability**: No proxy or forwarding that could introduce errors
3. **Performance**: Direct application access without network overhead
4. **Simplicity**: No complex middleware or connections between processes
5. **Resilience**: If one port becomes unavailable, the other continues to function

## Implementation Details

### 1. Main Application Files

- `main.py`: The original entry point for port 5000
- `main_8080.py`: A duplicate entry point for port 8080

Both files import the same Flask application from `app.py`, ensuring identical functionality.

### 2. Launch Script

`run_dual_port.sh` handles:

- Cleaning up any existing processes
- Starting gunicorn on port 5000 with `main.py`
- Starting gunicorn on port 8080 with `main_8080.py`
- Testing both ports to confirm they're operational

### 3. Automatic Startup

The `.bash_profile` file starts the dual-port solution automatically when the Replit environment starts.

## How to Use

### Manual Start

To manually start the dual-port solution:

```bash
./run_dual_port.sh
```

### Stopping the Servers

To stop both servers:

```bash
pkill -f "gunicorn.*main" || true
pkill -f "gunicorn.*main_8080" || true
```

## Monitoring

The application logs are written to:

- `port5000.log`: Logs for the main application on port 5000
- `port8080.log`: Logs for the secondary application on port 8080

## Troubleshooting

If one port is not responding:

1. Check the corresponding log file
2. Restart the dual-port solution with `./run_dual_port.sh`
3. Verify both ports with:
   ```bash
   curl -s http://localhost:5000/health
   curl -s http://localhost:8080/health
   ```

## Alternative Approaches (Previously Implemented)

1. **HTTP Forwarder**: Simple proxy that forwarded port 8080 requests to port 5000
2. **Flask Proxy Server**: Dedicated Flask app on port 8080 that proxied requests to port 5000
3. **netcat Port Forwarding**: Low-level network tool to forward connections

The native dual-port solution provides better reliability and performance than these alternatives.