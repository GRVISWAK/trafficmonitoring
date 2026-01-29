"""
Database migration script to add new anomaly fields
"""
from database import engine
from sqlalchemy import text

def migrate_database():
    """Add new columns to anomaly_logs table"""
    print("🔧 Migrating database...")
    
    with engine.connect() as conn:
        try:
            # Add new columns if they don't exist
            columns_to_add = [
                ("anomaly_type", "VARCHAR(100)"),
                ("severity", "VARCHAR(20)"),
                ("duration_seconds", "FLOAT"),
                ("impact_score", "FLOAT")
            ]
            
            for column_name, column_type in columns_to_add:
                try:
                    conn.execute(text(f"ALTER TABLE anomaly_logs ADD COLUMN {column_name} {column_type}"))
                    conn.commit()
                    print(f"✅ Added column: {column_name}")
                except Exception as e:
                    if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                        print(f"ℹ️  Column {column_name} already exists")
                    else:
                        print(f"⚠️  Error adding {column_name}: {e}")
            
            print("✅ Database migration complete!")
            
        except Exception as e:
            print(f"❌ Migration error: {e}")

if __name__ == "__main__":
    migrate_database()
