#!/usr/bin/env python3
"""
Database Setup Script for E-Commerce Application
This script helps set up the MySQL database and user for the application.
"""

import mysql.connector
from mysql.connector import Error

def setup_database():
    """Set up the database and user for the e-commerce application"""
    
    # Root connection (you'll need to provide root password)
    try:
        # Connect as root to create database and user
        root_connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=input("Enter MySQL root password: "),
            charset='utf8mb4'
        )
        
        cursor = root_connection.cursor()
        
        # Create database
        print("Creating database 'ecom_db'...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS ecom_db")
        
        # Create user
        print("Creating user 'anirudh'...")
        cursor.execute("CREATE USER IF NOT EXISTS 'anirudh'@'localhost' IDENTIFIED BY 'password123'")
        
        # Grant privileges
        print("Granting privileges to user 'anirudh'...")
        cursor.execute("GRANT ALL PRIVILEGES ON ecom_db.* TO 'anirudh'@'localhost'")
        cursor.execute("FLUSH PRIVILEGES")
        
        print("✅ Database setup completed successfully!")
        print("\nDatabase Details:")
        print("- Database: ecom_db")
        print("- User: anirudh")
        print("- Password: password123")
        print("- Host: localhost")
        
        cursor.close()
        root_connection.close()
        
    except Error as e:
        print(f"❌ Error setting up database: {e}")
        print("\nManual Setup Instructions:")
        print("1. Connect to MySQL as root:")
        print("   mysql -u root -p")
        print("2. Run these commands:")
        print("   CREATE DATABASE ecom_db;")
        print("   CREATE USER 'anirudh'@'localhost' IDENTIFIED BY 'password123';")
        print("   GRANT ALL PRIVILEGES ON ecom_db.* TO 'anirudh'@'localhost';")
        print("   FLUSH PRIVILEGES;")
        print("   EXIT;")

def test_connection():
    """Test the database connection with the configured credentials"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='anirudh',
            password='password123',
            database='ecom_db',
            charset='utf8mb4'
        )
        
        if connection.is_connected():
            print("✅ Database connection test successful!")
            connection.close()
            return True
        else:
            print("❌ Database connection test failed!")
            return False
            
    except Error as e:
        print(f"❌ Database connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 E-Commerce Database Setup")
    print("=" * 40)
    
    # Check if database already exists
    if test_connection():
        print("Database is already set up and working!")
    else:
        print("Database setup required...")
        setup_database()
        
        # Test connection after setup
        print("\nTesting connection after setup...")
        test_connection()
