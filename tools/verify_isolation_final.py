
import sqlite3
import os

DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"

def verify_isolation():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- Verifying SaaS Isolation Schema ---")

    # 1. Audit Logs
    try:
        cursor.execute("PRAGMA table_info(audit_logs)")
        cols = [c[1] for c in cursor.fetchall()]
        if 'company_id' in cols:
            print("✅ audit_logs has company_id")
        else:
            print("❌ audit_logs MISSING company_id")
    except Exception as e:
        print(f"Error checking audit_logs: {e}")

    # 2. System Settings
    try:
        cursor.execute("PRAGMA table_info(system_settings)")
        cols = [c[1] for c in cursor.fetchall()]
        if 'company_id' in cols:
            print("✅ system_settings has company_id")
        else:
            print("❌ system_settings MISSING company_id")
    except Exception as e:
        print(f"Error checking system_settings: {e}")

    # 3. User SDG Selections (SDG Isolation)
    try:
        cursor.execute("PRAGMA table_info(user_sdg_selections)")
        cols = [c[1] for c in cursor.fetchall()]
        if 'company_id' in cols:
            print("✅ user_sdg_selections has company_id (SDG Isolation)")
        else:
            print("❌ user_sdg_selections MISSING company_id")
    except Exception as e:
        print(f"Error checking user_sdg_selections: {e}")
        
    conn.close()

if __name__ == "__main__":
    verify_isolation()
