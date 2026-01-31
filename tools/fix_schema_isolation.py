
import sqlite3
import os

DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"

def list_sdg_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%sdg%'")
    tables = cursor.fetchall()
    print("SDG Tables found:")
    for t in tables:
        print(f"- {t[0]}")
    conn.close()

def add_company_id_to_audit_logs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(audit_logs)")
        cols = [c[1] for c in cursor.fetchall()]
        if 'company_id' in cols:
            print("audit_logs already has company_id")
        else:
            print("Adding company_id to audit_logs...")
            cursor.execute("ALTER TABLE audit_logs ADD COLUMN company_id INTEGER DEFAULT NULL")
            conn.commit()
            print("Added company_id to audit_logs.")
    except Exception as e:
        print(f"Error updating audit_logs: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    list_sdg_tables()
    add_company_id_to_audit_logs()
