import sqlite3
import os

DB_PATH = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("UPDATE regulations SET compliance_deadline = '2026-03-15' WHERE code = 'EU-CBAM'")
conn.commit()
print("Updated EU-CBAM deadline to 2026-03-15")
conn.close()
