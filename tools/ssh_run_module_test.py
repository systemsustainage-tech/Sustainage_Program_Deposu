import paramiko
import time

HOST = "72.62.150.207"
USER = "root"
KEY_PASS = "Z/2m?-JDp5VaX6q+HO(b"
LOCAL_SCRIPT = "c:/SDG/tools/remote_test_modules.py"
REMOTE_SCRIPT = "/var/www/sustainage/tools/remote_test_modules.py"

def deploy_and_run_test():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USER, password=KEY_PASS)
        print(f"Connected to {HOST}")

        sftp = client.open_sftp()
        
        # Ensure tools directory exists
        try:
            sftp.stat("/var/www/sustainage/tools")
        except FileNotFoundError:
            sftp.mkdir("/var/www/sustainage/tools")
        
        print(f"Uploading {LOCAL_SCRIPT} to {REMOTE_SCRIPT}...")
        sftp.put(LOCAL_SCRIPT, REMOTE_SCRIPT)
        sftp.close()

        # Run the script using the venv python
        print("Running test script on server...")
        cmd = f"/var/www/sustainage/venv/bin/python {REMOTE_SCRIPT}"
        stdin, stdout, stderr = client.exec_command(cmd)
        
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        print("--- Output ---")
        print(output)
        if error:
            print("--- Error Output ---")
            print(error)

        client.close()
        
    except Exception as e:
        print(f"Operation failed: {e}")

if __name__ == "__main__":
    deploy_and_run_test()
