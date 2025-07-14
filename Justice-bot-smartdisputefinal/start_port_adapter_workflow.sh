#!/bin/bash
# Start the Port 8080 Adapter Workflow

# Make the script executable
chmod +x port_adapter_workflow.py

# Kill any existing port adapters
echo "Cleaning up existing port adapters..."
pkill -f "python.*port_adapter_workflow.py" || true
pkill -f "python.*port_8080_adapter.py" || true
pkill -f "python.*minimal_port_forward.py" || true
pkill -f "python.*simple_port_forward.py" || true

# Start the port adapter
echo "Starting port 8080 adapter workflow..."
python port_adapter_workflow.py
