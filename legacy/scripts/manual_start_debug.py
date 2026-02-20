import paramiko

def manual_start():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        print("Attempting manual start to see error...")
        cmd = "cd /var/www/sustainage && venv/bin/gunicorn --workers 1 --bind 0.0.0.0:5000 web_app:app"
        stdin, stdout, stderr = client.exec_command(cmd)
        
        # Read a bit of output
        print("STDOUT:", stdout.read().decode())
        print("STDERR:", stderr.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    manual_start()
