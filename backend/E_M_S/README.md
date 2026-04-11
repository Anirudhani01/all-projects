# Employee Management System (EMS)

A comprehensive Employee Management System built with FastAPI and MySQL, providing full CRUD operations for employee data management.

## 🚀 Features

### Core Functionalities
- **Employee Data Management**: Complete CRUD operations for employee records
- **Database Integration**: Seamless MySQL database connectivity
- **RESTful API**: Clean and intuitive API endpoints
- **Data Validation**: Robust input validation using Pydantic models
- **Error Handling**: Comprehensive error handling with proper HTTP status codes
- **Interactive Documentation**: Auto-generated API documentation with Swagger UI

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API root endpoint with welcome message |
| GET | `/employees` | Retrieve all employees |
| GET | `/emp_id/{employee_id}` | Get employee by ID |
| GET | `/emp_name/{education}` | Get employees by education level |
| POST | `/employee` | Create new employee record |
| PUT | `/employee/{employee_id}` | Update existing employee record |
| DELETE | `/employee/{employee_id}` | Delete employee record |

## 🛠️ Tech Stack

### Backend Technologies
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) library
- **MySQL Connector**: Python driver for MySQL database
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for running FastAPI applications

### Database
- **MySQL**: Relational database management system
- **Database Name**: `employee_db`
- **Username**: `anirudh`
- **Password**: `password123`

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL Server installed and running
- MySQL database `employee_db` created
- MySQL user with appropriate permissions

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd E_M_S
```

### 2. Activate Virtual Environment
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
Ensure MySQL server is running and create the database:
```sql
CREATE DATABASE employee_db;
CREATE USER 'anirudh'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON employee_db.* TO 'anirudh'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Run the Application
```bash
python main.py
```

The API will be available at:
- **API Base URL**: `http://localhost:8000`
- **Interactive Documentation**: `http://localhost:8000/docs`
- **Alternative Documentation**: `http://localhost:8000/redoc`

## 📊 Database Schema

The `employees` table contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key, auto-increment |
| Education | String(50) | Education level (Bachelors, Masters, etc.) |
| JoiningYear | Integer | Year when employee joined |
| City | String(50) | Employee's city |
| PaymentTier | Integer | Payment tier level (1, 2, 3) |
| Age | Integer | Employee's age |
| Gender | String(10) | Employee's gender |
| EverBenched | String(5) | Whether employee was ever benched (Yes/No) |
| ExperienceInCurrentDomain | Integer | Years of experience in current domain |
| LeaveOrNot | Integer | Leave status (0/1) |

## 🔧 API Usage Examples

### Get All Employees
```bash
curl -X GET "http://localhost:8000/employees"
```

### Get Employee by ID
```bash
curl -X GET "http://localhost:8000/emp_id/1"
```

### Get Employees by Education
```bash
curl -X GET "http://localhost:8000/emp_name/Bachelors"
```

### Create New Employee
```bash
curl -X POST "http://localhost:8000/employee" \
  -H "Content-Type: application/json" \
  -d '{
    "Education": "Masters",
    "JoiningYear": 2023,
    "City": "Mumbai",
    "PaymentTier": 2,
    "Age": 28,
    "Gender": "Male",
    "EverBenched": "No",
    "ExperienceInCurrentDomain": 3,
    "LeaveOrNot": 0
  }'
```

### Update Employee
```bash
curl -X PUT "http://localhost:8000/employee/1" \
  -H "Content-Type: application/json" \
  -d '{
    "City": "Delhi",
    "PaymentTier": 3
  }'
```

### Delete Employee
```bash
curl -X DELETE "http://localhost:8000/employee/1"
```

## 📝 Project Structure

```
E_M_S/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
├── CHANGELOG.md        # Development log
└── venv/               # Virtual environment
```

## 🔍 Error Handling

The API includes comprehensive error handling:
- **404 Not Found**: When employee ID doesn't exist
- **422 Unprocessable Entity**: When request data validation fails
- **500 Internal Server Error**: For database connection issues

## 🚧 Future Enhancements

- [ ] Authentication and Authorization
- [ ] Pagination for large datasets
- [ ] Search and filtering capabilities
- [ ] Data export functionality
- [ ] Frontend web interface
- [ ] Docker containerization
- [ ] Unit and integration tests

## 📞 Support

For any issues or questions, please refer to the interactive API documentation at `http://localhost:8000/docs` or create an issue in the repository.

## 📄 License

This project is licensed under the MIT License.

## **Here's the solution to fix your database connection issue:**

### **Option 1: Fix MySQL User (Recommended)**

Since the user 'anirudh' exists, run these commands in your MySQL terminal:

```sql
-- Reset password and grant permissions
ALTER USER 'anirudh'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON employee_db.* TO 'anirudh'@'localhost';
FLUSH PRIVILEGES;

-- Test the connection
mysql -u anirudh -ppassword123 employee_db -e "SHOW TABLES;"
```

### **Option 2: Update the Database URL**

If Option 1 doesn't work, update line 12 in your `main.py` file:

```python
<code_block_to_apply_changes_from>
```

### **Option 3: Use Root User (Temporary)**

If you want to test quickly, temporarily use the root user:

```python
# Replace with your actual root password
DATABASE_URL = "mysql+mysqlconnector://root:your_root_password@localhost/employee_db"
```

### **Option 4: Create a New User**

If the above doesn't work, create a new user:

```sql
CREATE USER 'ems_user'@'localhost' IDENTIFIED BY 'ems_password123';
GRANT ALL PRIVILEGES ON employee_db.* TO 'ems_user'@'localhost';
FLUSH PRIVILEGES;
```

Then update the DATABASE_URL:
```python
DATABASE_URL = "mysql+mysqlconnector://ems_user:ems_password123@localhost/employee_db"
```

## **After fixing the database connection:**

1. **Run the application:**
   ```bash
   python main.py
   ```

2. **Test the API:**
   - Open browser: `http://localhost:8000/docs`
   - Test endpoints: `http://localhost:8000/employees`

**Try Option 1 first** (fixing the existing user), as it's the most straightforward solution. Let me know which option works for you!
