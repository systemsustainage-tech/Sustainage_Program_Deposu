#!/usr/bin/env python3
import logging
import os
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB = os.path.join(BASE, 'data', 'sdg_desktop.sqlite')

def main() -> None:
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # find a user with department
    c.execute("SELECT id, department FROM users WHERE department IS NOT NULL ORDER BY id LIMIT 1")
    row = c.fetchone()
    if not row:
        logging.info('No user with department found')
        return
    user_id, dept = row
    logging.info(f'Using user: {user_id} {dept}')
    # insert a task assigned to this user
    c.execute(
        """
        INSERT INTO tasks (company_id, title, description, priority, status, due_date, created_by, assigned_to, related_item, related_item_type)
        VALUES (1, ?, ?, 'Orta', 'Bekliyor', date('now','+7 days'), ?, ?, ?, 'Test')
        """,
        (f'Test Departman Görevi - {dept}', 'Departman link testi', user_id, user_id, 'TEST')
    )
    task_id = c.lastrowid
    conn.commit()
    logging.info(f'Created task id: {task_id}')
    # aggregate by department
    c.execute(
        """
        SELECT COALESCE(u.department,'Bilinmeyen') as department, COUNT(*)
        FROM tasks t LEFT JOIN users u ON t.assigned_to = u.id
        GROUP BY u.department ORDER BY COUNT(*) DESC
        """
    )
    for r in c.fetchall():
        logging.info(f' - {r}')
    conn.close()

if __name__ == '__main__':
    main()
