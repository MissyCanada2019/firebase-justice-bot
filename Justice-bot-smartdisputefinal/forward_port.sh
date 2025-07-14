#!/bin/bash
# Use socat to forward port 8080 to 5000
socat TCP-LISTEN:8080,fork TCP:localhost:5000 &
echo $! > socat.pid
echo "Port forwarding enabled from 8080 to 5000 (PID: $(cat socat.pid))"
echo "Use 'kill $(cat socat.pid)' to stop forwarding"
