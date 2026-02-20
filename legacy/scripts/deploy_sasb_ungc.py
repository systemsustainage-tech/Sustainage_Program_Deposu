import paramiko
import os
import time

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

FILES_TO_UPLOAD = [
    # SASB Files
    {'local': r'c:\SUSTAINAGESERVER\backend\modules\sasb\sasb_manager.py', 'remote': '/var/www/sustainage/backend/modules/sasb/sasb_manager.py'},
    {'local': r'c:\SUSTAINAGESERVER\backend\modules\sasb\data\sasb_gri_mapping.json', 'remote': '/var/www/sustainage/backend/modules/sasb/data/sasb_gri_mapping.json'},
    {'local': r'c:\SUSTAINAGESERVER\backend\modules\sasb\data\sasb_disclosure_topics.json', 'remote': '/var/www/sustainage/backend/modules/sasb/data/sasb_disclosure_topics.json'},
    {'local': r'c:\SUSTAINAGESERVER\backend\modules\sasb\data\sasb_metrics.json', 'remote': '/var/www/sustainage/backend/modules/sasb/data/sasb_metrics.json'},
    
    # UNGC Files
    {'local': r'c:\SUSTAINAGESERVER\backend\modules\ungc\ungc_manager.py', 'remote': '/var/www/sustainage/backend/modules/ungc/ungc_manager.py'},
    {'local': r'c:\SUSTAINAGESERVER\backend\modules\ungc\ungc_gui.py', 'remote': '/var/www/sustainage/backend/modules/ungc/ungc_gui.py'},
    
    # Web App & Templates
    {'local': r'c:\SUSTAINAGESERVER\web_app.py', 'remote': '/var/www/sustainage/web_app.py'},
    {'local': r'c:\SUSTAINAGESERVER\templates\ungc.html', 'remote': '/var/www/sustainage/templates/ungc.html'},
    
    # Verification Tools
    {'local': r'c:\SUSTAINAGESERVER\tools\verify_ungc_evidence.py', 'remote': '/var/www/sustainage/tools/verify_ungc_evidence.py'},
    {'local': r'c:\SUSTAINAGESERVER\tools\verify_sasb_ungc_final.py', 'remote': '/var/www/sustainage/tools/verify_sasb_ungc_final.py'}
]

def deploy():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        sftp = client.open_sftp()
        
        print("Starting deployment...")
        
        for item in FILES_TO_UPLOAD:
            local_path = item['local']
            remote_path = item['remote']
            
            # Ensure local file exists
            if not os.path.exists(local_path):
                print(f"Warning: Local file not found: {local_path}")
                continue
                
            # Ensure remote directory exists
            remote_dir = os.path.dirname(remote_path)
            try:
                sftp.stat(remote_dir)
            except FileNotFoundError:
                print(f"Creating remote directory: {remote_dir}")
                client.exec_command(f"mkdir -p {remote_dir}")
                time.sleep(0.5)
            
            print(f"Uploading {os.path.basename(local_path)} -> {remote_path}")
            sftp.put(local_path, remote_path)
            
        sftp.close()
        
        print("\nRestarting 'sustainage' service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Services restarted successfully.")
        else:
            print("Error restarting services:")
            print(stderr.read().decode())
            
        print("\nRunning verification on remote server...")
        # Verify UNGC
        stdin, stdout, stderr = client.exec_command("cd /var/www/sustainage && python3 tools/verify_ungc_evidence.py")
        print("--- UNGC Verification Output ---")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err: print(f"Errors: {err}")

        # Verify SASB
        stdin, stdout, stderr = client.exec_command("cd /var/www/sustainage && python3 tools/verify_sasb_ungc_final.py")
        print("--- SASB Verification Output ---")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err: print(f"Errors: {err}")

        client.close()
        print("\nDeployment sequence completed.")
        
    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == "__main__":
    deploy()
