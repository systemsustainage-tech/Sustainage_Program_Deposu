import paramiko

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def check_logs():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        
        print("Fetching service status...")
        stdin, stdout, stderr = ssh.exec_command("systemctl status sustainage")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("\nFetching last 100 log lines...")
        stdin, stdout, stderr = ssh.exec_command("journalctl -u sustainage -n 100 --no-pager")
        print(stdout.read().decode())
        
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_logs()
