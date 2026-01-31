import paramiko
import sys
import os

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def run_remote_script(local_script_path):
    if not os.path.exists(local_script_path):
        print(f"File not found: {local_script_path}")
        return

    with open(local_script_path, 'r', encoding='utf-8') as f:
        script_content = f.read()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print(f"Connecting to {HOSTNAME}...")
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        # Escape double quotes for shell
        # Actually, it's safer to write to a temp file on remote and run it
        remote_tmp_path = f"/tmp/{os.path.basename(local_script_path)}"
        
        sftp = client.open_sftp()
        sftp.put(local_script_path, remote_tmp_path)
        sftp.close()
        
        print(f"Uploaded {local_script_path} to {remote_tmp_path}")
        
        cmd = f"python3 {remote_tmp_path}"
        print(f"Running: {cmd}")
        
        stdin, stdout, stderr = client.exec_command(cmd)
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        if out: print(f"Output:\n{out}")
        if err: print(f"Error:\n{err}")
        
        # Cleanup
        client.exec_command(f"rm {remote_tmp_path}")
        
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_remote_python.py <local_script_path>")
    else:
        run_remote_script(sys.argv[1])
