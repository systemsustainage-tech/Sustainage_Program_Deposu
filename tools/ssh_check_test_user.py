import paramiko
import time

HOST = "72.62.150.207"
USER = "root"
KEY_PASS = "Z/2m?-JDp5VaX6q+HO(b"
LOCAL_SCRIPT = "c:/SDG/tools/remote_check_user.py"
REMOTE_SCRIPT = "/var/www/sustainage/tools/remote_check_user.py"

def run_check():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USER, password=KEY_PASS)
        
        sftp = client.open_sftp()
        try:
            sftp.stat("/var/www/sustainage/tools")
        except FileNotFoundError:
            sftp.mkdir("/var/www/sustainage/tools")
            
        sftp.put(LOCAL_SCRIPT, REMOTE_SCRIPT)
        sftp.close()

        cmd = f"/var/www/sustainage/venv/bin/python {REMOTE_SCRIPT}"
        stdin, stdout, stderr = client.exec_command(cmd)
        
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

        client.close()
        
    except Exception as e:
        print(f"Operation failed: {e}")

if __name__ == "__main__":
    run_check()
