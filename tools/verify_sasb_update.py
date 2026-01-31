
import sys
import os
import sqlite3

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from modules.sasb.sasb_manager import SASBManager
from config.database import DB_PATH

def verify_sasb():
    print("Initializing SASB Manager...")
    manager = SASBManager()
    
    print("Loading sector data...")
    success = manager.load_sector_data()
    
    if success:
        print("Data load successful.")
    else:
        print("Data load failed.")
        return

    # Verify IFRS-S2 topic
    conn = sqlite3.connect(manager.db_path)
    cursor = conn.cursor()
    
    print("\nVerifying IFRS-S2 Topic:")
    cursor.execute("SELECT * FROM sasb_disclosure_topics WHERE topic_code = 'IFRS-S2'")
    row = cursor.fetchone()
    if row:
        print(f"FOUND: {row}")
    else:
        print("NOT FOUND: IFRS-S2 topic")
        
    print("\nVerifying IFRS-S2 Metrics:")
    cursor.execute("""
        SELECT m.metric_code, m.metric_name 
        FROM sasb_metrics m
        JOIN sasb_disclosure_topics t ON m.disclosure_topic_id = t.id
        WHERE t.topic_code = 'IFRS-S2'
    """)
    rows = cursor.fetchall()
    if rows:
        for r in rows:
            print(f"FOUND METRIC: {r}")
    else:
        print("NOT FOUND: IFRS-S2 metrics")

    conn.close()

if __name__ == "__main__":
    verify_sasb()
