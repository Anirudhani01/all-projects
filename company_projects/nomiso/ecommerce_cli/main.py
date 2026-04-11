"""Main CLI application for ecommerce system."""

import json
from decimal import Decimal
from pathlib import Path
from typing import List, Optional
from uuid import UUID, uuid4

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .models import Order, OrderItem, OrderStatus, Product, ProductCategory, User
from .services import DataService

console = Console()


class EcommerceCLI:
    """Main CLI application class."""

    def __init__(self):
        """Initialize the CLI application."""
        self.service = DataService()

    def display_products(self, products: List[Product]) -> None:
        """Display products in a formatted table."""
        if not products:
            console.print("[yellow]No products found.[/yellow]")
            return

        table = Table(title="Products")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Price", style="magenta")
        table.add_column("Category", style="blue")
        table.add_column("Stock", style="red")
        table.add_column("SKU", style="yellow")

        for product in products:
            inventory = self.service.get_inventory(product.id)
            stock = str(inventory.quantity_in_stock) if inventory else "N/A"
            table.add_row(
                str(product.id)[:8] + "...",
                product.name,
                f"${product.price}",
                product.category.value,
                stock,
                product.sku,
            )

        console.print(table)

    def display_orders(self, orders: List[Order]) -> None:
        """Display orders in a formatted table."""
        if not orders:
            console.print("[yellow]No orders found.[/yellow]")
            return

        table = Table(title="Orders")
        table.add_column("ID", style="cyan")
        table.add_column("User", style="green")
        table.add_column("Status", style="blue")
        table.add_column("Total", style="magenta")
        table.add_column("Items", style="yellow")
        table.add_column("Date", style="white")

        for order in orders:
            user = self.service.get_user(order.user_id)
            username = user.username if user else "Unknown"
            status_color = {
                "pending": "yellow",
                "confirmed": "blue",
                "shipped": "cyan",
                "delivered": "green",
                "cancelled": "red",
            }.get(order.status.value, "white")

            table.add_row(
                str(order.id)[:8] + "...",
                username,
                Text(order.status.value.title(), style=status_color),
                f"${order.total_amount}",
                str(len(order.items)),
                order.created_at.strftime("%Y-%m-%d %H:%M"),
            )

        console.print(table)


@click.group()
@click.pass_context
def cli(ctx):
    """Ecommerce CLI Application - Manage products, orders, and users."""
    ctx.ensure_object(dict)
    ctx.obj["app"] = EcommerceCLI()


@cli.group()
def products():
    """Manage products."""
    pass


@products.command("list")
@click.option(
    "--category",
    type=click.Choice([cat.value for cat in ProductCategory]),
    help="Filter by category",
)
@click.option("--search", help="Search products by name, description, or tags")
@click.pass_context
def list_products(ctx, category, search):
    """List all products."""
    app = ctx.obj["app"]

    if search:
        products = app.service.search_products(search)
    else:
        cat_enum = ProductCategory(category) if category else None
        products = app.service.get_products(category=cat_enum)

    app.display_products(products)


@products.command("show")
@click.argument("product_id")
@click.pass_context
def show_product(ctx, product_id):
    """Show detailed product information."""
    app = ctx.obj["app"]

    try:
        pid = UUID(product_id)
        product = app.service.get_product(pid)
        if not product:
            console.print(f"[red]Product {product_id} not found.[/red]")
            return

        # Display product details
        console.print(f"\n[bold green]Product Details[/bold green]")
        console.print(f"ID: {product.id}")
        console.print(f"Name: {product.name}")
        console.print(f"Description: {product.description}")
        console.print(f"Price: ${product.price}")
        console.print(f"Category: {product.category.value}")
        console.print(f"Brand: {product.brand}")
        console.print(f"SKU: {product.sku}")
        console.print(f"Tags: {', '.join(product.tags)}")

        # Display inventory
        inventory = app.service.get_inventory(product.id)
        if inventory:
            console.print(f"\n[bold blue]Inventory[/bold blue]")
            console.print(f"Available: {inventory.quantity_available}")
            console.print(f"Reserved: {inventory.quantity_reserved}")
            console.print(f"In Stock: {inventory.quantity_in_stock}")
            console.print(f"Reorder Level: {inventory.reorder_level}")

        # Display reviews
        reviews = app.service.get_reviews(product_id=product.id)
        if reviews:
            console.print(f"\n[bold yellow]Reviews ({len(reviews)})[/bold yellow]")
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            console.print(f"Average Rating: {avg_rating:.1f}/5")

    except ValueError:
        console.print(f"[red]Invalid product ID format.[/red]")


