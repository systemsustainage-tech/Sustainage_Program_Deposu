import paramiko
import os
import sys

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
REMOTE_BASE = '/var/www/sustainage'

def deploy_and_run():
    try:
        print(f"Connecting to {HOST}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USER, password=PASS)
        sftp = client.open_sftp()
        
        # 1. Upload email_service.py
        local_email = os.path.join('backend', 'services', 'email_service.py')
        remote_email = f"{REMOTE_BASE}/backend/services/email_service.py"
        print(f"Uploading {local_email} to {remote_email}...")
        sftp.put(local_email, remote_email)
        
        # 1.5 Upload email_service.py to root services (where it is actually loaded from)
        remote_email_root = f"{REMOTE_BASE}/services/email_service.py"
        print(f"Uploading {local_email} to {remote_email_root}...")
        sftp.put(local_email, remote_email_root)
        
        # 2. Upload secure_user_create.py
        local_create = os.path.join('backend', 'yonetim', 'kullanici_yonetimi', 'secure_user_create.py')
        remote_create = f"{REMOTE_BASE}/backend/yonetim/kullanici_yonetimi/secure_user_create.py"
        print(f"Uploading {local_create} to {remote_create}...")
        sftp.put(local_create, remote_create)

        # 3. Create remote execution script
        remote_script_content = """
import sys
import os
import logging

# Add paths
sys.path.insert(0, '/var/www/sustainage')
sys.path.insert(0, '/var/www/sustainage/backend')

# Setup logging
logging.basicConfig(level=logging.INFO)

try:
    import services.email_service
    print(f"EmailService loaded from: {services.email_service.__file__}")
    from services.email_service import EmailService
    if hasattr(EmailService, 'send_new_user_welcome'):
        print("EmailService has send_new_user_welcome")
    else:
        print("EmailService MISSING send_new_user_welcome")

    from yonetim.kullanici_yonetimi.secure_user_create import create_user_with_temp_password
    from config.database import DB_PATH
    
    # If DB_PATH is relative or not correct, fix it
    if not os.path.exists(DB_PATH):
        DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
        
    print(f"Using DB: {DB_PATH}")

    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Delete existing user to retry
    cur.execute("DELETE FROM users WHERE username = ?", ('admin_digage',))
    if cur.rowcount > 0:
        print("Deleted existing admin_digage user.")
    conn.commit()
    
    cur.execute("PRAGMA table_info(users)")
    print("Table Schema:")
    for col in cur.fetchall():
        print(col)
    conn.close()
    
    success, msg, uid, pw = create_user_with_temp_password(
        db_path=DB_PATH,
        username='admin_digage',
        email='admin@digage.tr',
        display_name='Admin Digage',
        role='admin',
        is_active=True
    )
    
    if success:
        print("SUCCESS: User created.")
        print(f"User ID: {uid}")
        print(f"Password: {pw}")
        print(f"Message: {msg}")
    else:
        print(f"FAILURE: {msg}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
"""
        
        with sftp.file(f"{REMOTE_BASE}/run_user_create.py", "w") as f:
            f.write(remote_script_content)
            
        print("Remote script created.")
        
        # Verify file exists
        stdin, stdout, stderr = client.exec_command(f"ls -l {REMOTE_BASE}/run_user_create.py")
        print(f"File check: {stdout.read().decode()}")

        # 4. Execute the script
        print("Executing remote script...")
        # Redirect output to file to ensure capture
        cmd = f"{REMOTE_BASE}/venv/bin/python {REMOTE_BASE}/run_user_create.py > /tmp/user_create.log 2>&1"
        stdin, stdout, stderr = client.exec_command(cmd)
        
        exit_status = stdout.channel.recv_exit_status()
        print(f"Remote command finished with status: {exit_status}")
        
        # Read the log file
        stdin, stdout, stderr = client.exec_command("cat /tmp/user_create.log")
        out = stdout.read().decode()
        
        print("OUTPUT:")
        print(out)
        
        client.close()
        print("DONE")
        sys.stdout.flush()

    except Exception as e:
        print(f"Deploy/Run failed: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()

if __name__ == "__main__":
    deploy_and_run()
