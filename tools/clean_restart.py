import paramiko
import time

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

def clean_restart():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        
        print("Stopping service...")
        ssh.exec_command("systemctl stop sustainage.service")
        time.sleep(2)
        
        print("Cleaning pycache...")
        ssh.exec_command("find /var/www/sustainage -name '__pycache__' -type d -exec rm -rf {} +")
        
        print("Starting service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl start sustainage.service")
        
        err = stderr.read().decode()
        if err:
            print(f"Start error: {err}")
        else:
            print("Service started.")
            
        ssh.close()
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    clean_restart()
