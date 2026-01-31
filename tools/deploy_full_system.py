import paramiko
import os
import time
import fnmatch

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = '321'
REMOTE_BASE_DIR = '/var/www/sustainage'
LOCAL_BASE_DIR = r'c:\SUSTAINAGESERVER'

# Patterns to exclude
EXCLUDE_PATTERNS = [
    '*.pyc',
    '__pycache__',
    '.git',
    '.trae',
    'venv',
    'node_modules',
    '*.sqlite',
    '*.db',
    '*.log',
    '.DS_Store',
    'test_output*',
    'temp_*',
    'data/*.sqlite',
    'backend/data/*.sqlite',
    'backend/data/*.db',
    'server_log*',
    'error_log*',
    'output.log'
]

# Specific directories to include (to avoid scanning irrelevant root stuff if any)
# Actually, better to scan root and exclude.
# But root has many temp scripts.
# Let's define what constitutes the "Program":
# - web_app.py
# - backend/
# - templates/
# - static/
# - config/
# - locales/
# - utils/ (if exists in root)
# - requirements.txt
# - sustainage.md (maybe documentation?)

INCLUDED_ROOT_FILES = [
    'web_app.py',
    'requirements.txt',
    'sustainage.md',
    'PLANNED_IMPROVEMENTS.md',
    'REPORTING_GAPS_PLAN.md'
]

INCLUDED_DIRS = [
    'backend',
    'templates',
    'static',
    'config',
    'locales',
    'mapping',
    'services', # Saw this in LS
    'modules', # Saw this in LS
    'utils', # If exists
    'tools' # User said "bütün güncel dosyaları", tools might be useful for debugging remote
]

def should_exclude(path):
    name = os.path.basename(path)
    # Check strict excludes
    for pattern in EXCLUDE_PATTERNS:
        if fnmatch.fnmatch(name, pattern):
            return True
        # Check path-based excludes (e.g. data/*.sqlite)
        # Relativize path
        try:
            rel_path = os.path.relpath(path, LOCAL_BASE_DIR).replace('\\', '/')
            if fnmatch.fnmatch(rel_path, pattern):
                return True
        except:
            pass
    return False

def deploy():
    print(f"Connecting to {HOSTNAME}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        sftp = ssh.open_sftp()
        
        # 1. Deploy Root Files
        print("Deploying root files...")
        for filename in INCLUDED_ROOT_FILES:
            local_path = os.path.join(LOCAL_BASE_DIR, filename)
            if os.path.exists(local_path):
                remote_path = f"{REMOTE_BASE_DIR}/{filename}"
                print(f"  {filename}")
                sftp.put(local_path, remote_path)
        
        # 2. Deploy Directories
        for dir_name in INCLUDED_DIRS:
            local_dir_path = os.path.join(LOCAL_BASE_DIR, dir_name)
            if not os.path.exists(local_dir_path):
                continue
                
            print(f"Deploying directory: {dir_name}...")
            
            # Walk through the directory
            for root, dirs, files in os.walk(local_dir_path):
                # Remove excluded dirs in-place
                dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
                
                # Get relative path from LOCAL_BASE_DIR
                rel_dir = os.path.relpath(root, LOCAL_BASE_DIR).replace('\\', '/')
                remote_dir = f"{REMOTE_BASE_DIR}/{rel_dir}"
                
                # Ensure remote dir exists
                try:
                    sftp.stat(remote_dir)
                except FileNotFoundError:
                    # Create directory
                    # Note: mkdir usually creates only one level. For deep nesting, might need recursion or 'mkdir -p' via exec
                    # Using exec_command for mkdir -p is safer/easier
                    ssh.exec_command(f"mkdir -p {remote_dir}")
                    # Give it a split second?
                    pass

                for file in files:
                    file_path = os.path.join(root, file)
                    if should_exclude(file_path):
                        continue
                        
                    rel_file = os.path.relpath(file_path, LOCAL_BASE_DIR).replace('\\', '/')
                    remote_file_path = f"{REMOTE_BASE_DIR}/{rel_file}"
                    
                    try:
                        sftp.put(file_path, remote_file_path)
                        # print(f"  Uploaded: {rel_file}") # Too verbose for thousands of files
                    except Exception as e:
                        print(f"  Failed to upload {rel_file}: {e}")
                        
            print(f"  Finished {dir_name}")

        print("Restarting Sustainage Service...")
        ssh.exec_command("systemctl restart sustainage.service")
        print("Deployment Complete.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    deploy()
