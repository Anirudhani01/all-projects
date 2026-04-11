#!/usr/bin/env python3
"""
MySQL Setup Script for Employee Management System
This script helps you set up the MySQL database and user.
"""

import subprocess
import sys
import os


def check_mysql_installed():
    """Check if MySQL is installed"""
    try:
        result = subprocess.run(['mysql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ MySQL is installed")
            print(f"Version: {result.stdout.strip()}")
            return True
        else:
            print("❌ MySQL is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("❌ MySQL is not installed or not in PATH")
        return False


def create_database_and_user():
    """Create database and user"""
    print("\n🔧 Setting up MySQL database and user...")
    
    # MySQL commands to create database and user
    mysql_commands = [
        "CREATE DATABASE IF NOT EXISTS employee_db;",
        "CREATE USER IF NOT EXISTS 'anirudh'@'localhost' IDENTIFIED BY 'password 123';",
        "GRANT ALL PRIVILEGES ON employee_db.* TO 'anirudh'@'localhost';",
        "FLUSH PRIVILEGES;",
        "USE employee_db;",
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Education VARCHAR(50) NOT NULL,
            JoiningYear INT NOT NULL,
            City VARCHAR(100) NOT NULL,
            PaymentTier INT NOT NULL,
            Age INT NOT NULL,
            Gender VARCHAR(10) NOT NULL,
            EverBenched VARCHAR(3) NOT NULL,
            ExperienceInCurrentDomain INT NOT NULL,
            LeaveOrNot INT NOT NULL
        );
        """
    ]
    
    # Create a temporary SQL file
    sql_file = "setup_employee_db.sql"
    with open(sql_file, 'w') as f:
        f.write('\n'.join(mysql_commands))
    
    print(f"📝 Created SQL script: {sql_file}")
    print("\n🔑 To set up the database, run one of these commands:")
    print("\nOption 1 - If you have MySQL root password:")
    print(f"mysql -u root -p < {sql_file}")
    
    print("\nOption 2 - If MySQL root has no password:")
    print(f"mysql -u root < {sql_file}")
    
    print("\nOption 3 - Using MySQL Workbench or phpMyAdmin:")
    print("Copy and paste the contents of setup_employee_db.sql")
    
    print("\n📋 SQL Commands to run:")
    print("=" * 50)
    for cmd in mysql_commands:
        print(cmd)
    print("=" * 50)
    
    return sql_file


def test_connection():
    """Test the database connection"""
    print("\n🧪 Testing database connection...")
    try:
        # Test connection using the configured credentials
        test_cmd = [
            'mysql', '-u', 'anirudh', '-p"password 123"', 
            '-h', 'localhost', '-P', '3306', 'employee_db', '-e', 'SELECT 1;'
        ]
        
        result = subprocess.run(test_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 MySQL Setup for Employee Management System")
    print("=" * 50)
    
    # Check if MySQL is installed
    if not check_mysql_installed():
        print("\n📦 To install MySQL:")
        print("Windows: Download from https://dev.mysql.com/downloads/installer/")
        print("Ubuntu/Debian: sudo apt-get install mysql-server")
        print("macOS: brew install mysql")
        print("\nAfter installation, restart this script.")
        return
    
    # Create database and user
    sql_file = create_database_and_user()
    
    print(f"\n📖 Manual Setup Instructions:")
    print("1. Open MySQL command line or MySQL Workbench")
    print("2. Run the SQL commands listed above")
    print("3. Or execute the SQL file created")
    print("4. Test the connection")
    
    # Ask if user wants to test connection
    try:
        response = input("\n🤔 Would you like to test the connection now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            test_connection()
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled by user")
    
    print(f"\n📁 SQL file created: {sql_file}")
    print("You can delete this file after setup is complete.")


if __name__ == "__main__":
    main()
