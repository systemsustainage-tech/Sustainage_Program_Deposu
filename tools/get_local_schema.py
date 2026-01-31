import sqlite3
import os

DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"

def get_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ['sdg_goals', 'sdg_targets', 'sdg_indicators', 'sdg_question_bank']
    
    for table in tables:
        print(f"--- Schema for {table} ---")
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
        row = cursor.fetchone()
        if row:
            print(row[0])
        else:
            print(f"Table {table} not found!")
            
    conn.close()

if __name__ == "__main__":
    get_schema()
