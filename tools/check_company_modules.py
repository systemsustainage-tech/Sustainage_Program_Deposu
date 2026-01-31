import logging
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

conn = sqlite3.connect('sdg.db')
cur = conn.cursor()

logging.info('Firma 1 Modül Atamaları:')
cur.execute('SELECT company_id, module_id, is_enabled FROM company_modules WHERE company_id = 1')
assignments = cur.fetchall()
for assignment in assignments:
    status = "Açık" if assignment[2] else "Kapalı"
    logging.info(f'  Modül ID {assignment[1]}: {status}')

logging.info('\nModül Detayları:')
cur.execute('''
    SELECT m.module_name, cm.is_enabled 
    FROM modules m 
    LEFT JOIN company_modules cm ON m.id = cm.module_id AND cm.company_id = 1
    ORDER BY m.display_order
''')
modules = cur.fetchall()
for module in modules:
    status = "Açık" if module[1] else "Kapalı"
    logging.info(f'  {module[0]}: {status}')

conn.close()
