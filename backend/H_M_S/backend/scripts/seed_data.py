#!/usr/bin/env python3
"""
Script to populate the database with sample data for testing
"""
import sys
import os
from datetime import datetime, date, time, timedelta

# Add the parent directory to the path so we can import our app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models.models import *
from app.database import Base

def create_sample_data():
    """Create sample data for testing"""
    
    # Create all tables first
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Clear existing data
        print("🧹 Clearing existing data...")
        db.query(Appointment).delete()
        db.query(TimeSlot).delete()
        db.query(Patient).delete()
        db.query(Doctor).delete()
        db.query(BlogPost).delete()
        db.query(ContactMessage).delete()
        db.commit()
        
        # Create sample doctors
        print("👨‍⚕️ Creating sample doctors...")
        doctors = [
            Doctor(
                name="Dr. Sarah Johnson",
                specialization="Cardiology",
                education="MD in Cardiology, Harvard Medical School",
                experience=15,
                image_url="/static/images/doctors/dr_sarah_johnson.jpg",
                is_active=True
            ),
            Doctor(
                name="Dr. Michael Chen",
                specialization="Pulmonology",
                education="MD in Pulmonology, Johns Hopkins University",
                experience=12,
                image_url="/static/images/doctors/dr_michael_chen.jpg",
                is_active=True
            ),
            Doctor(
                name="Dr. Emily Rodriguez",
                specialization="Neurology",
                education="MD in Neurology, Stanford University",
                experience=10,
                image_url="/static/images/doctors/dr_emily_rodriguez.jpg",
                is_active=True
            ),
            Doctor(
                name="Dr. David Kim",
                specialization="Orthopedics",
                education="MD in Orthopedics, Mayo Clinic",
                experience=18,
                image_url="/static/images/doctors/dr_david_kim.jpg",
                is_active=True
            ),
            Doctor(
                name="Dr. Lisa Thompson",
                specialization="Dermatology",
                education="MD in Dermatology, Yale University",
                experience=8,
                image_url="/static/images/doctors/dr_lisa_thompson.jpg",
                is_active=True
            )
        ]
        
        for doctor in doctors:
            db.add(doctor)
        db.commit()
        
        # Create sample patients
        print("👥 Creating sample patients...")
        patients = [
            Patient(
                name="John Smith",
                phone="+1-555-0101",
                email="john.smith@email.com"
            ),
            Patient(
                name="Jane Doe",
                phone="+1-555-0102",
                email="jane.doe@email.com"
            ),
            Patient(
                name="Robert Johnson",
                phone="+1-555-0103",
                email="robert.johnson@email.com"
            ),
            Patient(
                name="Maria Garcia",
                phone="+1-555-0104",
                email="maria.garcia@email.com"
            ),
            Patient(
                name="Ahmed Hassan",
                phone="+1-555-0105",
                email="ahmed.hassan@email.com"
            )
        ]
        
        for patient in patients:
            db.add(patient)
        db.commit()
        
        # Create sample blog posts
        print("📝 Creating sample blog posts...")
        blog_posts = [
            BlogPost(
                title="Revolutionary Heart Surgery Technique",
                content="Our cardiology team has successfully performed 50+ minimally invasive heart surgeries using the latest robotic-assisted techniques. This breakthrough has reduced recovery time by 40% and improved patient outcomes significantly.",
                category="Cardiology",
                featured_image="/static/images/blog/heart_surgery.jpg",
                is_published=True
            ),
            BlogPost(
                title="New Treatment for Chronic Lung Disease",
                content="Our pulmonology department has introduced a new treatment protocol for chronic obstructive pulmonary disease (COPD) that has shown remarkable results in improving patients' quality of life and lung function.",
                category="Pulmonology",
                featured_image="/static/images/blog/lung_treatment.jpg",
                is_published=True
            ),
            BlogPost(
                title="Advanced Brain Imaging Technology",
                content="We've upgraded our neurology department with state-of-the-art MRI and CT scanning equipment, enabling our doctors to diagnose and treat neurological conditions with unprecedented precision.",
                category="Neurology",
                featured_image="/static/images/blog/brain_imaging.jpg",
                is_published=True
            ),
            BlogPost(
                title="Joint Replacement Success Stories",
                content="Our orthopedic team has achieved a 98% success rate in joint replacement surgeries, with patients reporting significant pain relief and improved mobility within weeks of surgery.",
                category="Orthopedics",
                featured_image="/static/images/blog/joint_replacement.jpg",
                is_published=True
            )
        ]
        
        for post in blog_posts:
            db.add(post)
        db.commit()
        
        # Create sample time slots for the next 30 days
        print("⏰ Creating sample time slots...")
        time_slots_data = [
            time(11, 0),  # 11:00 AM
            time(13, 0),  # 1:00 PM
            time(15, 0),  # 3:00 PM
            time(18, 0)   # 6:00 PM
        ]
        
        for i in range(30):  # Next 30 days
            current_date = date.today() + timedelta(days=i)
            for slot_time in time_slots_data:
                time_slot = TimeSlot(
                    time=slot_time,
                    date=current_date,
                    is_available=True
                )
                db.add(time_slot)
        db.commit()
        
        # Create sample appointments
        print("📅 Creating sample appointments...")
        appointments = [
            Appointment(
                patient_id=1,
                doctor_id=1,
                appointment_date=date.today() + timedelta(days=1),
                appointment_time=time(11, 0),
                status=AppointmentStatus.CONFIRMED,
                notes="Regular checkup"
            ),
            Appointment(
                patient_id=2,
                doctor_id=2,
                appointment_date=date.today() + timedelta(days=2),
                appointment_time=time(13, 0),
                status=AppointmentStatus.PENDING,
                notes="Lung function test"
            ),
            Appointment(
                patient_id=3,
                doctor_id=3,
                appointment_date=date.today() + timedelta(days=3),
                appointment_time=time(15, 0),
                status=AppointmentStatus.CONFIRMED,
                notes="Neurological examination"
            ),
            Appointment(
                patient_id=4,
                doctor_id=4,
                appointment_date=date.today() + timedelta(days=4),
                appointment_time=time(18, 0),
                status=AppointmentStatus.COMPLETED,
                notes="Knee replacement consultation"
            ),
            Appointment(
                patient_id=5,
                doctor_id=5,
                appointment_date=date.today() + timedelta(days=5),
                appointment_time=time(11, 0),
                status=AppointmentStatus.CONFIRMED,
                notes="Skin condition check"
            )
        ]
        
        for appointment in appointments:
            db.add(appointment)
        db.commit()
        
        # Create sample contact messages
        print("📧 Creating sample contact messages...")
        contact_messages = [
            ContactMessage(
                name="Alice Wilson",
                email="alice.wilson@email.com",
                phone="+1-555-0201",
                subject="Appointment Inquiry",
                message="I would like to schedule an appointment with Dr. Johnson for a heart checkup. Please let me know the available dates.",
                is_read=False
            ),
            ContactMessage(
                name="Bob Anderson",
                email="bob.anderson@email.com",
                phone="+1-555-0202",
                subject="Insurance Question",
                message="Does your hospital accept Blue Cross Blue Shield insurance? I need to confirm before scheduling my appointment.",
                is_read=True
            ),
            ContactMessage(
                name="Carol Davis",
                email="carol.davis@email.com",
                phone="+1-555-0203",
                subject="Emergency Contact",
                message="I need to contact someone about my father's emergency surgery. Please call me back as soon as possible.",
                is_read=False
            )
        ]
        
        for message in contact_messages:
            db.add(message)
        db.commit()
        
        print("✅ Sample data created successfully!")
        print(f"📊 Created {len(doctors)} doctors")
        print(f"👥 Created {len(patients)} patients")
        print(f"📝 Created {len(blog_posts)} blog posts")
        print(f"⏰ Created {len(time_slots_data) * 30} time slots")
        print(f"📅 Created {len(appointments)} appointments")
        print(f"📧 Created {len(contact_messages)} contact messages")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
