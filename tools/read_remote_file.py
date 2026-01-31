import paramiko
import sys

def read_remote(path, start_line, num_lines):
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        cmd = f"sed -n '{start_line},{start_line + num_lines}p' {path}"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        path = '/var/www/sustainage/web_app.py'
        start = 4650
        count = 100
    else:
        path = sys.argv[1]
        start = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        count = int(sys.argv[3]) if len(sys.argv) > 3 else 100
        
    read_remote(path, start, count)
