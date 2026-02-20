import paramiko

def download_reports_template():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        remote_path = "/var/www/sustainage/templates/reports.html"
        local_path = "c:\\SUSTAINAGESERVER\\reports.html"
        
        print(f"Downloading {remote_path} to {local_path}...")
        sftp.get(remote_path, local_path)
        print("Download complete.")
        
        sftp.close()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    download_reports_template()
