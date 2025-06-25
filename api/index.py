"""
Vercel serverless function entry point for Beth Assistant API
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app

# Vercel serverless function handler
def handler(request, response):
    """Vercel serverless function handler."""
    return app(request, response) 