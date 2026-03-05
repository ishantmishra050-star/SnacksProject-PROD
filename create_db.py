import psycopg2

try:
    conn = psycopg2.connect(host="localhost", user="postgres", password="postgres", dbname="postgres")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("CREATE DATABASE vintage_snacks")
    print("Database 'vintage_snacks' created successfully!")
    cur.close()
    conn.close()
except psycopg2.errors.DuplicateDatabase:
    print("Database 'vintage_snacks' already exists, skipping.")
except Exception as e:
    print(f"Error: {e}")
