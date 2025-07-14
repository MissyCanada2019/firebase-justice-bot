# SmartDispute.ai Deployment Solution

## Problem

Replit requires applications to listen on port 8080, while our application traditionally runs on port 5000 using gunicorn. We need a reliable solution that doesn't complicate the codebase.

## Solution Options

### Option 1: Direct 8080 Application (Recommended)

The file `main_8080.py` is a direct port 8080 implementation that imports all routes and functionality from the main application. This should be used as the primary entry point for Replit deployments.

**To deploy using this method:**

1. Create a new workflow in Replit with the following command:
   ```
   python main_8080.py
   ```

2. This runs the application directly on port 8080 with all the functionality of the main application.

### Option 2: Use the run_8080.sh Script

The `run_8080.sh` script is a wrapper that starts the main_8080.py application with proper logging.

**To deploy using this method:**

1. Create a new workflow in Replit with the following command:
   ```
   ./run_8080.sh
   ```

### Option 3: Port Forwarding (More Complex)

If for some reason the direct port 8080 application doesn't work, there are several port forwarding solutions:

1. **Dual Port Application**: `run_port_dual.py` - Runs both the main app on port 5000 and a forwarding app on port 8080

2. **Simple Port Forwarder**: `port8080_app.py` with `start_port8080.sh` - Runs a separate port forwarder

## Logs and Troubleshooting

Check these log files if you encounter issues:

- For Option 1: Terminal output directly shows logs
- For Option 2: Terminal output directly shows logs
- For Option 3: Check `port8080_app.log` for forwarding logs

## Conclusion

The direct port 8080 approach (Option 1) is the simplest and most reliable solution. It maintains all application functionality while meeting Replit's port requirements.
