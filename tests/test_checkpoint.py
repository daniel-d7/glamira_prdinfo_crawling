"""
Quick test for checkpoint database functionality
"""
import sqlite3
import os

def check_checkpoint_db():
    """Check if checkpoint database exists and show stats"""
    db_path = "checkpoint.db"
    
    print("🔍 Checking checkpoint database...")
    
    if not os.path.exists(db_path):
        print("❌ No checkpoint database found.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='checkpoints'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            print("❌ Checkpoints table doesn't exist.")
            conn.close()
            return False
        
        # Get total count
        cursor.execute('SELECT COUNT(*) FROM checkpoints')
        total = cursor.fetchone()[0]
        
        # Get stats by status
        cursor.execute('SELECT status, COUNT(*) FROM checkpoints GROUP BY status')
        stats = cursor.fetchall()
        
        conn.close()
        
        print(f"✅ Checkpoint database exists with {total} entries")
        
        if stats:
            print("📊 Status breakdown:")
            for status, count in stats:
                print(f"  {status}: {count}")
        
        return total > 0
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

if __name__ == "__main__":
    check_checkpoint_db()
