import paramiko
import os
import sys

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def create_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    return client

def upload_file(sftp, local_path, remote_path):
    print(f"Uploading {local_path} to {remote_path}...")
    sftp.put(local_path, remote_path)
    print("Upload complete.")

def execute_command(client, command):
    print(f"Executing: {command}")
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode()
    err = stderr.read().decode()
    
    if out:
        print(f"Output:\n{out}")
    if err:
        print(f"Error:\n{err}")
    
    if exit_status != 0:
        print(f"Command failed with exit status {exit_status}")
        return False
    return True

def main():
    try:
        print(f"Connecting to {HOST}...")
        client = create_ssh_client()
        sftp = client.open_sftp()
        
        # Paths
        local_populate = r'c:\SUSTAINAGESERVER\populate_kivanc_data.py'
        local_generate = r'c:\SUSTAINAGESERVER\generate_kivanc_report.py'
        remote_populate = '/var/www/sustainage/populate_kivanc_data.py'
        remote_generate = '/var/www/sustainage/generate_kivanc_report.py'
        
        # Upload files
        upload_file(sftp, local_populate, remote_populate)
        upload_file(sftp, local_generate, remote_generate)
        upload_file(sftp, r'c:\SUSTAINAGESERVER\setup_test_user.py', '/var/www/sustainage/setup_test_user.py')
        
        sftp.close()
        
        # Setup Test User
        print("Setting up test user...")
        execute_command(client, "python3 /var/www/sustainage/setup_test_user.py")
        
        # Install python-docx if needed
        print("Checking/Installing python-docx...")
        execute_command(client, "pip3 install python-docx")
        
        # Execute populate script
        print("Running data population...")
        if not execute_command(client, f"python3 {remote_populate}"):
            print("Data population failed. Aborting.")
            return

        # Execute generate script
        print("Running report generation...")
        if not execute_command(client, f"python3 {remote_generate}"):
            print("Report generation failed. Aborting.")
            return
            
        # Verify file existence and permissions
        print("Verifying report file...")
        report_path = '/var/www/sustainage/static/Kivanc_Demir_Celik_Surdurulebilirlik_Raporu_2025.docx'
        execute_command(client, f"ls -l {report_path}")
        
        # Ensure permissions
        execute_command(client, f"chmod 644 {report_path}")
        
        client.close()
        print("\nDeployment and execution successful!")
        print(f"Report should be available at: http://{HOST}/static/Kivanc_Demir_Celik_Surdurulebilirlik_Raporu_2025.docx")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
