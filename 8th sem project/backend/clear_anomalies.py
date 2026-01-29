"""
Clear all existing anomalies from database
"""
from database import SessionLocal, AnomalyLog

db = SessionLocal()
try:
    count = db.query(AnomalyLog).count()
    print(f"Current anomalies in database: {count}")
    
    # Delete all
    db.query(AnomalyLog).delete()
    db.commit()
    
    print(f"✅ Cleared all anomalies from database")
    print(f"✅ Database is now ready for fresh anomaly detection")
    print(f"\n💡 Now run simulation or test endpoints to see live anomaly detection with resolution suggestions!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
