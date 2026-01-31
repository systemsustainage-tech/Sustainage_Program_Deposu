import paramiko
import os

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def fix_502_v2():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        sftp = ssh.open_sftp()
        
        # Upload migration script
        local_path = 'c:/SUSTAINAGESERVER/tools/migrate_company_info.py'
        remote_path = '/var/www/sustainage/tools/migrate_company_info.py'
        print(f"Uploading {local_path}...")
        sftp.put(local_path, remote_path)
        sftp.close()
        
        # Run Migration
        print("Running DB Migration...")
        stdin, stdout, stderr = ssh.exec_command("cd /var/www/sustainage && python3 tools/migrate_company_info.py")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        # Restart Service
        print("Restarting sustainage service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Failed to restart service: {stderr.read().decode()}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    fix_502_v2()
