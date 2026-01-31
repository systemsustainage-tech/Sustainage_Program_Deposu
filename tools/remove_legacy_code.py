import paramiko
import time

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=username, password=password)

print("Stopping service...")
ssh.exec_command("systemctl stop sustainage")
time.sleep(2)

print("Deleting legacy directories...")
# Careful with rm -rf!
ssh.exec_command("rm -rf /var/www/sustainage/modules")
ssh.exec_command("rm -rf /var/www/sustainage/backend/modules/water_management")

print("Cleaning __pycache__ again...")
ssh.exec_command("find /var/www/sustainage -name '__pycache__' -type d -exec rm -rf {} +")
ssh.exec_command("find /var/www/sustainage -name '*.pyc' -delete")

print("Starting service...")
ssh.exec_command("systemctl start sustainage")
time.sleep(2)

print("Legacy cleanup complete.")
ssh.close()
