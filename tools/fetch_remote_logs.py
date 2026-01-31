import paramiko

def fetch_logs():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        # Check journalctl
        print("--- Journalctl Logs ---")
        stdin, stdout, stderr = client.exec_command("journalctl -u sustainage -n 50 --no-pager")
        print(stdout.read().decode())
        
        # Check specific log files if exist
        print("--- File Logs ---")
        stdin, stdout, stderr = client.exec_command("tail -n 50 /var/www/sustainage/logs/error.log 2>/dev/null")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fetch_logs()
