import paramiko
import time
import sys

# SSH Connection Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def fix_test_user_company():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOSTNAME}...")
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected.")
        
        # Python script to run on server
        remote_script = f"""
import sqlite3
import sys

DB_PATH = '{DB_PATH}'

try:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("Checking 'companies' table...")
    # Check if companies table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='companies'")
    if not cursor.fetchone():
        print("Creating 'companies' table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                sector TEXT,
                size TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # Check if any company exists
    cursor.execute("SELECT id, name FROM companies LIMIT 1")
    company = cursor.fetchone()
    
    company_id = None
    if company:
        print(f"Found existing company: {{company['name']}} (ID: {{company['id']}})")
        company_id = company['id']
    else:
        print("No company found. Creating 'SustainAge Demo Corp'...")
        cursor.execute("INSERT INTO companies (name, sector, size) VALUES (?, ?, ?)", 
                      ('SustainAge Demo Corp', 'Technology', 'Medium'))
        company_id = cursor.lastrowid
        print(f"Created company with ID: {{company_id}}")
        
    # Get test_user id
    cursor.execute("SELECT id FROM users WHERE username = 'test_user'")
    user = cursor.fetchone()
    if not user:
        print("ERROR: test_user not found!")
        sys.exit(1)
        
    user_id = user['id']
    print(f"Found test_user with ID: {{user_id}}")
    
    # Check user_companies
    print("Checking 'user_companies' table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_companies'")
    if not cursor.fetchone():
        print("Creating 'user_companies' table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_companies (
                user_id INTEGER,
                company_id INTEGER,
                is_primary BOOLEAN DEFAULT 1,
                PRIMARY KEY (user_id, company_id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        ''')
        
    # Check association
    cursor.execute("SELECT * FROM user_companies WHERE user_id = ?", (user_id,))
    assoc = cursor.fetchone()
    
    if assoc:
        print(f"User is already associated with company ID: {{assoc['company_id']}}")
    else:
        print(f"Associating user {{user_id}} with company {{company_id}}...")
        cursor.execute("INSERT INTO user_companies (user_id, company_id, is_primary) VALUES (?, ?, 1)", 
                      (user_id, company_id))
        print("Association created.")

    conn.commit()
    conn.close()
    print("Database updates completed successfully.")

except Exception as e:
    print(f"Error: {{e}}")
    sys.exit(1)
"""
        
        # Escape double quotes for the bash command
        remote_script_escaped = remote_script.replace('"', '\\"')
        
        # Execute the script on the server
        print("Executing remote database fix...")
        stdin, stdout, stderr = client.exec_command(f"python3 -c \"{remote_script_escaped}\"")
        
        # Print output
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        if out:
            print("Output:")
            print(out)
        if err:
            print("Errors:")
            print(err)
            
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fix_test_user_company()
