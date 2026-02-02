import paramiko
import os
import glob

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

LOCAL_BASE = r"c:\SUSTAINAGESERVER"
REMOTE_BASE = "/var/www/sustainage"

# List of specific files to deploy
SPECIFIC_FILES = [
    "web_app.py",
    "templates/reports.html",
    "templates/dashboard.html",
    "templates/base.html",
    "templates/social.html",
    "templates/prioritization.html",
    "templates/tcfd.html",
    "templates/surveys.html",
    "templates/ungc.html",
    "templates/sdg.html",
    "templates/issb.html",
    "templates/gri.html",
    "templates/esg.html",
    "templates/targets.html",
    "templates/reporting_journey.html",
    "templates/mapping.html"
]

# Directories to sync (recursively)
DIRS_TO_SYNC = [
    "locales",
    "backend/locales"
]

def deploy():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        sftp = ssh.open_sftp()
        
        # 1. Deploy specific files
        print("Deploying specific application files...")
        for rel_path in SPECIFIC_FILES:
            local_path = os.path.join(LOCAL_BASE, rel_path)
            remote_path = f"{REMOTE_BASE}/{rel_path.replace(os.sep, '/')}"
            
            if os.path.exists(local_path):
                print(f"Uploading {rel_path}...")
                try:
                    sftp.put(local_path, remote_path)
                except Exception as e:
                    print(f"Error uploading {rel_path}: {e}")
            else:
                print(f"Warning: Local file not found: {local_path}")

        # 2. Deploy directories (locales)
        print("Deploying translation directories...")
        for dir_name in DIRS_TO_SYNC:
            local_dir = os.path.join(LOCAL_BASE, dir_name)
            if not os.path.exists(local_dir):
                print(f"Warning: Directory not found {local_dir}")
                continue
                
            # Walk through local directory
            for root, dirs, files in os.walk(local_dir):
                for file in files:
                    if file.endswith('.bak'): continue # Skip backup files
                    
                    local_file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(local_file_path, LOCAL_BASE)
                    remote_file_path = f"{REMOTE_BASE}/{rel_path.replace(os.sep, '/')}"
                    
                    # Ensure remote directory exists
                    remote_dir = os.path.dirname(remote_file_path)
                    try:
                        sftp.stat(remote_dir)
                    except FileNotFoundError:
                        # Simple recursive mkdir for remote
                        parts = remote_dir.split('/')
                        path = ""
                        for part in parts:
                            if not part: continue
                            path += "/" + part
                            try:
                                sftp.stat(path)
                            except FileNotFoundError:
                                sftp.mkdir(path)
                    
                    print(f"Uploading {rel_path}...")
                    sftp.put(local_file_path, remote_file_path)
        
        sftp.close()
        
        # 3. Restart Service
        print("Restarting service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        
        if out: print(f"Output: {out}")
        if err: print(f"Error: {err}")
        
        # Verify status
        stdin, stdout, stderr = ssh.exec_command("systemctl is-active sustainage")
        status = stdout.read().decode().strip()
        print(f"Service status: {status}")
        
        ssh.close()
        print("Deploy completed successfully.")
        
    except Exception as e:
        print(f"Deploy failed: {str(e)}")

if __name__ == "__main__":
    deploy()
