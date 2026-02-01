
import paramiko
import os
import time

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

FILES_TO_DEPLOY = [
    {
        "local": "c:/SUSTAINAGESERVER/web_app.py",
        "remote": "/var/www/sustainage/web_app.py"
    },
    {
        "local": "c:/SUSTAINAGESERVER/backend/modules/supply_chain/supply_chain_manager.py",
        "remote": "/var/www/sustainage/backend/modules/supply_chain/supply_chain_manager.py"
    },
    {
        "local": "c:/SUSTAINAGESERVER/templates/supply_chain_profile.html",
        "remote": "/var/www/sustainage/templates/supply_chain_profile.html"
    },
    {
        "local": "c:/SUSTAINAGESERVER/templates/supply_chain.html",
        "remote": "/var/www/sustainage/templates/supply_chain.html"
    }
]

def deploy_supply_chain():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        print("Connected.")
        
        sftp = client.open_sftp()
        
        for file_info in FILES_TO_DEPLOY:
            local_path = file_info["local"]
            remote_path = file_info["remote"]
            print(f"Uploading {local_path} to {remote_path}...")
            try:
                sftp.put(local_path, remote_path)
            except Exception as e:
                print(f"Failed to upload {local_path}: {e}")
                # Try to verify remote directory exists?
                # For now just continue
        
        sftp.close()
        
        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        time.sleep(5)
        
        print("Checking status...")
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        status_output = stdout.read().decode()
        print(status_output)
        
        if "active (running)" in status_output:
            print("SUCCESS: Service is running.")
        else:
            print("WARNING: Service might not be running correctly.")
            stdin, stdout, stderr = client.exec_command("journalctl -u sustainage.service -n 50 --no-pager")
            print("--- Recent Logs ---")
            print(stdout.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_supply_chain()
