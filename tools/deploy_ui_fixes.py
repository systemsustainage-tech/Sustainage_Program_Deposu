import os
import paramiko
import time
import sys

# Configuration
HOSTNAME = os.environ.get('REMOTE_SERVER_IP', '72.62.150.207')
USERNAME = "root"
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b)'
REMOTE_DIR = "/var/www/sustainage"

def create_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        return client
    except Exception as e:
        print(f"SSH connection failed: {e}")
        sys.exit(1)

def upload_file(sftp, local_path, remote_path):
    try:
        print(f"Uploading {local_path} to {remote_path}...")
        # Ensure remote directory exists
        remote_dir = os.path.dirname(remote_path)
        try:
            sftp.stat(remote_dir)
        except IOError:
            print(f"Creating remote directory: {remote_dir}")
            # This is a simple mkdir, might fail if parent doesn't exist
            # But for these paths they should exist
            pass
            
        sftp.put(local_path, remote_path)
        print("Upload successful.")
    except Exception as e:
        print(f"Failed to upload {local_path}: {e}")

def run_command(client, command):
    print(f"Running command: {command}")
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print("Command executed successfully.")
        print(stdout.read().decode())
    else:
        print("Command failed.")
        print(stderr.read().decode())
    return exit_status

def main():
    print(f"Starting deployment to {HOSTNAME}...")
    client = create_ssh_client()
    sftp = client.open_sftp()

    # Upload files
    files_to_deploy = [
        ("templates/reporting_journey.html", "templates/reporting_journey.html"),
        ("locales/tr.json", "locales/tr.json"),
        ("backend/locales/tr.json", "backend/locales/tr.json"),
        ("backend/config/translations_tr.json", "backend/config/translations_tr.json")
    ]

    for local, remote in files_to_deploy:
        local_full = os.path.abspath(os.path.join("c:\\SUSTAINAGESERVER", local))
        remote_full = f"{REMOTE_DIR}/{remote}"
        
        if os.path.exists(local_full):
            upload_file(sftp, local_full, remote_full)
        else:
            print(f"Warning: Local file not found: {local_full}")

    sftp.close()

    # Restart service
    print("Restarting sustainage service...")
    run_command(client, "systemctl restart sustainage")
    
    # Wait for service to come up
    print("Waiting for service to restart...")
    time.sleep(5)
    
    # Check status
    run_command(client, "systemctl status sustainage --no-pager")

    client.close()
    print("Deployment complete.")

if __name__ == "__main__":
    main()
