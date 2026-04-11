#!/usr/bin/env python3
"""
Test script to verify database connection and data
"""
import sys
import os

# Add the parent directory to the path so we can import our app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.models import *

def test_database_connection():
    """Test database connection and data retrieval"""
    
    db = SessionLocal()
    
    try:
        print("🔍 Testing database connection...")
        
        # Test doctors
        doctors = db.query(Doctor).all()
        print(f"✅ Found {len(doctors)} doctors")
        for doctor in doctors:
            print(f"   - {doctor.name} ({doctor.specialization})")
        
        # Test patients
        patients = db.query(Patient).all()
        print(f"✅ Found {len(patients)} patients")
        for patient in patients:
            print(f"   - {patient.name} ({patient.email})")
        
        # Test appointments
        appointments = db.query(Appointment).all()
        print(f"✅ Found {len(appointments)} appointments")
        for appointment in appointments:
            print(f"   - {appointment.patient.name} -> {appointment.doctor.name} on {appointment.appointment_date} at {appointment.appointment_time}")
        
        # Test blog posts
        blog_posts = db.query(BlogPost).all()
        print(f"✅ Found {len(blog_posts)} blog posts")
        for post in blog_posts:
            print(f"   - {post.title} ({post.category})")
        
        # Test time slots
        time_slots = db.query(TimeSlot).limit(5).all()
        print(f"✅ Found {len(time_slots)} time slots (showing first 5)")
        for slot in time_slots:
            print(f"   - {slot.date} at {slot.time} (available: {slot.is_available})")
        
        # Test contact messages
        contact_messages = db.query(ContactMessage).all()
        print(f"✅ Found {len(contact_messages)} contact messages")
        for message in contact_messages:
            print(f"   - {message.name}: {message.subject}")
        
        print("\n🎉 Database connection and data retrieval successful!")
        
    except Exception as e:
        print(f"❌ Error testing database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_database_connection()
