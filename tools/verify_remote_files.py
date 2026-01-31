import paramiko

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=username, password=password)

print("Checking social_manager.py...")
stdin, stdout, stderr = ssh.exec_command("grep 'def get_training_hours_per_employee' /var/www/sustainage/backend/modules/social/social_manager.py")
print(stdout.read().decode())

print("Checking water_manager.py blue_water...")
stdin, stdout, stderr = ssh.exec_command("grep 'blue_water' /var/www/sustainage/backend/modules/environmental/water_manager.py")
print(stdout.read().decode())

ssh.close()
