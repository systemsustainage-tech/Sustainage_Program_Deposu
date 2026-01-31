#!/usr/bin/env python3
import logging
import os
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB = os.path.join(BASE, 'data', 'sdg_desktop.sqlite')

def main() -> None:
    logging.info('DB path:', DB)
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # 1) Departmanlar
    logging.info('\n[DEPARTMANLAR]')
    try:
        c.execute("PRAGMA table_info(departments)")
        cols = c.fetchall()
        logging.info('departments columns:', [col[1] for col in cols])
        c.execute("SELECT COUNT(*), MIN(name), MAX(name) FROM departments")
        logging.info('count/min/max:', c.fetchone())
        c.execute("SELECT id, name, code, is_active FROM departments ORDER BY name LIMIT 20")
        for row in c.fetchall():
            logging.info(' -', row)
    except Exception as e:
        logging.info('[ERR] departments:', e)

    # 2) Kullanıcı departman alanı ve örnek
    logging.info('\n[USERS]')
    try:
        c.execute("PRAGMA table_info(users)")
        ucols = [col[1] for col in c.fetchall()]
        logging.info('users columns:', ucols)
        c.execute("SELECT COUNT(*), COUNT(department) FROM users")
        logging.info('user_count/with_department:', c.fetchone())
        c.execute("SELECT id, username, department FROM users WHERE department IS NOT NULL ORDER BY id LIMIT 10")
        for row in c.fetchall():
            logging.info(' -', row)
    except Exception as e:
        logging.info('[ERR] users:', e)

    # 3) Görevler ve departman ilişkisi: tasks -> users.department
    logging.info('\n[GOREVLER]')
    try:
        c.execute("PRAGMA table_info(tasks)")
        tcols = [col[1] for col in c.fetchall()]
        logging.info('tasks columns:', tcols)
        c.execute("""
            SELECT COALESCE(u.department, 'Bilinmeyen') as department, COUNT(*)
            FROM tasks t
            LEFT JOIN users u ON t.assigned_to = u.id
            GROUP BY u.department
            ORDER BY COUNT(*) DESC
        """)
        for row in c.fetchall():
            logging.info(' -', row)
        c.execute("SELECT id, title, assigned_to FROM tasks ORDER BY id DESC LIMIT 5")
        for row in c.fetchall():
            logging.info('   task:', row)
    except Exception as e:
        logging.info('[ERR] tasks:', e)

    # 4) Anketler ve departman ilişkisi: user_surveys veya survey_assignments
    logging.info('\n[ANKETLER]')
    try:
        c.execute("PRAGMA table_info(user_surveys)")
        us_cols = [col[1] for col in c.fetchall()]
        if us_cols:
            logging.info('user_surveys columns:', us_cols)
            c.execute("""
                SELECT COALESCE(u.department,'Bilinmeyen') as department, us.status, COUNT(*)
                FROM user_surveys us
                LEFT JOIN users u ON us.user_id = u.id
                GROUP BY u.department, us.status
                ORDER BY COUNT(*) DESC
            """)
            for row in c.fetchall():
                logging.info(' -', row)
        else:
            logging.info('user_surveys tablosu yok')
    except Exception as e:
        logging.info('[INFO] user_surveys yok:', e)

    try:
        c.execute("PRAGMA table_info(survey_assignments)")
        sa_cols = [col[1] for col in c.fetchall()]
        if sa_cols:
            logging.info('survey_assignments columns:', sa_cols)
            c.execute("""
                SELECT COALESCE(u.department,'Bilinmeyen') as department, sa.status, COUNT(*)
                FROM survey_assignments sa
                LEFT JOIN users u ON sa.assigned_to = u.id
                GROUP BY u.department, sa.status
                ORDER BY COUNT(*) DESC
            """)
            rows = c.fetchall()
            if rows:
                for r in rows:
                    logging.info(' -', r)
            else:
                logging.info('survey_assignments boş veya departman eşleşmesi yok')
        else:
            logging.info('survey_assignments tablosu yok')
    except Exception as e:
        logging.info('[INFO] survey_assignments yok:', e)

    conn.close()

if __name__ == '__main__':
    main()
