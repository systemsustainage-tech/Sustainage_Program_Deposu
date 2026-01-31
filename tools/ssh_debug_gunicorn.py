
import paramiko

# SSH Credentials
HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def debug_gunicorn():
    print(f"Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)
    
    # 1. Check Gunicorn Content (Shebang)
    print("Reading first line of gunicorn...")
    stdin, stdout, stderr = ssh.exec_command("head -n 1 /var/www/sustainage/venv/bin/gunicorn")
    shebang = stdout.read().decode().strip()
    print(f"Shebang: {shebang}")
    
    if shebang.startswith('#!'):
        interpreter = shebang[2:].strip()
        print(f"Interpreter path: {interpreter}")
        
        # 2. Check Interpreter Existence and Perms
        print(f"Checking interpreter {interpreter}...")
        stdin, stdout, stderr = ssh.exec_command(f"ls -l {interpreter}")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        # Check if it is a symlink
        stdin, stdout, stderr = ssh.exec_command(f"file {interpreter}")
        print(stdout.read().decode())
    
    # 3. Check Gunicorn Permissions again
    print("Checking Gunicorn permissions again...")
    stdin, stdout, stderr = ssh.exec_command("ls -l /var/www/sustainage/venv/bin/gunicorn")
    print(stdout.read().decode())

    ssh.close()

if __name__ == "__main__":
    debug_gunicorn()
