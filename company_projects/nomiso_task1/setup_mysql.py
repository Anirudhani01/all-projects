#!/usr/bin/env python3
"""
MySQL Database Setup Script
This script creates the shopping_cart database and tables if they don't exist.
"""

import pymysql
from sqlalchemy import create_engine, text
from database.database import Base, engine

def create_database():
    """Create the shopping_cart database if it doesn't exist."""
    try:
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host='localhost',
            user='anirudh',
            password='password123',
            port=3306
        )
        
        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS shopping_cart")
            print("Database 'shopping_cart' created or already exists")
            
            # Use the database
            cursor.execute("USE shopping_cart")
            print("Using database 'shopping_cart'")
            
        connection.close()
        print("Database setup completed successfully!")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False
    
    return True

def create_tables():
    """Create all tables defined in the models."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("All tables created successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False

def main():
    """Main function to set up the database."""
    print("Setting up MySQL database for shopping cart application...")
    
    # Step 1: Create database
    if not create_database():
        print("Failed to create database. Exiting.")
        return
    
    # Step 2: Create tables
    if not create_tables():
        print("Failed to create tables. Exiting.")
        return
    
    print("\nDatabase setup completed successfully!")
    print("You can now run the application with: python main.py")

if __name__ == "__main__":
    main()
