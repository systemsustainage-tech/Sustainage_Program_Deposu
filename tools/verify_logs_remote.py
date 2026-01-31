import sqlite3
import os

def check_logs():
    db_path = os.path.join(os.getcwd(), 'backend', 'data', 'sdg_desktop.sqlite')
    print(f"Checking DB at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='system_logs'")
        exists = cursor.fetchone()[0]
        print(f"Table 'system_logs' exists: {exists}")
        
        if exists:
            cursor.execute("SELECT count(*) FROM system_logs")
            count = cursor.fetchone()[0]
            print(f"Log count: {count}")
            
            if count > 0:
                print("Last 5 logs:")
                cursor.execute("SELECT * FROM system_logs ORDER BY id DESC LIMIT 5")
                for row in cursor.fetchall():
                    print(row)
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_logs()
