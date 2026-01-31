import paramiko

def explore():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)
    
    commands = [
        "ls -la /var/www/sustainage",
        "ls -la /var/www/sustainage/venv",
        "python3 -c 'import argon2; print(\"Argon2 available\")' || echo 'Argon2 NOT available'",
        "/var/www/sustainage/venv/bin/python -c 'import argon2; print(\"Venv Argon2 available\")' || echo 'Venv python not found or Argon2 missing'"
    ]
    
    for cmd in commands:
        print(f"Running: {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())
        
    client.close()

if __name__ == "__main__":
    explore()
