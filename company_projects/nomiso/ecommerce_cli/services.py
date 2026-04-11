"""Service layer for the ecommerce CLI application."""

import json
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID

from .models import (
    Cart,
    Inventory,
    Order,
    OrderItem,
    OrderStatus,
    Product,
    ProductCategory,
    Review,
    User,
    UserRole,
)


class DataService:
    """Service for managing ecommerce data."""

    def __init__(self, data_file: Optional[Path] = None):
        """Initialize the data service."""
        self.data_file = (
            data_file or Path(__file__).parent.parent / "data" / "sample_data.json"
        )
        self._products: Dict[UUID, Product] = {}
        self._users: Dict[UUID, User] = {}
        self._orders: Dict[UUID, Order] = {}
        self._carts: Dict[UUID, Cart] = {}
        self._inventory: Dict[UUID, Inventory] = {}
        self._reviews: Dict[UUID, Review] = {}
        self.load_data()

    def load_data(self) -> None:
        """Load data from JSON file."""
        if not self.data_file.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_file}")

        with open(self.data_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Load products
        for item in data.get("products", []):
            product = Product(**item)
            self._products[product.id] = product

        # Load users
        for item in data.get("users", []):
            user = User(**item)
            self._users[user.id] = user

        # Load orders
        for item in data.get("orders", []):
            order = Order(**item)
            self._orders[order.id] = order

        # Load carts
        for item in data.get("carts", []):
            cart = Cart(**item)
            self._carts[cart.id] = cart

        # Load inventory
        for item in data.get("inventory", []):
            inventory = Inventory(**item)
            self._inventory[inventory.product_id] = inventory

        # Load reviews
        for item in data.get("reviews", []):
            review = Review(**item)
            self._reviews[review.id] = review

    def save_data(self) -> None:
        """Save data to JSON file."""
        data = {
            "products": [product.dict() for product in self._products.values()],
            "users": [user.dict() for user in self._users.values()],
            "orders": [order.dict() for order in self._orders.values()],
            "carts": [cart.dict() for cart in self._carts.values()],
            "inventory": [inventory.dict() for inventory in self._inventory.values()],
            "reviews": [review.dict() for review in self._reviews.values()],
        }

        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    # Product methods
    def get_products(
        self, category: Optional[ProductCategory] = None, active_only: bool = True
    ) -> List[Product]:
        """Get all products, optionally filtered by category."""
        products = list(self._products.values())

        if active_only:
            products = [p for p in products if p.is_active]

        if category:
            products = [p for p in products if p.category == category]

        return sorted(products, key=lambda x: x.name)

    def get_product(self, product_id: UUID) -> Optional[Product]:
        """Get a product by ID."""
        return self._products.get(product_id)

    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """Get a product by SKU."""
        for product in self._products.values():
            if product.sku == sku.upper():
                return product
        return None

    def search_products(self, query: str) -> List[Product]:
        """Search products by name, description, or tags."""
        query = query.lower()
        results = []

        for product in self._products.values():
            if not product.is_active:
                continue

            if (
                query in product.name.lower()
                or query in product.description.lower()
                or any(query in tag.lower() for tag in product.tags)
                or query in product.brand.lower()
            ):
                results.append(product)

        return sorted(results, key=lambda x: x.name)

    def add_product(self, product: Product) -> None:
        """Add a new product."""
        self._products[product.id] = product

    def update_product(self, product: Product) -> None:
        """Update an existing product."""
        if product.id in self._products:
            self._products[product.id] = product
        else:
            raise ValueError(f"Product with ID {product.id} not found")

    def delete_product(self, product_id: UUID) -> bool:
        """Delete a product (soft delete by setting is_active to False)."""
        if product_id in self._products:
            self._products[product_id].is_active = False
            return True
        return False

    # User methods
    def get_users(self, role: Optional[UserRole] = None) -> List[User]:
        """Get all users, optionally filtered by role."""
        users = list(self._users.values())

        if role:
            users = [u for u in users if u.role == role]

        return sorted(users, key=lambda x: x.username)

    def get_user(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID."""
        return self._users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        for user in self._users.values():
            if user.username == username.lower():
                return user
        return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        for user in self._users.values():
            if user.email.lower() == email.lower():
                return user
        return None

    def add_user(self, user: User) -> None:
        """Add a new user."""
        self._users[user.id] = user

    def update_user(self, user: User) -> None:
        """Update an existing user."""
        if user.id in self._users:
            self._users[user.id] = user
        else:
            raise ValueError(f"User with ID {user.id} not found")

    # Order methods
    def get_orders(
        self, user_id: Optional[UUID] = None, status: Optional[OrderStatus] = None
    ) -> List[Order]:
        """Get orders, optionally filtered by user or status."""
        orders = list(self._orders.values())

        if user_id:
            orders = [o for o in orders if o.user_id == user_id]

        if status:
            orders = [o for o in orders if o.status == status]

        return sorted(orders, key=lambda x: x.created_at, reverse=True)

    def get_order(self, order_id: UUID) -> Optional[Order]:
        """Get an order by ID."""
        return self._orders.get(order_id)

    def add_order(self, order: Order) -> None:
        """Add a new order."""
        self._orders[order.id] = order

    def update_order(self, order: Order) -> None:
        """Update an existing order."""
        if order.id in self._orders:
            self._orders[order.id] = order
        else:
            raise ValueError(f"Order with ID {order.id} not found")

    def update_order_status(self, order_id: UUID, status: OrderStatus) -> bool:
        """Update order status."""
        if order_id in self._orders:
            self._orders[order_id].status = status
            return True
        return False

    # Cart methods
    def get_cart(self, user_id: UUID) -> Optional[Cart]:
        """Get user's cart."""
        for cart in self._carts.values():
            if cart.user_id == user_id:
                return cart
        return None

    def add_cart(self, cart: Cart) -> None:
        """Add a new cart."""
        self._carts[cart.id] = cart

    def update_cart(self, cart: Cart) -> None:
        """Update an existing cart."""
        if cart.id in self._carts:
            self._carts[cart.id] = cart
        else:
            raise ValueError(f"Cart with ID {cart.id} not found")

    def clear_cart(self, user_id: UUID) -> bool:
        """Clear user's cart."""
        cart = self.get_cart(user_id)
        if cart:
            cart.items.clear()
            return True
        return False

    # Inventory methods
    def get_inventory(self, product_id: UUID) -> Optional[Inventory]:
        """Get inventory for a product."""
        return self._inventory.get(product_id)

    def get_all_inventory(self) -> List[Inventory]:
        """Get all inventory records."""
        return list(self._inventory.values())

    def update_inventory(self, inventory: Inventory) -> None:
        """Update inventory."""
        self._inventory[inventory.product_id] = inventory

    def check_stock(self, product_id: UUID, quantity: int) -> bool:
        """Check if enough stock is available."""
        inventory = self.get_inventory(product_id)
        if not inventory:
            return False
        return inventory.quantity_in_stock >= quantity

    def reserve_stock(self, product_id: UUID, quantity: int) -> bool:
        """Reserve stock for an order."""
        inventory = self.get_inventory(product_id)
        if not inventory or inventory.quantity_in_stock < quantity:
            return False

        inventory.quantity_reserved += quantity
        return True

    def release_stock(self, product_id: UUID, quantity: int) -> bool:
        """Release reserved stock."""
        inventory = self.get_inventory(product_id)
        if not inventory:
            return False

        inventory.quantity_reserved = max(0, inventory.quantity_reserved - quantity)
        return True

    def fulfill_stock(self, product_id: UUID, quantity: int) -> bool:
        """Fulfill stock (remove from available and reserved)."""
        inventory = self.get_inventory(product_id)
        if not inventory:
            return False

        if inventory.quantity_reserved >= quantity:
            inventory.quantity_reserved -= quantity
            inventory.quantity_available -= quantity
            return True

        return False

    # Review methods
    def get_reviews(
        self, product_id: Optional[UUID] = None, user_id: Optional[UUID] = None
    ) -> List[Review]:
        """Get reviews, optionally filtered by product or user."""
        reviews = list(self._reviews.values())

        if product_id:
            reviews = [r for r in reviews if r.product_id == product_id]

        if user_id:
            reviews = [r for r in reviews if r.user_id == user_id]

        return sorted(reviews, key=lambda x: x.created_at, reverse=True)

    def get_review(self, review_id: UUID) -> Optional[Review]:
        """Get a review by ID."""
        return self._reviews.get(review_id)

    def add_review(self, review: Review) -> None:
        """Add a new review."""
        self._reviews[review.id] = review

    def update_review(self, review: Review) -> None:
        """Update an existing review."""
        if review.id in self._reviews:
            self._reviews[review.id] = review
        else:
            raise ValueError(f"Review with ID {review.id} not found")

    def delete_review(self, review_id: UUID) -> bool:
        """Delete a review."""
        if review_id in self._reviews:
            del self._reviews[review_id]
            return True
        return False

    # Analytics methods
    def get_low_stock_products(self) -> List[tuple[Product, Inventory]]:
        """Get products that need restocking."""
        low_stock = []
        for inventory in self._inventory.values():
            if inventory.needs_restock:
                product = self.get_product(inventory.product_id)
                if product:
                    low_stock.append((product, inventory))
        return low_stock

    def get_product_stats(self, product_id: UUID) -> Dict:
        """Get statistics for a product."""
        product = self.get_product(product_id)
        if not product:
            return {}

        reviews = self.get_reviews(product_id=product_id)
        inventory = self.get_inventory(product_id)

        total_orders = 0
        total_quantity_sold = 0
        total_revenue = Decimal("0")

        for order in self._orders.values():
            for item in order.items:
                if item.product_id == product_id:
                    total_orders += 1
                    total_quantity_sold += item.quantity
                    total_revenue += item.total_price

        avg_rating = 0
        if reviews:
            avg_rating = sum(r.rating for r in reviews) / len(reviews)

        return {
            "product": product,
            "total_orders": total_orders,
            "total_quantity_sold": total_quantity_sold,
            "total_revenue": total_revenue,
            "average_rating": round(avg_rating, 2),
            "total_reviews": len(reviews),
            "current_stock": inventory.quantity_in_stock if inventory else 0,
            "needs_restock": inventory.needs_restock if inventory else True,
        }
