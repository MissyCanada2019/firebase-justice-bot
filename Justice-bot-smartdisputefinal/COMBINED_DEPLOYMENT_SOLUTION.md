# Combined Deployment Solution for SmartDispute.ai

## Overview

This document provides instructions for deploying the SmartDispute.ai application on Replit with a dual-port solution. The application runs on port 5000, while a redirector handles traffic on port 8080 (Replit's required port).

## Solution Architecture

1. **Main Application**: Runs on port 5000 using gunicorn
2. **Port Redirector**: Runs on port 8080 and redirects all requests to port 5000
3. **Combined Workflow**: A single workflow that manages both servers

## Key Files

- `combined_workflow.py`: Manages both the main application and port redirector in a single process
- `simple_redirect.py`: Simple HTTP server that redirects requests from port 8080 to port 5000
- `workflows/combined.toml`: Workflow configuration for Replit

## How to Deploy

### Option 1: Use the Combined Workflow (Recommended)

1. Go to the Workflows tab in Replit
2. Select the "Combined Application" workflow
3. Click Start to launch both the main application and port redirector

### Option 2: Run Services Separately

If you need to run the services separately for debugging:

1. Start the main application with gunicorn: `gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app`
2. Start the port redirector: `python simple_redirect.py`

### Option 3: Quick Manual Deploy

For a quick deployment directly in the shell:

```bash
python combined_workflow.py
```

## Verification

After deployment, verify that both services are running:

1. The main application on port 5000: `curl http://localhost:5000/`
2. The redirector on port 8080: `curl http://localhost:8080/`

You should see responses from both ports.

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Check for running processes: `ps aux | grep -E "gunicorn|redirect"`
   - Kill any existing processes: `kill -9 [PID]`

2. **Redirector not starting**
   - Check for errors in the logs
   - Ensure port 8080 is not being used by another process

3. **Application not accessible**
   - Verify that both services are running
   - Check the Replit logs for errors
   - Ensure the redirector is properly configured to forward to the correct port

## Maintenance

To update the deployment:

1. Stop the current workflow
2. Make your changes to the application code
3. Restart the workflow

## Conclusion

This deployment solution ensures that SmartDispute.ai is accessible through Replit's required port 8080 while maintaining the application's actual port at 5000. The combined workflow approach simplifies management by handling both services together.

---

For any questions or issues, contact the SmartDispute.ai support team at support@smartdispute.ai.
