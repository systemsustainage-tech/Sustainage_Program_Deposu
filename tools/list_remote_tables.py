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
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("--- Remote Tables ---")
    for t in tables:
        print(t[0])
    conn.close()
else:
    print(f"DB not found at {DB_PATH}")
"""

def list_tables():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        
        print("Executing remote script...")
        stdin, stdout, stderr = ssh.exec_command("python3 -c \"" + REMOTE_SCRIPT.replace('"', '\\"') + "\"")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Error: {err}")
            
        ssh.close()
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    list_tables()
