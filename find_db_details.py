import paramiko

def find_db_details():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        print("Listing all files in /var/www/sustainage:")
        stdin, stdout, stderr = client.exec_command("ls -F /var/www/sustainage")
        print(stdout.read().decode())
        
        print("\nReading get_db implementation:")
        # Read lines around 'def get_db'
        stdin, stdout, stderr = client.exec_command("grep -A 10 'def get_db' /var/www/sustainage/web_app.py")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    find_db_details()
