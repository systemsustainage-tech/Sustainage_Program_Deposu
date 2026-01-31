
import sys
import os
import sqlite3
import logging

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from backend.modules.esg.esg_manager import ESGManager

# Setup logging
logging.basicConfig(level=logging.INFO)

def check_esg_schema():
    print("Initializing ESGManager...")
    manager = ESGManager()
    
    print("Checking database schema...")
    conn = sqlite3.connect(manager.db_path)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(esg_scores)")
    columns = [info[1] for info in cursor.fetchall()]
    
    print(f"Columns in esg_scores: {columns}")
    
    if 'year' in columns and 'quarter' in columns:
        print("SUCCESS: 'year' and 'quarter' columns exist.")
    else:
        print("FAILURE: Missing columns.")
        
    conn.close()

if __name__ == "__main__":
    check_esg_schema()
