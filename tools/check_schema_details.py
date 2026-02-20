import sqlite3
import os

DB_PATH = 'c:/SUSTAINAGESERVER/backend/data/sdg_desktop.sqlite'
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
tables = ['users','companies','roles','permissions','audit_logs','system_settings','translations','company_info']

for t in tables:
    try:
        cur.execute(f"PRAGMA table_info({t})")
        cols = [r[1] for r in cur.fetchall()]
        print(f"{t}: {cols}")
        if 'company_id' in cols:
            print(f"  -> HAS company_id")
        else:
            print(f"  -> MISSING company_id")
    except Exception as e:
        print(f"{t}: Error {e}")
