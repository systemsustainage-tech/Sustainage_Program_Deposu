import paramiko
import time

# Server credentials
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def diagnose_remote():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD, look_for_keys=False, allow_agent=False)
        
        print("Connected. Running manual python check...")
        
        # 1. Check syntax/import by running python web_app.py directly (just import check)
        cmd = "cd /var/www/sustainage && ./venv/bin/python -c 'import web_app; print(\"Import Successful\")'"
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        if "Import Successful" in out:
            print("SUCCESS: web_app.py imports correctly.")
        else:
            print("FAILURE: web_app.py failed to import.")
            print("--- STDERR ---")
            print(err)
            print("--- STDOUT ---")
            print(out)
            ssh.close()
            return # Stop if basic import fails

        # 2. Check the logs again, but specifically look for the error message
        print("\nChecking systemd logs for 'Traceback' or 'Error'...")
        # Get the last 100 lines and look for python tracebacks
        cmd = "journalctl -u sustainage -n 100 --no-pager"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        logs = stdout.read().decode()
        
        if "Traceback" in logs or "Error" in logs or "Exception" in logs:
             print("--- SUSPICIOUS LOGS FOUND ---")
             # Print lines containing Traceback/Error and surrounding lines
             # Simple python filtering since grep via ssh might behave differently with tty
             lines = logs.split('\n')
             for i, line in enumerate(lines):
                 if "Traceback" in line or "Error" in line:
                     print('\n'.join(lines[max(0, i-5):min(len(lines), i+20)]))
                     break
        else:
            print("No explicit Traceback found in last 100 lines. Showing last 20 lines:")
            print('\n'.join(logs.split('\n')[-20:]))

        ssh.close()
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    diagnose_remote()
