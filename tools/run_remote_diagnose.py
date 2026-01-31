
import paramiko
import sys

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'
remote_base = '/var/www/sustainage'

def run_diagnostics():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        
        print("Running diagnose_500.py on remote...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/diagnose_500.py")
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print("STDOUT:")
        print(out)
        if err:
            print("STDERR:")
            print(err)

        print("-" * 50)
        print("Running inspect_db_schema.py on remote...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/inspect_db_schema.py")
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print("STDOUT:")
        print(out)
        if err:
            print("STDERR:")
            print(err)
            
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    run_diagnostics()
