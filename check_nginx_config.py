import paramiko

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def create_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    return client

def execute_command(client, command):
    print(f"Executing: {command}")
    stdin, stdout, stderr = client.exec_command(command)
    out = stdout.read().decode()
    if out:
        print(f"Output:\n{out}")
    else:
        print("No output.")

def main():
    try:
        print(f"Connecting to {HOST}...")
        client = create_ssh_client()
        
        print("Listing Nginx sites-enabled...")
        execute_command(client, "ls -F /etc/nginx/sites-enabled/")
        
        # Try to cat the first file found if any, or check sustainage.conf
        execute_command(client, "cat /etc/nginx/sites-enabled/*")
        
        print("Checking static directory permissions...")
        execute_command(client, "ls -ld /var/www/sustainage/static")
        
        client.close()
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
