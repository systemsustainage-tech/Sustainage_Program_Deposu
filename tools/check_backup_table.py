import paramiko

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

REMOTE_SCRIPT = """
import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM survey_responses_old_backup")
        count = cursor.fetchone()[0]
        print(f"survey_responses_old_backup count: {count}")
    except Exception as e:
        print(f"Error: {e}")
    conn.close()
"""

def check_backup_table():
    print(f"Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)
    
    stdin, stdout, stderr = ssh.exec_command("python3 -c \"" + REMOTE_SCRIPT.replace('"', '\\"') + "\"")
    print(stdout.read().decode())
    ssh.close()

if __name__ == "__main__":
    check_backup_table()
