import paramiko
import sys

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def tail_logs():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        stdin, stdout, stderr = client.exec_command("ls -t /var/www/sustainage/logs")
        files = stdout.read().decode().splitlines()
        
        if not files:
            print("No log files found.")
            return

        latest_log = files[0]
        print(f"Reading latest log: {latest_log}")
        
        stdin, stdout, stderr = client.exec_command(f"tail -n 50 /var/www/sustainage/logs/{latest_log}")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("\n--- Systemd Service Logs ---")
        stdin, stdout, stderr = client.exec_command("journalctl -u sustainage -n 50 --no-pager")
        print(stdout.read().decode())
        
        print("\n--- sustainage.cloud Apache/Plesk Error Log ---")
        cmd = "tail -n 50 /var/www/vhosts/system/sustainage.cloud/logs/error_log 2>/dev/null || echo 'no domain error_log'"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(err)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    tail_logs()
