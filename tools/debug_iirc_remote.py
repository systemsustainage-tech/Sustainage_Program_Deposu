import paramiko

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

REMOTE_SCRIPT = """
import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Ensure paths
sys.path.insert(0, '/var/www/sustainage')
sys.path.insert(0, '/var/www/sustainage/backend')

print("Importing IIRCManager...")
try:
    from backend.modules.iirc.iirc_manager import IIRCManager
    print("Import successful.")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)

print("Instantiating IIRCManager...")
try:
    manager = IIRCManager('/var/www/sustainage/backend/data/sdg_desktop.sqlite')
    print("Instantiation successful.")
except Exception as e:
    print(f"Instantiation failed: {e}")
    sys.exit(1)

print("Calling get_dashboard_stats(1)...")
try:
    stats = manager.get_dashboard_stats(1)
    print(f"Stats: {stats}")
except Exception as e:
    print(f"get_dashboard_stats failed: {e}")

print("Calling get_recent_reports(1)...")
try:
    reports = manager.get_recent_reports(1)
    print(f"Reports: {reports}")
except Exception as e:
    print(f"get_recent_reports failed: {e}")
"""

def debug_iirc():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    
    # Write script
    stdin, stdout, stderr = client.exec_command("cat > /tmp/debug_iirc_remote.py")
    stdin.write(REMOTE_SCRIPT)
    stdin.close()
    
    # Run script
    print("Running debug script on remote...")
    stdin, stdout, stderr = client.exec_command("python3 /tmp/debug_iirc_remote.py")
    print(stdout.read().decode())
    err = stderr.read().decode()
    if err:
        print("Errors:", err)
    
    client.close()

if __name__ == "__main__":
    debug_iirc()
