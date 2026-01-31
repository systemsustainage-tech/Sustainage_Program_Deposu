import sqlite3
import os

DB_PATH = os.path.join("c:\\SUSTAINAGESERVER", "sustainage.db")

def list_tables():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in database:")
        for table in tables:
            print(f"- {table[0]}")
            
            # Eğer company ile ilgili bir tablo varsa sütunlarını da yazdıralım
            if 'company' in table[0] or 'firma' in table[0]:
                cursor.execute(f"PRAGMA table_info({table[0]})")
                columns = cursor.fetchall()
                print(f"  Columns in {table[0]}: {[col[1] for col in columns]}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_tables()
