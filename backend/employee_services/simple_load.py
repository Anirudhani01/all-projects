import pandas as pd
import mysql.connector
from sqlalchemy import create_engine

def load_csv_to_mysql():
    """
    Load Employee.csv file to MySQL database
    """
    print("Employee CSV to MySQL Database Loader")
    print("=" * 50)
    
    try:
        print("Loading CSV file: Employee.csv")
        
        # Load CSV data
        df = pd.read_csv('Employee.csv')
        
        print(f"Successfully loaded {len(df)} records from CSV")
        print(f"Columns: {list(df.columns)}")
        
        # Display sample data
        print("\nSample data:")
        print(df.head())
        
        # MySQL connection parameters
        mysql_config = {
            'host': 'localhost',
            'user': 'anirudh',
            'password': 'password123',
            'database': 'employee_db',
            'port': 3306
        }
        
        print("\nConnecting to MySQL database...")
        
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
            print(f"Error creating database: {e}")
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
        print(f"MySQL Error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure MySQL server is running")
        print("2. Check if the user 'anirudh' exists with password 'password123'")
        print("3. Try connecting with root user instead")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = load_csv_to_mysql()
    if success:
        print("\n✅ Data loaded successfully to MySQL!")
    else:
        print("\n❌ Failed to load data to MySQL")
