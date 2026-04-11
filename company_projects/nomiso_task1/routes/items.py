from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db, Item
from schemas.schemas import Item as ItemSchema
from typing import List

router = APIRouter()

@router.get("/", response_model=List[ItemSchema])
async def get_all_items(db: Session = Depends(get_db)):
    """Get all items."""
    items = db.query(Item).order_by(Item.name).all()
    return items

@router.get("/{item_id}", response_model=ItemSchema)
async def get_item_by_id(item_id: int, db: Session = Depends(get_db)):
    """Get item by ID."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return item

@router.get("/category/{category}", response_model=List[ItemSchema])
async def get_items_by_category(category: str, db: Session = Depends(get_db)):
    """Get items by category."""
    items = db.query(Item).filter(Item.category == category).order_by(Item.name).all()
    return items

@router.get("/search/{query}", response_model=List[ItemSchema])
async def search_items(query: str, db: Session = Depends(get_db)):
    """Search items by name or description."""
    items = db.query(Item).filter(
        (Item.name.contains(query)) | (Item.description.contains(query))
    ).order_by(Item.name).all()
    return items

@router.get("/inventory/low-stock", response_model=List[ItemSchema])
async def get_low_stock_items(threshold: int = 10, db: Session = Depends(get_db)):
    """Get items with low stock."""
    items = db.query(Item).filter(Item.stock_quantity <= threshold).order_by(Item.stock_quantity.asc()).all()
    return items
