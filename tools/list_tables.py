import sqlite3

DB_PATH = r'c:\SUSTAINAGESERVER\sustainage.db'

def list_tables():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in DB:")
        for t in tables:
            print(t[0])
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_tables()
