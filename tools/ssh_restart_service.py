import paramiko
import sys

# Server Details
HOST = "72.62.150.207"
USER = "root"
KEY = "Z/2m?-JDp5VaX6q+HO(b"

def restart_service():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=KEY)
        
        print("Restarting sustainage service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Error restarting service: {stderr.read().decode()}")
            
        ssh.close()
        return True
    except Exception as e:
        print(f"Restart failed: {e}")
        return False

if __name__ == "__main__":
    if restart_service():
        sys.exit(0)
    else:
        sys.exit(1)
