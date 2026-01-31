
import sqlite3
import os
import sys

# Add parent dir to path to allow importing config if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define DB_PATH logic
if os.name == 'nt':
    DB_PATH = 'c:\\SUSTAINAGESERVER\\backend\\data\\sdg_desktop.sqlite'
else:
    # Remote server path
    DB_PATH = '/var/www/sustainage/sustainage.db'

def migrate():
    print(f"Connecting to {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        # Try alternative name just in case
        alt_path = '/var/www/sustainage/backend/data/sdg.db'
        if os.path.exists(alt_path):
            print(f"Found alternative DB at {alt_path}")
            conn = sqlite3.connect(alt_path)
        else:
             return
    else:
        conn = sqlite3.connect(DB_PATH)

    cur = conn.cursor()
    
    # Check if table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ai_feedback'")
    if cur.fetchone():
        print("Table ai_feedback already exists.")
    else:
        print("Creating ai_feedback table...")
        cur.execute("""
            CREATE TABLE ai_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER,
                user_id INTEGER,
                company_id INTEGER,
                rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES report_registry(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("Table created.")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
