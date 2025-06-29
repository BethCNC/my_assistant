#!/bin/bash

echo "🔥 Starting Beth's Assistant Development Environment..."

# Run setup scripts
echo "1️⃣ Setting up backend..."
./setup_backend.sh

echo "2️⃣ Setting up frontend..."
./setup_frontend.sh

echo "3️⃣ Starting services..."

# Start backend in background
echo "🚀 Starting backend server..."
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Give backend time to start
sleep 3

# Start frontend
echo "🎨 Starting frontend development server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ Both services started!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 Backend Health: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for user interrupt
trap 'echo "🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID; exit' INT
wait 