# Gunicorn configuration for SmartDispute.ai

# Basic server configuration
bind = "0.0.0.0:8080"
workers = 2
threads = 2
timeout = 120
backlog = 2048
keepalive = 2

# SSL configuration
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Logging configuration
logfile = "logs/gunicorn.log"
loglevel = "info"

# Worker process name
procname = "smartdispute"

# Process management
daemon = False
pidfile = "gunicorn.pid"

# Server hooks
def on_starting(server):
    print("Starting SmartDispute.ai server on port 8080")

def on_reload(server):
    print("Reloading SmartDispute.ai server")

def post_fork(server, worker):
    print(f"Worker {worker.pid} forked")
