import paramiko
import sys

def ls_remote(path):
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        cmd = f"ls -la {path}"
        print(f"Running: {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "/var/www/sustainage"
    ls_remote(path)
