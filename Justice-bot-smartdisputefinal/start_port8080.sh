#!/bin/bash

# Kill any existing port 8080 applications
pkill -f "python port8080_app.py" > /dev/null 2>&1

# Start the port 8080 application
echo "Starting port 8080 application..."
nohup python port8080_app.py > port8080_app.log 2>&1 &

# Store the PID
echo $! > port8080_app.pid

echo "Port 8080 application started with PID $(cat port8080_app.pid)"
echo "The application will redirect requests from port 8080 to the main application on port 5000."
echo "You can check port8080_app.log for activity."
