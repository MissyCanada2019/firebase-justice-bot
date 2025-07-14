#!/bin/bash

# A simple NC-based port forwarder for port 8080->5000
# This will open port 8080 and forward connections to localhost:5000

while true; do
  # Start a new listener on port 8080, which forwards to port 5000
  nc -l 0.0.0.0 8080 -c "nc localhost 5000" &
  pid=$!
  
  # Save the PID to a file so we can kill it later if needed
  echo $pid > port_adaptor.pid
  
  # Wait for this nc process to complete
  wait $pid
  
  # Brief pause before restarting
  sleep 1
done
