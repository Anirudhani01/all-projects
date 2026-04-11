# Employee Management System

A comprehensive full-stack employee management application with JWT authentication, built with FastAPI, MySQL, and a clean minimal UI.

## 🚀 Features

### Core Functionality
- **Complete CRUD Operations** for employee management
- **JWT Authentication** with secure token-based access
- **Admin Management** with bcrypt password hashing
- **Advanced Search & Filtering** with real-time results
- **Pagination** for efficient data handling
- **Statistics Dashboard** with employee metrics
- **Responsive Design** that works on all devices

### User Interface
- **Clean Minimal Design** with white background theme
- **2-Column Form Layout** for better UX
- **Neat Search Bar** with integrated controls
- **Professional Table Design** with action buttons
- **Modal Forms** for add/edit operations
- **Real-time Validation** and error handling

## 📁 Project Structure

```
emp_sys/
├── backend/
│   ├── main.py              # FastAPI application with all endpoints
│   ├── auth_models.py       # Authentication models and JWT utilities
│   ├── config.py            # Database configuration
│   ├── bootstrap_admin.py   # Admin user creation script
│   ├── populate_employees.py # Sample data population script
│   ├── start_wsl_server.sh  # WSL server startup script
│   └── requirements.txt     # Python dependencies
├── frontend/
│   └── index.html          # Complete frontend application
├── README.md               # This file
└── prompts.md             # Development history and changes log
```

## 🛠 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **MySQL** - Database server
- **JWT** - Token-based authentication
- **Bcrypt** - Password hashing
- **Uvicorn** - ASGI server

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with CSS Grid/Flexbox
- **JavaScript (ES6+)** - Interactive functionality
- **Fetch API** - HTTP client for backend communication

### Database
- **MySQL** - Primary database
- **WSL MySQL Instance** - Development environment

## ⚡ Quick Start

### Prerequisites
- Python 3.7+
- MySQL Server (WSL recommended)
- Web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd emp_sys
   ```

2. **Set up the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure database**
   - Ensure MySQL is running with credentials: `anirudh:password123`
   - Database: `employee_db`
   - Tables will be created automatically

4. **Create admin user**
   ```bash
   python bootstrap_admin.py
   ```

5. **Populate sample data (optional)**
   ```bash
   python populate_employees.py
   ```

6. **Start the backend server**
   ```bash
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Start the frontend server**
   ```bash
   cd ../frontend
   python -m http.server 3000
   ```

8. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Login: `admin` / `admin123`

## 🔐 Authentication

### Login Credentials
- **Username**: `admin`
- **Password**: `admin123`

### API Authentication
- All employee endpoints require JWT token
- Token is automatically handled by the frontend
- Token expires in 60 minutes

### Protected Endpoints
```
GET    /employees/          # List employees with pagination
POST   /employees/          # Create new employee
GET    /employees/{id}      # Get employee by ID
PUT    /employees/{id}      # Update employee
DELETE /employees/{id}      # Delete employee
```

### Public Endpoints
```
POST   /auth/login          # User login
POST   /admin/register      # Admin registration (admin only)
GET    /                    # Health check
```

## 📊 Database Schema

### Admin Table
```sql
CREATE TABLE admin (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);
```

### Employees Table
```sql
CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    Name VARCHAR(255),
    Email VARCHAR(255),
    Education VARCHAR(255),
    JoiningYear INT,
    City VARCHAR(255),
    PaymentTier INT,
    Age INT,
    Gender VARCHAR(10),
    EverBenched VARCHAR(10),
    ExperienceInCurrentDomain INT,
    LeaveOrNot TINYINT
);
```

## 🎨 UI Features

### Dashboard
- **Statistics Cards**: Total employees, active employees, average age, etc.
- **Search Functionality**: Real-time search by employee name
- **Pagination Controls**: Configurable page sizes (5, 10, 20, 50)
- **Action Buttons**: Edit and Delete for each employee
- **Responsive Table**: Horizontal scroll for smaller screens

### Forms
- **2-Column Layout**: Name & Email, Education & Joining Year, etc.
- **Field Validation**: Required fields and data type validation
- **Modal Interface**: Clean overlay forms for add/edit operations
- **Auto-close**: Forms close automatically after successful submission

