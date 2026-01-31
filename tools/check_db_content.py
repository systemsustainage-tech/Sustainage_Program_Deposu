import sqlite3
import os

db_paths = [
    'c:\\SUSTAINAGESERVER\\backend\\sustainage.db',
    'c:\\SUSTAINAGESERVER\\sustainage.db'
]

for db_path in db_paths:
    print(f"\nChecking DB at: {db_path}")
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # List tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [t[0] for t in cursor.fetchall()]
            print(f"Tables: {tables}")
            
            if 'tsrs_indicators' in tables:
                cursor.execute("SELECT id, code, title FROM tsrs_indicators LIMIT 5")
                indicators = cursor.fetchall()
                print("First 5 indicators:")
                for i in indicators:
                    print(i)
            else:
                print("tsrs_indicators table NOT found")

            if 'map_tsrs_esrs' in tables:
                 cursor.execute("SELECT count(*) FROM map_tsrs_esrs")
                 count = cursor.fetchone()[0]
                 print(f"map_tsrs_esrs count: {count}")
            
            conn.close()
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("File does not exist")
