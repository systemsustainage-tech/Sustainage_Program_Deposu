import paramiko

def download_dashboard():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)
    
    sftp = client.open_sftp()
    
    remote_path = '/var/www/sustainage/templates/dashboard.html'
    local_path = 'c:\\SUSTAINAGESERVER\\dashboard_local.html'
    
    print(f"Downloading {remote_path} to {local_path}...")
    sftp.get(remote_path, local_path)
    print("Download complete.")
    
    sftp.close()
    client.close()

if __name__ == "__main__":
    download_dashboard()
