from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import diary, mood, booster, analytics, context, decision, external_apis
from app.database import engine
from app.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MoodBooster API",
    description="A diary-style mood analysis and wellness app API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(diary.router, prefix="/api/v1/diary", tags=["diary"])
app.include_router(mood.router, prefix="/api/v1/mood", tags=["mood"])
app.include_router(booster.router, prefix="/api/v1/booster", tags=["booster"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(context.router, prefix="/api/v1/context", tags=["context"])
app.include_router(decision.router, prefix="/api/v1/decision", tags=["decision"])
app.include_router(external_apis.router, prefix="/api/v1/external", tags=["external-apis"])

@app.get("/")
async def root():
    return {"message": "Welcome to MoodBooster API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "MoodBooster API is running"}
