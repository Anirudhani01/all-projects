"""
Doctor API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.models import Doctor
from ..schemas.doctor import DoctorCreate, DoctorUpdate, DoctorResponse, DoctorList

router = APIRouter()


@router.get("/", response_model=DoctorList)
async def get_doctors(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    specialization: Optional[str] = Query(None, description="Filter by specialization"),
    search: Optional[str] = Query(None, description="Search by name"),
    db: Session = Depends(get_db)
):
    """Get all doctors with optional filtering"""
    
    query = db.query(Doctor).filter(Doctor.is_active == True)
    
    # Apply filters
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f"%{specialization}%"))
    
    if search:
        query = query.filter(Doctor.name.ilike(f"%{search}%"))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    doctors = query.offset(skip).limit(limit).all()
    
    return DoctorList(
        doctors=doctors,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """Get a specific doctor by ID"""
    
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return doctor


@router.post("/", response_model=DoctorResponse)
async def create_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)):
    """Create a new doctor (Admin only)"""
    
    # Check if doctor with same name already exists
    existing_doctor = db.query(Doctor).filter(Doctor.name == doctor.name).first()
    if existing_doctor:
        raise HTTPException(status_code=400, detail="Doctor with this name already exists")
    
    # Create new doctor
    db_doctor = Doctor(**doctor.dict())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    
    return db_doctor


@router.put("/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(
    doctor_id: int, 
    doctor: DoctorUpdate, 
    db: Session = Depends(get_db)
):
    """Update a doctor (Admin only)"""
    
    db_doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Update only provided fields
    update_data = doctor.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_doctor, field, value)
    
    db.commit()
    db.refresh(db_doctor)
    
    return db_doctor


@router.delete("/{doctor_id}")
async def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """Delete a doctor (Admin only)"""
    
    db_doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Soft delete - mark as inactive
    db_doctor.is_active = False
    db.commit()
    
    return {"message": "Doctor deleted successfully"}


@router.get("/specializations/list", response_model=List[str])
async def get_specializations(db: Session = Depends(get_db)):
    """Get list of all specializations"""
    
    specializations = db.query(Doctor.specialization).filter(
        Doctor.is_active == True
    ).distinct().all()
    
    return [spec[0] for spec in specializations]
