import paramiko
import os

HOST = "72.62.150.207"
USER = "root"
PASS = "Z/2m?-JDp5VaX6q+HO(b"

def migrate_db():
    print("--- Migrating Database Schema (Part 2) ---")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        
        migration_script = """
import sqlite3
db_path = '/var/www/sustainage/data/sdg_desktop.sqlite'
conn = sqlite3.connect(db_path)
c = conn.cursor()

def add_column(table, col, type):
    try:
        c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {type}")
        print(f"Added column {col} to {table}")
    except Exception as e:
        print(f"Column {col} might already exist: {e}")

add_column('water_consumption', 'blue_water', 'REAL')
add_column('water_consumption', 'green_water', 'REAL')
add_column('water_consumption', 'grey_water', 'REAL')
add_column('water_consumption', 'total_water', 'REAL')

conn.commit()
conn.close()
"""
        
        sftp = ssh.open_sftp()
        with sftp.file("/tmp/migrate_water_2.py", "w") as f:
            f.write(migration_script)
            
        print("Running migration script...")
        stdin, stdout, stderr = ssh.exec_command("python3 /tmp/migrate_water_2.py")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        sftp.close()
        ssh.close()
        print("--- Migration Complete ---")
        
    except Exception as e:
        print(f"Migration Failed: {e}")

if __name__ == "__main__":
    migrate_db()
