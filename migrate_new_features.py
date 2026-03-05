import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import engine, Base
from backend.models.user import UserAddress, User
from backend.models.store import Store
from backend.models.order import Order
import psycopg2

# Create new tables (like user_addresses)
Base.metadata.create_all(bind=engine)

conn = psycopg2.connect(host="localhost", user="postgres", password="postgres", dbname="vintage_snacks")
conn.autocommit = True
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS gstin VARCHAR(15)")
    print("Added gstin to users")
except Exception as e:
    print(f"Error adding gstin to users: {e}")
    
try:
    cur.execute("ALTER TABLE stores ADD COLUMN IF NOT EXISTS gstin VARCHAR(15)")
    print("Added gstin to stores")
except Exception as e:
    print(f"Error adding gstin to stores: {e}")

try:
    cur.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS cgst_amount FLOAT DEFAULT 0")
    cur.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS sgst_amount FLOAT DEFAULT 0")
    cur.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS igst_amount FLOAT DEFAULT 0")
    cur.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS is_gift BOOLEAN DEFAULT FALSE")
    cur.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS gift_message TEXT")
    print("Added GST splits and gift fields to orders")
except Exception as e:
    print(f"Error adding fields to orders: {e}")

cur.close()
conn.close()
print("Done migrating new columns and tables!")
