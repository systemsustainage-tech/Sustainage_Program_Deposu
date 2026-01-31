import paramiko
import os

HOST = "72.62.150.207"
USER = "root"
PASS = "Z/2m?-JDp5VaX6q+HO(b"

def deploy_water_manager():
    print("--- Deploying Water Manager ---")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        sftp = ssh.open_sftp()
        
        local_path = r"c:\SDG\modules\water_management\water_manager.py"
        remote_path = "/var/www/sustainage/modules/water_management/water_manager.py"
        
        sftp.put(local_path, remote_path)
        print(f"Uploaded: {local_path} -> {remote_path}")
        
        # Also deploy water_reporting.py as it might have been missed or updated locally
        local_path_rep = r"c:\SDG\modules\water_management\water_reporting.py"
        remote_path_rep = "/var/www/sustainage/modules/water_management/water_reporting.py"
        sftp.put(local_path_rep, remote_path_rep)
        print(f"Uploaded: {local_path_rep} -> {remote_path_rep}")

        sftp.close()
        
        # Restart server
        print("Restarting Gunicorn...")
        ssh.exec_command("pkill -HUP gunicorn")
        
        ssh.close()
        print("--- Deployment Complete ---")
        
    except Exception as e:
        print(f"Deployment Failed: {e}")

if __name__ == "__main__":
    deploy_water_manager()
