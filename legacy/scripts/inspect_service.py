import paramiko

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def inspect_service():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        
        print("\n--- /etc/systemd/system/sustainage.service ---")
        stdin, stdout, stderr = client.exec_command("cat /etc/systemd/system/sustainage.service")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("\n--- /etc/systemd/system/sustainage_web.service ---")
        stdin, stdout, stderr = client.exec_command("cat /etc/systemd/system/sustainage_web.service")
        print(stdout.read().decode())
        
        print("\n--- ls -F /var/www/sustainage/backend ---")
        stdin, stdout, stderr = client.exec_command("ls -F /var/www/sustainage/backend")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    inspect_service()