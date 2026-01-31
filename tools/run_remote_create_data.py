import paramiko
import os
import sys

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def run_create_data():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected to server.")

        print("Running create_test_survey_data.py...")
        # First ensure the file is up to date on remote
        sftp = client.open_sftp()
        sftp.put(r"C:\SUSTAINAGESERVER\tools\create_test_survey_data.py", "/var/www/sustainage/tools/create_test_survey_data.py")
        sftp.close()
        
        stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/tools/create_test_survey_data.py")
        print("STDOUT:", stdout.read().decode())
        print("STDERR:", stderr.read().decode())
        
        client.close()

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == '__main__':
    run_create_data()
