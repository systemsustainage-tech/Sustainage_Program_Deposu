import paramiko
import os
import hashlib
import logging

# Configuration
HOST = '72.62.150.207'
PORT = 22
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
LOCAL_DIR = r'c:\SDG'
REMOTE_DIR = '/var/www/sustainage'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def get_local_checksums(directory):
    checksums = {}
    for root, _, files in os.walk(directory):
        if '.git' in root or '__pycache__' in root or 'venv' in root:
            continue
        for file in files:
            if file.endswith(('.py', '.html', '.css', '.js', '.json', '.sql')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    rel_path = os.path.relpath(filepath, directory).replace('\\', '/')
                    checksums[rel_path] = file_hash
                except Exception as e:
                    logging.warning(f"Could not read {filepath}: {e}")
    return checksums

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        logging.info("Calculating local checksums...")
        local_checksums = get_local_checksums(LOCAL_DIR)
        logging.info(f"Found {len(local_checksums)} relevant local files.")

        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        
        logging.info("Calculating remote checksums (this might take a moment)...")
        # Python script to run on server to get checksums
        remote_script = """
import os
import hashlib
import json

directory = '/var/www/sustainage'
checksums = {}

for root, _, files in os.walk(directory):
    if '.git' in root or '__pycache__' in root or 'venv' in root or 'logs' in root:
        continue
    for file in files:
        if file.endswith(('.py', '.html', '.css', '.js', '.json', '.sql')):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                rel_path = os.path.relpath(filepath, directory)
                checksums[rel_path] = file_hash
            except:
                pass

print(json.dumps(checksums))
"""
        stdin, stdout, stderr = client.exec_command(f"python3 -c \"{remote_script}\"")
        remote_output = stdout.read().decode()
        err_output = stderr.read().decode()
        
        if err_output:
            logging.error(f"Remote error: {err_output}")
        
        import json
        remote_checksums = json.loads(remote_output)
        logging.info(f"Found {len(remote_checksums)} relevant remote files.")
        
        # Compare
        missing_on_remote = []
        different_content = []
        
        for file, checksum in local_checksums.items():
            # Adjust path for server structure mapping if necessary
            # Assuming c:\SDG maps directly to /var/www/sustainage root for now
            # But we know c:\SDG\server maps to /var/www/sustainage usually
            
            # Let's handle the mapping logic:
            # Local: c:\SDG\server\* -> Remote: /var/www/sustainage/*
            # Local: c:\SDG\modules\* -> Remote: /var/www/sustainage/backend/modules/* or /var/www/sustainage/modules/*?
            # Based on previous context, user wants exact mirror of c:\SDG structure BUT server structure is different.
            # We need to be careful. The user said "c:\sdg altında çalışan program ile, sunucudaki programın dosyalarının tamamını karşılaştır"
            
            # Simplified check: Just check if the file exists remotely with same path first
            # If not, we might need to map it.
            
            # Common mapping based on previous tasks:
            # c:\SDG\server\* -> /var/www/sustainage/*
            # c:\SDG\modules\* -> /var/www/sustainage/backend/modules/* (sometimes)
            
            remote_file_path = file
            
            # Adjust for server structure (server content is root in /var/www/sustainage)
            if file.startswith('server/'):
                remote_file_path = file[7:] # Remove 'server/' prefix
            
            if remote_file_path not in remote_checksums:
                missing_on_remote.append(file)
            elif remote_checksums[remote_file_path] != checksum:
                different_content.append(file)
                
        print("\n--- MISSING ON REMOTE (Top 50) ---")
        for f in missing_on_remote[:50]:
            print(f)
            
        print("\n--- DIFFERENT CONTENT (Top 50) ---")
        for f in different_content[:50]:
            print(f)
            
        print(f"\nTotal Missing: {len(missing_on_remote)}")
        print(f"Total Different: {len(different_content)}")

        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
