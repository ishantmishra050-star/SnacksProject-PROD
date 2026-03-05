"""Add new columns to existing database tables."""
import psycopg2

conn = psycopg2.connect(host="localhost", user="postgres", password="postgres", dbname="vintage_snacks")
conn.autocommit = True
cur = conn.cursor()

cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS gst_rate FLOAT DEFAULT 12.0")
print("Added gst_rate to products")

cur.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS subtotal FLOAT DEFAULT 0")
cur.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS gst_amount FLOAT DEFAULT 0")
print("Added subtotal, gst_amount to orders")

cur.close()
conn.close()
print("Done!")
