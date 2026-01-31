import paramiko
import sys

# Server details
HOST = "72.62.150.207"
USER = "root"
PASS = "Z/2m?-JDp5VaX6q+HO(b"

def restart_service():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USER, password=PASS)
        
        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Error restarting service: {stderr.read().decode()}")
            
        client.close()
        return exit_status == 0
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    if restart_service():
        sys.exit(0)
    else:
        sys.exit(1)
