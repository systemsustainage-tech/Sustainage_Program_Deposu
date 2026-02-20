import paramiko
import os

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_ed25519")

print(f"Testing connection to {HOST} with key {KEY_FILE}")

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, key_filename=KEY_FILE)
    print("Connected successfully!")
    stdin, stdout, stderr = ssh.exec_command("ls -la /var/www/sustainage")
    print(stdout.read().decode())
    ssh.close()
except Exception as e:
    print(f"Connection failed: {e}")
