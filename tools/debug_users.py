import logging
import os
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main() -> None:
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'sdg_desktop.sqlite')
    logging.info('DB path:', db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute('SELECT id, username, display_name, email, role, is_active FROM users')
        rows = cur.fetchall()
        if not rows:
            logging.info('No users found.')
        else:
            logging.info('Users:')
            for r in rows:
                logging.info(r)
    except Exception as e:
        logging.error('Error querying users:', e)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
