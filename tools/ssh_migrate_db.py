import paramiko
import os

HOST = "72.62.150.207"
USER = "root"
PASS = "Z/2m?-JDp5VaX6q+HO(b"

def migrate_db():
    print("--- Migrating Database Schema ---")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        
        # SQL command to add column
        # SQLite doesn't support IF NOT EXISTS for ADD COLUMN directly in all versions, 
        # but we can try and catch error, or check pragma.
        
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

add_column('water_consumption', 'water_source', 'TEXT')
add_column('water_consumption', 'water_quality_parameters', 'TEXT')
add_column('water_consumption', 'efficiency_ratio', 'REAL')
add_column('water_consumption', 'recycling_rate', 'REAL')
add_column('water_consumption', 'location', 'TEXT')
add_column('water_consumption', 'process_description', 'TEXT')
add_column('water_consumption', 'responsible_person', 'TEXT')
add_column('water_consumption', 'measurement_method', 'TEXT')
add_column('water_consumption', 'data_quality', 'TEXT')
add_column('water_consumption', 'source', 'TEXT')
add_column('water_consumption', 'evidence_file', 'TEXT')
add_column('water_consumption', 'notes', 'TEXT')

conn.commit()
conn.close()
"""
        
        # Execute migration via python one-liner or temporary script
        # I'll write a temp file
        sftp = ssh.open_sftp()
        with sftp.file("/tmp/migrate_water.py", "w") as f:
            f.write(migration_script)
            
        print("Running migration script...")
        stdin, stdout, stderr = ssh.exec_command("python3 /tmp/migrate_water.py")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        sftp.close()
        ssh.close()
        print("--- Migration Complete ---")
        
    except Exception as e:
        print(f"Migration Failed: {e}")

if __name__ == "__main__":
    migrate_db()
