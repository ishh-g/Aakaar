import os
import sys
import psycopg2

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "ulpin_db")

def init_database():
    try:
        # First connect to default postgres DB to create ulpin_db if missing
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname="postgres"
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cur.fetchone()
        if not exists:
            cur.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"Database '{DB_NAME}' created successfully.")
        else:
            print(f"Database '{DB_NAME}' already exists.")
        
        cur.close()
        conn.close()

        # Connect to target DB
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Read and execute schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        cur.execute(schema_sql)
        print("Schema DDL applied successfully.")

        # Read and execute seed.sql
        seed_path = os.path.join(os.path.dirname(__file__), "seed.sql")
        with open(seed_path, "r", encoding="utf-8") as f:
            seed_sql = f.read()
        cur.execute(seed_sql)
        print("Seed data applied successfully.")

        # Confirm PostGIS version
        cur.execute("SELECT PostGIS_Full_Version();")
        postgis_ver = cur.fetchone()[0]
        print(f"PostGIS Version: {postgis_ver}")

        cur.close()
        conn.close()
        print("Database initialization completed cleanly.")
        return True

    except Exception as e:
        print(f"Database connection or execution warning/error: {e}")
        return False

if __name__ == "__main__":
    init_database()
