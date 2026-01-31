import paramiko

def check_data_add():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        print("Checking data_add function in web_app.py...")
        stdin, stdout, stderr = client.exec_command("grep -A 20 'def data_add' /var/www/sustainage/web_app.py")
        content = stdout.read().decode()
        print(content)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_data_add()
