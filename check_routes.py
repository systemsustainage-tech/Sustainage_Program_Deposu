import paramiko

def check_routes():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        cmd = "grep -n '@app.route' /var/www/sustainage/web_app.py | grep 'report'"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_routes()
