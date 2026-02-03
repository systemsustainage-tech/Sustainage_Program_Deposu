import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
REMOTE_PATH = "/var/www/sustainage"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

# Directories to sync (recursive)
DIRS_TO_SYNC = ["templates", "anket", "tools", "locales", "static", "backend", "TESTLER", "tests"]
# Files to sync (in root)
FILES_TO_SYNC = ["web_app.py", "requirements.txt", "wsgi.py", "gunicorn_config.py", "mocks_for_missing_deps.py", "target_schema.sql"]

# Exclude patterns
EXCLUDE_EXT = ['.pyc', '.pyo', '.git', '.DS_Store', '.sqlite', '.db']
EXCLUDE_DIRS = ['__pycache__', 'node_modules', 'venv', '.git', '.idea', '.vscode', 'data']

def should_skip(name):
    if name in EXCLUDE_DIRS:
        return True
    if any(name.endswith(ext) for ext in EXCLUDE_EXT):
        return True
    return False

def deploy():
    print(f"Starting deployment to {HOST}:{REMOTE_PATH}...")
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Check for key file
        if not os.path.exists(KEY_FILE):
             print(f"Warning: Default SSH key not found at {KEY_FILE}")
             # We might still try to connect if agent is active?
             # paramiko usually needs key_filename or look_for_keys=True
        
        try:
            ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
        except paramiko.AuthenticationException:
            print("Authentication failed. Please check your SSH keys.")
            return
        except Exception as e:
            print(f"Connection failed: {e}")
            return

        sftp = ssh.open_sftp()
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        print("Connected. Uploading files...")

        # 1. Upload Root Files
        for f in FILES_TO_SYNC:
            local_path = os.path.join(base_dir, f)
            if os.path.exists(local_path):
                remote_file = f"{REMOTE_PATH}/{f}"
                print(f"Uploading {f} -> {remote_file}")
                sftp.put(local_path, remote_file)
        
        # 2. Upload Directories
        for d in DIRS_TO_SYNC:
            local_dir = os.path.join(base_dir, d)
            if not os.path.exists(local_dir):
                continue
                
            remote_dir_base = f"{REMOTE_PATH}/{d}"
            
            # Walk local dir
            for root, dirs, files in os.walk(local_dir):
                # Filter excluded dirs in-place
                dirs[:] = [d for d in dirs if not should_skip(d)]
                
                rel_path = os.path.relpath(root, local_dir)
                if rel_path == ".":
                    current_remote_dir = remote_dir_base
                else:
                    current_remote_dir = f"{remote_dir_base}/{rel_path.replace(os.sep, '/')}"
                
                # Ensure remote dir exists
                try:
                    sftp.stat(current_remote_dir)
                except IOError:
                    # Create directory
                    try:
                        sftp.mkdir(current_remote_dir)
                    except:
                        # Parent might not exist, but usually base structure exists
                        pass

                for file in files:
                    if should_skip(file):
                        continue
                        
                    local_file_path = os.path.join(root, file)
                    remote_file_path = f"{current_remote_dir}/{file}"
                    
                    try:
                        # Simple check: timestamp or size? 
                        # For now, just overwrite to ensure latest version
                        sftp.put(local_file_path, remote_file_path)
                        # print(f"Uploaded {file}") 
                    except Exception as e:
                        print(f"Failed to upload {file}: {e}")

        print("Files uploaded.")
        
        # 3. Restart Service
        print("Restarting service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("✅ Service restarted successfully.")
        else:
            print(f"❌ Error restarting service: {stderr.read().decode()}")

        sftp.close()
        ssh.close()
        print("Deployment finished.")

    except Exception as e:
        print(f"Deployment Error: {e}")

if __name__ == "__main__":
    deploy()
