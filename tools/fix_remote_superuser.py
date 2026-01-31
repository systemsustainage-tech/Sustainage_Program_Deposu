import paramiko

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

REMOTE_SCRIPT = """
import sqlite3
import os
import sys

# Ensure backend path is in sys.path
sys.path.insert(0, '/var/www/sustainage')

try:
    from backend.yonetim.security.core.crypto import hash_password
    print("Imported hash_password successfully.")
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

if not os.path.exists(DB_PATH):
    print("DB does not exist!")
    sys.exit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 1. Update Password for __super__
new_hash = hash_password('Kayra_1507')
print(f"Generated new hash: {new_hash}")

cur.execute("UPDATE users SET password_hash = ? WHERE username = '__super__'", (new_hash,))
print(f"Updated password for __super__. Row count: {cur.rowcount}")

# 2. Ensure Company Association
# Get __super__ ID
cur.execute("SELECT id FROM users WHERE username = '__super__'")
row = cur.fetchone()
if row:
    user_id = row[0]
    print(f"__super__ ID: {user_id}")
    
    # Check if association exists
    cur.execute("SELECT * FROM user_companies WHERE user_id = ?", (user_id,))
    assoc = cur.fetchone()
    if not assoc:
        print("No company association found. Adding to Company 1...")
        # Check if Company 1 exists
        cur.execute("SELECT id FROM companies WHERE id = 1")
        if not cur.fetchone():
             print("Company 1 not found. Creating default company...")
             cur.execute("INSERT INTO companies (id, name, sector, country) VALUES (1, 'Sustainage Demo', 'Technology', 'Turkey')")
        
        cur.execute("INSERT INTO user_companies (user_id, company_id, is_primary) VALUES (?, 1, 1)", (user_id,))
        print("Company association added.")
    else:
        print("Company association already exists.")
else:
    print("User __super__ not found (unexpected)!")

conn.commit()
conn.close()
print("Fix completed.")
"""

def fix_superuser():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    
    # Write script
    stdin, stdout, stderr = client.exec_command("cat > /tmp/fix_remote_superuser.py")
    stdin.write(REMOTE_SCRIPT)
    stdin.close()
    
    # Run script
    print("Running fix script on remote...")
    stdin, stdout, stderr = client.exec_command("python3 /tmp/fix_remote_superuser.py")
    print(stdout.read().decode())
    print("Errors:", stderr.read().decode())
    
    client.close()

if __name__ == "__main__":
    fix_superuser()
