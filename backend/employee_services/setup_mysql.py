import mysql.connector
import pandas as pd
from sqlalchemy import create_engine

def setup_mysql_user():
    """
    Instructions to set up MySQL user and database
    """
    print("MySQL Setup Instructions")
    print("=" * 50)
    print("\nTo set up the MySQL user and database, follow these steps:")
    print("\n1. Connect to MySQL as root:")
    print("   mysql -u root -p")
    print("\n2. Create the user and database:")
    print("   CREATE USER 'anirudh'@'localhost' IDENTIFIED BY 'password123';")
    print("   CREATE DATABASE employee_db;")
    print("   GRANT ALL PRIVILEGES ON employee_db.* TO 'anirudh'@'localhost';")
    print("   FLUSH PRIVILEGES;")
    print("\n3. Exit MySQL:")
    print("   EXIT;")
    print("\nAlternative: If you don't have root access, try using existing credentials.")

def test_common_connections():
    """
    Test common MySQL connection methods
    """
    print("\nTesting common MySQL connections...")
    
    # Test different connection methods
    connections = [
        {'user': 'root', 'password': '', 'name': 'root (no password)'},
        {'user': 'root', 'password': 'root', 'name': 'root (password: root)'},
        {'user': 'root', 'password': 'password', 'name': 'root (password: password)'},
        {'user': 'anirudh', 'password': 'password123', 'name': 'anirudh (password: password123)'},
    ]
    
    working_connection = None
    
    for conn_info in connections:
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user=conn_info['user'],
                password=conn_info['password'],
                port=3306
            )
            print(f"✅ {conn_info['name']} - SUCCESS")
            conn.close()
            working_connection = conn_info
            break
        except mysql.connector.Error as e:
            print(f"❌ {conn_info['name']} - FAILED: {e}")
    
    return working_connection

def load_with_working_connection(conn_info):
    """
    Load CSV data using working connection
    """
    try:
        print(f"\nUsing connection: {conn_info['name']}")
        
        # Load CSV data
        print("Loading CSV file: Employee.csv")
        df = pd.read_csv('Employee.csv')
        print(f"Successfully loaded {len(df)} records from CSV")
        
        # Create database if it doesn't exist
        conn = mysql.connector.connect(
            host='localhost',
            user=conn_info['user'],
            password=conn_info['password'],
            port=3306
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS employee_db")
        conn.close()
        print("Database 'employee_db' is ready")
        
        # Connect to specific database
        conn = mysql.connector.connect(
            host='localhost',
            user=conn_info['user'],
            password=conn_info['password'],
            database='employee_db',
            port=3306
        )
        
        # Create engine for pandas
        engine = create_engine(f'mysql+mysqlconnector://{conn_info["user"]}:{conn_info["password"]}@localhost:3306/employee_db')
        
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
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

def main():
    """
    Main function
    """
    print("Employee CSV to MySQL Database Loader")
    print("=" * 50)
    
    # Test connections
    working_connection = test_common_connections()
    
    if working_connection:
        print(f"\n✅ Found working connection: {working_connection['name']}")
        
        # Load data with working connection
        if load_with_working_connection(working_connection):
            print("\n✅ Data loaded successfully to MySQL!")
        else:
            print("\n❌ Failed to load data to MySQL")
    else:
        print("\n❌ No working MySQL connection found")
        setup_mysql_user()

if __name__ == "__main__":
    main()
