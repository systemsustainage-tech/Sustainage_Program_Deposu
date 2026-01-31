import paramiko
import os
import time

# Sunucu bilgileri
HOST = "72.62.150.207"
USERNAME = "root"
PASSWORD = "Z/2m?-JDp5VaX6q+HO(b)"

def run_remote_check():
    try:
        # SSH istemcisi oluştur
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"Connecting to {HOST}...")
        client.connect(hostname=HOST, username=USERNAME, password=PASSWORD)
        
        # SFTP istemcisi
        sftp = client.open_sftp()
        
        # Dosya yükle
        local_file = r'c:\SUSTAINAGESERVER\tools\check_db_schema_remote.py'
        remote_file = '/var/www/sustainage/tools/check_db_schema_remote.py'
        
        print(f"Uploading {local_file} to {remote_file}...")
        sftp.put(local_file, remote_file)
        
        # Scripti çalıştır
        print("Running schema check script...")
        stdin, stdout, stderr = client.exec_command('python3 /var/www/sustainage/tools/check_db_schema_remote.py')
        
        print("\n--- Output ---")
        print(stdout.read().decode())
        print("\n--- Errors ---")
        print(stderr.read().decode())
        
        client.close()
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_remote_check()
