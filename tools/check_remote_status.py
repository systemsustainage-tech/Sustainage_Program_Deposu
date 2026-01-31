
import paramiko
import time

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

def check_status():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        print("Connected.")
        
        # print("\n--- Cleaning up manual Gunicorn ---")
        # client.exec_command("pkill -f gunicorn")
        # client.exec_command("fuser -k 5000/tcp")
        # time.sleep(2)
        
        # print("\n--- Starting sustainage.service ---")
        # stdin, stdout, stderr = client.exec_command("systemctl start sustainage.service")
        # print(stdout.read().decode())
        # print(stderr.read().decode())
        # time.sleep(3)
        
        print("\n--- Checking Service Status ---")
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage.service")
        status_out = stdout.read().decode()
        print(status_out)
        
        print("\n--- Logs ---")
        stdin, stdout, stderr = client.exec_command("journalctl -u sustainage.service -n 200 --no-pager")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_status()
