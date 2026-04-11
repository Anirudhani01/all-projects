# 🌟 MoodBooster - Your Daily Mood Companion

A beautiful, interactive diary-style mood analysis app that helps you understand your emotions and provides personalized wellness boosters.

## ✨ Features

- **Diary Interface**: Beautiful, handwritten-style interface for daily mood entries
- **AI Mood Analysis**: Analyzes your text to detect emotions (happy, sad, angry, stressed, neutral)
- **Personalized Boosters**: Get customized content based on your mood (stories, games, meditations, activities)
- **Mood History**: Track your emotional journey over time
- **Beautiful UI**: Engaging, interactive design that makes you want to return daily

## 🏗️ Tech Stack

### Frontend
- React 18 + Vite
- Tailwind CSS for styling
- Framer Motion for animations
- React Router for navigation
- Axios for API calls

### Backend
- FastAPI (Python)
- SQLAlchemy ORM
- MySQL database
- Alembic for migrations
- Pydantic for data validation

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- MySQL 8.0+

### Installation

1. **Clone and setup the project:**
   ```bash
   cd moodbooster
   chmod +x scripts/*.sh
   ./scripts/setup.sh
   ```

2. **Start MySQL server:**
   ```bash
   # Ubuntu/Debian
   sudo service mysql start
   
   # macOS
   brew services start mysql
   ```

3. **Run the development servers:**
   ```bash
   ./scripts/run_dev.sh
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
moodbooster/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Main application pages
│   │   ├── services/       # API services
│   │   ├── hooks/          # Custom React hooks
│   │   ├── utils/          # Utility functions
│   │   └── styles/         # CSS and styling
│   └── public/             # Static assets
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   └── alembic/            # Database migrations
├── scripts/                 # Setup and run scripts
└── docs/                   # Documentation
```

## 🎯 Usage

1. **Start Your Diary**: Click "Start My Diary" on the landing page
2. **Write Your Entry**: Share how your day went in the diary interface
3. **Get Mood Analysis**: The app analyzes your text and detects your mood
4. **Receive Boosters**: Get personalized content to boost your mood
5. **Track Progress**: View your mood history and trends over time

## 🔧 Development

### Backend Development
```bash
cd backend
source ../venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Database Migrations
```bash
cd backend
source ../venv/bin/activate
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## 📊 API Endpoints

- `POST /api/v1/diary/entry` - Create a new diary entry
- `GET /api/v1/diary/entries/{session_id}` - Get entries for a session
- `POST /api/v1/mood/analyze` - Analyze mood from text
- `GET /api/v1/booster/{mood_type}` - Get booster for mood type
- `GET /api/v1/analytics/trends/{session_id}` - Get mood trends

## 🎨 Design System

- **Colors**: Warm, cozy palette with mood-specific colors
- **Typography**: Handwritten fonts for personal touch
- **Animations**: Smooth, engaging micro-interactions
- **Layout**: Mobile-first, responsive design

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- React and FastAPI communities
- Tailwind CSS for beautiful styling
- Framer Motion for smooth animations
- All the open-source libraries that made this possible

---

**Made with ❤️ for better mental health and emotional wellness**
