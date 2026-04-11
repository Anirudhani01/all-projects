from datetime import datetime
from enum import Enum
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from database import create_db_and_tables, get_session, engine
from models import MenuItem, Order, OrderItem, OrderStatus, PaymentMethod
from schemas import (
    MenuItemRead, MenuItemToggleOutOfStock, OrderItemAdd, OrderItemUpdate,
    OrderItemRead, OrderRead, TableSummary, PayOrder, MenuItemCreate, MenuItemUpdate
)

app = FastAPI(title="Restaurant Orders", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    with Session(engine) as session:
        seed_menu(session)

def seed_menu(session: Session):
    exists = session.exec(select(MenuItem.id)).first()
    if exists:
        return
    items = [
        # Veg Rice
        MenuItem(name="Veg Fried Rice", main_category="veg", sub_category="rice", price=90.0, description="Stir-fried rice with vegetables"),
        MenuItem(name="Jeera Rice", main_category="veg", sub_category="rice", price=80.0, description="Basmati rice with cumin seeds"),
        
        # Non-Veg Rice
        MenuItem(name="Chicken Fried Rice", main_category="non-veg", sub_category="rice", price=120.0, description="Stir-fried rice with chicken"),
        MenuItem(name="Egg Fried Rice", main_category="non-veg", sub_category="rice", price=100.0, description="Stir-fried rice with egg"),
        
        # Veg Noodles
        MenuItem(name="Veg Hakka Noodles", main_category="veg", sub_category="noodles", price=85.0, description="Stir-fried noodles with vegetables"),
        MenuItem(name="Veg Chow Mein", main_category="veg", sub_category="noodles", price=90.0, description="Chinese style noodles with vegetables"),
        
        # Non-Veg Noodles
        MenuItem(name="Chicken Noodles", main_category="non-veg", sub_category="noodles", price=110.0, description="Stir-fried noodles with chicken"),
        
        # Veg Starters
        MenuItem(name="Veg Spring Roll", main_category="veg", sub_category="starters", price=60.0, description="Crispy spring rolls with vegetables"),
        MenuItem(name="Paneer Tikka", main_category="veg", sub_category="starters", price=120.0, description="Grilled cottage cheese with spices"),
        
        # Non-Veg Starters
        MenuItem(name="Chicken 65", main_category="non-veg", sub_category="starters", price=140.0, description="Spicy fried chicken"),
        MenuItem(name="Chicken Manchurian", main_category="non-veg", sub_category="starters", price=130.0, description="Indo-Chinese chicken dish"),
        
        # Veg Biryani
        MenuItem(name="Veg Biryani", main_category="veg", sub_category="biryani", price=150.0, description="Aromatic rice with vegetables"),
        MenuItem(name="Paneer Biryani", main_category="veg", sub_category="biryani", price=180.0, description="Aromatic rice with paneer"),
        
        # Non-Veg Biryani
        MenuItem(name="Chicken Biryani", main_category="non-veg", sub_category="biryani", price=200.0, description="Aromatic rice with chicken"),
        MenuItem(name="Mutton Biryani", main_category="non-veg", sub_category="biryani", price=250.0, description="Aromatic rice with mutton"),
        
        # Beverages
        MenuItem(name="Tea", main_category="beverages", sub_category="hot", price=15.0, description="Hot tea"),
        MenuItem(name="Coffee", main_category="beverages", sub_category="hot", price=20.0, description="Hot coffee"),
        MenuItem(name="Lassi", main_category="beverages", sub_category="cold", price=30.0, description="Sweet yogurt drink"),
    ]
    session.add_all(items)
    session.commit()

def calc_total(order: Order) -> float:
    return sum(oi.price_snapshot * oi.quantity for oi in order.items)

def ensure_table_number(n: int):
    if n < 1 or n > 12:
        raise HTTPException(status_code=400, detail="table_number must be 1..12")

def get_open_order_for_table(session: Session, table_number: int) -> Optional[Order]:
    return session.exec(
        select(Order).where(Order.table_number == table_number, Order.status == OrderStatus.open)
    ).first()

def serialize_order(order: Order) -> OrderRead:
    items = [
        OrderItemRead(
            id=oi.id,
            menu_item_id=oi.menu_item_id,
            name_snapshot=oi.name_snapshot,
            price_snapshot=oi.price_snapshot,
            quantity=oi.quantity,
        ) for oi in order.items
    ]
    return OrderRead(
        id=order.id,
        table_number=order.table_number,
        status=order.status.value,
        opened_at=order.opened_at,
        paid_at=order.paid_at,
        payment_method=order.payment_method.value if order.payment_method else None,
        items=items,
        total_amount=calc_total(order),
    )

@app.get("/")
def read_root():
    return {"message": "Restaurant Management System API", "version": "1.0.0"}

@app.get("/menu", response_model=List[MenuItemRead])
def list_menu(
    search: Optional[str] = Query(default=None), 
    category: Optional[str] = Query(default=None),
    session: Session = Depends(get_session)
):
    query = select(MenuItem).where(MenuItem.is_active == True)  # noqa: E712
    
    if search:
        like = f"%{search}%"
        query = query.where(MenuItem.name.like(like))
    
    if category:
        query = query.where(MenuItem.main_category == category)
    
    return session.exec(query.order_by(MenuItem.name)).all()

@app.put("/menu/out-of-stock", response_model=List[MenuItemRead])
def set_out_of_stock(payload: MenuItemToggleOutOfStock, session: Session = Depends(get_session)):
    all_items = session.exec(select(MenuItem)).all()
    target_ids = set(payload.ids)
    changed = []
    for item in all_items:
        new_state = item.id in target_ids
        if item.is_out_of_stock != new_state:
            item.is_out_of_stock = new_state
            changed.append(item)
    if changed:
        session.add_all(changed)
        session.commit()
    return session.exec(select(MenuItem).order_by(MenuItem.name)).all()

@app.post("/menu", response_model=MenuItemRead)
def create_menu_item(payload: MenuItemCreate, session: Session = Depends(get_session)):
    """Create a new menu item"""
    menu_item = MenuItem(
        name=payload.name,
        main_category=payload.main_category,
        sub_category=payload.sub_category,
        price=payload.price,
        description=payload.description
    )
    session.add(menu_item)
    session.commit()
    session.refresh(menu_item)
    return menu_item

@app.get("/menu/categories")
def get_menu_categories(session: Session = Depends(get_session)):
    """Get all available categories"""
    categories = session.exec(
        select(MenuItem.main_category, MenuItem.sub_category)
        .where(MenuItem.is_active == True)  # noqa: E712
        .distinct()
    ).all()
    
    # Organize by main category
    organized = {}
    for main_cat, sub_cat in categories:
        if main_cat not in organized:
            organized[main_cat] = []
        if sub_cat not in organized[main_cat]:
            organized[main_cat].append(sub_cat)
    
    return organized

@app.get("/menu/category/{main_category}")
def get_menu_by_category(main_category: str, session: Session = Depends(get_session)):
    """Get all menu items by main category"""
    items = session.exec(
        select(MenuItem)
        .where(MenuItem.main_category == main_category, MenuItem.is_active == True)  # noqa: E712
        .order_by(MenuItem.sub_category, MenuItem.name)
    ).all()
    return items

@app.get("/menu/category/{main_category}/{sub_category}")
def get_menu_by_subcategory(main_category: str, sub_category: str, session: Session = Depends(get_session)):
    """Get all menu items by sub category"""
    items = session.exec(
        select(MenuItem)
        .where(
            MenuItem.main_category == main_category,
            MenuItem.sub_category == sub_category,
            MenuItem.is_active == True  # noqa: E712
        )
        .order_by(MenuItem.name)
    ).all()
    return items

@app.get("/menu/{menu_item_id}", response_model=MenuItemRead)
def get_menu_item(menu_item_id: int, session: Session = Depends(get_session)):
    """Get a specific menu item by ID"""
    menu_item = session.get(MenuItem, menu_item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_item

@app.put("/menu/{menu_item_id}", response_model=MenuItemRead)
def update_menu_item(menu_item_id: int, payload: MenuItemUpdate, session: Session = Depends(get_session)):
    """Update a menu item"""
    menu_item = session.get(MenuItem, menu_item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(menu_item, field, value)
    
    session.add(menu_item)
    session.commit()
    session.refresh(menu_item)
    return menu_item

@app.delete("/menu/{menu_item_id}")
def delete_menu_item(menu_item_id: int, session: Session = Depends(get_session)):
    """Delete a menu item (soft delete by setting is_active=False)"""
    menu_item = session.get(MenuItem, menu_item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    menu_item.is_active = False
    session.add(menu_item)
    session.commit()
    return {"message": "Menu item deleted successfully"}

@app.get("/tables", response_model=List[TableSummary])
def get_tables(session: Session = Depends(get_session)):
    summaries: List[TableSummary] = []
    for n in range(1, 13):
        open_order = get_open_order_for_table(session, n)
        if open_order:
            summaries.append(TableSummary(
                table_number=n,
                status="open",
                items=[
                    OrderItemRead(
                        id=oi.id,
                        menu_item_id=oi.menu_item_id,
                        name_snapshot=oi.name_snapshot,
                        price_snapshot=oi.price_snapshot,
                        quantity=oi.quantity
                    ) for oi in open_order.items
                ],
                total_amount=calc_total(open_order),
            ))
        else:
            summaries.append(TableSummary(table_number=n, status="idle", items=[], total_amount=0.0))
    return summaries

@app.post("/tables/{table_number}/order", response_model=OrderRead)
def open_or_get_order(table_number: int, session: Session = Depends(get_session)):
    ensure_table_number(table_number)
    order = get_open_order_for_table(session, table_number)
    if order:
        session.refresh(order)
        return serialize_order(order)
    order = Order(table_number=table_number, status=OrderStatus.open)
    session.add(order)
    session.commit()
    session.refresh(order)
    return serialize_order(order)

@app.get("/orders/{order_id}", response_model=OrderRead)
def get_order(order_id: int, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return serialize_order(order)

@app.post("/orders/{order_id}/items", response_model=OrderRead)
def add_item(order_id: int, payload: OrderItemAdd, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.open:
        raise HTTPException(status_code=400, detail="Cannot modify a paid order")

    item = session.get(MenuItem, payload.menu_item_id)
    if not item or not item.is_active:
        raise HTTPException(status_code=400, detail="Menu item not available")
    if item.is_out_of_stock:
        raise HTTPException(status_code=400, detail=f"{item.name} is out of stock")

    existing = session.exec(
        select(OrderItem).where(OrderItem.order_id == order.id, OrderItem.menu_item_id == item.id)
    ).first()
    if existing:
        existing.quantity += payload.quantity
        session.add(existing)
    else:
        session.add(OrderItem(
            order_id=order.id,
            menu_item_id=item.id,
            name_snapshot=item.name,
            price_snapshot=item.price,
            quantity=payload.quantity
        ))
    session.commit()
    session.refresh(order)
    return serialize_order(order)

@app.patch("/orders/{order_id}/items/{order_item_id}", response_model=OrderRead)
def update_item(order_id: int, order_item_id: int, payload: OrderItemUpdate, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.open:
        raise HTTPException(status_code=400, detail="Cannot modify a paid order")
    oi = session.get(OrderItem, order_item_id)
    if not oi or oi.order_id != order_id:
        raise HTTPException(status_code=404, detail="Order item not found")
    if payload.quantity <= 0:
        session.delete(oi)
    else:
        oi.quantity = payload.quantity
        session.add(oi)
    session.commit()
    session.refresh(order)
    return serialize_order(order)

@app.delete("/orders/{order_id}/items/{order_item_id}", response_model=OrderRead)
def delete_item(order_id: int, order_item_id: int, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.open:
        raise HTTPException(status_code=400, detail="Cannot modify a paid order")
    oi = session.get(OrderItem, order_item_id)
    if not oi or oi.order_id != order_id:
        raise HTTPException(status_code=404, detail="Order item not found")
    session.delete(oi)
    session.commit()
    session.refresh(order)
    return serialize_order(order)

@app.post("/orders/{order_id}/pay", response_model=OrderRead)
def pay_order(order_id: int, payload: PayOrder, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.open:
        raise HTTPException(status_code=400, detail="Order already paid")
    if len(order.items) == 0:
        raise HTTPException(status_code=400, detail="Cannot pay an empty order")
    order.status = OrderStatus.paid
    order.paid_at = datetime.utcnow()
    order.payment_method = PaymentMethod(payload.payment_method)
    session.add(order)
    session.commit()
    session.refresh(order)
    return serialize_order(order)

@app.get("/admin/orders", response_model=List[OrderRead])
def admin_orders(
    status: Optional[str] = Query(default=None),
    table: Optional[int] = Query(default=None),
    payment: Optional[str] = Query(default=None),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    session: Session = Depends(get_session),
):
    query = select(Order)
    if status in {"open", "paid"}:
        query = query.where(Order.status == OrderStatus(status))
    if table:
        query = query.where(Order.table_number == table)
    if payment in {"cash", "online"}:
        query = query.where(Order.payment_method == PaymentMethod(payment))
    if date_from:
        query = query.where(Order.opened_at >= date_from)
    if date_to:
        query = query.where(Order.opened_at <= date_to)
    orders = session.exec(query.order_by(Order.opened_at.desc())).all()
    return [serialize_order(o) for o in orders]

@app.get("/admin/metrics")
def admin_metrics(session: Session = Depends(get_session)):
    paid_orders = session.exec(select(Order).where(Order.status == OrderStatus.paid)).all()
    total_revenue = 0.0
    cash = 0.0
    online = 0.0
    items_sold = 0
    for o in paid_orders:
        amt = sum(oi.price_snapshot * oi.quantity for oi in o.items)
        total_revenue += amt
        if o.payment_method == PaymentMethod.cash:
            cash += amt
        elif o.payment_method == PaymentMethod.online:
            online += amt
        items_sold += sum(oi.quantity for oi in o.items)
    return {"total_revenue": total_revenue, "cash": cash, "online": online, "orders_paid": len(paid_orders), "items_sold": items_sold}
