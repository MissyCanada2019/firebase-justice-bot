#!/bin/bash
# This file runs when the Replit environment starts

# Start SmartDispute.ai port connectivity solution
echo "===== SmartDispute.ai Replit Environment ====="
echo "Starting SmartDispute.ai with port forwarding..."

# Clean up any existing port forwarders and servers
echo "Cleaning up any existing port forwarders..."
pkill -f "python.*simple_port_forward.py" || true
pkill -f "python.*port8080.py" || true
pkill -f "python.*replit_port_8080.py" || true
pkill -f "python.*port_adapter.py" || true
pkill -f "python.*auto_port_adapter.py" || true
pkill -f "python.*auto_port_forward.py" || true
pkill -f "nc -l 8080" || true

# Start the port forwarding solution
echo "Starting port 8080 adapter..."
chmod +x replit_port_8080.py
chmod +x start_port_adapter.sh
./start_port_adapter.sh

# Display a welcome message
echo ""
echo "=========================================="
echo "SmartDispute.ai is ready to use!"
echo "The application will be accessible through both:"
echo "- Port 5000 (Main application)"
echo "- Port 8080 (Flask-based port adapter)"
echo ""
echo "Port adapter solutions available:"
echo "- ./start_port_adapter.sh (Flask adapter)"
echo "- ./run_port8080.sh (Standard adapter)"
echo "- ./port_adapter.sh (Auto-restarting adapter)"
echo "- ./run_replit_port_adapter.sh (Socket adapter)"
echo "=========================================="