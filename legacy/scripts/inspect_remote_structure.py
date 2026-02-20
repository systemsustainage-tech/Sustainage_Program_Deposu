import paramiko
import time

def inspect_remote():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'  # Using known credentials

    print(f"Connecting to {hostname}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        # 1. List modules directory
        print("\nListing /var/www/sustainage/modules:")
        stdin, stdout, stderr = client.exec_command("ls -F /var/www/sustainage/modules")
        print(stdout.read().decode())
        
        # 2. Grep for blueprint registrations in web_app.py or similar
        print("\nSearching for register_blueprint in /var/www/sustainage/web_app.py:")
        stdin, stdout, stderr = client.exec_command("grep -n 'register_blueprint' /var/www/sustainage/web_app.py")
        print(stdout.read().decode())

        # 3. Check for other potential main files if web_app.py doesn't have it
        print("\nListing /var/www/sustainage/*.py:")
        stdin, stdout, stderr = client.exec_command("ls -F /var/www/sustainage/*.py")
        print(stdout.read().decode())

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    inspect_remote()
