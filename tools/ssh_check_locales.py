import paramiko
import os

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def check_locales():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)
    
    stdin, stdout, stderr = ssh.exec_command("ls -F /var/www/sustainage/locales/")
    out = stdout.read().decode()
    err = stderr.read().decode()
    
    print("Output:", out)
    print("Error:", err)
    
    ssh.close()

if __name__ == "__main__":
    check_locales()
