import paramiko
import os

HOSTNAME = "72.62.150.207"
USERNAME = "root"
PASSWORD = os.environ.get("REMOTE_SSH_PASS", "Kayra_1507")

def run_debug():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        sftp = client.open_sftp()
        sftp.put('tools/get_flask_error.py', '/var/www/sustainage/get_flask_error.py')
        sftp.close()
        
        stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/get_flask_error.py")
        print("Output:")
        print(stdout.read().decode())
        print("Errors:")
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    run_debug()
