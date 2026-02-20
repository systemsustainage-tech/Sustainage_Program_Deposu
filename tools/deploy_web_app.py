import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def deploy_web_app():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
        except paramiko.AuthenticationException:
            print("Key authentication failed.")
            return

        sftp = ssh.open_sftp()
        
        # Upload web_app.py
        local_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web_app.py')
        remote_path = '/var/www/sustainage/web_app.py'
        
        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
        print("Upload successful.")
        
        # Upload templates/survey_detail.html just in case
        local_tpl = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates', 'survey_detail.html')
        remote_tpl = '/var/www/sustainage/templates/survey_detail.html'
        print(f"Uploading {local_tpl} to {remote_tpl}...")
        sftp.put(local_tpl, remote_tpl)
        print("Upload successful.")

        # Restart service
        print("Restarting sustainage service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Error restarting service: {stderr.read().decode()}")

        # Check logs
        print("Fetching last 50 lines of logs...")
        stdin, stdout, stderr = ssh.exec_command("journalctl -u sustainage -n 50 --no-pager")
        print(stdout.read().decode())
        
        sftp.close()
        ssh.close()
        
    except Exception as e:
        print(f"Operation failed: {e}")

if __name__ == "__main__":
    deploy_web_app()
