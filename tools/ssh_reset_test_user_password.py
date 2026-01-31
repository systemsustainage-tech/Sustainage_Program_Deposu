import paramiko
import sys

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def reset_password():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOSTNAME}...")
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected.")
        
        # Python script to run on server
        remote_script = """
import sys
import sqlite3
# Add path to find modules
sys.path.append('/var/www/sustainage/server')
sys.path.append('/var/www/sustainage')

try:
    from yonetim.security.core.crypto import hash_password
    print("Imported hash_password from crypto module.")
except ImportError:
    print("Could not import crypto module. Using fallback.")
    def hash_password(p): return p # Fallback (not secure but for testing)

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    username = 'test_user'
    new_pass = 'password123'
    hashed_pass = hash_password(new_pass)
    
    print(f"Resetting password for {username}...")
    
    cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (hashed_pass, username))
    
    if cursor.rowcount > 0:
        print("Password updated successfully.")
    else:
        print("User not found.")
        
    conn.commit()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
"""
        
        # Escape double quotes for the bash command
        remote_script_escaped = remote_script.replace('"', '\\"')
        
        print("Executing remote password reset...")
        stdin, stdout, stderr = client.exec_command(f"python3 -c \"{remote_script_escaped}\"")
        
        print(stdout.read().decode())
        print(stderr.read().decode())
            
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    reset_password()
