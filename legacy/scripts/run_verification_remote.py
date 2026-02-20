import paramiko
import sys
import time

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_remote_verification():
    print(f"Connecting to {hostname}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname, username=username, password=password)
        
        # Upload updated verification script
        sftp = client.open_sftp()
        
        files_to_upload = [
            (r'c:\SUSTAINAGESERVER\tools\verify_full_system.py', '/var/www/sustainage/tools/verify_full_system.py'),
            (r'c:\SUSTAINAGESERVER\web_app.py', '/var/www/sustainage/web_app.py'),
            (r'c:\SUSTAINAGESERVER\backend\modules\reporting\unified_report_docx.py', '/var/www/sustainage/backend/modules/reporting/unified_report_docx.py'),
            (r'c:\SUSTAINAGESERVER\tools\init_missing_tables_remote.py', '/var/www/sustainage/tools/init_missing_tables_remote.py')
        ]
        
        for local, remote in files_to_upload:
            print(f"Uploading {local} to {remote}...")
            sftp.put(local, remote)
            
        sftp.close()

        print("Initializing missing tables...")
        stdin, stdout, stderr = client.exec_command('python3 /var/www/sustainage/tools/init_missing_tables_remote.py')
        print(stdout.read().decode())
        print(stderr.read().decode())

        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command('systemctl restart sustainage')
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Service restart failed: {stderr.read().decode()}")
        
        # Give it a moment to restart
        time.sleep(5)

        print("Running verify_full_system.py on remote...")
        # Run and redirect output
        stdin, stdout, stderr = client.exec_command('python3 /var/www/sustainage/tools/verify_full_system.py > /var/www/sustainage/verification_result.txt 2>&1')
        
        # Wait for completion
        exit_status = stdout.channel.recv_exit_status()
        print(f"Command finished with exit status: {exit_status}")
        
        # Read the result file
        stdin, stdout, stderr = client.exec_command('cat /var/www/sustainage/verification_result.txt')
        output = stdout.read().decode()
        print("Output:")
        print(output)
        
        print("-" * 50)
        print("Fetching recent system logs...")
        stdin, stdout, stderr = client.exec_command('journalctl -u sustainage -n 100 --no-pager')
        logs = stdout.read().decode()
        print(logs)
            
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    run_remote_verification()