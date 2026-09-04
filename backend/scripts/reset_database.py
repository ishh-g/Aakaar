import os
import psycopg2
from pathlib import Path

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "ulpin_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def reset_database():
    project_root = Path(__file__).resolve().parent.parent.parent
    schema_path = project_root / "db" / "schema.sql"
    seed_path = project_root / "db" / "seed.sql"

    print(f"Connecting to {DB_NAME} at {DB_HOST}:{DB_PORT} as {DB_USER}...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.autocommit = True

    with conn.cursor() as cur:
        print(f"Executing schema from: {schema_path}")
        with open(schema_path, "r", encoding="utf-8") as f:
            cur.execute(f.read())

        print(f"Executing seed data from: {seed_path}")
        with open(seed_path, "r", encoding="utf-8") as f:
            cur.execute(f.read())

        print("\n" + "="*45)
        print("DATABASE RESET SUCCESSFUL - VERIFYING COUNTS")
        print("="*45)

        tables = ["parcels", "buildings", "properties", "conflict_logs", "users", "owners"]
        counts = {}
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            counts[table] = cur.fetchone()[0]
            print(f"  {table:<15}: {counts[table]}")

        print("\nConflict Types Breakdown in conflict_logs:")
        cur.execute("SELECT conflict_type, COUNT(*) FROM conflict_logs GROUP BY conflict_type ORDER BY conflict_type;")
        for ctype, cnt in cur.fetchall():
            print(f"  - {ctype:<25}: {cnt}")

        print("\nProperty Verification Status Breakdown:")
        cur.execute("SELECT verification_status, COUNT(*) FROM properties GROUP BY verification_status ORDER BY verification_status;")
        for status_val, cnt in cur.fetchall():
            print(f"  - {status_val:<15}: {cnt}")

    conn.close()
    print("="*45 + "\n")

if __name__ == "__main__":
    reset_database()
