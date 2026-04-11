#!/usr/bin/env python3
"""
Test script to verify database connection and basic functionality
"""

import sys
from sqlalchemy import text
from database import engine, SessionLocal
from logger import logger


def test_database_connection():
    """Test database connection"""
    try:
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            logger.log_operation("TEST", "Database connection test passed")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        logger.log_error("Database connection test failed", str(e))
        return False


def test_table_exists():
    """Test if employees table exists"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SHOW TABLES LIKE 'employees'"))
            if result.fetchone():
                print("✅ Employees table exists!")
                logger.log_operation("TEST", "Employees table exists")
                return True
            else:
                print("❌ Employees table does not exist")
                logger.log_error("Employees table not found")
                return False
    except Exception as e:
        print(f"❌ Error checking table: {e}")
        logger.log_error("Table check failed", str(e))
        return False


def test_sample_data():
    """Test if there's sample data in the table"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM employees"))
            count = result.fetchone()[0]
            print(f"✅ Found {count} employees in the database")
            logger.log_operation("TEST", f"Found {count} employees in database")
            return True
    except Exception as e:
        print(f"❌ Error checking sample data: {e}")
        logger.log_error("Sample data check failed", str(e))
        return False


def main():
    """Run all tests"""
    print("🔍 Testing Employee Management System...")
    print("=" * 50)
    
    # Test database connection
    if not test_database_connection():
        print("\n❌ Database connection test failed. Please check your MySQL configuration.")
        sys.exit(1)
    
    # Test table existence
    if not test_table_exists():
        print("\n❌ Employees table not found. Please ensure the table exists.")
        sys.exit(1)
    
    # Test sample data
    if not test_sample_data():
        print("\n❌ No data found in employees table.")
        sys.exit(1)
    
    print("\n✅ All tests passed! The system is ready to use.")
    print("\n🚀 You can now start the application with: python main.py")
    print("📚 API documentation will be available at: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
