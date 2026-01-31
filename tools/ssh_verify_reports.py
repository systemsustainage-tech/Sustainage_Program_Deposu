import paramiko
import os

HOST = "72.62.150.207"
USER = "root"
PASS = "Z/2m?-JDp5VaX6q+HO(b"

def run_test():
    print("--- Running Reporting Tests on Server ---")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        sftp = ssh.open_sftp()
        
        # Upload test script
        local_path = r"c:\SDG\tools\remote_test_reports.py"
        remote_path = "/var/www/sustainage/tools/remote_test_reports.py"
        
        # Ensure tools dir exists
        ssh.exec_command("mkdir -p /var/www/sustainage/tools")
        
        sftp.put(local_path, remote_path)
        print(f"Uploaded: {local_path} -> {remote_path}")
        
        # Run test
        print("Executing test script...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 {remote_path}")
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print("\n[STDOUT]\n" + out)
        if err:
            print("\n[STDERR]\n" + err)
            
        sftp.close()
        ssh.close()
        
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    run_test()
