import paramiko

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=username, password=password)

print("Checking /var/www/sustainage/modules existence...")
stdin, stdout, stderr = ssh.exec_command("ls -F /var/www/sustainage/modules")
print(stdout.read().decode())
print(stderr.read().decode())

print("Checking /var/www/sustainage/backend/modules existence...")
stdin, stdout, stderr = ssh.exec_command("ls -F /var/www/sustainage/backend/modules")
print(stdout.read().decode())
print(stderr.read().decode())

ssh.close()
