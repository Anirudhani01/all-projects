#!/usr/bin/env python3
"""
Database initialization script for MoodBooster
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import *
from app.services.booster_service import get_booster_for_mood
from datetime import datetime
import json

def init_database():
    """Initialize the database with tables and sample data"""
    print("🚀 Initializing MoodBooster database...")
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    
    # Add sample booster data
    print("Adding sample booster data...")
    add_sample_boosters()
    print("✅ Sample data added successfully!")
    
    print("🎉 Database initialization complete!")

def add_sample_boosters():
    """Add sample booster data to the database"""
    from sqlalchemy.orm import sessionmaker
    from app.models.booster import Booster
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if boosters already exist
        existing_boosters = db.query(Booster).count()
        if existing_boosters > 0:
            print("Sample boosters already exist, skipping...")
            return
        
        # Get sample boosters for each mood
        moods = ['happy', 'sad', 'angry', 'stressed', 'neutral']
        
        for mood in moods:
            booster_data = get_booster_for_mood(mood)
            
            booster = Booster(
                mood_type=mood,
                content_type=booster_data['type'],
                title=booster_data['title'],
                content=booster_data['content'],
                booster_metadata=booster_data.get('booster_metadata', {}),
                popularity_score=0.0,
                is_active="true",
                created_at=datetime.utcnow()
            )
            
            db.add(booster)
        
        db.commit()
        print(f"Added {len(moods)} sample boosters")
        
    except Exception as e:
        print(f"Error adding sample boosters: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
