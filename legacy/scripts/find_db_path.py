import paramiko

def find_db_path():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        print("Searching for .db in web_app.py:")
        stdin, stdout, stderr = client.exec_command("grep '.db' /var/www/sustainage/web_app.py")
        print(stdout.read().decode())
        
        print("\nSearching for DATABASE in web_app.py:")
        stdin, stdout, stderr = client.exec_command("grep 'DATABASE' /var/www/sustainage/web_app.py")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    find_db_path()
