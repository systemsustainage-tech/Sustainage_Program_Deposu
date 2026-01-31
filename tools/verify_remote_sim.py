import paramiko
import os
import time

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'
remote_base = '/var/www/sustainage'

def verify_sim():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        
        print("Running simulate_user_actions.py on remote...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/simulate_user_actions.py")
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print("--- STDOUT ---")
        print(out)
        print("--- STDERR ---")
        print(err)
        
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    verify_sim()
