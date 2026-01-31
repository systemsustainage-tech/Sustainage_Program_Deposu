import paramiko
import os

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def check_remote_schema():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {HOSTNAME}...")
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        script = """
import sqlite3
conn = sqlite3.connect('/var/www/sustainage/sustainage.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(users)")
print("--- users table columns ---")
for col in cursor.fetchall():
    print(col)
    
print("\\n--- roles table content ---")
try:
    cursor.execute("SELECT * FROM roles")
    for row in cursor.fetchall():
        print(row)
except Exception as e:
    print(e)
conn.close()
"""
        # Run python script via stdin
        stdin, stdout, stderr = client.exec_command('python3')
        stdin.write(script)
        stdin.channel.shutdown_write()
        
        print(stdout.read().decode())
        print(stderr.read().decode())

        client.close()

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    check_remote_schema()
