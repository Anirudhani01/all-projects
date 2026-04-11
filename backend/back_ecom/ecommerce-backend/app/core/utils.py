from typing import Dict, List, Any, Optional
from bson import ObjectId
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def create_pagination_info(page: int, limit: int, total: int) -> Dict[str, Any]:
    """Create pagination information."""
    total_pages = (total + limit - 1) // limit
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": total_pages,
        "hasNext": page < total_pages,
        "hasPrev": page > 1
    }


def build_product_filter(
    search: Optional[str] = None,
    category: Optional[str] = None,
    material: Optional[str] = None,
    size: Optional[str] = None,
    color: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    featured: Optional[bool] = None
) -> Dict[str, Any]:
    """Build MongoDB filter for products."""
    filter_query = {}
    
    # Text search
    if search:
        filter_query["$text"] = {"$search": search}
    
    # Category filter
    if category:
        filter_query["category"] = category
    
    # Material filter
    if material:
        filter_query["material"] = material
    
    # Size filter
    if size:
        filter_query["sizes"] = size
    
    # Color filter
    if color:
        filter_query["colors.name"] = color
    
    # Price range filter
    if price_min is not None or price_max is not None:
        price_filter = {}
        if price_min is not None:
            price_filter["$gte"] = price_min
        if price_max is not None:
            price_filter["$lte"] = price_max
        filter_query["price"] = price_filter
    
    # Featured filter
    if featured is not None:
        filter_query["isFeatured"] = featured
    
    return filter_query


def build_sort_query(sort_field: str, sort_order: str) -> List[tuple]:
    """Build MongoDB sort query."""
    order = 1 if sort_order == "asc" else -1
    
    # Map frontend sort fields to database fields
    field_mapping = {
        "price": "price",
        "rating": "rating",
        "date": "createdAt",
        "name": "name",
        "createdAt": "createdAt"
    }
    
    db_field = field_mapping.get(sort_field, "createdAt")
    return [(db_field, order)]


def format_product_response(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format product data for API response."""
    if "_id" in product_data:
        product_data["id"] = str(product_data.pop("_id"))
    
    # Convert Decimal to float for JSON serialization
    if "price" in product_data:
        product_data["price"] = float(product_data["price"])
    if "originalPrice" in product_data and product_data["originalPrice"]:
        product_data["originalPrice"] = float(product_data["originalPrice"])
    if "discount" in product_data and product_data["discount"]:
        product_data["discount"] = float(product_data["discount"])
    if "rating" in product_data:
        product_data["rating"] = float(product_data["rating"])
    
    return product_data


def format_user_response(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format user data for API response."""
    # Create a copy to avoid modifying the original
    formatted_data = user_data.copy()
    
    # Convert _id to id for Pydantic model compatibility
    if "_id" in formatted_data:
        # Handle both ObjectId and string cases
        if hasattr(formatted_data["_id"], '__str__'):
            formatted_data["id"] = str(formatted_data["_id"])
        else:
            formatted_data["id"] = formatted_data["_id"]
    
    # Remove sensitive information
    formatted_data.pop("hashedPassword", None)
    
    # Ensure required fields are present and properly formatted
    if "createdAt" not in formatted_data:
        formatted_data["createdAt"] = datetime.utcnow()
    elif hasattr(formatted_data["createdAt"], 'isoformat'):
        formatted_data["createdAt"] = formatted_data["createdAt"].isoformat()
    
    if "updatedAt" not in formatted_data:
        formatted_data["updatedAt"] = datetime.utcnow()
    elif hasattr(formatted_data["updatedAt"], 'isoformat'):
        formatted_data["updatedAt"] = formatted_data["updatedAt"].isoformat()
    
    if "isActive" not in formatted_data:
        formatted_data["isActive"] = True
    if "isAdmin" not in formatted_data:
        formatted_data["isAdmin"] = False
    
    return formatted_data


def validate_object_id(object_id: str) -> bool:
    """Validate if string is a valid MongoDB ObjectId."""
    try:
        ObjectId(object_id)
        return True
    except Exception:
        return False


def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Create standardized success response."""
    return {
        "success": True,
        "data": data,
        "message": message
    }


def create_error_response(message: str, error_code: str = None) -> Dict[str, Any]:
    """Create standardized error response."""
    response = {
        "success": False,
        "message": message
    }
    if error_code:
        response["error_code"] = error_code
    return response


def extract_token_from_header(authorization: str) -> Optional[str]:
    """Extract JWT token from Authorization header."""
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
        return token
    except ValueError:
        return None


def sanitize_input(text: str) -> str:
    """Basic input sanitization."""
    if not text:
        return text
    
    # Remove potentially dangerous characters
    dangerous_chars = ["<", ">", '"', "'", "&"]
    for char in dangerous_chars:
        text = text.replace(char, "")
    
    return text.strip()
