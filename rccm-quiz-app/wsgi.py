#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI entry point for Render.com deployment
Explicit entry point to ensure proper app loading
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask app
from app import app

# Set application for WSGI
application = app

if __name__ == "__main__":
    # Local development
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
