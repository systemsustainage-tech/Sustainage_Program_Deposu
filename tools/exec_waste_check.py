import paramiko
import time

HOSTNAME = "72.62.150.207"
USERNAME = "root"
KEY_FILE = "C:\\Users\\Administrator\\.ssh\\id_rsa"

def run_check():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOSTNAME, username=USERNAME, key_filename=KEY_FILE)
        
        # Upload
        sftp = ssh.open_sftp()
        local_path = "c:/SUSTAINAGESERVER/tools/check_waste_schema.py"
        remote_path = "/var/www/sustainage/tools/check_waste_schema.py"
        sftp.put(local_path, remote_path)
        sftp.close()
        
        # Run
        stdin, stdout, stderr = ssh.exec_command(f"python3 {remote_path}")
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        print("Output:")
        print(output)
        if error:
            print("Error:")
            print(error)
            
        ssh.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    run_check()
