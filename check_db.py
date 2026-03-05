from backend.database import SessionLocal
from backend.models.product import Product

db = SessionLocal()
products = db.query(Product).all()
print(f"Total products: {len(products)}")
for p in products:
    print(f"- {p.name}: {p.image_url}")
db.close()
