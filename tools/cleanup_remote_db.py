import paramiko

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

REMOTE_SCRIPT = """
import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
JUNK_DB_PATH = '/var/www/sustainage/sustainage.db'

# 1. Drop backup table
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DROP TABLE IF EXISTS survey_responses_old_backup")
        print("Dropped table: survey_responses_old_backup")
        conn.commit()
    except Exception as e:
        print(f"Error dropping table: {e}")
    conn.close()

# 2. Delete junk DB file
if os.path.exists(JUNK_DB_PATH):
    try:
        os.remove(JUNK_DB_PATH)
        print(f"Deleted junk file: {JUNK_DB_PATH}")
    except Exception as e:
        print(f"Error deleting file: {e}")
else:
    print(f"File not found (already clean): {JUNK_DB_PATH}")
"""

def cleanup_db():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        
        print("Executing remote cleanup script...")
        stdin, stdout, stderr = ssh.exec_command("python3 -c \"" + REMOTE_SCRIPT.replace('"', '\\"') + "\"")
        print(stdout.read().decode())
        
        ssh.close()
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    cleanup_db()
