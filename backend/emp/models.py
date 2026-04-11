from sqlalchemy import Column, Integer, String, Boolean
from database import Base


class Employee(Base):
    """Employee model representing the employees table"""
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Education = Column(String(50), nullable=False)
    JoiningYear = Column(Integer, nullable=False)
    City = Column(String(100), nullable=False)
    PaymentTier = Column(Integer, nullable=False)
    Age = Column(Integer, nullable=False)
    Gender = Column(String(10), nullable=False)
    EverBenched = Column(String(3), nullable=False)  # "Yes" or "No"
    ExperienceInCurrentDomain = Column(Integer, nullable=False)
    LeaveOrNot = Column(Integer, nullable=False)  # 0 or 1
