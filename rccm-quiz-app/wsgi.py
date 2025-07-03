#!/usr/bin/env python3
"""
🚀 WSGI Entry Point - Production Server Configuration
本番環境用WSGIサーバー設定（Gunicorn対応）
"""

import os
import sys
from pathlib import Path

# Add application directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import the Flask application
from app import app

# 🛡️ Production environment configuration
if __name__ != "__main__":
    # Running under WSGI server (Gunicorn)
    
    # Force production settings when running under WSGI
    os.environ.setdefault('FLASK_ENV', 'production')
    
    # Ensure security settings are applied
    if not os.environ.get('SECRET_KEY'):
        raise ValueError(
            "🚨 SECURITY ERROR: SECRET_KEY environment variable is required for production deployment.\n"
            "Set it with: export SECRET_KEY='your-cryptographically-secure-random-key'"
        )
    
    # Configure logging for production
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 RCCM Quiz Application starting in production mode via WSGI")
    logger.info(f"🛡️ Security: SECRET_KEY configured: {bool(os.environ.get('SECRET_KEY'))}")
    logger.info(f"🌐 Environment: {os.environ.get('FLASK_ENV', 'development')}")

# Export the application for WSGI server
application = app

if __name__ == "__main__":
    # This should not be used in production
    print("⚠️  WARNING: This file is for WSGI servers. Use gunicorn to run in production.")
    print("🚀 Production command: gunicorn -w 4 -b 0.0.0.0:5000 wsgi:application")
    sys.exit(1)