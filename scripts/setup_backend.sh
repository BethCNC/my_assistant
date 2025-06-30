#!/bin/bash

echo "🚀 Setting up Beth's Assistant Backend..."

# Copy environment variables if they don't exist
if [ ! -f "backend/.env" ]; then
    echo "📋 Copying environment template..."
    cp config.env.example backend/.env
    echo "⚠️  Please edit backend/.env with your actual API keys"
fi

# Navigate to backend directory
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend setup complete!"
echo "📝 Next steps:"
echo "   1. Edit backend/.env with your API keys"
echo "   2. Run: cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000" 