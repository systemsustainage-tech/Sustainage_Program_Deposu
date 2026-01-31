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

    # 1. Ensure Company 1 exists
    print("Checking for Company ID 1...")
    try:
        # Check if companies table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='companies'")
        if not cur.fetchone():
             print("companies table not found. Creating it...")
             cur.execute("CREATE TABLE IF NOT EXISTS companies (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, is_active INTEGER DEFAULT 1)")
        
        cur.execute("SELECT id, name FROM companies WHERE id=1")
        company = cur.fetchone()
        if not company:
            print("Company 1 not found. Creating it...")
            # Assuming companies table has name column.
            cur.execute("INSERT INTO companies (id, name, is_active) VALUES (1, 'Sustainage Demo', 1)")
            print("Company 1 created.")
        else:
            print(f"Company 1 exists: {company['name']}")
    except Exception as e:
        print(f"Error checking/creating company: {e}")

    # 2. Assign Company 1 to __super__
    print("Assigning Company 1 to __super__...")
    try:
        # Check if company_id column exists in users
        cur.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cur.fetchall()]
        if 'company_id' not in columns:
            print("company_id column missing in users table. Adding it...")
            try:
                cur.execute("ALTER TABLE users ADD COLUMN company_id INTEGER")
                print("Column added.")
            except Exception as e:
                print(f"Error adding column: {e}")
                return

        cur.execute("UPDATE users SET company_id=1 WHERE username='__super__'")
        if cur.rowcount > 0:
            print(f"Updated company_id for __super__. Rows affected: {cur.rowcount}")
        else:
            print("User __super__ not found or no change needed.")
            
        # Verify
        cur.execute("SELECT id, username, company_id FROM users WHERE username='__super__'")
        user = cur.fetchone()
        if user:
            print(f"User: {user['username']}, Company ID: {user['company_id']}")
    except Exception as e:
        print(f"Error updating user: {e}")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    assign_company()
