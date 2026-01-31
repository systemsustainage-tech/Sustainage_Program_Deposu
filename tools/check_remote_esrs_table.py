
import paramiko
import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

VERIFY_SCRIPT = """
import sys
import os
import sqlite3

# Add project root to path
sys.path.append('/var/www/sustainage')

try:
    from backend.modules.esrs.esrs_manager import ESRSManager
    manager = ESRSManager()
    manager.init_assessments_table()
    
    conn = sqlite3.connect(manager.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='esrs_materiality'")
    if not cursor.fetchone():
        print("ERROR: esrs_materiality table does NOT exist.")
        sys.exit(1)
        
    cursor.execute("PRAGMA table_info(esrs_materiality)")
    columns = [row[1] for row in cursor.fetchall()]
    
    required_columns = ['topic', 'impact_score', 'likelihood', 'financial_effect', 'environmental_effect']
    missing = [col for col in required_columns if col not in columns]
    
    if missing:
        print(f"ERROR: Missing columns in esrs_materiality: {missing}")
        sys.exit(1)
        
    print("SUCCESS: esrs_materiality table exists with all required columns.")
    
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
"""

def check_remote():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, port=PORT, username=USER, password=PASS)
        logging.info("Connected to SSH")
        
        # Write verification script to a temp file on remote
        stdin, stdout, stderr = ssh.exec_command('cat > /tmp/verify_esrs.py')
        stdin.write(VERIFY_SCRIPT)
        stdin.close()
        
        # Execute it
        logging.info("Running verification script on remote...")
        stdin, stdout, stderr = ssh.exec_command('python3 /tmp/verify_esrs.py')
        
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        
        if output:
            print(f"Output: {output}")
        if error:
            print(f"Error: {error}")
            
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            logging.info("Verification PASSED.")
        else:
            logging.error("Verification FAILED.")
            
        ssh.close()
        
    except Exception as e:
        logging.error(f"Connection failed: {e}")

if __name__ == '__main__':
    check_remote()
