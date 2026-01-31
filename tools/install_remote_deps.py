import paramiko

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b)'

def install_deps():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print(f"Connected to {HOSTNAME}")

        print("Installing dependencies...")
        stdin, stdout, stderr = client.exec_command("python3 -m pip install beautifulsoup4 requests --break-system-packages")
        
        # Stream output
        print(stdout.read().decode())
        print(stderr.read().decode())

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    install_deps()
