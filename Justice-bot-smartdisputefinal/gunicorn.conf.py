# Gunicorn configuration for SmartDispute.ai
import os

# Server socket - Keep port 5000 for Replit, 8080 for Cloud Run
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
backlog = 2048

# Worker processes - Optimized for Cloud Run
workers = 1
worker_class = "sync"
worker_connections = 1000
timeout = 0
keepalive = 30

# Application
max_requests = 1000
max_requests_jitter = 50
preload_app = False

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "smartdispute_gunicorn"

# SSL (if needed)
keyfile = None
certfile = None

# File upload limits for heavy legal cases
limit_request_line = 8190
limit_request_fields = 200
limit_request_field_size = 8190
max_worker_memory = 1073741824  # 1GB per worker

# Custom settings for large file uploads
def when_ready(server):
    server.log.info("SmartDispute.ai server is ready. Accepting connections.")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)