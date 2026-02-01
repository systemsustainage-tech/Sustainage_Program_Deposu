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
        "local": "c:/SUSTAINAGESERVER/templates/benchmark.html",
        "remote": "/var/www/sustainage/templates/benchmark.html"
    },
    {
        "local": "c:/SUSTAINAGESERVER/templates/regulation.html",
        "remote": "/var/www/sustainage/templates/regulation.html"
    },
    {
        "local": "c:/SUSTAINAGESERVER/backend/modules/analytics/sector_benchmark_database.py",
        "remote": "/var/www/sustainage/backend/modules/analytics/sector_benchmark_database.py"
    },
    {
        "local": "c:/SUSTAINAGESERVER/backend/modules/regulation/regulation_manager.py",
        "remote": "/var/www/sustainage/backend/modules/regulation/regulation_manager.py"
    },
    {
        "local": "c:/SUSTAINAGESERVER/locales/tr.json",
        "remote": "/var/www/sustainage/locales/tr.json"
    }
]

def deploy_benchmark_regulation():
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
                # Ensure remote directory exists (simple check)
                remote_dir = os.path.dirname(remote_path).replace("\\", "/")
                try:
                    sftp.stat(remote_dir)
                except IOError:
                    # Create directory if it doesn't exist
                    print(f"Directory {remote_dir} might not exist. Attempting to create...")
                    try:
                        sftp.mkdir(remote_dir)
                    except:
                        pass # might fail if parent doesn't exist, but we assume main structure exists
                
                sftp.put(local_path, remote_path)
            except Exception as e:
                print(f"Failed to upload {local_path}: {e}")
        
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
    deploy_benchmark_regulation()
