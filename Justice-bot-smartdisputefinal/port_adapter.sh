#!/bin/bash

# Port adapter shell script for SmartDispute.ai
# This script starts both the main application on port 5000 and the port 8080 adapter
# Usage: ./port_adapter.sh start|stop|restart|status

MAIN_APP_PORT=5000
FORWARD_PORT=8080
MAIN_APP_COMMAND="gunicorn --bind 0.0.0.0:$MAIN_APP_PORT --reuse-port --reload main:app"
FORWARDER_COMMAND="python simple_port8080.py"
MAIN_APP_PID_FILE="main_app.pid"
FORWARDER_PID_FILE="port8080.pid"
MAIN_APP_LOG="main_app.log"
FORWARDER_LOG="port8080.log"

# Functions
start_main_app() {
    echo "Starting main application on port $MAIN_APP_PORT..."
    nohup $MAIN_APP_COMMAND > $MAIN_APP_LOG 2>&1 &
    echo $! > $MAIN_APP_PID_FILE
    echo "Main application started with PID $(cat $MAIN_APP_PID_FILE)"
}

start_forwarder() {
    echo "Starting port forwarder on port $FORWARD_PORT..."
    nohup $FORWARDER_COMMAND > $FORWARDER_LOG 2>&1 &
    echo $! > $FORWARDER_PID_FILE
    echo "Port forwarder started with PID $(cat $FORWARDER_PID_FILE)"
}

stop_main_app() {
    if [ -f "$MAIN_APP_PID_FILE" ]; then
        PID=$(cat $MAIN_APP_PID_FILE)
        echo "Stopping main application with PID $PID..."
        kill $PID 2>/dev/null || true
        rm -f $MAIN_APP_PID_FILE
        echo "Main application stopped"
    else
        echo "Main application is not running"
    fi
    
    # Also try to kill by command
    pkill -f "$MAIN_APP_COMMAND" 2>/dev/null || true
}

stop_forwarder() {
    if [ -f "$FORWARDER_PID_FILE" ]; then
        PID=$(cat $FORWARDER_PID_FILE)
        echo "Stopping port forwarder with PID $PID..."
        kill $PID 2>/dev/null || true
        rm -f $FORWARDER_PID_FILE
        echo "Port forwarder stopped"
    else
        echo "Port forwarder is not running"
    fi
    
    # Also try to kill by command
    pkill -f "$FORWARDER_COMMAND" 2>/dev/null || true
    pkill -f "simple_port8080.py" 2>/dev/null || true
}

check_main_app() {
    if [ -f "$MAIN_APP_PID_FILE" ]; then
        PID=$(cat $MAIN_APP_PID_FILE)
        if ps -p $PID > /dev/null; then
            echo "Main application is running with PID $PID"
            return 0
        else
            echo "Main application PID file exists but process is not running"
            rm -f $MAIN_APP_PID_FILE
            return 1
        fi
    else
        echo "Main application is not running"
        return 1
    fi
}

check_forwarder() {
    if [ -f "$FORWARDER_PID_FILE" ]; then
        PID=$(cat $FORWARDER_PID_FILE)
        if ps -p $PID > /dev/null; then
            echo "Port forwarder is running with PID $PID"
            return 0
        else
            echo "Port forwarder PID file exists but process is not running"
            rm -f $FORWARDER_PID_FILE
            return 1
        fi
    else
        echo "Port forwarder is not running"
        return 1
    fi
}

check_port() {
    PORT=$1
    nc -z localhost $PORT >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "Port $PORT is OPEN"
        return 0
    else
        echo "Port $PORT is CLOSED"
        return 1
    fi
}

start() {
    echo "Starting all services..."
    start_main_app
    sleep 5  # Give the main app time to start
    start_forwarder
    echo "All services started"
}

stop() {
    echo "Stopping all services..."
    stop_forwarder
    stop_main_app
    echo "All services stopped"
}

restart() {
    echo "Restarting all services..."
    stop
    sleep 5  # Give processes time to clean up
    start
    echo "All services restarted"
}

status() {
    echo "Checking service status..."
    check_main_app
    check_forwarder
    
    # Also check port status
    echo "\nChecking port status:"
    check_port $MAIN_APP_PORT
    check_port $FORWARD_PORT
}

# Command handling
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 start|stop|restart|status"
        exit 1
        ;;
esac

exit 0
