"""
Drop all tables from Railway database
Run with: railway run python drop_tables.py
"""
import os
from sqlalchemy import create_engine, text

# Try to get public DATABASE_URL first, fallback to regular one
database_url = os.getenv("DATABASE_PUBLIC_URL") or os.getenv("DATABASE_URL")

if not database_url:
    print("❌ DATABASE_URL not found. Make sure to run with: railway run python drop_tables.py")
    exit(1)

# Replace internal hostname with public one if needed
if "railway.internal" in database_url:
    print("⚠️  Detected internal URL, trying to get public URL...")
    database_url = os.getenv("DATABASE_PUBLIC_URL")
    if not database_url:
        print("❌ Could not find public DATABASE_URL. Please set DATABASE_PUBLIC_URL in Railway.")
        exit(1)

print(f"🔗 Connecting to database...")

# Create engine
engine = create_engine(database_url)

# Drop and recreate schema
with engine.connect() as conn:
    print("🗑️  Dropping public schema...")
    conn.execute(text("DROP SCHEMA public CASCADE;"))
    conn.commit()
    
    print("✨ Creating new public schema...")
    conn.execute(text("CREATE SCHEMA public;"))
    conn.commit()
    
    print("🔐 Granting permissions...")
    conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
    conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
    conn.commit()

print("✅ All tables dropped successfully!")
print("🔄 Now restart your Railway web service to recreate tables.")
