import psycopg2

conn = psycopg2.connect(host="localhost", user="postgres", password="postgres", dbname="vintage_snacks")
conn.autocommit = True
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS discount_amount FLOAT DEFAULT 0")
    print("Added discount_amount to orders")
except Exception as e:
    print(f"Error adding discount_amount to orders: {e}")

cur.close()
conn.close()
print("Done migrating discount_amount!")
