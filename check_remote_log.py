import paramiko
import sys

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def check_log():
    try:
        print(f"Connecting to {HOST}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USER, password=PASS)
        
        print("Reading /tmp/retry_email.log...")
        stdin, stdout, stderr = client.exec_command("cat /tmp/retry_email.log")
        out = stdout.read().decode()
        print("--- LOG CONTENT ---")
        print(out)
        print("-------------------")
        
        client.close()

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    check_log()
