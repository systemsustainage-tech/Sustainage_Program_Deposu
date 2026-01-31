import sqlite3
import os

DB_PATH = '/var/www/sustainage/sustainage.db'

def diagnose():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        print(f"Connected to {DB_PATH}")
        
        # Check users table schema
        print("\n--- Users Table Schema ---")
        cur.execute("PRAGMA table_info(users)")
        columns = cur.fetchall()
        for col in columns:
            print(f"{col['cid']}: {col['name']} ({col['type']})")

        # Check users
        print("\n--- Checking Users ---")
        try:
            # Dynamically build query based on columns
            col_names = [col['name'] for col in columns]
            query_cols = ['id', 'username', 'is_active']
            if 'password' in col_names:
                query_cols.append('password')
            elif 'password_hash' in col_names:
                query_cols.append('password_hash')
            
            query = f"SELECT {', '.join(query_cols)} FROM users WHERE username = 'test_user'"
            cur.execute(query)
            user = cur.fetchone()
        except Exception as e:
            print(f"Error querying user: {e}")
            user = None

        if user:
            print(f"Found test_user: ID={user['id']}, Active={user['is_active']}")
            # Check role
            cur.execute("""
                SELECT r.name 
                FROM roles r 
                JOIN user_roles ur ON r.id = ur.role_id 
                WHERE ur.user_id = ?
            """, (user['id'],))
            role = cur.fetchone()
            if role:
                print(f"Role: {role['name']}")
            else:
                print("Role: NONE")
        else:
            print("test_user NOT FOUND")
            
        # Check waste_generation table
        print("\n--- Checking Tables ---")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='waste_generation'")
        table = cur.fetchone()
        if table:
            print("waste_generation table EXISTS")
            # Check columns
            cur.execute("PRAGMA table_info(waste_generation)")
            columns = cur.fetchall()
            col_names = [col['name'] for col in columns]
            print(f"Columns: {col_names}")
        else:
            print("waste_generation table MISSING")
            
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    diagnose()
