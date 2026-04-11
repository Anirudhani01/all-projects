from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

from database import get_db, engine
from models import Base
from schemas import EmployeeCreate, EmployeeUpdate, Employee, EmployeeResponse, EmployeeListResponse
from crud import EmployeeCRUD
from logger import logger
from config import settings

# Create database tables (with error handling)
try:
    Base.metadata.create_all(bind=engine)
    logger.log_operation("DB_INIT", "Database tables created successfully")
except Exception as e:
    logger.log_error("Database initialization failed", str(e))
    print(f"⚠️  Warning: Database connection failed: {e}")
    print("The application will start but database operations will fail.")
    print("Please ensure MySQL is running and the database is properly configured.")

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Employee Management System API with CRUD operations",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Log application startup
logger.log_operation("APP_STARTUP", f"Employee Management System v{settings.app_version} started")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    logger.log_api_request("GET", "/", 200)
    return {
        "message": "Employee Management System API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/employees", response_model=EmployeeListResponse, tags=["Employees"])
async def get_all_employees(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get all employees with pagination
    """
    try:
        employees = EmployeeCRUD.get_all_employees(db, skip=skip, limit=limit)
        total_count = EmployeeCRUD.get_employee_count(db)
        
        logger.log_database_operation("SELECT", "employees")
        logger.log_api_request("GET", f"/employees?skip={skip}&limit={limit}", 200)
        
        return EmployeeListResponse(
            success=True,
            message=f"Retrieved {len(employees)} employees",
            data=employees,
            total_count=total_count
        )
    except Exception as e:
        logger.log_error("Failed to get all employees", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/emp_id/{employee_id}", response_model=EmployeeResponse, tags=["Employees"])
async def get_employee_by_id(employee_id: int, db: Session = Depends(get_db)):
    """
    Get employee by ID
    """
    try:
        employee = EmployeeCRUD.get_employee_by_id(db, employee_id)
        
        if not employee:
            logger.log_api_request("GET", f"/emp_id/{employee_id}", 404)
            raise HTTPException(status_code=404, detail="Employee not found")
        
        logger.log_database_operation("SELECT", "employees", employee_id)
        logger.log_api_request("GET", f"/emp_id/{employee_id}", 200)
        
        return EmployeeResponse(
            success=True,
            message="Employee retrieved successfully",
            data=employee
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error("Failed to get employee by ID", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/emp_name/{name}", response_model=EmployeeListResponse, tags=["Employees"])
async def get_employees_by_name(name: str, db: Session = Depends(get_db)):
    """
    Get employees by name (searches in Education and City fields)
    """
    try:
        employees = EmployeeCRUD.get_employees_by_name(db, name)
        
        logger.log_database_operation("SELECT", "employees")
        logger.log_api_request("GET", f"/emp_name/{name}", 200)
        
        return EmployeeListResponse(
            success=True,
            message=f"Found {len(employees)} employees matching '{name}'",
            data=employees,
            total_count=len(employees)
        )
    except Exception as e:
        logger.log_error("Failed to get employees by name", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/employee", response_model=EmployeeResponse, tags=["Employees"])
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """
    Create a new employee
    """
    try:
        new_employee = EmployeeCRUD.create_employee(db, employee)
        
        logger.log_database_operation("INSERT", "employees", new_employee.id)
        logger.log_api_request("POST", "/employee", 201)
        
        return EmployeeResponse(
            success=True,
            message="Employee created successfully",
            data=new_employee
        )
    except Exception as e:
        logger.log_error("Failed to create employee", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put("/employee/{employee_id}", response_model=EmployeeResponse, tags=["Employees"])
async def update_employee(
    employee_id: int, 
    employee_update: EmployeeUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update employee details
    """
    try:
        updated_employee = EmployeeCRUD.update_employee(db, employee_id, employee_update)
        
        if not updated_employee:
            logger.log_api_request("PUT", f"/employee/{employee_id}", 404)
            raise HTTPException(status_code=404, detail="Employee not found")
        
        logger.log_database_operation("UPDATE", "employees", employee_id)
        logger.log_api_request("PUT", f"/employee/{employee_id}", 200)
        
        return EmployeeResponse(
            success=True,
            message="Employee updated successfully",
            data=updated_employee
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error("Failed to update employee", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/employee/{employee_id}", response_model=EmployeeResponse, tags=["Employees"])
async def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """
    Delete employee by ID
    """
    try:
        success = EmployeeCRUD.delete_employee(db, employee_id)
        
        if not success:
            logger.log_api_request("DELETE", f"/employee/{employee_id}", 404)
            raise HTTPException(status_code=404, detail="Employee not found")
        
        logger.log_database_operation("DELETE", "employees", employee_id)
        logger.log_api_request("DELETE", f"/employee/{employee_id}", 200)
        
        return EmployeeResponse(
            success=True,
            message="Employee deleted successfully",
            data=None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error("Failed to delete employee", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    logger.log_api_request("GET", "/health", 200)
    return {"status": "healthy", "message": "Employee Management System is running"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
