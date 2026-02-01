import paramiko
import time

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

LOCAL_SCRIPT = r'c:\SUSTAINAGESERVER\tools\check_active_routes.py'
REMOTE_SCRIPT = '/tmp/check_active_routes.py'

def run_check():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS, look_for_keys=False, allow_agent=False)
        print("Connected.")

        sftp = ssh.open_sftp()
        sftp.put(LOCAL_SCRIPT, REMOTE_SCRIPT)
        sftp.close()
        print("Script uploaded.")

        # Run with venv python. Need to install requests if not present?
        # Flask is installed, requests usually is too or comes with it/pip.
        # If not, use urllib in the script?
        # Let's assume requests is there (it's a common dep).
        # If not, I'll rewrite to use urllib.
        
        cmd = f"/var/www/sustainage/venv/bin/python {REMOTE_SCRIPT}"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print("Errors:", err)
            
        ssh.close()
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    run_check()
