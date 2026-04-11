import pandas as pd
import mysql.connector
import sqlite3
from sqlalchemy import create_engine
import os

def load_csv_data():
    """
    Load CSV data and return DataFrame
    """
    try:
        print("Loading CSV file: Employee.csv")
        df = pd.read_csv('Employee.csv')
        print(f"✅ Successfully loaded {len(df)} records from CSV")
        print(f"Columns: {list(df.columns)}")
        print("\nSample data:")
        print(df.head())
        return df
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return None

def load_to_sqlite(df):
    """
    Load data to SQLite database (fallback option)
    """
    try:
        print("\nLoading to SQLite database...")
        
        # Create SQLite database
        conn = sqlite3.connect('employee_data.db')
        
        # Load data to database
        df.to_sql('employees', conn, if_exists='replace', index=False)
        
        # Verify data was loaded
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ Successfully loaded {count} records to SQLite table 'employees'")
        print("Database file: employee_data.db")
        return True
        
    except Exception as e:
        print(f"❌ Error loading to SQLite: {e}")
        return False

def load_to_mysql(df):
    """
    Load data to MySQL database
    """
    try:
        print("\nLoading to MySQL database...")
        
        # MySQL connection parameters
        mysql_config = {
            'host': 'localhost',
            'user': 'anirudh',
            'password': 'password123',
            'database': 'employee_db',
            'port': 3306
        }
        
        # First, try to create database if it doesn't exist
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='anirudh',
                password='password123',
                port=3306
            )
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS employee_db")
            conn.close()
            print("Database 'employee_db' is ready")
        except mysql.connector.Error as e:
            print(f"❌ Error creating database: {e}")
            return False
        
        # Connect to the specific database
        conn = mysql.connector.connect(**mysql_config)
        
        # Create engine for pandas
        engine = create_engine(f'mysql+mysqlconnector://anirudh:password123@localhost:3306/employee_db')
        
        # Load data to database
        print("Loading data to MySQL table 'employees'...")
        df.to_sql('employees', engine, if_exists='replace', index=False)
        
        # Verify data was loaded
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ Successfully loaded {count} records to MySQL table 'employees'")
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ MySQL Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_mysql_setup_instructions():
    """
    Show instructions for setting up MySQL
    """
    print("\n" + "="*60)
    print("MySQL Setup Instructions")
    print("="*60)
    print("\nTo set up MySQL for this script, follow these steps:")
    print("\n1. Install MySQL Server (if not already installed):")
    print("   - Windows: Download from https://dev.mysql.com/downloads/mysql/")
    print("   - Linux: sudo apt-get install mysql-server")
    print("   - macOS: brew install mysql")
    print("\n2. Start MySQL service:")
    print("   - Windows: Start MySQL service from Services")
    print("   - Linux: sudo systemctl start mysql")
    print("   - macOS: brew services start mysql")
    print("\n3. Connect to MySQL as root:")
    print("   mysql -u root -p")
    print("\n4. Create user and database:")
    print("   CREATE USER 'anirudh'@'localhost' IDENTIFIED BY 'password123';")
    print("   CREATE DATABASE employee_db;")
    print("   GRANT ALL PRIVILEGES ON employee_db.* TO 'anirudh'@'localhost';")
    print("   FLUSH PRIVILEGES;")
    print("   EXIT;")
    print("\n5. Run this script again to load data to MySQL")
    print("\nAlternative: Use SQLite option below (no setup required)")

def main():
    """
    Main function
    """
    print("Employee CSV to Database Loader")
    print("=" * 50)
    
    # Load CSV data
    df = load_csv_data()
    if df is None:
        return
    
    print("\nChoose database option:")
    print("1. MySQL (requires setup)")
    print("2. SQLite (no setup required)")
    print("3. Show MySQL setup instructions")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        if load_to_mysql(df):
            print("\n✅ Data loaded successfully to MySQL!")
        else:
            print("\n❌ Failed to load to MySQL. Try SQLite option instead.")
    elif choice == "2":
        if load_to_sqlite(df):
            print("\n✅ Data loaded successfully to SQLite!")
        else:
            print("\n❌ Failed to load to SQLite")
    elif choice == "3":
        show_mysql_setup_instructions()
    else:
        print("Invalid choice. Using SQLite as default...")
        if load_to_sqlite(df):
            print("\n✅ Data loaded successfully to SQLite!")

if __name__ == "__main__":
    main()
