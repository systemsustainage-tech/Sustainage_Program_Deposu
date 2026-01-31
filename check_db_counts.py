import sqlite3
import os

db_path = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"
print(f"Checking DB: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT count(*) FROM sdg_goals")
    print(f"Goals count: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT count(*) FROM sdg_targets")
    print(f"Targets count: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT count(*) FROM sdg_indicators")
    print(f"Indicators count: {cursor.fetchone()[0]}")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
