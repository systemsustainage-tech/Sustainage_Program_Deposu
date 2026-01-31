import paramiko
import os
import sys

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
REMOTE_BASE = '/var/www/sustainage'

def deploy_and_retry():
    try:
        print(f"Connecting to {HOST}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USER, password=PASS)
        sftp = client.open_sftp()
        
        # Define remote script content
        remote_script_content = """
import sys
import os
import logging
import time
from dotenv import load_dotenv

# Add paths
sys.path.insert(0, '/var/www/sustainage')
sys.path.insert(0, '/var/www/sustainage/backend')

# Load .env explicitly
env_path = '/var/www/sustainage/.env'
if os.path.exists(env_path):
    print(f"Loading .env from {env_path}")
    load_dotenv(env_path)
else:
    # Fallback to backend/.env just in case
    backend_env = '/var/www/sustainage/backend/.env'
    if os.path.exists(backend_env):
        print(f"Loading .env from {backend_env}")
        load_dotenv(backend_env)
    else:
        print(f"WARNING: .env not found at {env_path} or {backend_env}")

# Setup logging
logging.basicConfig(level=logging.INFO)

try:
    print("Loading EmailService...")
    try:
        from services.email_service import EmailService
    except ImportError:
        # Fallback for different path structure
        sys.path.append('/var/www/sustainage/backend')
        from services.email_service import EmailService

    print(f"EmailService loaded from: {os.path.abspath(sys.modules['services.email_service'].__file__)}")

    email_service = EmailService()
    
    # Target details
    to_email = "admin@digage.tr"
    user_name = "Admin Digage"
    
    print(f"Retrying sending welcome email to {to_email}...")
    
    # Using the exact same parameters as secure_user_create.py
    success = email_service.send_new_user_welcome(
        to_email=to_email,
        user_name=user_name,
        login_url="https://sustainage.cloud/login",
        program_name="Sustainage SDG Platformu",
        short_description="Hesabınız oluşturuldu ve Sustainage SDG programına erişim sağlandı.",
        reason="Admin tarafından kullanıcı oluşturuldu",
        support_email="sdg@digage.tr"
    )
    
    if success:
        print("SUCCESS: Email sent successfully on retry.")
    else:
        print("FAILURE: Email sending returned False on retry.")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
"""
        
        # Write script to remote
        remote_script_path = f"{REMOTE_BASE}/retry_welcome_email.py"
        print(f"Writing remote script to {remote_script_path}...")
        with sftp.file(remote_script_path, "w") as f:
            f.write(remote_script_content)
            
        # Execute the script
        print("Executing remote script...")
        cmd = f"{REMOTE_BASE}/venv/bin/python {remote_script_path} > /tmp/retry_email.log 2>&1"
        stdin, stdout, stderr = client.exec_command(cmd)
        
        exit_status = stdout.channel.recv_exit_status()
        print(f"Remote command finished with status: {exit_status}")
        
        # Read the log file
        stdin, stdout, stderr = client.exec_command("cat /tmp/retry_email.log")
        out = stdout.read().decode()
        
        print("OUTPUT:")
        print(out)
        
        client.close()
        print("DONE")

    except Exception as e:
        print(f"Deploy/Run failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    deploy_and_retry()
