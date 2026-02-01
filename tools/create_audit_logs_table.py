import sqlite3
import os

db_path = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'

def create_audit_logs_table():
    if not os.path.exists(os.path.dirname(db_path)):
        print(f"Directory not found: {os.path.dirname(db_path)}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    sql = """
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        user_id INTEGER,
        action TEXT NOT NULL,
        resource_type TEXT NOT NULL,
        resource_id TEXT,
        details TEXT,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        cursor.execute(sql)
        conn.commit()
        print(f"Table 'audit_logs' created successfully in {db_path}.")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_audit_logs_table()
