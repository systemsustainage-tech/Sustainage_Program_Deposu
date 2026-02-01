import paramiko

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

def read_logs():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        
        # Read last 100 lines of journal for the service
        cmd = "journalctl -u sustainage.service -n 100 --no-pager"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        print(stdout.read().decode())
        
        ssh.close()
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    read_logs()
