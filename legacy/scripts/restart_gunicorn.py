import paramiko

def restart_service():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("Service status:")
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    restart_service()
