import paramiko
import os

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_remote_simulation():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        print("Connected.")
        
        # 1. Upload simulation script
        print("\n--- Uploading simulate_login_and_images.py ---")
        sftp = ssh.open_sftp()
        local_path = r'c:\SUSTAINAGESERVER\tools\simulate_login_and_images.py'
        remote_path = '/var/www/sustainage/tools/simulate_login_and_images.py'
        
        # Ensure tools directory exists
        try:
            sftp.mkdir('/var/www/sustainage/tools')
        except IOError:
            pass # Already exists
            
        sftp.put(local_path, remote_path)
        sftp.close()
        print("Uploaded.")
        
        # 2. Run simulation script
        print("\n--- Running simulation ---")
        # We need to install requests if not present, but it's likely there.
        # Running with python3
        stdin, stdout, stderr = ssh.exec_command(f"python3 {remote_path}")
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print("Output:")
        print(out)
        
        if err:
            print("Errors:")
            print(err)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    run_remote_simulation()
