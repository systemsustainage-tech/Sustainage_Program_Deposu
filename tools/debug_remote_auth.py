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
    from backend.yonetim.security.core.crypto import verify_password_compat
    print("Imported verify_password_compat successfully.")
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

if not os.path.exists(DB_PATH):
    print("DB does not exist!")
    sys.exit(1)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Check __super__
print("Checking for user '__super__'...")
user = cur.execute("SELECT * FROM users WHERE username='__super__'").fetchone()
if user:
    print(f"User __super__ found. ID: {user['id']}")
    stored_hash = user['password_hash']
    print(f"Stored Hash: {stored_hash}")
    
    # Try Verify
    try:
        is_valid = verify_password_compat(stored_hash, 'Kayra_1507')
        print(f"Password 'Kayra_1507' valid? {is_valid}")
    except Exception as e:
        print(f"Verification error: {e}")

    # Check Company
    comps = cur.execute("SELECT * FROM user_companies WHERE user_id=?", (user['id'],)).fetchall()
    print(f"User Companies: {[dict(c) for c in comps]}")
else:
    print("User __super__ NOT found.")

conn.close()
"""

def debug_auth():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    
    # Write script
    stdin, stdout, stderr = client.exec_command("cat > /tmp/debug_auth_remote.py")
    stdin.write(REMOTE_SCRIPT)
    stdin.close()
    
    # Run script
    print("Running debug script on remote...")
    stdin, stdout, stderr = client.exec_command("python3 /tmp/debug_auth_remote.py")
    print(stdout.read().decode())
    print("Errors:", stderr.read().decode())
    
    client.close()

if __name__ == "__main__":
    debug_auth()
