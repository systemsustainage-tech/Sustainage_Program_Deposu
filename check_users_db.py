import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'backend', 'data', 'sdg_desktop.sqlite')

def check_users_schema():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("Checking 'users' table columns:")
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        has_email = False
        for col in columns:
            print(col)
            if col[1] == 'email':
                has_email = True
        
        if not has_email:
            print("\nWARNING: 'email' column is MISSING in 'users' table.")
        else:
            print("\n'email' column exists.")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_users_schema()
