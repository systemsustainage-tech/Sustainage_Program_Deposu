import sqlite3
import os

db_path = 'c:/SUSTAINAGESERVER/sustainage.db'

def check_audit_log():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_logs'")
    table = cursor.fetchone()
    
    if table:
        print("Table 'audit_logs' exists.")
        # Get columns
        cursor.execute("PRAGMA table_info(audit_logs)")
        columns = cursor.fetchall()
        for col in columns:
            print(col)
    else:
        print("Table 'audit_logs' does NOT exist.")
    
    conn.close()

if __name__ == "__main__":
    check_audit_log()
