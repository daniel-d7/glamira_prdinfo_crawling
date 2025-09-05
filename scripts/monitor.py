"""
Monitor the scraping progress
"""
import sqlite3
import os
import json
import time
from datetime import datetime

def check_progress():
    """Check the current progress of scraping"""
    
    print("=== Glamira Scraping Progress Monitor ===")
    print(f"Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check database
    if os.path.exists("checkpoint.db"):
        conn = sqlite3.connect("checkpoint.db")
        cursor = conn.cursor()
        
        # Get overall stats
        cursor.execute("SELECT status, COUNT(*) FROM checkpoints GROUP BY status")
        status_counts = cursor.fetchall()
        
        print("📊 Database Progress:")
        total_processed = 0
        for status, count in status_counts:
            print(f"  {status}: {count}")
            total_processed += count
        
        print(f"  Total processed: {total_processed}")
        
        # Get recent activity
        cursor.execute("""
            SELECT domain, product_id, status, timestamp 
            FROM checkpoints 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        recent = cursor.fetchall()
        
        if recent:
            print("\n📝 Recent Activity:")
            for domain, product_id, status, timestamp in recent:
                ts = datetime.fromtimestamp(float(timestamp)).strftime('%H:%M:%S')
                print(f"  {ts} - {domain}/{product_id}: {status}")
        
        conn.close()
    else:
        print("📊 No database found yet (scraping not started)")
    
    # Check output files
    if os.path.exists("data/scraped/output"):
        json_files = [f for f in os.listdir("data/scraped/output") if f.endswith('.json')]
        print(f"\n📁 Output Files: {len(json_files)} JSON files created")
        
        if json_files:
            # Show sample of latest files
            json_files.sort(key=lambda x: os.path.getmtime(os.path.join("data/scraped/output", x)), reverse=True)
            print("  Latest files:")
            for i, filename in enumerate(json_files[:5]):
                filepath = os.path.join("data/scraped/output", filename)
                size = os.path.getsize(filepath)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%H:%M:%S')
                print(f"    {mtime} - {filename} ({size} bytes)")
    else:
        print("📁 No output directory found yet")
    
    # Check log file
    if os.path.exists("logs/glamira_scraping.log"):
        print("\n📋 Log file exists - check for detailed progress")
        # Show last few lines
        try:
            with open("logs/glamira_scraping.log", 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print("  Last few log entries:")
                    for line in lines[-3:]:
                        print(f"    {line.strip()}")
        except:
            pass
    
    print("\n" + "="*50)

def monitor_continuous():
    """Continuously monitor progress"""
    try:
        while True:
            check_progress()
            print("Press Ctrl+C to stop monitoring...")
            time.sleep(30)  # Check every 30 seconds
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "continuous":
        monitor_continuous()
    else:
        check_progress()
