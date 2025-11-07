"""Quick database setup script with verbose output."""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def setup_database():
    """Quick database setup with verbose output."""
    password = "Deepesh@123"
    
    print("=" * 70)
    print("QUICK DATABASE SETUP")
    print("=" * 70)
    print()
    
    # Step 1: Test connection
    print("Step 1: Testing PostgreSQL connection...")
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="postgres",
            user="postgres",
            password=password
        )
        print("[OK] Connected to PostgreSQL successfully")
        conn.close()
    except psycopg2.OperationalError as e:
        print(f"[ERROR] Connection failed: {e}")
        print("\nPossible issues:")
        print("1. PostgreSQL service not running")
        print("2. Wrong password")
        print("3. Port 5432 blocked")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False
    
    # Step 2: Create database
    print("\nStep 2: Creating database 'library_db'...")
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="postgres",
            user="postgres",
            password=password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'library_db'")
        exists = cur.fetchone()
        
        if exists:
            print("[OK] Database 'library_db' already exists")
        else:
            cur.execute('CREATE DATABASE library_db')
            print("[OK] Database 'library_db' created successfully")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False
    
    # Step 3: Create schema
    print("\nStep 3: Creating tables...")
    try:
        with open('schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="library_db",
            user="postgres",
            password=password
        )
        cur = conn.cursor()
        cur.execute(schema_sql)
        conn.commit()
        cur.close()
        conn.close()
        
        print("[OK] All tables created successfully")
    except psycopg2.errors.DuplicateTable:
        print("[OK] Tables already exist (skipping)")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("[OK] DATABASE SETUP COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. python seed_database.py   (optional: add books)")
    print("  2. python main.py            (start API server)")
    print("  3. Open http://localhost:8000/docs")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = setup_database()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

