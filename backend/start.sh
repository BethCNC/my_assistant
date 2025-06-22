#!/bin/bash

echo "🚀 Starting Beth's Unified Assistant Backend..."
echo "📍 Health check: http://localhost:8000/health"
echo "📖 API docs: http://localhost:8000/docs"
echo "🔧 Admin panel: http://localhost:8000/admin"
echo ""

# Activate virtual environment if it exists
if [ -d "../.venv" ]; then
    echo "📦 Activating virtual environment..."
    source ../.venv/bin/activate
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install -q -r ../requirements.txt

# Start the server
echo "🎯 Starting server on http://localhost:8000"
python main.py 