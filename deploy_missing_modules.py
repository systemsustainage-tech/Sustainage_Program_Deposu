import paramiko
import os
import sys

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
REMOTE_PATH = '/var/www/sustainage'

def deploy():
    print(f"Connecting to {HOST}...")
    transport = paramiko.Transport((HOST, 22))
    transport.connect(username=USER, password=PASS)
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    files_to_upload = [
        ('c:\\SUSTAINAGESERVER\\web_app.py', 'web_app.py'),
        ('c:\\SUSTAINAGESERVER\\templates\\human_rights.html', 'templates/human_rights.html'),
        ('c:\\SUSTAINAGESERVER\\templates\\labor.html', 'templates/labor.html'),
        ('c:\\SUSTAINAGESERVER\\templates\\fair_operating.html', 'templates/fair_operating.html'),
        ('c:\\SUSTAINAGESERVER\\templates\\consumer.html', 'templates/consumer.html'),
        ('c:\\SUSTAINAGESERVER\\templates\\community.html', 'templates/community.html'),
    ]
    
    for local, remote in files_to_upload:
        remote_full = f"{REMOTE_PATH}/{remote}"
        print(f"Uploading {local} to {remote_full}...")
        try:
            sftp.put(local, remote_full)
        except Exception as e:
            print(f"Error uploading {local}: {e}")
            
    sftp.close()
    
    print("Restarting service...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS, look_for_keys=False, allow_agent=False)
    
    stdin, stdout, stderr = ssh.exec_command('systemctl restart sustainage.service')
    exit_status = stdout.channel.recv_exit_status()
    
    if exit_status == 0:
        print("Service restarted successfully.")
    else:
        print(f"Error restarting service: {stderr.read().decode()}")
        
    ssh.close()
    print("Deployment complete.")

if __name__ == "__main__":
    deploy()
