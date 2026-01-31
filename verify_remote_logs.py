import paramiko
import time

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def verify_logs():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname, username=username, password=password)
        
        print("Checking system_logs table...")
        command = (
            "cd /var/www/sustainage && "
            "python3 -c \""
            "import sqlite3; "
            "import os; "
            "db_path = os.path.join('backend', 'data', 'sdg_desktop.sqlite'); "
            "conn = sqlite3.connect(db_path); "
            "cursor = conn.cursor(); "
            "cursor.execute('SELECT count(*) FROM sqlite_master WHERE type=\\'table\\' AND name=\\'system_logs\\''); "
            "exists = cursor.fetchone()[0]; "
            "print(f'Table exists: {exists}'); "
            "if exists: "
            "    cursor.execute('SELECT count(*) FROM system_logs'); "
            "    count = cursor.fetchone()[0]; "
            "    print(f'Log count: {count}'); "
            "conn.close();\""
        )
        
        stdin, stdout, stderr = ssh.exec_command(command)
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        ssh.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == '__main__':
    verify_logs()
