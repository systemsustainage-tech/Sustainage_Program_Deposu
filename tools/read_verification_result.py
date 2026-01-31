import paramiko

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def read_result():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname, username=username, password=password)
        stdin, stdout, stderr = client.exec_command('cat /var/www/sustainage/verification_result.txt')
        print(stdout.read().decode())
    finally:
        client.close()

if __name__ == "__main__":
    read_result()
