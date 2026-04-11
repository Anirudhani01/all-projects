# Employee CSV to Database Loader

This project provides a comprehensive Python solution to load the `Employee.csv` file into various database systems including SQLite, MySQL, and PostgreSQL.

## Features

- **Multi-database support**: SQLite, MySQL, and PostgreSQL
- **Data validation**: Checks for data quality issues
- **Comprehensive logging**: Detailed logging for debugging and monitoring
- **Error handling**: Robust error handling with informative messages
- **Data type validation**: Validates age, joining year, and payment tier ranges
- **Missing value detection**: Identifies and reports missing data

## File Structure

```
employee_services/
├── Employee.csv                    # Source CSV file (4,655 records)
├── load_to_db.py                  # Main database loader script
├── example_usage.py               # Example usage demonstrations
├── requirements.txt               # Python dependencies
└── README.md                     # This file
```

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify the CSV file exists:**
   ```bash
   ls -la Employee.csv
   ```

## Quick Start

### Option 1: Run the main script (SQLite by default)

```bash
python load_to_db.py
```

This will:
- Load the CSV data
- Validate the data
- Create a SQLite database file (`employee_data.db`)
- Load all records into the `employees` table

### Option 2: Use the example script

```bash
python example_usage.py
```

This demonstrates usage with different database types.

## Database Options

### 1. SQLite (Default - No setup required)

```python
from load_to_db import DatabaseLoader

loader = DatabaseLoader("Employee.csv")
loader.load_csv_data()
loader.load_to_sqlite(db_path="employee_data.db", table_name="employees")
```

### 2. MySQL (Requires MySQL server)

```python
from load_to_db import DatabaseLoader

loader = DatabaseLoader("Employee.csv")
loader.load_csv_data()

mysql_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database',
    'table_name': 'employees',
    'port': 3306
}

loader.load_to_mysql(**mysql_config)
```

### 3. PostgreSQL (Requires PostgreSQL server)

```python
from load_to_db import DatabaseLoader

loader = DatabaseLoader("Employee.csv")
loader.load_csv_data()

postgres_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database',
    'table_name': 'employees',
    'port': 5432
}

loader.load_to_postgresql(**postgres_config)
```

## CSV Data Structure

The `Employee.csv` file contains the following columns:

| Column | Type | Description | Validation Rules |
|--------|------|-------------|------------------|
| Education | Text | Education level (Bachelors, Masters, PHD) | - |
| JoiningYear | Integer | Year employee joined | 1990-2024 |
| City | Text | Employee's city | - |
| PaymentTier | Integer | Payment tier level | 1, 2, or 3 |
| Age | Integer | Employee age | 18-70 |
| Gender | Text | Employee gender | - |
| EverBenched | Text | Whether employee was ever benched | Yes/No |
| ExperienceInCurrentDomain | Integer | Years of experience | - |
| LeaveOrNot | Integer | Whether employee left (0/1) | 0 or 1 |

## Data Validation

The script performs the following validations:

1. **File existence**: Checks if CSV file exists
2. **Data loading**: Verifies CSV can be loaded
3. **Missing values**: Reports any missing data
4. **Age validation**: Ensures age is between 18-70
5. **Joining year validation**: Ensures year is between 1990-2024
6. **Payment tier validation**: Ensures tier is 1, 2, or 3

## Database Schema

### SQLite Schema
```sql
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Education TEXT,
    JoiningYear INTEGER,
    City TEXT,
    PaymentTier INTEGER,
    Age INTEGER,
    Gender TEXT,
    EverBenched TEXT,
    ExperienceInCurrentDomain INTEGER,
    LeaveOrNot INTEGER
);
```

### MySQL Schema
```sql
CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Education VARCHAR(50),
    JoiningYear INT,
    City VARCHAR(100),
    PaymentTier INT,
    Age INT,
    Gender VARCHAR(10),
    EverBenched VARCHAR(5),
    ExperienceInCurrentDomain INT,
    LeaveOrNot INT
);
```

### PostgreSQL Schema
```sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    Education VARCHAR(50),
    JoiningYear INTEGER,
    City VARCHAR(100),
    PaymentTier INTEGER,
    Age INTEGER,
    Gender VARCHAR(10),
    EverBenched VARCHAR(5),
    ExperienceInCurrentDomain INTEGER,
    LeaveOrNot INTEGER
);
```

## Usage Examples

### Basic Usage
```python
from load_to_db import DatabaseLoader

# Initialize loader
loader = DatabaseLoader("Employee.csv")

# Load and validate CSV data
if loader.load_csv_data():
    # Validate data quality
    loader.validate_data()
    
    # Load to SQLite
    success = loader.load_to_sqlite()
    if success:
        print("Data loaded successfully!")
```

### Custom Configuration
```python
# Custom SQLite configuration
loader.load_to_sqlite(
    db_path="my_employee_db.db",
    table_name="employee_records"
)

# Custom MySQL configuration
loader.load_to_mysql(
    host="my-mysql-server.com",
    user="dbuser",
    password="dbpass",
    database="hr_database",
    table_name="employees",
    port=3306
)
```

## Error Handling

The script includes comprehensive error handling:

- **File not found**: Graceful handling of missing CSV file
- **Database connection errors**: Detailed error messages for connection issues
- **Data validation errors**: Warnings for data quality issues
- **Permission errors**: Clear messages for database access issues

## Logging

The script provides detailed logging:

- **INFO level**: General progress information
- **WARNING level**: Data validation issues
- **ERROR level**: Critical errors that prevent operation

## Dependencies

- `pandas>=1.5.0`: Data manipulation and CSV reading
- `sqlalchemy>=1.4.0`: Database abstraction layer
- `mysql-connector-python>=8.0.0`: MySQL database connector
- `psycopg2-binary>=2.9.0`: PostgreSQL database connector

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Install dependencies with `pip install -r requirements.txt`
2. **Database connection errors**: Verify database credentials and server status
3. **Permission errors**: Ensure write permissions for SQLite file creation
4. **CSV file not found**: Verify `Employee.csv` is in the same directory

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance

- **SQLite**: Fastest for local development and testing
- **MySQL/PostgreSQL**: Better for production environments with concurrent access
- **Memory usage**: Efficient pandas-based processing
- **Large datasets**: Handles the 4,655 records efficiently

## Security Notes

- Never commit database credentials to version control
- Use environment variables for production database credentials
- Consider using connection pooling for production MySQL/PostgreSQL deployments
