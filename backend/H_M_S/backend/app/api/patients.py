"""
Patient API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.models import Patient
from ..schemas.patient import PatientCreate, PatientUpdate, PatientResponse

router = APIRouter()


@router.post("/", response_model=PatientResponse)
async def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """Register a new patient"""
    
    # Check if patient with same email already exists
    existing_patient = db.query(Patient).filter(Patient.email == patient.email).first()
    if existing_patient:
        raise HTTPException(status_code=400, detail="Patient with this email already exists")
    
    # Create new patient
    db_patient = Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    
    return db_patient


@router.get("/", response_model=List[PatientResponse])
async def get_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all patients (Admin only)"""
    
    query = db.query(Patient)
    
    # Apply search filter
    if search:
        query = query.filter(
            Patient.name.ilike(f"%{search}%") |
            Patient.email.ilike(f"%{search}%")
        )
    
    # Apply pagination
    patients = query.offset(skip).limit(limit).all()
    
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Get a specific patient by ID"""
    
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient: PatientUpdate,
    db: Session = Depends(get_db)
):
    """Update a patient (Admin only)"""
    
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Update only provided fields
    update_data = patient.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_patient, field, value)
    
    db.commit()
    db.refresh(db_patient)
    
    return db_patient


@router.delete("/{patient_id}")
async def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """Delete a patient (Admin only)"""
    
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    db.delete(db_patient)
    db.commit()
    
    return {"message": "Patient deleted successfully"}
