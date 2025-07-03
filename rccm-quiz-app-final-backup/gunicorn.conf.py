#!/usr/bin/env python3
"""
🚀 Gunicorn Configuration - Production WSGI Server Settings
本番環境用Gunicorn設定ファイル
"""

import os
import multiprocessing

# 🌐 Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
backlog = 2048

# 🔧 Worker processes
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 60

# 🔄 Worker lifecycle
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# 🛡️ Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# 📊 Logging
accesslog = "-"  # stdout
errorlog = "-"   # stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')

# 🚀 Process naming
proc_name = 'rccm-quiz-app'

# 🔧 Performance tuning
forwarded_allow_ips = '*'
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("🚀 RCCM Quiz Application server is ready. Workers: %s", workers)

def worker_int(worker):
    """Called when a worker receives the SIGINT or QUIT signal."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")

# 🔧 Environment-specific overrides
if os.environ.get('FLASK_ENV') == 'development':
    # Development overrides
    workers = 1
    reload = True
    loglevel = 'debug'
elif os.environ.get('RENDER'):
    # Render.com specific settings
    workers = 2  # Render has memory limits
    timeout = 120
    keepalive = 30
    max_requests = 500
elif os.environ.get('HEROKU'):
    # Heroku specific settings
    workers = int(os.environ.get('WEB_CONCURRENCY', 2))
    timeout = 120
    keepalive = 30