from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Employee Management System", version="1.0.0")

# Database configuration
DATABASE_URL = "mysql+mysqlconnector://anirudh:password123@127.0.0.1/employee_db?charset=utf8mb4"
engine = create_engine(DATABASE_URL, echo=True)  # Enable SQL logging
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    Education = Column(String(50))
    JoiningYear = Column(Integer)
    City = Column(String(50))
    PaymentTier = Column(Integer)
    Age = Column(Integer)
    Gender = Column(String(10))
    EverBenched = Column(String(5))
    ExperienceInCurrentDomain = Column(Integer)
    LeaveOrNot = Column(Integer)

class EmployeeBase(BaseModel):
    Education: str
    JoiningYear: int
    City: str
    PaymentTier: int
    Age: int
    Gender: str
    EverBenched: str
    ExperienceInCurrentDomain: int
    LeaveOrNot: int

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    Education: Optional[str] = None
    JoiningYear: Optional[int] = None
    City: Optional[str] = None
    PaymentTier: Optional[int] = None
    Age: Optional[int] = None
    Gender: Optional[str] = None
    EverBenched: Optional[str] = None
    ExperienceInCurrentDomain: Optional[int] = None
    LeaveOrNot: Optional[int] = None

class EmployeeResponse(EmployeeBase):
    id: int
    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test database connection
try:
    with engine.connect() as conn:
        logger.info("✅ Database connection successful!")
except Exception as e:
    logger.error(f"⚠️  Database connection failed: {e}")

try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created successfully")
except Exception as e:
    logger.error(f"⚠️  Warning: Could not create database tables: {e}")
    logger.error("   The application will start but database operations may fail.")

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Employee Management System API"}

@app.get("/employees", response_model=List[EmployeeResponse])
def get_all_employees(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    logger.info(f"Fetching employees with skip={skip} and limit={limit}")
    try:
        employees = db.query(Employee).offset(skip).limit(limit).all()
        logger.info(f"Found {len(employees)} employees")
        return employees
    except Exception as e:
        logger.error(f"Error fetching employees: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/emp_id/{employee_id}", response_model=EmployeeResponse)
def get_employee_by_id(employee_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching employee with id={employee_id}")
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee is None:
        logger.warning(f"Employee with id={employee_id} not found")
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@app.get("/emp_name/{education}", response_model=List[EmployeeResponse])
def get_employees_by_education(education: str, db: Session = Depends(get_db)):
    logger.info(f"Fetching employees with education={education}")
    employees = db.query(Employee).filter(Employee.Education == education).all()
    if not employees:
        logger.warning(f"No employees found with education={education}")
        raise HTTPException(status_code=404, detail="No employees found with this education")
    return employees

@app.post("/employee", response_model=EmployeeResponse)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    logger.info("Creating new employee")
    try:
        db_employee = Employee(**employee.dict())
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        logger.info(f"Employee created with id={db_employee.id}")
        return db_employee
    except Exception as e:
        logger.error(f"Error creating employee: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/employee/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: int, employee_update: EmployeeUpdate, db: Session = Depends(get_db)):
    logger.info(f"Updating employee with id={employee_id}")
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if db_employee is None:
        logger.warning(f"Employee with id={employee_id} not found")
        raise HTTPException(status_code=404, detail="Employee not found")
    
    try:
        update_data = employee_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_employee, field, value)
        db.commit()
        db.refresh(db_employee)
        logger.info(f"Employee {employee_id} updated successfully")
        return db_employee
    except Exception as e:
        logger.error(f"Error updating employee: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/employee/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    logger.info(f"Deleting employee with id={employee_id}")
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if db_employee is None:
        logger.warning(f"Employee with id={employee_id} not found")
        raise HTTPException(status_code=404, detail="Employee not found")
    
    try:
        db.delete(db_employee)
        db.commit()
        logger.info(f"Employee {employee_id} deleted successfully")
        return {"message": "Employee deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting employee: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("🚀 Starting Employee Management System API...")
    logger.info(f"📊 Database URL: {DATABASE_URL}")
    logger.info("🌐 Server will be available at: http://localhost:8080")
    logger.info("📚 API Documentation: http://localhost:8080/docs")
    logger.info("=" * 50)
    
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8080,
        log_level="info",
        reload=True  # Enable auto-reload on code changes
    )
    server = uvicorn.Server(config)
    server.run()