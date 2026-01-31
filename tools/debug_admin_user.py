import sqlite3
import os
import sys

# Define path directly as on remote server
DB_PATH = '/var/www/sustainage/sustainage.db'

def check_admin():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print(f"--- Checking user 'admin' in {DB_PATH} ---")
        cursor.execute("SELECT * FROM users WHERE username='admin'")
        columns = [description[0] for description in cursor.description]
        row = cursor.fetchone()
        
        if row:
            for col, val in zip(columns, row):
                print(f"{col}: {val}")
        else:
            print("User 'admin' NOT FOUND.")
            
        print("\n--- Checking user '__super__' ---")
        cursor.execute("SELECT * FROM users WHERE username='__super__'")
        row = cursor.fetchone()
        if row:
             for col, val in zip(columns, row):
                print(f"{col}: {val}")
        else:
            print("User '__super__' NOT FOUND.")

        print("\n--- Checking user_roles ---")
        cursor.execute("""
            SELECT u.username, r.name 
            FROM user_roles ur 
            JOIN users u ON u.id = ur.user_id 
            JOIN roles r ON r.id = ur.role_id
        """)
        for row in cursor.fetchall():
            print(f"User: {row[0]}, Role: {row[1]}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_admin()
