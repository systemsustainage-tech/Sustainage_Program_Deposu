
import paramiko
import time

HOST = "72.62.150.207"
USER = "root"
KEY = "Z/2m?-JDp5VaX6q+HO(b"

def install_sqlite3():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=KEY)
        
        print("Updating package list and installing sqlite3...")
        # Non-interactive mode for apt-get
        command = "export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y sqlite3"
        stdin, stdout, stderr = ssh.exec_command(command)
        
        # Wait for command to complete and print output periodically
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode(), end="")
            if stderr.channel.recv_ready():
                print(stderr.channel.recv(1024).decode(), end="")
            time.sleep(1)
            
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("\nsqlite3 installed successfully.")
            
            # Verify installation
            stdin, stdout, stderr = ssh.exec_command("sqlite3 --version")
            print(f"Version: {stdout.read().decode().strip()}")
        else:
            print(f"\nError installing sqlite3. Exit status: {exit_status}")
            print(stderr.read().decode())
        
        ssh.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    install_sqlite3()
