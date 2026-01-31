import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def assign_company():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        # Get user id
        cur.execute("SELECT id FROM users WHERE username='__super__'")
        row = cur.fetchone()
        if not row:
            print("User __super__ not found.")
            return
        user_id = row[0]
        print(f"Found __super__ ID: {user_id}")

        # Check user_companies table
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_companies'")
        if not cur.fetchone():
            print("user_companies table missing. Creating it...")
            cur.execute("""
                CREATE TABLE user_companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    company_id INTEGER NOT NULL,
                    is_primary INTEGER DEFAULT 0,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(company_id) REFERENCES companies(id)
                )
            """)

        # Check existing assignment
        cur.execute("SELECT * FROM user_companies WHERE user_id=? AND company_id=1", (user_id,))
        if cur.fetchone():
            print("User already assigned to Company 1. Updating to primary...")
            cur.execute("UPDATE user_companies SET is_primary=1 WHERE user_id=? AND company_id=1", (user_id,))
        else:
            print("Assigning Company 1 to user...")
            cur.execute("INSERT INTO user_companies (user_id, company_id, is_primary) VALUES (?, 1, 1)", (user_id,))

        print("Assignment complete.")
        
    except Exception as e:
        print(f"Error: {e}")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    assign_company()
