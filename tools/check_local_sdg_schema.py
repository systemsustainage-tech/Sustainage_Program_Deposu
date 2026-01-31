import sqlite3
import os

DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"

def check_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("Local sdg_question_bank Schema:")
    cursor.execute("PRAGMA table_info(sdg_question_bank)")
    for col in cursor.fetchall():
        print(col)
    conn.close()

if __name__ == "__main__":
    check_schema()
