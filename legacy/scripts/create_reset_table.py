import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
if not os.path.exists(DB_PATH):
    # Fallback for local testing if needed, or just print error
    local_path = os.path.join(os.getcwd(), 'backend', 'data', 'sdg_desktop.sqlite')
    if os.path.exists(local_path):
        DB_PATH = local_path
    else:
        # One more try for C:\SUSTAINAGESERVER structure
        local_path_win = r'C:\SUSTAINAGESERVER\sdg_desktop.sqlite'
        if os.path.exists(local_path_win):
            DB_PATH = local_path_win
        else:
            print(f"Warning: Database not found at default locations. Trying: {DB_PATH}")

print(f"Using database at: {DB_PATH}")

def create_reset_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Creating password_resets table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            code VARCHAR(6) NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            is_used BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    conn.commit()
    print("Table created.")
    conn.close()

if __name__ == '__main__':
    create_reset_table()
