#!/usr/bin/env python3
"""
Script to insert example employee data for testing
"""

from database import SessionLocal
from models import Employee
from logger import logger


def insert_example_data():
    """Insert example employee data"""
    db = SessionLocal()
    
    # Example employee data
    example_employees = [
        {
            "Education": "Bachelors",
            "JoiningYear": 2020,
            "City": "Mumbai",
            "PaymentTier": 3,
            "Age": 28,
            "Gender": "Male",
            "EverBenched": "No",
            "ExperienceInCurrentDomain": 2,
            "LeaveOrNot": 0
        },
        {
            "Education": "Masters",
            "JoiningYear": 2019,
            "City": "Delhi",
            "PaymentTier": 4,
            "Age": 32,
            "Gender": "Female",
            "EverBenched": "No",
            "ExperienceInCurrentDomain": 4,
            "LeaveOrNot": 1
        },
        {
            "Education": "Bachelors",
            "JoiningYear": 2021,
            "City": "Bangalore",
            "PaymentTier": 2,
            "Age": 25,
            "Gender": "Male",
            "EverBenched": "Yes",
            "ExperienceInCurrentDomain": 1,
            "LeaveOrNot": 0
        },
        {
            "Education": "PhD",
            "JoiningYear": 2018,
            "City": "Chennai",
            "PaymentTier": 5,
            "Age": 35,
            "Gender": "Female",
            "EverBenched": "No",
            "ExperienceInCurrentDomain": 6,
            "LeaveOrNot": 1
        },
        {
            "Education": "Bachelors",
            "JoiningYear": 2022,
            "City": "Pune",
            "PaymentTier": 2,
            "Age": 24,
            "Gender": "Male",
            "EverBenched": "No",
            "ExperienceInCurrentDomain": 0,
            "LeaveOrNot": 0
        }
    ]
    
    try:
        # Check if data already exists
        existing_count = db.query(Employee).count()
        if existing_count > 0:
            print(f"⚠️  Database already contains {existing_count} employees")
            print("Skipping example data insertion to avoid duplicates.")
            return
        
        # Insert example data
        for emp_data in example_employees:
            employee = Employee(**emp_data)
            db.add(employee)
        
        db.commit()
        print(f"✅ Successfully inserted {len(example_employees)} example employees")
        logger.log_operation("DATA_INSERT", f"Inserted {len(example_employees)} example employees")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Failed to insert example data: {e}")
        logger.log_error("Example data insertion failed", str(e))
    finally:
        db.close()


if __name__ == "__main__":
    print("📝 Inserting example employee data...")
    insert_example_data()
    print("🎉 Example data insertion completed!")
