# Employee Management System

A monolithic FastAPI backend application for managing employee records with comprehensive CRUD operations.

## 🚀 Features

- **Complete CRUD Operations**: Create, Read, Update, Delete employee records
- **Database Integration**: MySQL database with SQLAlchemy ORM
- **Comprehensive Logging**: All operations are logged with timestamps
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation
- **Input Validation**: Pydantic schemas for data validation
- **Error Handling**: Proper HTTP status codes and error messages
- **Pagination**: Support for paginated results
- **Health Check**: System health monitoring endpoint

## 📋 Requirements

- Python 3.8+
- MySQL Database
- Virtual Environment (recommended)

## 🛠️ Installation

1. **Clone the repository** (if applicable)
2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**:
   - Ensure MySQL is running
   - Create database: `employee_db`
   - Update database credentials in `config.py` if needed

## ⚙️ Configuration

The application uses the following database credentials:
- **Username**: anirudh
- **Password**: password 123
- **Database**: employee_db
- **Host**: localhost
- **Port**: 3306

You can modify these settings in `config.py`.

## 🚀 Running the Application

### Development Mode
```bash
python main.py
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The application will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### 1. Get All Employees
- **GET** `/employees`
- **Query Parameters**:
  - `skip` (int): Number of records to skip (default: 0)
  - `limit` (int): Number of records to return (default: 100, max: 1000)
- **Response**: List of employees with pagination info

### 2. Get Employee by ID
- **GET** `/emp_id/{employee_id}`
- **Path Parameters**:
  - `employee_id` (int): Employee ID
- **Response**: Single employee record

### 3. Get Employees by Name
- **GET** `/emp_name/{name}`
- **Path Parameters**:
  - `name` (string): Search term (searches in Education and City fields)
- **Response**: List of matching employees

### 4. Create Employee
- **POST** `/employee`
- **Body**: Employee data (JSON)
- **Response**: Created employee record

### 5. Update Employee
- **PUT** `/employee/{employee_id}`
- **Path Parameters**:
  - `employee_id` (int): Employee ID
- **Body**: Employee data to update (JSON, partial updates supported)
- **Response**: Updated employee record

### 6. Delete Employee
- **DELETE** `/employee/{employee_id}`
- **Path Parameters**:
  - `employee_id` (int): Employee ID
- **Response**: Success message

### 7. Health Check
- **GET** `/health`
- **Response**: System health status

## 📊 Database Schema

The `employees` table has the following structure:

| Field | Type | Description |
|-------|------|-------------|
| id | INT | Primary key, auto-increment |
| Education | VARCHAR(50) | Education level (e.g., Bachelors, Masters) |
| JoiningYear | INT | Year when employee joined |
| City | VARCHAR(100) | Employee's city |
| PaymentTier | INT | Payment tier (1-5) |
| Age | INT | Employee's age |
| Gender | VARCHAR(10) | Employee's gender |
| EverBenched | VARCHAR(3) | Whether employee was ever benched (Yes/No) |
| ExperienceInCurrentDomain | INT | Experience in current domain |
| LeaveOrNot | INT | Leave status (0 or 1) |

## 📝 Logging

All operations are logged in the `logs/employee_management.log` file with:
- Timestamp
- Operation type
- Details
- User information (when available)
- Error details (if applicable)

## 🏗️ Project Structure

```
emp/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration settings
├── database.py          # Database connection and session management
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas for validation
├── crud.py              # CRUD operations
├── logger.py            # Logging functionality
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── logs/               # Log files directory
    └── employee_management.log
```

## 🔧 Development

### Adding New Features
1. Update the appropriate module (models, schemas, crud, main)
2. Add logging for new operations
3. Update this README with new endpoints/features
4. Test thoroughly

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Add docstrings for functions and classes
- Log all operations

## 🧪 Testing

You can test the API using:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **cURL** or **Postman**

### Example cURL Commands

```bash
# Get all employees
curl http://localhost:8000/employees

# Get employee by ID
curl http://localhost:8000/emp_id/1

# Create new employee
curl -X POST http://localhost:8000/employee \
  -H "Content-Type: application/json" \
  -d '{
    "Education": "Bachelors",
    "JoiningYear": 2023,
    "City": "Mumbai",
    "PaymentTier": 3,
    "Age": 28,
    "Gender": "Male",
    "EverBenched": "No",
    "ExperienceInCurrentDomain": 2,
    "LeaveOrNot": 0
  }'
```

## 📈 Future Enhancements

- [ ] Authentication and Authorization
- [ ] Rate Limiting
- [ ] Caching Layer
- [ ] Bulk Operations
- [ ] Advanced Search and Filtering
- [ ] Data Export/Import
- [ ] Frontend Integration
- [ ] Unit Tests
- [ ] Docker Support

## 🤝 Contributing

1. Follow the existing code structure
2. Add proper logging for new features
3. Update documentation
4. Test your changes

## 📄 License

This project is for educational purposes.

---

**Last Updated**: December 2024
**Version**: 1.0.0
