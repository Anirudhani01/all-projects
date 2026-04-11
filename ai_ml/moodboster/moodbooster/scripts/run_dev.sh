#!/bin/bash

echo "🚀 Starting MoodBooster in development mode..."

# Check if MySQL is running
if ! pgrep -x "mysqld" > /dev/null; then
    echo "⚠️  MySQL is not running. Please start MySQL first."
    echo "   On Ubuntu: sudo service mysql start"
    echo "   On macOS: brew services start mysql"
    exit 1
fi

# Start backend
echo "Starting backend server..."
cd backend
source ../venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "Starting frontend server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Both servers running!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop
wait $BACKEND_PID $FRONTEND_PID
