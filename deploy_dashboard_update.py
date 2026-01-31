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
        ("web_app.py", "web_app.py"),
        ("templates/dashboard.html", "templates/dashboard.html")
    ]

    for local, remote in files_to_deploy:
        local_full = os.path.abspath(local)
        remote_full = f"{REMOTE_DIR}/{remote}"
        upload_file(sftp, local_full, remote_full)

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
