import paramiko
import sys

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def fix_schema():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOSTNAME}...")
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected.")
        
        # Python script to run on server
        remote_script = """
import sqlite3
import sys

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

try:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print(f"Connected to DB: {DB_PATH}")

    # 1. Check and Create sasb_standards
    print("Checking sasb_standards...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sasb_standards'")
    if not cursor.fetchone():
        print("Creating sasb_standards table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sasb_standards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sector TEXT,
                industry TEXT,
                topic TEXT,
                code TEXT,
                description TEXT,
                unit TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        print("sasb_standards exists.")

    # 2. Check and Create tcfd_recommendations
    print("Checking tcfd_recommendations...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tcfd_recommendations'")
    if not cursor.fetchone():
        print("Creating tcfd_recommendations table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tcfd_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pillar TEXT,
                recommendation TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        print("tcfd_recommendations exists.")

    # 3. Check and Create tnfd_recommendations
    print("Checking tnfd_recommendations...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tnfd_recommendations'")
    if not cursor.fetchone():
        print("Creating tnfd_recommendations table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tnfd_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pillar TEXT,
                recommendation TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        print("tnfd_recommendations exists.")

    # 4. Check carbon_emissions columns
    print("Checking carbon_emissions columns...")
    cursor.execute("PRAGMA table_info(carbon_emissions)")
    columns = [row['name'] for row in cursor.fetchall()]
    
    if 'data_json' not in columns:
        print("Adding data_json column to carbon_emissions...")
        cursor.execute("ALTER TABLE carbon_emissions ADD COLUMN data_json TEXT")
    else:
        print("data_json column exists.")
        
    if 'fuel_type' not in columns:
        print("Adding fuel_type column to carbon_emissions...")
        cursor.execute("ALTER TABLE carbon_emissions ADD COLUMN fuel_type TEXT")
    else:
        print("fuel_type column exists.")

    conn.commit()
    conn.close()
    print("Schema updates completed successfully.")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
"""
        
        # Escape double quotes for the bash command
        remote_script_escaped = remote_script.replace('"', '\\"')
        
        # Execute the script on the server
        print("Executing remote schema fix...")
        stdin, stdout, stderr = client.exec_command(f"python3 -c \"{remote_script_escaped}\"")
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        if out: print("Output:\n" + out)
        if err: print("Errors:\n" + err)
            
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fix_schema()
