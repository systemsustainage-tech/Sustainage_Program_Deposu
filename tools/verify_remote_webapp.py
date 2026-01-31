import paramiko

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=username, password=password)

print("Checking web_app.py imports...")
stdin, stdout, stderr = ssh.exec_command("grep -C 5 'WaterManager' /var/www/sustainage/web_app.py")
print(stdout.read().decode())

ssh.close()
