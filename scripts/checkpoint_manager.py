"""
Utility script to manage checkpoint database
"""
import sqlite3
import os
from datetime import datetime

def show_checkpoint_stats():
    """Show current checkpoint statistics"""
    db_path = "checkpoint.db"
    
    if not os.path.exists(db_path):
        print("❌ No checkpoint database found.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get total counts by status
        cursor.execute('SELECT status, COUNT(*) FROM checkpoints GROUP BY status')
        stats = cursor.fetchall()
        
        # Get total count
        cursor.execute('SELECT COUNT(*) FROM checkpoints')
        total = cursor.fetchone()[0]
        
        # Get recent entries
        cursor.execute('''
            SELECT domain, product_id, status, timestamp 
            FROM checkpoints 
            ORDER BY timestamp DESC 
            LIMIT 5
        ''')
        recent = cursor.fetchall()
        
        conn.close()
        
        print("📊 Checkpoint Database Statistics")
        print("=" * 40)
        print(f"Total entries: {total}")
        print()
        
        if stats:
            print("Status breakdown:")
            for status, count in stats:
                print(f"  {status}: {count}")
        
        if recent:
            print("\nRecent entries:")
            for domain, product_id, status, timestamp in recent:
                print(f"  {domain}/{product_id}: {status} at {timestamp}")
        
        return total > 0
        
    except Exception as e:
        print(f"❌ Error reading checkpoint database: {e}")
        return False

def clear_checkpoint_database():
    """Clear all checkpoints from the database"""
    db_path = "checkpoint.db"
    
    if not os.path.exists(db_path):
        print("❌ No checkpoint database found.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get count before clearing
        cursor.execute('SELECT COUNT(*) FROM checkpoints')
        count_before = cursor.fetchone()[0]
        
        if count_before == 0:
            print("📭 Checkpoint database is already empty.")
            conn.close()
            return
        
        # Clear all checkpoints
        cursor.execute('DELETE FROM checkpoints')
        conn.commit()
        conn.close()
        
        print(f"✅ Cleared {count_before} entries from checkpoint database.")
        print("🔄 Ready for fresh scraping run.")
        
    except Exception as e:
        print(f"❌ Error clearing checkpoint database: {e}")

def backup_checkpoint_database():
    """Create a backup of the checkpoint database"""
    db_path = "checkpoint.db"
    
    if not os.path.exists(db_path):
        print("❌ No checkpoint database found.")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"logs/checkpoint_backup_{timestamp}.db"
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Checkpoint database backed up to: {backup_path}")
    except Exception as e:
        print(f"❌ Error creating backup: {e}")

def main():
    print("🗄️ Checkpoint Database Manager")
    print("=" * 40)
    
    options = {
        "1": ("Show statistics", show_checkpoint_stats),
        "2": ("Clear database", clear_checkpoint_database),
        "3": ("Create backup", backup_checkpoint_database),
    }
    
    print("\nOptions:")
    for key, (description, _) in options.items():
        print(f"  {key}. {description}")
    print("  q. Quit")
    
    while True:
        choice = input("\nSelect option (1-3, q): ").strip().lower()
        
        if choice == 'q':
            print("👋 Goodbye!")
            break
        elif choice in options:
            description, function = options[choice]
            print(f"\n🔄 {description}...")
            function()
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()
