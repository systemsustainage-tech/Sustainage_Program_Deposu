import paramiko
import os

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
REMOTE_DIR = '/var/www/sustainage'
LOCAL_SERVICES_DIR = os.path.join(os.getcwd(), 'services')

def deploy():
    try:
        print(f"Connecting to {HOST}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USER, password=PASS)
        print("Connected.")
        
        sftp = client.open_sftp()
        
        # Ensure remote services dir exists
        remote_services_dir = f"{REMOTE_DIR}/services"
        try:
            sftp.stat(remote_services_dir)
        except FileNotFoundError:
            print(f"Creating directory {remote_services_dir}...")
            sftp.mkdir(remote_services_dir)
            
        # Upload files
        files_to_upload = ['email_service.py', 'icons.py', '__init__.py']
        for filename in files_to_upload:
            local_path = os.path.join(LOCAL_SERVICES_DIR, filename)
            remote_path = f"{remote_services_dir}/{filename}"
            if os.path.exists(local_path):
                print(f"Uploading {filename} to {remote_path}...")
                sftp.put(local_path, remote_path)
            else:
                print(f"Warning: {filename} not found locally.")
        
        sftp.close()
        
        print("Files uploaded successfully.")
        
        # Check services
        print("Checking supervisor status...")
        stdin, stdout, stderr = client.exec_command("supervisorctl status")
        supervisor_output = stdout.read().decode()
        print(supervisor_output)
        
        if supervisor_output:
            # Try to restart sustainage service if found
            for line in supervisor_output.splitlines():
                if "sustainage" in line or "web" in line:
                    service_name = line.split()[0]
                    print(f"Restarting service {service_name}...")
                    client.exec_command(f"supervisorctl restart {service_name}")
                    print(f"Service {service_name} restarted.")
        
        client.close()
        print("Deployment complete.")

    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == "__main__":
    deploy()
