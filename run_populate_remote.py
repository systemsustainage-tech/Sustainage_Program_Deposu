import paramiko

def run_populate_remote():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)
    
    sftp = client.open_sftp()
    
    local_path = 'c:\\SUSTAINAGESERVER\\populate_kivanc_data.py'
    remote_path = '/var/www/sustainage/populate_kivanc_data_fixed.py'
    
    print(f"Uploading {local_path} to {remote_path}...")
    sftp.put(local_path, remote_path)
    
    print("Running populate script remotely...")
    stdin, stdout, stderr = client.exec_command(f"python3 {remote_path}")
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    sftp.close()
    client.close()

if __name__ == "__main__":
    run_populate_remote()
