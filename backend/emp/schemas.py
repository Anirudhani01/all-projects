from pydantic import BaseModel, Field
from typing import Optional, List


class EmployeeBase(BaseModel):
    """Base schema for employee data"""
    Education: str = Field(..., description="Employee's education level")
    JoiningYear: int = Field(..., ge=1900, le=2024, description="Year when employee joined")
    City: str = Field(..., description="Employee's city")
    PaymentTier: int = Field(..., ge=1, le=5, description="Payment tier (1-5)")
    Age: int = Field(..., ge=18, le=100, description="Employee's age")
    Gender: str = Field(..., description="Employee's gender")
    EverBenched: str = Field(..., description="Whether employee was ever benched (Yes/No)")
    ExperienceInCurrentDomain: int = Field(..., ge=0, description="Experience in current domain")
    LeaveOrNot: int = Field(..., ge=0, le=1, description="Leave status (0 or 1)")


class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee"""
    pass


class EmployeeUpdate(BaseModel):
    """Schema for updating employee data - all fields optional"""
    Education: Optional[str] = Field(None, description="Employee's education level")
    JoiningYear: Optional[int] = Field(None, ge=1900, le=2024, description="Year when employee joined")
    City: Optional[str] = Field(None, description="Employee's city")
    PaymentTier: Optional[int] = Field(None, ge=1, le=5, description="Payment tier (1-5)")
    Age: Optional[int] = Field(None, ge=18, le=100, description="Employee's age")
    Gender: Optional[str] = Field(None, description="Employee's gender")
    EverBenched: Optional[str] = Field(None, description="Whether employee was ever benched (Yes/No)")
    ExperienceInCurrentDomain: Optional[int] = Field(None, ge=0, description="Experience in current domain")
    LeaveOrNot: Optional[int] = Field(None, ge=0, le=1, description="Leave status (0 or 1)")


class Employee(EmployeeBase):
    """Schema for employee response"""
    id: int = Field(..., description="Employee ID")
    
    class Config:
        from_attributes = True


class EmployeeResponse(BaseModel):
    """Response schema for employee operations"""
    success: bool
    message: str
    data: Optional[Employee] = None


class EmployeeListResponse(BaseModel):
    """Response schema for employee list operations"""
    success: bool
    message: str
    data: List[Employee] = []
    total_count: int = 0
