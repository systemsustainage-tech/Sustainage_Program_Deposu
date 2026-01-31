import paramiko
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def check_schema():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        # Check file existence
        cmd = "ls -l /var/www/sustainage/sustainage.db"
        print(f"\nRunning: {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())

        # Check if sqlite3 is installed
        cmd = "which sqlite3"
        print(f"\nRunning: {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())

        # Try python script instead of sqlite3 CLI
        py_script = """
import sqlite3
try:
    conn = sqlite3.connect('/var/www/sustainage/sustainage.db')
    cursor = conn.cursor()
    print('--- survey_questions columns ---')
    for row in cursor.execute('PRAGMA table_info(survey_questions)'):
        print(row)
    print('--- online_surveys columns ---')
    for row in cursor.execute('PRAGMA table_info(online_surveys)'):
        print(row)
    conn.close()
except Exception as e:
    print(e)
"""
        cmd = f"python3 -c \"{py_script}\""
        print(f"\nRunning python script check...")
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())

    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_schema()
