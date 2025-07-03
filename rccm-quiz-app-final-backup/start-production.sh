#!/bin/bash
# 🚀 Production Server Startup Script
# 本番環境用サーバー起動スクリプト（Gunicorn + セキュリティ設定）

set -e  # Exit on any error

# 🛡️ Security: Check required environment variables
check_env_vars() {
    echo "🔍 Checking required environment variables..."
    
    if [ -z "$SECRET_KEY" ]; then
        echo "❌ ERROR: SECRET_KEY environment variable is required for production"
        echo "💡 Set it with: export SECRET_KEY='your-cryptographically-secure-random-key'"
        exit 1
    fi
    
    echo "✅ SECRET_KEY is configured"
}

# 🔧 Set production environment
setup_production_env() {
    echo "🔧 Setting up production environment..."
    
    export FLASK_ENV="production"
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    
    # Default values
    export PORT="${PORT:-5000}"
    export GUNICORN_WORKERS="${GUNICORN_WORKERS:-4}"
    export GUNICORN_LOG_LEVEL="${GUNICORN_LOG_LEVEL:-info}"
    
    echo "🌐 Environment: $FLASK_ENV"
    echo "🔧 Port: $PORT"
    echo "👥 Workers: $GUNICORN_WORKERS"
    echo "📊 Log Level: $GUNICORN_LOG_LEVEL"
}

# 🧪 Pre-flight checks
preflight_checks() {
    echo "🧪 Running pre-flight checks..."
    
    # Check if gunicorn is available
    if ! command -v gunicorn &> /dev/null; then
        echo "❌ ERROR: gunicorn is not installed"
        echo "💡 Install with: pip install gunicorn"
        exit 1
    fi
    
    # Check if wsgi.py exists
    if [ ! -f "wsgi.py" ]; then
        echo "❌ ERROR: wsgi.py not found"
        echo "💡 Make sure you're in the correct directory"
        exit 1
    fi
    
    # Check if app.py exists
    if [ ! -f "app.py" ]; then
        echo "❌ ERROR: app.py not found"
        echo "💡 Make sure you're in the correct directory"
        exit 1
    fi
    
    echo "✅ Pre-flight checks passed"
}

# 🚀 Start the production server
start_server() {
    echo "🚀 Starting RCCM Quiz Application (Production Mode)..."
    echo "⚠️  Using Gunicorn WSGI server (not Flask development server)"
    
    # Production server command
    exec gunicorn \
        --config gunicorn.conf.py \
        --bind "0.0.0.0:$PORT" \
        --workers $GUNICORN_WORKERS \
        --timeout 30 \
        --keepalive 60 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --limit-request-line 4096 \
        --limit-request-fields 100 \
        --limit-request-field-size 8190 \
        --access-logfile - \
        --error-logfile - \
        --log-level $GUNICORN_LOG_LEVEL \
        --preload \
        --forwarded-allow-ips='*' \
        wsgi:application
}

# 🏃‍♂️ Main execution
main() {
    echo "================================================================================"
    echo "🛡️ RCCM Quiz Application - Production Server Startup"
    echo "================================================================================"
    
    check_env_vars
    setup_production_env
    preflight_checks
    start_server
}

# Parse command line arguments
case "${1:-start}" in
    "start")
        main
        ;;
    "check")
        echo "🧪 Running checks only..."
        check_env_vars
        setup_production_env
        preflight_checks
        echo "✅ All checks passed. Ready for production deployment."
        ;;
    "dev")
        echo "🔧 Starting in development mode with auto-reload..."
        export FLASK_ENV="development"
        export GUNICORN_WORKERS="1"
        export GUNICORN_LOG_LEVEL="debug"
        main
        ;;
    *)
        echo "Usage: $0 [start|check|dev]"
        echo "  start  - Start production server (default)"
        echo "  check  - Run pre-flight checks only"
        echo "  dev    - Start development server with auto-reload"
        exit 1
        ;;
esac