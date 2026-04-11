from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import Employee
from schemas import EmployeeCreate, EmployeeUpdate
from typing import List, Optional


class EmployeeCRUD:
    """CRUD operations for Employee model"""
    
    @staticmethod
    def get_all_employees(db: Session, skip: int = 0, limit: int = 100) -> List[Employee]:
        """Get all employees with pagination"""
        return db.query(Employee).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_employee_by_id(db: Session, employee_id: int) -> Optional[Employee]:
        """Get employee by ID"""
        return db.query(Employee).filter(Employee.id == employee_id).first()
    
    @staticmethod
    def get_employees_by_name(db: Session, name: str) -> List[Employee]:
        """Get employees by name (search in Education field as proxy for name)"""
        # Since the table doesn't have a name field, we'll search in Education
        # This is a workaround - in real scenario, you'd have a proper name field
        return db.query(Employee).filter(
            or_(
                Employee.Education.ilike(f"%{name}%"),
                Employee.City.ilike(f"%{name}%")
            )
        ).all()
    
    @staticmethod
    def create_employee(db: Session, employee: EmployeeCreate) -> Employee:
        """Create a new employee"""
        db_employee = Employee(**employee.dict())
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee
    
    @staticmethod
    def update_employee(db: Session, employee_id: int, employee_update: EmployeeUpdate) -> Optional[Employee]:
        """Update employee details"""
        db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not db_employee:
            return None
        
        # Update only provided fields
        update_data = employee_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_employee, field, value)
        
        db.commit()
        db.refresh(db_employee)
        return db_employee
    
    @staticmethod
    def delete_employee(db: Session, employee_id: int) -> bool:
        """Delete employee by ID"""
        db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not db_employee:
            return False
        
        db.delete(db_employee)
        db.commit()
        return True
    
    @staticmethod
    def get_employee_count(db: Session) -> int:
        """Get total number of employees"""
        return db.query(Employee).count()
