import paramiko
import sys
import os

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def run_remote_fix():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        key_path = KEY_FILE
        if not os.path.exists(key_path):
            # Fallback for Windows if needed, or rely on agent/password if set up
            # But the user's environment seems to imply key usage or it's handled by paramiko defaults
            pass
            
        print(f"Connecting to {HOST}...")
        ssh.connect(HOST, username=USER, key_filename=key_path if os.path.exists(key_path) else None)
        
        # Upload the fix script first to ensure it exists
        sftp = ssh.open_sftp()
        local_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools', 'fix_survey_schema.py')
        remote_path = '/var/www/sustainage/tools/fix_survey_schema.py'
        print(f"Uploading {local_path} -> {remote_path}")
        try:
            sftp.put(local_path, remote_path)
            print("Upload successful.")
        except Exception as e:
            print(f"Upload failed: {e}")
            # Try creating directory if it fails?
            try:
                sftp.mkdir('/var/www/sustainage/tools')
                sftp.put(local_path, remote_path)
            except:
                pass
        
        cmd = "cd /var/www/sustainage && python3 tools/fix_survey_schema.py"
        print(f"Executing: {cmd}")
        
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        exit_status = stdout.channel.recv_exit_status()
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print("Output:")
        print(out)
        
        if err:
            print("Errors:")
            print(err)
            
        if exit_status == 0:
            print("Remote fix script executed successfully.")
        else:
            print(f"Remote fix script failed with exit code {exit_status}")
            
        ssh.close()
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_remote_fix()
