import sqlite3
import os
import sys

# Common DB paths to check
DB_PATHS = [
    '/var/www/sustainage/sustainage.db',
    '/var/www/sustainage/backend/data/sdg_desktop.sqlite',
    '/var/www/sustainage/data/sdg_desktop.sqlite'
]

def find_all_dbs():
    found_dbs = []
    for path in DB_PATHS:
        if os.path.exists(path):
            found_dbs.append(path)
    
    # Search recursively
    print("Searching for .db or .sqlite files in /var/www/sustainage...")
    for root, dirs, files in os.walk('/var/www/sustainage'):
        for file in files:
            if file.endswith('.db') or file.endswith('.sqlite'):
                full_path = os.path.join(root, file)
                if full_path not in found_dbs:
                    found_dbs.append(full_path)
    return found_dbs

def inspect_logs():
    dbs = find_all_dbs()
    if not dbs:
        print("No database files found.")
        return

    print(f"Found databases: {dbs}")

    for db_path in dbs:
        print(f"\n==========================================")
        print(f"Inspecting: {db_path}")
        print(f"==========================================")
        
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            
            # List all tables
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            all_tables = [row[0] for row in cur.fetchall()]
            print(f"Total tables: {len(all_tables)}")
            print(f"Tables: {all_tables[:20]}...")

            # Check specific log tables
            target_tables = ['system_logs', 'audit_logs', 'security_logs']
            found_targets = [t for t in target_tables if t in all_tables]
            
            if found_targets:
                print(f"Found log tables: {found_targets}")
                for table in found_targets:
                    print(f"\n--- {table} ---")
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cur.fetchone()[0]
                    print(f"Row count: {count}")
                    
                    if count > 0:
                        cur.execute(f"PRAGMA table_info({table})")
                        columns = [col[1] for col in cur.fetchall()]
                        print(f"Columns: {columns}")
                        
                        sort_col = 'id' if 'id' in columns else columns[0]
                        cur.execute(f"SELECT * FROM {table} ORDER BY {sort_col} DESC LIMIT 3")
                        rows = cur.fetchall()
                        for row in rows:
                            print(row)
            else:
                print("No log tables found in this DB.")
                
            conn.close()
            
        except Exception as e:
            print(f"Error inspecting {db_path}: {e}")

if __name__ == "__main__":
    inspect_logs()
