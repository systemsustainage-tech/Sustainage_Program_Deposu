import paramiko

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_remote_fix():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        print("Connected.")
        
        # Upload
        sftp = ssh.open_sftp()
        local_path = r'c:\SUSTAINAGESERVER\tools\fix_sdg_ids_remote.py'
        remote_path = '/var/www/sustainage/tools/fix_sdg_ids_remote.py'
        sftp.put(local_path, remote_path)
        sftp.close()
        
        # Run
        print("Running fix script...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 {remote_path}")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Errors: {err}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    run_remote_fix()
