"""
Contact API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.models import ContactMessage
from ..schemas.contact import ContactMessageCreate, ContactMessageUpdate, ContactMessageResponse, ContactMessageList

router = APIRouter()


@router.post("/", response_model=ContactMessageResponse)
async def create_contact_message(message: ContactMessageCreate, db: Session = Depends(get_db)):
    """Submit a contact form message"""
    
    # Create new contact message
    db_message = ContactMessage(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    return db_message


@router.get("/", response_model=ContactMessageList)
async def get_contact_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    unread_only: bool = Query(False),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get contact messages (Admin only)"""
    
    query = db.query(ContactMessage)
    
    # Apply filters
    if unread_only:
        query = query.filter(ContactMessage.is_read == False)
    
    if search:
        query = query.filter(
            ContactMessage.name.ilike(f"%{search}%") |
            ContactMessage.email.ilike(f"%{search}%") |
            ContactMessage.subject.ilike(f"%{search}%")
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    messages = query.order_by(ContactMessage.created_at.desc()).offset(skip).limit(limit).all()
    
    return ContactMessageList(
        messages=messages,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{message_id}", response_model=ContactMessageResponse)
async def get_contact_message(message_id: int, db: Session = Depends(get_db)):
    """Get a specific contact message by ID (Admin only)"""
    
    message = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Contact message not found")
    
    return message


@router.put("/{message_id}", response_model=ContactMessageResponse)
async def update_contact_message(
    message_id: int,
    message: ContactMessageUpdate,
    db: Session = Depends(get_db)
):
    """Update a contact message (Admin only)"""
    
    db_message = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    
    if not db_message:
        raise HTTPException(status_code=404, detail="Contact message not found")
    
    # Update only provided fields
    update_data = message.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_message, field, value)
    
    db.commit()
    db.refresh(db_message)
    
    return db_message


@router.delete("/{message_id}")
async def delete_contact_message(message_id: int, db: Session = Depends(get_db)):
    """Delete a contact message (Admin only)"""
    
    db_message = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    
    if not db_message:
        raise HTTPException(status_code=404, detail="Contact message not found")
    
    db.delete(db_message)
    db.commit()
    
    return {"message": "Contact message deleted successfully"}


@router.get("/stats/summary")
async def get_contact_stats(db: Session = Depends(get_db)):
    """Get contact message statistics (Admin only)"""
    
    total_messages = db.query(ContactMessage).count()
    unread_messages = db.query(ContactMessage).filter(ContactMessage.is_read == False).count()
    read_messages = total_messages - unread_messages
    
    # Recent messages (last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.now() - timedelta(days=7)
    recent_messages = db.query(ContactMessage).filter(
        ContactMessage.created_at >= week_ago
    ).count()
    
    return {
        "total_messages": total_messages,
        "unread_messages": unread_messages,
        "read_messages": read_messages,
        "recent_messages": recent_messages
    }
