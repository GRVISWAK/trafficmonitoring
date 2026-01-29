"""
Migration: Add is_simulation column to APILog and AnomalyLog tables
This enforces strict separation between live and simulation data.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "api_logs.db"

def migrate():
    print("Starting migration to add is_simulation column...")
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Add is_simulation to api_logs table
        print("Adding is_simulation to api_logs table...")
        cursor.execute("""
            ALTER TABLE api_logs 
            ADD COLUMN is_simulation BOOLEAN DEFAULT 0
        """)
        print("  Column added to api_logs")
        
        # Add is_simulation to anomaly_logs table
        print("Adding is_simulation to anomaly_logs table...")
        cursor.execute("""
            ALTER TABLE anomaly_logs 
            ADD COLUMN is_simulation BOOLEAN DEFAULT 0
        """)
        print("  Column added to anomaly_logs")
        
        # Create indexes for better query performance
        print("Creating indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_api_logs_simulation 
            ON api_logs(is_simulation)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_anomaly_logs_simulation 
            ON anomaly_logs(is_simulation)
        """)
        print("  Indexes created")
        
        conn.commit()
        print("\nMigration completed successfully!")
        print("All existing records defaulted to is_simulation=False (live mode)")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column already exists, skipping migration")
        else:
            print(f"Error during migration: {e}")
            conn.rollback()
            raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