@products.command("add")
@click.option("--name", prompt=True, help="Product name")
@click.option("--description", prompt=True, help="Product description")
@click.option("--price", prompt=True, type=float, help="Product price")
@click.option(
    "--category",
    prompt=True,
    type=click.Choice([cat.value for cat in ProductCategory]),
    help="Product category",
)
@click.option("--stock", prompt=True, type=int, help="Initial stock quantity")
@click.option("--sku", prompt=True, help="Product SKU")
@click.option("--brand", prompt=True, help="Product brand")
@click.pass_context
def add_product(ctx, name, description, price, category, stock, sku, brand):
    """Add a new product."""
    app = ctx.obj["app"]

    try:
        product = Product(
            name=name,
            description=description,
            price=Decimal(str(price)),
            category=ProductCategory(category),
            stock_quantity=stock,
            sku=sku,
            brand=brand,
        )

        app.service.add_product(product)
        app.service.save_data()

        console.print(f"[green]Product '{name}' added successfully![/green]")
        console.print(f"Product ID: {product.id}")

    except Exception as e:
        console.print(f"[red]Error adding product: {e}[/red]")


@cli.group()
def orders():
    """Manage orders."""
    pass


@orders.command("list")
@click.option("--user", help="Filter by username")
@click.option(
    "--status",
    type=click.Choice([status.value for status in OrderStatus]),
    help="Filter by status",
)
@click.pass_context
def list_orders(ctx, user, status):
    """List orders."""
    app = ctx.obj["app"]

    user_id = None
    if user:
        user_obj = app.service.get_user_by_username(user)
        if not user_obj:
            console.print(f"[red]User '{user}' not found.[/red]")
            return
        user_id = user_obj.id

    status_enum = OrderStatus(status) if status else None
    orders = app.service.get_orders(user_id=user_id, status=status_enum)
    app.display_orders(orders)


@orders.command("show")
@click.argument("order_id")
@click.pass_context
def show_order(ctx, order_id):
    """Show detailed order information."""
    app = ctx.obj["app"]

    try:
        oid = UUID(order_id)
        order = app.service.get_order(oid)
        if not order:
            console.print(f"[red]Order {order_id} not found.[/red]")
            return

        user = app.service.get_user(order.user_id)
        username = user.username if user else "Unknown"

        console.print(f"\n[bold green]Order Details[/bold green]")
        console.print(f"ID: {order.id}")
        console.print(f"User: {username}")
        console.print(f"Status: {order.status.value}")
        console.print(f"Total: ${order.total_amount}")
        console.print(f"Created: {order.created_at}")

        # Display items
        console.print(f"\n[bold blue]Items[/bold blue]")
        table = Table()
        table.add_column("Product")
        table.add_column("Quantity")
        table.add_column("Unit Price")
        table.add_column("Total")

        for item in order.items:
            product = app.service.get_product(item.product_id)
            product_name = product.name if product else "Unknown"
            table.add_row(
                product_name,
                str(item.quantity),
                f"${item.unit_price}",
                f"${item.total_price}",
            )

        console.print(table)

    except ValueError:
        console.print(f"[red]Invalid order ID format.[/red]")


