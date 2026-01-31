import paramiko
import time

def kill_and_restart():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        print("Killing process on port 5000...")
        # Find PID using lsof or netstat and kill it
        cmd = "fuser -k 5000/tcp"
        client.exec_command(cmd)
        time.sleep(2)
        
        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("Service status:")
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    kill_and_restart()
