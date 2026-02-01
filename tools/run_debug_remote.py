import paramiko
import os

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"
LOCAL_FILE = "tools/debug_remote_lang.py"
REMOTE_FILE = "/var/www/sustainage/tools/debug_remote_lang.py"

def run_debug():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        sftp = ssh.open_sftp()
        
        # Ensure remote tools dir exists
        try:
            sftp.mkdir("/var/www/sustainage/tools")
        except:
            pass
            
        print(f"Uploading {LOCAL_FILE}...")
        sftp.put(os.path.abspath(LOCAL_FILE), REMOTE_FILE)
        sftp.close()
        
        print("Running remote script...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 {REMOTE_FILE}")
        
        print("--- STDOUT ---")
        print(stdout.read().decode())
        print("--- STDERR ---")
        print(stderr.read().decode())
        
        ssh.close()
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    run_debug()