@orders.command("create")
@click.option("--user", prompt=True, help="Username")
@click.pass_context
def create_order(ctx, user):
    """Create a new order from user's cart."""
    app = ctx.obj["app"]

    user_obj = app.service.get_user_by_username(user)
    if not user_obj:
        console.print(f"[red]User '{user}' not found.[/red]")
        return

    cart = app.service.get_cart(user_obj.id)
    if not cart or not cart.items:
        console.print(f"[red]Cart is empty for user '{user}'.[/red]")
        return

    try:
        # Create order items
        order_items = []
        for cart_item in cart.items:
            if not app.service.check_stock(cart_item.product_id, cart_item.quantity):
                product = app.service.get_product(cart_item.product_id)
                console.print(
                    f"[red]Insufficient stock for {product.name if product else 'unknown product'}[/red]"
                )
                return

            order_items.append(cart_item)

        # Calculate totals
        subtotal = sum(item.total_price for item in order_items)
        shipping_cost = Decimal("10.00") if subtotal < 100 else Decimal("0.00")
        tax_amount = subtotal * Decimal("0.08")  # 8% tax
        total_amount = subtotal + shipping_cost + tax_amount

        # Create order
        order = Order(
            user_id=user_obj.id,
            items=order_items,
            total_amount=total_amount,
            shipping_address=user_obj.address or {},
            payment_method="credit_card",
            shipping_cost=shipping_cost,
            tax_amount=tax_amount,
        )

        # Reserve stock
        for item in order_items:
            app.service.reserve_stock(item.product_id, item.quantity)

        app.service.add_order(order)
        app.service.clear_cart(user_obj.id)
        app.service.save_data()

        console.print(f"[green]Order created successfully![/green]")
        console.print(f"Order ID: {order.id}")
        console.print(f"Total: ${order.total_amount}")

    except Exception as e:
        console.print(f"[red]Error creating order: {e}[/red]")


@cli.group()
def users():
    """Manage users."""
    pass


@users.command("list")
@click.pass_context
def list_users(ctx):
    """List all users."""
    app = ctx.obj["app"]
    users = app.service.get_users()

    if not users:
        console.print("[yellow]No users found.[/yellow]")
        return

    table = Table(title="Users")
    table.add_column("ID", style="cyan")
    table.add_column("Username", style="green")
    table.add_column("Email", style="blue")
    table.add_column("Name", style="magenta")
    table.add_column("Role", style="yellow")

    for user in users:
        table.add_row(
            str(user.id)[:8] + "...",
            user.username,
            user.email,
            f"{user.first_name} {user.last_name}",
            user.role.value,
        )

    console.print(table)


@cli.group()
def inventory():
    """Manage inventory."""
    pass


@inventory.command("status")
@click.pass_context
def inventory_status(ctx):
    """Show inventory status."""
    app = ctx.obj["app"]
    low_stock = app.service.get_low_stock_products()

    if low_stock:
        console.print("[bold red]Low Stock Alert![/bold red]")
        table = Table()
        table.add_column("Product", style="green")
        table.add_column("Current Stock", style="red")
        table.add_column("Reorder Level", style="yellow")

        for product, inventory in low_stock:
            table.add_row(
                product.name,
                str(inventory.quantity_in_stock),
                str(inventory.reorder_level),
            )

        console.print(table)
    else:
        console.print("[green]All products are adequately stocked.[/green]")


@cli.command("stats")
@click.argument("product_id")
@click.pass_context
def product_stats(ctx, product_id):
    """Show product statistics."""
    app = ctx.obj["app"]

    try:
        pid = UUID(product_id)
        stats = app.service.get_product_stats(pid)

        if not stats:
            console.print(f"[red]Product {product_id} not found.[/red]")
            return

        console.print(
            f"\n[bold green]Statistics for {stats['product'].name}[/bold green]"
        )
        console.print(f"Total Orders: {stats['total_orders']}")
        console.print(f"Total Quantity Sold: {stats['total_quantity_sold']}")
        console.print(f"Total Revenue: ${stats['total_revenue']}")
        console.print(f"Average Rating: {stats['average_rating']}/5")
        console.print(f"Total Reviews: {stats['total_reviews']}")
        console.print(f"Current Stock: {stats['current_stock']}")
        console.print(f"Needs Restock: {'Yes' if stats['needs_restock'] else 'No'}")

    except ValueError:
        console.print(f"[red]Invalid product ID format.[/red]")


if __name__ == "__main__":
    cli()
