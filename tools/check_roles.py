import logging
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

conn = sqlite3.connect('sdg.db')
cur = conn.cursor()

cur.execute("PRAGMA table_info(roles)")
columns = [row[1] for row in cur.fetchall()]

logging.info('Roles Columns:')
for col in columns:
    logging.info(f'  {col}')

logging.info('\nRoles Data:')
cur.execute("SELECT * FROM roles LIMIT 5")
rows = cur.fetchall()
for row in rows:
    logging.info(f'  {row}')

conn.close()
