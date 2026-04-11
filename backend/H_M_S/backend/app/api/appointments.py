"""
Appointment API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import date, time, datetime
from ..database import get_db
from ..models.models import Appointment, Doctor, Patient, TimeSlot, AppointmentStatus
from ..schemas.appointment import (
    AppointmentCreate, 
    AppointmentUpdate, 
    AppointmentResponse, 
    AppointmentWithDetails,
    TimeSlotRequest,
    TimeSlotResponse
)

router = APIRouter()


def validate_appointment_status(appointment_date: date, status: str) -> None:
    """Validate appointment status based on appointment date"""
    today = date.today()
    status = status.upper()
    
    if appointment_date > today:
        # Future appointment - can only be PENDING, CONFIRMED, or CANCELLED
        valid_statuses = ['PENDING', 'CONFIRMED', 'CANCELLED']
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status for future appointment. Valid statuses: {', '.join(valid_statuses)}"
            )
    elif appointment_date < today:
        # Past appointment - can only be COMPLETED or CANCELLED
        valid_statuses = ['COMPLETED', 'CANCELLED']
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status for past appointment. Valid statuses: {', '.join(valid_statuses)}"
            )
    else:
        # Today's appointment - can be any status
        valid_statuses = ['PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED']
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Valid statuses: {', '.join(valid_statuses)}"
            )


def auto_update_appointment_statuses(db: Session) -> None:
    """Automatically update appointment statuses based on date"""
    today = date.today()
    
    # Update past appointments that are still PENDING or CONFIRMED to COMPLETED
    past_appointments = db.query(Appointment).filter(
        and_(
            Appointment.appointment_date < today,
            Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
        )
    ).all()
    
    for appointment in past_appointments:
        appointment.status = AppointmentStatus.COMPLETED
        appointment.updated_at = datetime.now()
    
    if past_appointments:
        db.commit()


@router.post("/", response_model=AppointmentResponse)
async def book_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    """Book a new appointment"""
    
    # Validate appointment date (cannot book in the past)
    today = date.today()
    if appointment.appointment_date < today:
        raise HTTPException(
            status_code=400, 
            detail="Cannot book appointments in the past. Please select today or a future date."
        )
    
    # Check if doctor exists
    doctor = db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Handle patient - if patient_id is an email string, find or create patient
    if isinstance(appointment.patient_id, str) and '@' in appointment.patient_id:
        # It's an email, find or create patient
        patient = db.query(Patient).filter(Patient.email == appointment.patient_id).first()
        if not patient:
            # Create a new patient with minimal info
            patient = Patient(
                name="Patient",  # Will be updated when they provide more info
                email=appointment.patient_id,
                phone="0000000000"  # Default phone
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)
    else:
        # It's an integer ID, find patient by ID
        patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
    
    # Check if appointment slot is available
    existing_appointment = db.query(Appointment).filter(
        and_(
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.appointment_date == appointment.appointment_date,
            Appointment.appointment_time == appointment.appointment_time,
            Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
        )
    ).first()
    
    if existing_appointment:
        raise HTTPException(status_code=400, detail="This time slot is already booked")
    
    # Create appointment
    db_appointment = Appointment(
        patient_id=patient.id,
        doctor_id=appointment.doctor_id,
        appointment_date=appointment.appointment_date,
        appointment_time=appointment.appointment_time,
        notes=appointment.notes,
        status=AppointmentStatus.PENDING
    )
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment


@router.get("/slots", response_model=List[TimeSlotResponse])
async def get_available_slots(
    doctor_id: int = Query(..., description="Doctor ID"),
    appointment_date: date = Query(..., description="Appointment date"),
    db: Session = Depends(get_db)
):
    """Get available time slots for a doctor on a specific date"""
    
    # Check if doctor exists
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Get all time slots for the date
    time_slots = db.query(TimeSlot).filter(
        TimeSlot.date == appointment_date
    ).all()
    
    # Get booked appointments for the doctor on this date
    booked_appointments = db.query(Appointment).filter(
        and_(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
        )
    ).all()
    
    booked_times = {apt.appointment_time for apt in booked_appointments}
    
    # Filter available slots
    available_slots = []
    for slot in time_slots:
        is_available = slot.is_available and slot.time not in booked_times
        available_slots.append(TimeSlotResponse(
            time=slot.time,
            is_available=is_available
        ))
    
    return available_slots


@router.get("/", response_model=List[AppointmentWithDetails])
async def get_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    doctor_id: Optional[int] = Query(None),
    patient_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    appointment_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get appointments with optional filtering (Admin only)"""
    
    # Auto-update appointment statuses based on date
    auto_update_appointment_statuses(db)
    
    query = db.query(Appointment)
    
    # Apply filters
    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)
    
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    
    if status:
        query = query.filter(Appointment.status == status)
    
    if appointment_date:
        query = query.filter(Appointment.appointment_date == appointment_date)
    
    # Apply pagination
    appointments = query.offset(skip).limit(limit).all()
    
    return appointments


@router.get("/{appointment_id}", response_model=AppointmentWithDetails)
async def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Get a specific appointment by ID"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment: AppointmentUpdate,
    db: Session = Depends(get_db)
):
    """Update an appointment (Admin only)"""
    
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Get the appointment date (use updated date if provided, otherwise current date)
    appointment_date = appointment.appointment_date if appointment.appointment_date else db_appointment.appointment_date
    today = date.today()
    
    # Validate status based on appointment date
    if appointment.status:
        validate_appointment_status(appointment_date, appointment.status)
    
    # Update only provided fields
    update_data = appointment.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_appointment, field, value)
    
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment


@router.delete("/{appointment_id}")
async def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Cancel an appointment"""
    
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Cancel appointment
    db_appointment.status = AppointmentStatus.CANCELLED
    db.commit()
    
    return {"message": "Appointment cancelled successfully"}


@router.get("/stats/summary")
async def get_appointment_stats(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get appointment statistics (Admin only)"""
    
    query = db.query(Appointment)
    
    if start_date:
        query = query.filter(Appointment.appointment_date >= start_date)
    
    if end_date:
        query = query.filter(Appointment.appointment_date <= end_date)
    
    total_appointments = query.count()
    
    # Count by status
    status_counts = {}
    for status in AppointmentStatus:
        count = query.filter(Appointment.status == status).count()
        status_counts[status.value] = count
    
    # Count by doctor
    doctor_stats = db.query(
        Doctor.name,
        Doctor.specialization,
        db.func.count(Appointment.id).label('appointment_count')
    ).join(Appointment).group_by(Doctor.id, Doctor.name, Doctor.specialization).all()
    
    return {
        "total_appointments": total_appointments,
        "status_breakdown": status_counts,
        "doctor_stats": [
            {
                "doctor_name": stat.name,
                "specialization": stat.specialization,
                "appointment_count": stat.appointment_count
            }
            for stat in doctor_stats
        ]
    }
