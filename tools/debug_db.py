import sqlite3
import os

DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"

print(f"Checking DB: {DB_PATH}")

def check_sdg_indicator():
    print("\n--- SDG Indicators (id=1) ---")
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, code, title_tr FROM sdg_indicators WHERE id=1")
        row = cursor.fetchone()
        if row:
            print(f"Found: {row}")
        else:
            print("Not Found: id=1")
        
        print("--- Recent SDG Responses ---")
        cursor.execute("SELECT * FROM responses ORDER BY created_at DESC LIMIT 5")
        rows = cursor.fetchall()
        for r in rows:
            print(r)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn: conn.close()

def check_iirc_reports():
    print("\n--- IIRC Reports ---")
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM integrated_reports ORDER BY created_at DESC LIMIT 5")
        rows = cursor.fetchall()
        for r in rows:
            print(r)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn: conn.close()

def check_csrd_materiality():
    print("\n--- CSRD Materiality ---")
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM double_materiality_assessment ORDER BY created_at DESC LIMIT 5")
        rows = cursor.fetchall()
        for r in rows:
            print(r)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        check_sdg_indicator()
        check_iirc_reports()
        check_csrd_materiality()
    else:
        print(f"File not found: {DB_PATH}")
