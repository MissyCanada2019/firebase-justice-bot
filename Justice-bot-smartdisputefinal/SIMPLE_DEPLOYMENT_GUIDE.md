# SmartDispute.ai Deployment Guide

## Overview

This guide explains the deployment strategy for SmartDispute.ai on Replit. We use a two-server approach to solve the port compatibility issue:

1. The main application runs on port 5000 using gunicorn (as designed)
2. A simple HTTP redirect server runs on port 8080 (for Replit compatibility) and forwards requests to port 5000

## Quick Start

### Deploy the Application

Run the deployment script:

```bash
./deploy.sh
```

This will:
- Stop any existing servers
- Start the main application on port 5000
- Start the redirect server on port 8080
- Save PIDs for future reference

### Stop the Application

Run the stop script:

```bash
./stop.sh
```

This will gracefully stop all running servers.

## Files Explanation

1. `deploy.sh` - Deployment script that starts both servers
2. `stop.sh` - Script to stop all running servers
3. `simple_redirect.py` - HTTP server that redirects from port 8080 to port 5000
4. `main.py` - Main Flask application entry point (running on port 5000)

## Logs

Logs are available in these files:
- `gunicorn.log` - Main application logs
- `redirect.log` - Redirect server logs

## Troubleshooting

If you encounter issues:

1. Check log files for errors
2. Ensure no other processes are using ports 5000 or 8080
3. Run `./stop.sh` followed by `./deploy.sh` to restart both servers

## Replit Workflow

If you want to use Replit's workflow feature, set up a workflow with this command:

```
./deploy.sh
```

This will start both servers correctly with a single command.
