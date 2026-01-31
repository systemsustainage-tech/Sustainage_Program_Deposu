import sqlite3

DB_PATH = 'backend/data/sdg_desktop.sqlite'

def check_pk():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(system_settings)")
    columns = cursor.fetchall()
    print("Columns:")
    for col in columns:
        print(col)
        
    print("\nPrimary Key columns:")
    pk_cols = [col[1] for col in columns if col[5] > 0]
    print(pk_cols)
    conn.close()

if __name__ == "__main__":
    check_pk()
