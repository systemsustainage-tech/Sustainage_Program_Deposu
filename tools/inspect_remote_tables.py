import paramiko
import os
import sys

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def inspect_tables():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected to server.")

        cmd = """python3 -c "import sqlite3; conn = sqlite3.connect('/var/www/sustainage/backend/data/sdg_desktop.sqlite'); cur = conn.cursor(); 
for table in ['surveys', 'survey_responses', 'survey_answers']:
    print(f'--- {table} ---');
    try:
        cur.execute(f'PRAGMA table_info({table})');
        for row in cur.fetchall(): print(row);
    except: print('Error or not found');
" """
        
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print("Error:", err)
        
        client.close()

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == '__main__':
    inspect_tables()
