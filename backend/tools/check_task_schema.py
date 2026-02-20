import sqlite3
import os

DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"

def check_schema():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(task_attachments)")
        columns = cursor.fetchall()
        if not columns:
            print("Table task_attachments does not exist.")
        else:
            print("Table task_attachments columns:")
            for col in columns:
                print(col)
                
        cursor.execute("PRAGMA table_info(tasks)")
        columns = cursor.fetchall()
        if not columns:
            print("Table tasks does not exist.")
        else:
            print("Table tasks columns:")
            for col in columns:
                print(col)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_schema()
