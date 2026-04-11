#!/usr/bin/env python3
"""
MySQL Test Database Setup Script
This script creates the shopping_cart_test database for testing.
"""

import pymysql

def create_test_database():
    """Create the shopping_cart_test database if it doesn't exist."""
    try:
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host='localhost',
            user='anirudh',
            password='password123',
            port=3306
        )
        
        with connection.cursor() as cursor:
            # Create test database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS shopping_cart_test")
            print("Test database 'shopping_cart_test' created or already exists")
            
        connection.close()
        print("Test database setup completed successfully!")
        
    except Exception as e:
        print(f"Error setting up test database: {e}")
        return False
    
    return True

def main():
    """Main function to set up the test database."""
    print("Setting up MySQL test database for shopping cart application...")
    
    if create_test_database():
        print("\nTest database setup completed successfully!")
        print("You can now run the tests with: python -m pytest tests/ -v")
    else:
        print("Failed to set up test database.")

if __name__ == "__main__":
    main()
