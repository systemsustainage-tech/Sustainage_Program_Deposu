
import paramiko
import sys
import time

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def deploy_fixes():
    print(f"Connecting to {hostname}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        # Deploy web_app.py
        local_path = r'c:\SUSTAINAGESERVER\web_app.py'
        remote_path = '/var/www/sustainage/web_app.py'
        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)

        # Deploy unified_report_docx.py
        local_path = r'c:\SUSTAINAGESERVER\backend\modules\reporting\unified_report_docx.py'
        remote_path = '/var/www/sustainage/backend/modules/reporting/unified_report_docx.py'
        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
        
        sftp.close()

        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command('systemctl restart sustainage')
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Service restart failed: {stderr.read().decode()}")

    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_fixes()
