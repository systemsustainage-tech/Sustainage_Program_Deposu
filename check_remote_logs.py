import paramiko

def check_logs():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        print("Checking recent errors in /var/www/sustainage/logs/app.log:")
        stdin, stdout, stderr = client.exec_command("tail -n 50 /var/www/sustainage/logs/app.log")
        print(stdout.read().decode())
        
        # Also check journalctl for gunicorn errors if app.log is empty or not helpful
        print("\nChecking journalctl for sustainage service:")
        stdin, stdout, stderr = client.exec_command("journalctl -u sustainage -n 50 --no-pager")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_logs()
