import sqlite3
import os

DB_PATH = os.path.join('backend', 'data', 'sdg_desktop.sqlite')

def inspect_auth():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tables = ['users', 'roles', 'permissions', 'role_permissions', 'user_roles']
    
    print(f"Inspecting Auth Tables in {DB_PATH}...\n")
    
    for table in tables:
        print(f"--- Table: {table} ---")
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            if not columns:
                print("  (Table does not exist)")
            else:
                for col in columns:
                    print(f"  {col[1]} ({col[2]})")
        except Exception as e:
            print(f"  Error: {e}")
        print("")

    conn.close()

if __name__ == "__main__":
    inspect_auth()
