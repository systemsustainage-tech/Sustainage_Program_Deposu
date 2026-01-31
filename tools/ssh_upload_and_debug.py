import paramiko
import logging
import sys

# Configuration
HOST = '72.62.150.207'
PORT = 22
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        
        py_script = """
import os
import sqlite3

DB_PATH = os.path.join('/var/www/sustainage', 'backend', 'data', 'sdg_desktop.sqlite')
print(f'DB_PATH: {DB_PATH}')

if not os.path.exists(DB_PATH):
    print('DB file does not exist')
else:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute('CREATE TABLE IF NOT EXISTS sdg_goals (id INTEGER PRIMARY KEY AUTOINCREMENT, code INTEGER UNIQUE, title_tr TEXT, created_at TEXT)')
        cur.execute('SELECT COUNT(*) FROM sdg_goals')
        count = cur.fetchone()[0]
        print(f'Initial sdg_goals count: {count}')
        if count == 0:
            goals_data = [
                (1, "Yoksulluğa Son"),
                (2, "Açlığa Son"),
                (3, "Sağlık ve Kaliteli Yaşam"),
                (4, "Nitelikli Eğitim"),
                (5, "Toplumsal Cinsiyet Eşitliği"),
                (6, "Temiz Su ve Sanitasyon"),
                (7, "Erişilebilir ve Temiz Enerji"),
                (8, "İnsana Yakışır İş ve Ekonomik Büyüme"),
                (9, "Sanayi, Yenilikçilik ve Altyapı"),
                (10, "Eşitsizliklerin Azaltılması"),
                (11, "Sürdürülebilir Şehirler ve Topluluklar"),
                (12, "Sorumlu Üretim ve Tüketim"),
                (13, "İklim Eylemi"),
                (14, "Sudaki Yaşam"),
                (15, "Karasal Yaşam"),
                (16, "Barış, Adalet ve Güçlü Kurumlar"),
                (17, "Amaçlar için Ortaklıklar"),
            ]
            for g in goals_data:
                cur.execute('INSERT OR IGNORE INTO sdg_goals (code, title_tr) VALUES (?, ?)', (g[0], g[1]))
            conn.commit()
            print('Inserted 17 SDG goals.')
        cur.execute('SELECT COUNT(*) FROM sdg_goals')
        final_count = cur.fetchone()[0]
        print(f'Final sdg_goals count: {final_count}')
        cur.execute('SELECT id, code, title_tr FROM sdg_goals ORDER BY id LIMIT 5')
        rows = cur.fetchall()
        print('First goals:')
        for r in rows:
            print(r)
    except Exception as e:
        print(f'Error updating sdg_goals: {e}')
    finally:
        conn.close()
"""
        # Upload script
        sftp = client.open_sftp()
        with sftp.file('/var/www/sustainage/debug_imports.py', 'w') as f:
            f.write(py_script)
        sftp.chmod('/var/www/sustainage/debug_imports.py', 0o755)
        sftp.close()
        
        logging.info("Running debug script on server...")
        stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/debug_imports.py")
        out = stdout.read().decode()
        err = stderr.read().decode()
        logging.info(f"Output:\n{out}")
        if err:
            logging.info(f"Error:\n{err}")

        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
