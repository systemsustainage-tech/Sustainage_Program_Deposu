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

    # ensure surveys table
    c.execute("PRAGMA table_info(surveys)")
    if not c.fetchall():
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS surveys (
                id INTEGER PRIMARY KEY,
                company_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'draft',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()

    # create simple survey
    c.execute("INSERT INTO surveys (company_id, name, description, status) VALUES (1, ?, ?, 'active')",
              ('Departman Test Anketi', 'Departman bazlı atama testi'))
    survey_id = c.lastrowid
    logging.info(f'Created survey id: {survey_id}')

    # find a user with department
    c.execute("SELECT id, department FROM users WHERE department IS NOT NULL ORDER BY id LIMIT 1")
    row = c.fetchone()
    if not row:
        logging.info('No user with department found')
        return
    user_id, dept = row
    logging.info(f'Using user: {user_id}, {dept}')

    # ensure survey_assignments table
    c.execute("PRAGMA table_info(survey_assignments)")
    sa_cols = [col[1] for col in c.fetchall()]
    if not sa_cols:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS survey_assignments (
                id INTEGER PRIMARY KEY,
                survey_id INTEGER NOT NULL,
                assigned_to INTEGER,
                assigned_by INTEGER,
                due_date TEXT,
                status TEXT DEFAULT 'Bekliyor',
                completed_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()

    # insert assignment
    c.execute(
        """
        INSERT INTO survey_assignments (survey_id, assigned_to, assigned_by, due_date, status)
        VALUES (?, ?, ?, date('now','+10 days'), 'Bekliyor')
        """,
        (survey_id, user_id, user_id)
    )
    assign_id = c.lastrowid
    conn.commit()
    logging.info(f'Created assignment id: {assign_id}')

    # aggregate by department
    c.execute(
        """
        SELECT COALESCE(u.department,'Bilinmeyen') as department, sa.status, COUNT(*)
        FROM survey_assignments sa
        LEFT JOIN users u ON sa.assigned_to = u.id
        GROUP BY u.department, sa.status
        ORDER BY COUNT(*) DESC
        """
    )
    for r in c.fetchall():
        logging.info(f' - {r}')

    conn.close()

if __name__ == '__main__':
    main()
