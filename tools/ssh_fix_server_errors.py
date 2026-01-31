
import paramiko
import os
import time

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def fix_server():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        sftp = client.open_sftp()
        
        # 1. Upload fixed email_service.py
        local_email_service = r'c:\SDG\tasks\email_service.py'
        remote_email_service = '/var/www/sustainage/tasks/email_service.py'
        
        # Ensure remote dir exists
        client.exec_command('mkdir -p /var/www/sustainage/tasks')
        
        print(f"Uploading {local_email_service}...")
        sftp.put(local_email_service, remote_email_service)
        
        # 2. Fix audit_logs schema
        schema_fix_script = """
import sqlite3
import sys
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def fix_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if payload_json exists in audit_logs
        cursor.execute("PRAGMA table_info(audit_logs)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'payload_json' not in columns:
            print("Adding payload_json column to audit_logs...")
            cursor.execute("ALTER TABLE audit_logs ADD COLUMN payload_json TEXT")
            conn.commit()
            print("Column payload_json added.")
        else:
            print("Column payload_json already exists.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    fix_schema()
"""
        with sftp.file('/tmp/fix_schema.py', 'w') as f:
            f.write(schema_fix_script)
            
        print("Running schema fix...")
        stdin, stdout, stderr = client.exec_command("python3 /tmp/fix_schema.py")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        sftp.close()
        
        # Restart service to pick up code changes
        print("Restarting service...")
        client.exec_command("systemctl restart sustainage")
        time.sleep(3)
        print("Done.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    fix_server()
