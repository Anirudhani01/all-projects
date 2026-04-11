from database import SessionLocal, engine
from models import Base, Product

Base.metadata.create_all(bind=engine)
db = SessionLocal()

products = [
    # Laptops (3 units each)
    Product(name="HP Laptop 6GB/512SSD", description="6GB RAM, 512GB SSD", price=50000, image_url="/static/images/laptop1.png", category="laptops", stock=3),
    Product(name="HP Laptop 16GB/512SSD", description="16GB RAM, 512GB SSD", price=60000, image_url="/static/images/laptop2.png", category="laptops", stock=3),
    Product(name="HP Laptop 32GB/512SSD", description="32GB RAM, 512GB SSD", price=70000, image_url="/static/images/laptop3.png", category="laptops", stock=3),
    Product(name="HP Laptop 32GB/1TB SSD", description="32GB RAM, 1TB SSD", price=80000, image_url="/static/images/laptop4.png", category="laptops", stock=3),

    # Mobiles (2 units each)
    Product(name="Apple 16 (6GB/128GB)", description="Apple 16, 6GB RAM, 128GB", price=90000, image_url="/static/images/mobile1.png", category="mobiles", stock=2),
    Product(name="Apple 16 (8GB/128GB)", description="Apple 16, 8GB RAM, 128GB", price=95000, image_url="/static/images/mobile2.png", category="mobiles", stock=2),
    Product(name="Apple 16 Plus (6GB/128GB)", description="Apple 16 Plus, 6GB RAM", price=97000, image_url="/static/images/mobile3.png", category="mobiles", stock=2),
    Product(name="Apple 16 Plus (8GB/128GB)", description="Apple 16 Plus, 8GB RAM", price=99000, image_url="/static/images/mobile4.png", category="mobiles", stock=2),

    # Smartwatches (2 units each)
    Product(name="Samsung Galaxy Watch 5", description="1.4-inch AMOLED, 16GB", price=18000, image_url="/static/images/watch1.png", category="smartwatch", stock=2),
    Product(name="Apple Watch Series 8", description="1.9-inch Retina, 32GB", price=40000, image_url="/static/images/watch2.png", category="smartwatch", stock=2),

    # TVs (2 units each)
    Product(name="Samsung 43-inch 4K TV", description="Ultra HD LED Smart TV", price=35000, image_url="/static/images/tv1.png", category="tv", stock=2),
    Product(name="Sony Bravia 55-inch OLED", description="Premium OLED Google TV", price=120000, image_url="/static/images/tv2.png", category="tv", stock=2)
]

db.query(Product).delete()  # Clean before inserting
for p in products:
    db.add(p)

db.commit()
db.close()
