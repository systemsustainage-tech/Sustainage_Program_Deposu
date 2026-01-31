import paramiko

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def get_logs():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname, username=username, password=password)
        stdin, stdout, stderr = client.exec_command('journalctl -u sustainage -n 50 --no-pager')
        print(stdout.read().decode())
    finally:
        client.close()

if __name__ == "__main__":
    get_logs()
