import paramiko

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = '321'
REMOTE_BASE_DIR = '/var/www/sustainage'

def verify_files():
    print("Verifying remote files content...")
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        checks = [
            {
                "file": "web_app.py",
                "pattern": "get_tsrs_esrs_mappings",
                "desc": "web_app.py should call get_tsrs_esrs_mappings"
            },
            {
                "file": "templates/tsrs.html",
                "pattern": "tsrs_esrs_mappings",
                "desc": "tsrs.html should have mappings section key"
            },
            {
                "file": "backend/modules/tsrs/tsrs_manager.py",
                "pattern": "def get_tsrs_esrs_mappings",
                "desc": "tsrs_manager.py should have get_tsrs_esrs_mappings function"
            }
        ]
        
        for check in checks:
            cmd = f"grep -F '{check['pattern']}' {REMOTE_BASE_DIR}/{check['file']}"
            stdin, stdout, stderr = client.exec_command(cmd)
            result = stdout.read().decode().strip()
            
            if result:
                print(f"[PASS] {check['desc']}")
            else:
                print(f"[FAIL] {check['desc']}")
                print(f"Command: {cmd}")
                
    except Exception as e:
        print(f"Error verifying files: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    verify_files()
