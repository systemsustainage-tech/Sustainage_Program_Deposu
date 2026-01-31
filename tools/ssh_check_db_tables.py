
import paramiko
import sys

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def check_tables():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        
        cmd = "python3 -c \"import sqlite3; conn = sqlite3.connect('/var/www/sustainage/backend/data/sdg_desktop.sqlite'); cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\\\'table\\\';'); print(cursor.fetchall()); conn.close()\""
        
        print("Executing DB check...")
        stdin, stdout, stderr = client.exec_command(cmd)
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        if err:
            print(f"Error: {err}")
        
        print("Tables found:")
        print(out)
        
    except Exception as e:
        print(f"SSH Error: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    check_tables()
