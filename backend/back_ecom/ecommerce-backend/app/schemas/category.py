from typing import List, Optional
from datetime import datetime


class SubcategorySchema:
    def __init__(
        self,
        name: str,
        slug: str,
        categoryId: str,
        description: Optional[str] = None,
        isActive: bool = True
    ):
        self.name = name
        self.slug = slug
        self.categoryId = categoryId
        self.description = description
        self.isActive = isActive
        self.createdAt = datetime.utcnow()
        self.updatedAt = datetime.utcnow()
    
    def to_dict(self):
        return {
            "name": self.name,
            "slug": self.slug,
            "categoryId": self.categoryId,
            "description": self.description,
            "isActive": self.isActive,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data["name"],
            slug=data["slug"],
            categoryId=data["categoryId"],
            description=data.get("description"),
            isActive=data.get("isActive", True)
        )
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updatedAt = datetime.utcnow()


class CategorySchema:
    def __init__(
        self,
        name: str,
        slug: str,
        description: Optional[str] = None,
        image: Optional[str] = None,
        icon: Optional[str] = None,
        isActive: bool = True,
        isFeatured: bool = False,
        sortOrder: int = 0
    ):
        self.name = name
        self.slug = slug
        self.description = description
        self.image = image
        self.icon = icon
        self.isActive = isActive
        self.isFeatured = isFeatured
        self.sortOrder = sortOrder
        self.productCount = 0
        self.createdAt = datetime.utcnow()
        self.updatedAt = datetime.utcnow()
    
    def to_dict(self):
        return {
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "image": self.image,
            "icon": self.icon,
            "isActive": self.isActive,
            "isFeatured": self.isFeatured,
            "sortOrder": self.sortOrder,
            "productCount": self.productCount,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data["name"],
            slug=data["slug"],
            description=data.get("description"),
            image=data.get("image"),
            icon=data.get("icon"),
            isActive=data.get("isActive", True),
            isFeatured=data.get("isFeatured", False),
            sortOrder=data.get("sortOrder", 0)
        )
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updatedAt = datetime.utcnow()
    
    def increment_product_count(self):
        """Increment the product count for this category."""
        self.productCount += 1
        self.updatedAt = datetime.utcnow()
    
    def decrement_product_count(self):
        """Decrement the product count for this category."""
        if self.productCount > 0:
            self.productCount -= 1
            self.updatedAt = datetime.utcnow()
