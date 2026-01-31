import paramiko
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def run_remote_fix():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOSTNAME}...")
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD, banner_timeout=30)
        
        print("Executing tools/fix_remote_schema_final.py...")
        stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/tools/fix_remote_schema_final.py")
        
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        print("Output:")
        print(output)
        
        if error:
            print("Error:")
            print(error)
            
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    run_remote_fix()
