
import paramiko
import os

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def deploy_and_run():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected to server.")

        sftp = client.open_sftp()

        # Upload script
        local_script = os.path.join(BASE_DIR, 'tools', 'fix_remote_db_schemas.py')
        remote_script = '/var/www/sustainage/fix_remote_db_schemas.py'
        print(f"Uploading {local_script} to {remote_script}...")
        sftp.put(local_script, remote_script)

        print("Running fix script...")
        stdin, stdout, stderr = client.exec_command(f'python3 {remote_script}')
        print("STDOUT:", stdout.read().decode())
        print("STDERR:", stderr.read().decode())
        
        # Restart Gunicorn just in case DB locks or caching needs refresh
        print("Restarting Gunicorn...")
        client.exec_command("pkill -HUP gunicorn")

        sftp.close()
        client.close()
        print("Done.")

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == '__main__':
    deploy_and_run()
