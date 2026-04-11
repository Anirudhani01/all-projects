#!/bin/bash

echo "🚀 Setting up MoodBooster project..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install --legacy-peer-deps

# Create MySQL database
echo "Creating MySQL database..."
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS moodbooster;"

# Initialize database
cd ../backend
alembic upgrade head

echo "✅ Setup complete!"
echo "To run the project:"
echo "1. Start MySQL server"
echo "2. Run: cd moodbooster && source venv/bin/activate && cd backend && uvicorn app.main:app --reload --port 8000"
echo "3. In another terminal: cd moodbooster/frontend && npm run dev"
echo ""
echo "Frontend will be available at: http://localhost:3000"
echo "Backend API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
