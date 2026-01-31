import paramiko

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=username, password=password)

print("Searching for error string on remote...")
# Use single quotes for grep argument, so double quotes inside are fine.
stdin, stdout, stderr = ssh.exec_command("grep -r 'Su ayak izi hesaplama hatası' /var/www/sustainage")
print(stdout.read().decode())
print(stderr.read().decode())

ssh.close()
