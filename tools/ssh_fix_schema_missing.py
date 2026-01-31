import paramiko
import sys

# Server details
HOST = "72.62.150.207"
USER = "root"
PASS = "Z/2m?-JDp5VaX6q+HO(b"
DB_PATH_VAL = "/var/www/sustainage/backend/data/sdg_desktop.sqlite"

def fix_schema():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        print("Connected.")
        
        # Python script to run on server
        remote_script = """
import sqlite3
import sys

DB_PATH = 'REPLACE_DB_PATH'

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"Connected to database at {DB_PATH}")
    
    # 1. Add data_json to carbon_emissions if missing
    try:
        cursor.execute("SELECT data_json FROM carbon_emissions LIMIT 1")
    except sqlite3.OperationalError:
        print("Adding data_json column to carbon_emissions...")
        cursor.execute("ALTER TABLE carbon_emissions ADD COLUMN data_json TEXT")
        print("data_json column added.")
    else:
        print("data_json column already exists.")
        
    # 2. Add fuel_type to carbon_emissions if missing
    try:
        cursor.execute("SELECT fuel_type FROM carbon_emissions LIMIT 1")
    except sqlite3.OperationalError:
        print("Adding fuel_type column to carbon_emissions...")
        cursor.execute("ALTER TABLE carbon_emissions ADD COLUMN fuel_type TEXT")
        print("fuel_type column added.")
    else:
        print("fuel_type column already exists.")

    # 3. Create sasb_standards table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sasb_standards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sector TEXT,
        industry TEXT,
        topic TEXT,
        code TEXT,
        metric TEXT,
        category TEXT,
        unit TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("sasb_standards table checked/created.")

    # 4. Create tcfd_recommendations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tcfd_recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pillar TEXT,
        recommendation TEXT,
        guidance TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("tcfd_recommendations table checked/created.")

    # 5. Create tnfd_recommendations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tnfd_recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pillar TEXT,
        recommendation TEXT,
        guidance TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("tnfd_recommendations table checked/created.")

    conn.commit()
    conn.close()
    print("Schema fix completed successfully.")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
"""
        remote_script = remote_script.replace("REPLACE_DB_PATH", DB_PATH_VAL)
        
        # Escape double quotes for shell command
        remote_script_escaped = remote_script.replace('"', '\\"')
        
        stdin, stdout, stderr = client.exec_command(f"python3 -c \"{remote_script_escaped}\"")
        
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        print(output)
        if error:
            print(f"Errors: {error}")
            
        client.close()
        return "Schema fix completed successfully" in output

    except Exception as e:
        print(f"Deployment failed: {e}")
        return False

if __name__ == "__main__":
    if fix_schema():
        print("Schema update successful.")
        sys.exit(0)
    else:
        sys.exit(1)
