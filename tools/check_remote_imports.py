import paramiko

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def check_imports():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, password=PASS)
        print("Connected.")
        
        script = """
import sys
sys.path.append('/var/www/sustainage')
try:
    from backend.modules.lca.lca_manager import LCAManager
    print("LCAManager import: SUCCESS")
except Exception as e:
    print(f"LCAManager import: FAILED - {e}")

try:
    from web_app import app
    print("web_app import: SUCCESS")
except Exception as e:
    print(f"web_app import: FAILED - {e}")
"""
        # Escape quotes for command line
        # Easier to just write to a temporary file on remote
        
        # We can use 'python -c "..."'
        # But script is multi-line.
        
        # Let's just run it as a one-liner or simple blocks.
        
        cmd = "cd /var/www/sustainage && /var/www/sustainage/venv/bin/python -c \"import sys; sys.path.append('/var/www/sustainage'); from backend.modules.lca.lca_manager import LCAManager; print('LCAManager OK')\""
        stdin, stdout, stderr = client.exec_command(cmd)
        print("Checking LCAManager...")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        cmd = "cd /var/www/sustainage && /var/www/sustainage/venv/bin/python -c \"import sys; sys.path.append('/var/www/sustainage'); import web_app; print('web_app OK')\""
        stdin, stdout, stderr = client.exec_command(cmd)
        print("Checking web_app...")
        print(stdout.read().decode())
        print(stderr.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_imports()
