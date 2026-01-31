import paramiko

def search_routes():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        patterns = ["def companies", "def reports", "def messages", "def help", "def gri", "def sdg", "def ifrs"]
        
        for p in patterns:
            stdin, stdout, stderr = client.exec_command(f"grep '{p}' /var/www/sustainage/web_app.py")
            print(f"Search for '{p}':\n{stdout.read().decode()}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    search_routes()
