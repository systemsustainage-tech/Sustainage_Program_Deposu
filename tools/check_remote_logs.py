
import paramiko

HOSTNAME = "72.62.150.207"
USERNAME = "root"
PASSWORD = "Sustainage123!"

def check_logs():
    print(f"Connecting to {HOSTNAME}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        print("Connected. Fetching last 50 lines of logs...")
        stdin, stdout, stderr = ssh.exec_command("journalctl -u sustainage.service -n 50 --no-pager")
        print(stdout.read().decode())
        print("STDERR:", stderr.read().decode())
        
        print("Checking DB table online_surveys...")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /var/www/sustainage/backend/sustainage.db 'PRAGMA table_info(online_surveys);'")
        print(stdout.read().decode())
        print("STDERR:", stderr.read().decode())

        ssh.close()

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    check_logs()
