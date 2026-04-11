from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from decimal import Decimal
from datetime import datetime


class ColorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    hex: str = Field(..., min_length=6, max_length=7)
    image: str = Field(..., min_length=1)


class ColorCreate(ColorBase):
    pass


class Color(ColorBase):
    pass


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    price: Decimal = Field(..., ge=0)
    originalPrice: Optional[Decimal] = Field(None, ge=0)
    discount: Optional[Decimal] = Field(None, ge=0, le=100)
    material: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=100)  # Category slug
    subcategory: Optional[str] = Field(None, min_length=1, max_length=100)  # Subcategory slug (optional)
    tags: List[str] = Field(default_factory=list)
    images: List[str] = Field(..., min_items=1)
    colors: List[ColorCreate] = Field(..., min_items=1)
    sizes: List[str] = Field(..., min_items=1)
    availableSizes: Optional[List[str]] = None
    care: Optional[str] = None
    features: Optional[List[str]] = None
    isFeatured: bool = False


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    price: Optional[Decimal] = Field(None, ge=0)
    originalPrice: Optional[Decimal] = Field(None, ge=0)
    discount: Optional[Decimal] = Field(None, ge=0, le=100)
    material: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, min_length=1, max_length=100)  # Category slug
    subcategory: Optional[str] = Field(None, min_length=1, max_length=100)  # Subcategory slug (optional)
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    colors: Optional[List[ColorCreate]] = None
    sizes: Optional[List[str]] = None
    availableSizes: Optional[List[str]] = None
    care: Optional[str] = None
    features: Optional[List[str]] = None
    isFeatured: Optional[bool] = None


class Product(ProductBase):
    id: str = Field(alias="_id")
    rating: Optional[Decimal] = 0
    reviewCount: int = 0
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class ProductList(BaseModel):
    items: List[Product]
    pagination: dict
    filters: dict


class ProductFilter(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(12, ge=1, le=50)
    search: Optional[str] = None
    category: Optional[str] = None  # Category slug
    subcategory: Optional[str] = None  # Subcategory slug
    material: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    sort: str = Field("createdAt", regex="^(price|rating|date|name|createdAt)$")
    order: str = Field("desc", regex="^(asc|desc)$")
    featured: Optional[bool] = None
