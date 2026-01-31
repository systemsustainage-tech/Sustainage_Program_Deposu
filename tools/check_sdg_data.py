import sqlite3
import os

DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"

def check_sdg_data():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- SDG Responses ---")
    try:
        cursor.execute("SELECT * FROM responses ORDER BY created_at DESC LIMIT 5")
        rows = cursor.fetchall()
        
        # Get column names
        names = [description[0] for description in cursor.description]
        print(f"Columns: {names}")

        if not rows:
            print("No rows found in 'responses' table.")
        for row in rows:
            print(row)
    except Exception as e:
        print(f"Error querying responses: {e}")
        
    print("\n--- SDG Selections ---")
    try:
        cursor.execute("SELECT * FROM selections LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    except Exception as e:
        print(f"Error querying selections: {e}")

    print("\n--- SDG Indicators ---")
    try:
        cursor.execute("SELECT count(*) FROM sdg_indicators")
        count = cursor.fetchone()[0]
        print(f"Total indicators: {count}")
        if count > 0:
            cursor.execute("SELECT * FROM sdg_indicators LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                print(row)
    except Exception as e:
        print(f"Error querying indicators: {e}")

    print("\n--- SDG Targets ---")
    try:
        cursor.execute("SELECT count(*) FROM sdg_targets")
        count = cursor.fetchone()[0]
        print(f"Total targets: {count}")
        if count > 0:
            cursor.execute("SELECT * FROM sdg_targets LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                print(row)
    except Exception as e:
        print(f"Error querying targets: {e}")

    print("\n--- SDG Goals ---")
    try:
        cursor.execute("SELECT count(*) FROM sdg_goals")
        count = cursor.fetchone()[0]
        print(f"Total goals: {count}")
        if count > 0:
            cursor.execute("SELECT * FROM sdg_goals LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                print(row)
    except Exception as e:
        print(f"Error querying goals: {e}")

    conn.close()

if __name__ == "__main__":
    check_sdg_data()
