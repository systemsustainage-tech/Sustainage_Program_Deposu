import paramiko

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=username, password=password)

print("Searching for 'blue_water' on remote...")
stdin, stdout, stderr = ssh.exec_command("grep -r 'blue_water' /var/www/sustainage")
print(stdout.read().decode())
print(stderr.read().decode())

ssh.close()
