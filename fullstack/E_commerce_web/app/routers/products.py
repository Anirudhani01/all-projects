from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlmodel import Session
from ..models import Product, ProductResponse
from ..db import get_session

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[ProductResponse])
def get_products(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    session: Session = Depends(get_session)
):
    """Get all available products with optional category filtering"""
    try:
        # Use SQLModel ORM - get all products first
        products = session.query(Product).all()
        
        # Filter in Python for stock and category
        filtered_products = []
        for product in products:
            if product.stock_quantity > 0:
                if category_id is None or product.category_id == category_id:
                    filtered_products.append(product)
        
        # Convert to ProductResponse models
        return [
            ProductResponse(
                product_id=product.product_id,
                name=product.name,
                description=product.description,
                price=product.price,
                stock_quantity=product.stock_quantity,
                category_id=product.category_id
            )
            for product in filtered_products
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific product by ID"""
    try:
        product = session.get(Product, product_id)
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return ProductResponse(
            product_id=product.product_id,
            name=product.name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
            category_id=product.category_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
