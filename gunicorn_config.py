import multiprocessing
import os

# Gunicorn Configuration for Sustainage
# Path: /var/www/sustainage/gunicorn_config.py

# Bind to localhost on a specific port (handled by Nginx reverse proxy)
bind = "127.0.0.1:8000"

# Worker Options
# Use (2 x num_cores) + 1 workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"  # Use threads for handling concurrent requests
threads = 4              # Threads per worker
timeout = 120            # Timeout in seconds (increased for long reports)
keepalive = 5            # Keep connections alive for 5 seconds

# Logging
accesslog = "/var/log/sustainage/access.log"
errorlog = "/var/log/sustainage/error.log"
loglevel = "info"

# Process Naming
proc_name = "sustainage_app"

# Reload
reload = False  # Disable auto-reload in production

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

def on_starting(server):
    print("Starting Sustainage Gunicorn Server...")

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")
