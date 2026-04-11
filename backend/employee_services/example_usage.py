#!/usr/bin/env python3
"""
Example usage of the DatabaseLoader class to load Employee.csv into different databases.
"""

from load_to_db import DatabaseLoader
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def example_sqlite_loading():
    """Example: Load data to SQLite database"""
    print("\n=== SQLite Example ===")
    
    # Initialize loader
    loader = DatabaseLoader("Employee.csv")
    
    # Load CSV data
    if loader.load_csv_data():
        # Validate data
        loader.validate_data()
        
        # Load to SQLite
        success = loader.load_to_sqlite(
            db_path="employee_data.db",
            table_name="employees"
        )
        
        if success:
            print("✅ Successfully loaded data to SQLite!")
        else:
            print("❌ Failed to load data to SQLite")
    else:
        print("❌ Failed to load CSV data")

def example_mysql_loading():
    """Example: Load data to MySQL database (requires MySQL server)"""
    print("\n=== MySQL Example ===")
    
    # Initialize loader
    loader = DatabaseLoader("Employee.csv")
    
    # Load CSV data
    if loader.load_csv_data():
        # MySQL configuration (update with your MySQL credentials)
        mysql_config = {
            'host': 'localhost',
            'user': 'your_username',
            'password': 'your_password',
            'database': 'your_database',
            'table_name': 'employees',
            'port': 3306
        }
        
        print("⚠️  Please update MySQL credentials in the script before running")
        print("MySQL config:", mysql_config)
        
        # Uncomment the following lines after updating credentials:
        # success = loader.load_to_mysql(**mysql_config)
        # if success:
        #     print("✅ Successfully loaded data to MySQL!")
        # else:
        #     print("❌ Failed to load data to MySQL")
    else:
        print("❌ Failed to load CSV data")

def example_postgresql_loading():
    """Example: Load data to PostgreSQL database (requires PostgreSQL server)"""
    print("\n=== PostgreSQL Example ===")
    
    # Initialize loader
    loader = DatabaseLoader("Employee.csv")
    
    # Load CSV data
    if loader.load_csv_data():
        # PostgreSQL configuration (update with your PostgreSQL credentials)
        postgres_config = {
            'host': 'localhost',
            'user': 'your_username',
            'password': 'your_password',
            'database': 'your_database',
            'table_name': 'employees',
            'port': 5432
        }
        
        print("⚠️  Please update PostgreSQL credentials in the script before running")
        print("PostgreSQL config:", postgres_config)
        
        # Uncomment the following lines after updating credentials:
        # success = loader.load_to_postgresql(**postgres_config)
        # if success:
        #     print("✅ Successfully loaded data to PostgreSQL!")
        # else:
        #     print("❌ Failed to load data to PostgreSQL")
    else:
        print("❌ Failed to load CSV data")

def show_table_schema():
    """Show the table schema for different database types"""
    print("\n=== Table Schema Examples ===")
    
    loader = DatabaseLoader()
    
    # SQLite schema
    print("\nSQLite Schema:")
    print(loader.create_table_schema("sqlite"))
    
    # MySQL schema
    print("\nMySQL Schema:")
    print(loader.create_table_schema("mysql"))
    
    # PostgreSQL schema
    print("\nPostgreSQL Schema:")
    print(loader.create_table_schema("postgresql"))

if __name__ == "__main__":
    print("Employee CSV to Database Loader - Examples")
    print("=" * 50)
    
    # Run examples
    example_sqlite_loading()
    example_mysql_loading()
    example_postgresql_loading()
    show_table_schema()
    
    print("\n" + "=" * 50)
    print("To run the main loader script directly:")
    print("python load_to_db.py")
