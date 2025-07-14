#!/bin/bash
# Script to check if the port forwarding solution is working correctly

echo "===== SmartDispute.ai Port Forwarding Check ====="
echo "Checking if both ports are accessible and forwarding is working"
echo ""

# Check if main app is running on port 5000
echo "Checking main application (port 5000):"
MAIN_RESPONSE=$(curl -s http://localhost:5000/health)
MAIN_EXIT_CODE=$?

if [ $MAIN_EXIT_CODE -eq 0 ]; then
  echo "✓ Main application is running on port 5000"
  echo "  Response: $MAIN_RESPONSE"
else
  echo "✗ Main application is NOT running on port 5000"
  echo "  Error code: $MAIN_EXIT_CODE"
fi

echo ""

# Check if port forwarder is running on port 8080
echo "Checking port forwarder (port 8080):"
FORWARDER_RESPONSE=$(curl -s http://localhost:8080/health)
FORWARDER_EXIT_CODE=$?

if [ $FORWARDER_EXIT_CODE -eq 0 ]; then
  echo "✓ Port forwarder is running on port 8080"
  echo "  Response: $FORWARDER_RESPONSE"
else
  echo "✗ Port forwarder is NOT running on port 8080"
  echo "  Error code: $FORWARDER_EXIT_CODE"
fi

echo ""

# Check if the responses match (indicating forwarding is working)
if [ "$MAIN_RESPONSE" == "$FORWARDER_RESPONSE" ] && [ $MAIN_EXIT_CODE -eq 0 ] && [ $FORWARDER_EXIT_CODE -eq 0 ]; then
  echo "✓ Port forwarding is working correctly!"
  echo "  Both ports returned the same response."
else
  echo "✗ Port forwarding may not be working correctly."
  echo "  The responses from port 5000 and port 8080 are different."
fi

echo ""

# Check processes
echo "Active port forwarding processes:"
ps aux | grep -E "gunicorn.*port8080|nc -l 8080|simple_port_adapter" | grep -v grep

echo ""
echo "For troubleshooting, see PORT_SOLUTION.md"