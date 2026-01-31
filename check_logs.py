import paramiko

def check_error_logs():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        # Read the last 100 lines of the error log
        cmd = "tail -n 100 /var/www/sustainage/logs/error.log"
        stdin, stdout, stderr = client.exec_command(cmd)
        
        output = stdout.read().decode()
        print(output)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_error_logs()