### Design
- **Minimal White Theme**: Clean, professional appearance
- **Consistent Typography**: Inter font family throughout
- **Subtle Shadows**: Depth without overwhelming the design
- **Smooth Transitions**: 0.2s ease transitions for interactions
- **Focus States**: Clear visual feedback for form elements

## 🔧 Development History

### Phase 1: Core Backend (Initial Setup)
- ✅ FastAPI application with basic CRUD
- ✅ MySQL database integration
- ✅ Employee model and endpoints
- ✅ Pagination support

### Phase 2: Authentication System
- ✅ JWT token implementation
- ✅ Admin user management
- ✅ Password hashing with bcrypt
- ✅ Protected route middleware
- ✅ HTTPBearer token mechanism

### Phase 3: Frontend Development
- ✅ Standalone HTML/CSS/JavaScript frontend
- ✅ Login page with backend integration
- ✅ Employee dashboard with full CRUD
- ✅ Search and pagination functionality
- ✅ Dark theme implementation (later changed to minimal white)

### Phase 4: Database Fixes
- ✅ WSL MySQL connection setup
- ✅ Employee ID auto-generation fix
- ✅ 4653 sample records population
- ✅ API endpoint corrections

### Phase 5: UI/UX Enhancements
- ✅ Add/Edit employee functionality
- ✅ Modal forms with validation
- ✅ Experience column display fix
- ✅ Action column with Edit/Delete buttons
- ✅ Table responsiveness improvements

### Phase 6: Design Overhaul
- ✅ Colorful gradient theme implementation
- ✅ Glassmorphism login page
- ✅ Modern dashboard with animations
- ✅ Vibrant color palette

### Phase 7: Minimal Design Transformation
- ✅ Clean white background theme
- ✅ Minimal color usage
- ✅ Professional typography
- ✅ Subtle shadows and borders
- ✅ Neat, organized layout

### Phase 8: Form & Controls Enhancement
- ✅ 2-column form layout implementation
- ✅ Neat search bar and dropdown styling
- ✅ Integrated search container design
- ✅ Responsive grid layout for controls

## 🐛 Troubleshooting

### Common Issues

1. **401 Unauthorized Error**
   - Check if backend server is running on port 8000
   - Verify API_BASE URL in frontend (127.0.0.1:8000 vs localhost:8000)
   - Clear browser cache and localStorage

2. **Database Connection Error**
   - Ensure MySQL is running in WSL
   - Verify credentials: `anirudh:password123`
   - Check database name: `employee_db`

3. **Employee ID Error**
   - Fixed: Auto-generation using `func.max(Employee.emp_id)`
   - New employees get next available ID automatically

4. **Frontend Not Updating**
   - Hard refresh: `Ctrl + Shift + R`
   - Clear browser cache
   - Try incognito mode

### Server Commands

```bash
# Check if ports are in use
wsl -d Ubuntu -e bash -c "ss -tuln | grep ':3000\|:8000'"

# Kill processes on specific ports
wsl -d Ubuntu -e bash -c "pkill -f 'python.*http.server.*3000'"
wsl -d Ubuntu -e bash -c "pkill -f 'uvicorn.*main:app'"

# Restart servers
cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
cd frontend && python -m http.server 3000
```

## 📈 Performance Features

- **Efficient Pagination**: Database-level LIMIT/OFFSET queries
- **Optimized Search**: Real-time filtering with debouncing
- **Minimal API Calls**: Smart caching and batch operations
- **Responsive Design**: CSS Grid and Flexbox for performance
- **Clean Code**: Modular structure for maintainability

## 🔮 Future Enhancements

- [ ] Role-based access control
- [ ] Employee photo upload
- [ ] Advanced reporting and analytics
- [ ] Data export functionality (CSV, PDF)
- [ ] Email notifications
- [ ] Audit trail for changes
- [ ] Bulk operations (import/export)
- [ ] Advanced search filters

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Developed as part of a comprehensive full-stack development project.

---

**Version**: 2.0  
**Last Updated**: August 9, 2025  
**Status**: ✅ Production Ready with Minimal UI Design