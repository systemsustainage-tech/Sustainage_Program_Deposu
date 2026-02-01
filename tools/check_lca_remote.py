import paramiko
import time

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

def verify_remote_lca():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        print("Connected.")
        
        # 1. Check DB Tables
        print("\n--- Checking Remote DB Tables ---")
        check_db_script = """
import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
if not os.path.exists(DB_PATH):
    print(f"DB not found at {DB_PATH}")
else:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    tables = ['lca_products', 'lca_assessments', 'lca_entries']
    all_exist = True
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if cursor.fetchone():
            print(f"[OK] Table {table} exists.")
        else:
            print(f"[FAIL] Table {table} MISSING.")
            all_exist = False
    conn.close()
"""
        # Run python script on remote
        # Escape quotes properly for shell
        # Actually, using a file is safer but let's try heredoc or just one-liner
        # To avoid quote hell, let's just upload a script and run it.
        
        # Create temp script locally
        with open("temp_check_lca.py", "w") as f:
            f.write(check_db_script)
            
        sftp = client.open_sftp()
        sftp.put("temp_check_lca.py", "/tmp/check_lca.py")
        sftp.close()
        
        stdin, stdout, stderr = client.exec_command("python3 /tmp/check_lca.py")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        # 2. Check Routes via curl
        print("\n--- Checking Routes via localhost curl ---")
        cmd = "curl -I http://localhost:5000/lca"
        stdin, stdout, stderr = client.exec_command(cmd)
        head_out = stdout.read().decode()
        print(head_out)
        
        if "HTTP/1.1 404" in head_out or "HTTP/1.0 404" in head_out:
            print("[FAIL] /lca route returned 404.")
        elif "HTTP" in head_out:
            print("[OK] /lca route is reachable (not 404).")
        else:
            print("[WARN] Could not verify route.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
        if os.path.exists("temp_check_lca.py"):
            os.remove("temp_check_lca.py")

if __name__ == "__main__":
    verify_remote_lca()
