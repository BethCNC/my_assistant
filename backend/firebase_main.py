"""
Firebase Functions entry point for Beth Assistant API
"""
from functions_framework import create_app
from main import app

# Create the Firebase Functions app
firebase_app = create_app(app)

# Export for Firebase Functions
def main(request):
    """Entry point for Firebase Functions."""
    return firebase_app(request) 