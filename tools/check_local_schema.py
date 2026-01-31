import sqlite3

def check_users_schema():
    conn = sqlite3.connect('sustainage.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    print("--- users table columns ---")
    for col in cursor.fetchall():
        print(col)
        
    cursor.execute("SELECT * FROM roles")
    print("\n--- roles table content ---")
    for row in cursor.fetchall():
        print(row)
        
    conn.close()

if __name__ == "__main__":
    check_users_schema()
