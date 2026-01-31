import paramiko
import sys

# Remote server details
hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b'

def read_log(lines=100):
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        
        cmd = f"journalctl -u sustainage -n {lines} --no-pager"
        print(f"Running: {cmd}")
        
        stdin, stdout, stderr = ssh.exec_command(cmd)
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
    lines = 100
    if len(sys.argv) > 1:
        lines = int(sys.argv[1])
    read_log(lines)