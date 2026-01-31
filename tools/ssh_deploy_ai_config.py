import paramiko
import os
import sys

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def deploy_ai_config():
    print("--- Deploying AI Configuration ---")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)
    sftp = ssh.open_sftp()
    
    # 1. Upload Google Key
    local_key = r'C:\SUSTAINAGESERVER\config\google_key.json'
    remote_key = '/var/www/sustainage/config/google_key.json'
    
    if os.path.exists(local_key):
        print(f"Uploading {local_key} to {remote_key}")
        try:
            sftp.put(local_key, remote_key)
            ssh.exec_command(f"chmod 600 {remote_key}")
            print("Google Key uploaded successfully.")
        except Exception as e:
            print(f"Error uploading Google Key: {e}")
    else:
        print(f"Local Google Key not found at {local_key}")

    # 2. Update .env
    env_path = '/var/www/sustainage/.env'
    print(f"Updating {env_path}")
    
    try:
        # Read existing .env
        stdin, stdout, stderr = ssh.exec_command(f"cat {env_path}")
        current_env = stdout.read().decode()
        
        new_lines = []
        has_google = False
        has_openai = False
        
        for line in current_env.splitlines():
            if line.startswith('GOOGLE_APPLICATION_CREDENTIALS='):
                has_google = True
                # Update path just in case
                new_lines.append(f"GOOGLE_APPLICATION_CREDENTIALS={remote_key}")
            elif line.startswith('OPENAI_API_KEY='):
                has_openai = True
                new_lines.append(line)
            else:
                new_lines.append(line)
        
        if not has_google:
            new_lines.append(f"GOOGLE_APPLICATION_CREDENTIALS={remote_key}")
            print("Added GOOGLE_APPLICATION_CREDENTIALS")
            
        if not has_openai:
            new_lines.append("OPENAI_API_KEY=")
            print("Added OPENAI_API_KEY placeholder")
            
        # Write back
        with sftp.file(env_path, 'w') as f:
            f.write('\n'.join(new_lines) + '\n')
            
        print(".env updated.")
        
    except Exception as e:
        print(f"Error updating .env: {e}")

    # 3. Restart Service
    print("Restarting service...")
    ssh.exec_command("systemctl restart sdg")
    
    # 4. Verify AI Module (Simple Import Test)
    print("Verifying AI Module...")
    verify_script = """
import sys
import os
sys.path.append('/var/www/sustainage')
try:
    from modules.ai.ai_manager import AIManager
    print('AIManager imported.')
    ai = AIManager()
    print(f'AI Available: {ai.is_available()}')
    if not ai.is_available():
        print('Reason: Client is None (likely missing API Key)')
except Exception as e:
    print(f'Error: {e}')
"""
    stdin, stdout, stderr = ssh.exec_command("python3 -c \"" + verify_script.replace('"', '\\"') + "\"")
    print("Verification Output:")
    print(stdout.read().decode())
    print("Verification Errors:")
    print(stderr.read().decode())

    sftp.close()
    ssh.close()

if __name__ == "__main__":
    deploy_ai_config()
