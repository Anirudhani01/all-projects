from typing import List, Optional
from datetime import datetime
from decimal import Decimal


class ColorSchema:
    def __init__(self, name: str, hex: str, image: str):
        self.name = name
        self.hex = hex
        self.image = image
    
    def to_dict(self):
        return {
            "name": self.name,
            "hex": self.hex,
            "image": self.image
        }


class ProductSchema:
    def __init__(
        self,
        name: str,
        description: str,
        price: Decimal,
        material: str,
        category: str,
        images: List[str],
        colors: List[ColorSchema],
        sizes: List[str],
        originalPrice: Optional[Decimal] = None,
        discount: Optional[Decimal] = None,
        availableSizes: Optional[List[str]] = None,
        care: Optional[str] = None,
        features: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        subcategory: Optional[str] = None,
        isFeatured: bool = False,
        rating: Decimal = Decimal('0'),
        reviewCount: int = 0
    ):
        self.name = name
        self.description = description
        self.price = price
        self.originalPrice = originalPrice
        self.discount = discount
        self.rating = rating
        self.reviewCount = reviewCount
        self.images = images
        self.colors = colors
        self.sizes = sizes
        self.availableSizes = availableSizes or sizes
        self.material = material
        self.care = care
        self.features = features or []
        self.category = category
        self.subcategory = subcategory
        self.tags = tags or []
        self.isFeatured = isFeatured
        self.createdAt = datetime.utcnow()
        self.updatedAt = datetime.utcnow()
    
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "originalPrice": self.originalPrice,
            "discount": self.discount,
            "rating": self.rating,
            "reviewCount": self.reviewCount,
            "images": self.images,
            "colors": [color.to_dict() for color in self.colors],
            "sizes": self.sizes,
            "availableSizes": self.availableSizes,
            "material": self.material,
            "care": self.care,
            "features": self.features,
            "category": self.category,
            "subcategory": self.subcategory,
            "tags": self.tags,
            "isFeatured": self.isFeatured,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        colors = [ColorSchema(**color) for color in data.get("colors", [])]
        return cls(
            name=data["name"],
            description=data["description"],
            price=data["price"],
            material=data["material"],
            category=data["category"],
            images=data["images"],
            colors=colors,
            sizes=data["sizes"],
            originalPrice=data.get("originalPrice"),
            discount=data.get("discount"),
            availableSizes=data.get("availableSizes"),
            care=data.get("care"),
            features=data.get("features"),
            tags=data.get("tags"),
            subcategory=data.get("subcategory"),
            isFeatured=data.get("isFeatured", False),
            rating=data.get("rating", Decimal('0')),
            reviewCount=data.get("reviewCount", 0)
        )
