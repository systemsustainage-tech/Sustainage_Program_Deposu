import paramiko
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Kayra_1507'

FILES_TO_UPLOAD = [
    {'local': 'c:\\SUSTAINAGESERVER\\tools\\fix_remote_schema_v4.py', 'remote': '/var/www/sustainage/tools/fix_remote_schema_v4.py'},
    {'local': 'c:\\SUSTAINAGESERVER\\backend\\modules\\csrd\\csrd_compliance_manager.py', 'remote': '/var/www/sustainage/backend/modules/csrd/csrd_compliance_manager.py'},
    {'local': 'c:\\SUSTAINAGESERVER\\tools\\verify_all_modules.py', 'remote': '/var/www/sustainage/tools/verify_all_modules.py'},
    {'local': 'c:\\SUSTAINAGESERVER\\templates\\iirc.html', 'remote': '/var/www/sustainage/templates/iirc.html'},
    {'local': 'c:\\SUSTAINAGESERVER\\templates\\targets.html', 'remote': '/var/www/sustainage/templates/targets.html'}
]

def deploy_and_verify():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    except:
        print("Auth failed, trying fallback password...")
        client.connect(HOSTNAME, username=USERNAME, password='Z/2m?-JDp5VaX6q+HO(b')

    sftp = client.open_sftp()
    
    # 1. Upload files
    print("\n--- Uploading Files ---")
    for item in FILES_TO_UPLOAD:
        local_path = item['local']
        remote_path = item['remote']
        print(f"Uploading {local_path} -> {remote_path}...")
        try:
            sftp.put(local_path, remote_path)
        except Exception as e:
            print(f"Failed to upload {local_path}: {e}")
    
    sftp.close()
    
    # 2. Run Schema Fix
    print("\n--- Running Schema Fix v4 ---")
    stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/tools/fix_remote_schema_v4.py")
    print(stdout.read().decode())
    err = stderr.read().decode()
    if err:
        print(f"Schema Fix Errors: {err}")
        
    # 3. Restart Services
    print("\n--- Restarting Services ---")
    stdin, stdout, stderr = client.exec_command("systemctl restart sustainage && pkill -HUP gunicorn")
    print(stdout.read().decode())
    time.sleep(5) # Wait for restart
    
    # 4. Verify Modules
    print("\n--- Verifying Modules ---")
    stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/tools/verify_all_modules.py")
    out = stdout.read().decode()
    print(out)
    
    if "FAIL" in out:
        print("\n!!! Verification Failed !!!")
    else:
        print("\nAll systems green.")

    client.close()

if __name__ == "__main__":
    deploy_and_verify()
