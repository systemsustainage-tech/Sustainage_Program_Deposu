import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}, checking config...")
    # Try to find where the app thinks the DB is
    try:
        from config.settings import get_db_path
        db_path = get_db_path()
    except:
        pass

print(f"Checking database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(sdg_indicators)")
    columns = cursor.fetchall()
    print("Columns in sdg_indicators:")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
