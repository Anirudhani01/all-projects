from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SubcategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    slug: str = Field(..., min_length=1, max_length=100, regex="^[a-z0-9-]+$")


class SubcategoryCreate(SubcategoryBase):
    pass


class SubcategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    slug: Optional[str] = Field(None, min_length=1, max_length=100, regex="^[a-z0-9-]+$")


class Subcategory(SubcategoryBase):
    id: str = Field(alias="_id")
    categoryId: str
    isActive: bool = True
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    slug: str = Field(..., min_length=1, max_length=100, regex="^[a-z0-9-]+$")
    image: Optional[str] = None  # URL or path to category image/icon
    icon: Optional[str] = None   # Icon class or identifier
    isActive: bool = True
    isFeatured: bool = False
    sortOrder: int = 0  # For custom ordering


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    slug: Optional[str] = Field(None, min_length=1, max_length=100, regex="^[a-z0-9-]+$")
    image: Optional[str] = None
    icon: Optional[str] = None
    isActive: Optional[bool] = None
    isFeatured: Optional[bool] = None
    sortOrder: Optional[int] = None


class Category(CategoryBase):
    id: str = Field(alias="_id")
    subcategories: List[Subcategory] = []
    productCount: int = 0  # Number of products in this category
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True


class CategoryWithSubcategories(Category):
    """Category model with populated subcategories."""
    subcategories: List[Subcategory] = []


class CategoryList(BaseModel):
    success: bool
    data: List[Category]
    message: str


class CategoryResponse(BaseModel):
    success: bool
    data: Category
    message: str


class SubcategoryList(BaseModel):
    success: bool
    data: List[Subcategory]
    message: str


class SubcategoryResponse(BaseModel):
    success: bool
    data: Subcategory
    message: str


class CategoryFilter(BaseModel):
    """Filter options for categories."""
    isActive: Optional[bool] = None
    isFeatured: Optional[bool] = None
    search: Optional[str] = None
    sortBy: str = Field("sortOrder", regex="^(name|sortOrder|createdAt|productCount)$")
    sortOrder: str = Field("asc", regex="^(asc|desc)$")
