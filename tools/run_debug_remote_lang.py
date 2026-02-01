import paramiko
import os

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

LOCAL_SCRIPT = "tools/debug_remote_lang.py"
REMOTE_SCRIPT = "/var/www/sustainage/tools/debug_remote_lang.py"

def run_remote_debug():
    print(f"Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        sftp = ssh.open_sftp()
        
        # Ensure remote tools dir exists
        try:
            sftp.stat("/var/www/sustainage/tools")
        except FileNotFoundError:
            ssh.exec_command("mkdir -p /var/www/sustainage/tools")

        print(f"Uploading {LOCAL_SCRIPT} to {REMOTE_SCRIPT}...")
        sftp.put(LOCAL_SCRIPT, REMOTE_SCRIPT)
        sftp.close()
        
        print("Executing script...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 {REMOTE_SCRIPT}")
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print("--- OUTPUT ---")
        print(out)
        if err:
            print("--- ERROR ---")
            print(err)
            
        ssh.close()
        
    except Exception as e:
        print(f"Operation failed: {e}")

if __name__ == "__main__":
    run_remote_debug()
