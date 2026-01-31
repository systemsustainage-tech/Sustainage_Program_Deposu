import paramiko
import os

HOST = "72.62.150.207"
USER = "root"
PASS = "Z/2m?-JDp5VaX6q+HO(b"

LOCAL_SCRIPT = r"c:\SDG\server\scripts\backup_db.sh"
REMOTE_SCRIPT_DIR = "/var/www/sustainage/server/scripts"
REMOTE_SCRIPT = f"{REMOTE_SCRIPT_DIR}/backup_db.sh"

def setup_backup():
    print("--- Setting up Backup System ---")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        sftp = ssh.open_sftp()
        
        # Create directory
        ssh.exec_command(f"mkdir -p {REMOTE_SCRIPT_DIR}")
        
        # Upload script
        print(f"Uploading {os.path.basename(LOCAL_SCRIPT)}...")
        sftp.put(LOCAL_SCRIPT, REMOTE_SCRIPT)
        sftp.chmod(REMOTE_SCRIPT, 0o755) # Make executable
        
        sftp.close()
        
        # Setup Cron Job
        print("Configuring Cron Job...")
        cron_cmd = f"0 3 * * * {REMOTE_SCRIPT}"
        
        # Check if cron job already exists
        stdin, stdout, stderr = ssh.exec_command("crontab -l")
        current_cron = stdout.read().decode().strip()
        
        if REMOTE_SCRIPT not in current_cron:
            new_cron = f"{current_cron}\n{cron_cmd}\n"
            # Write new cron
            # Use printf to handle newlines correctly
            cmd = f'echo "{new_cron}" | crontab -'
            ssh.exec_command(cmd)
            print("Cron job added.")
        else:
            print("Cron job already exists.")
            
        # Verify
        stdin, stdout, stderr = ssh.exec_command("crontab -l")
        print("\nCurrent Crontab:")
        print(stdout.read().decode())
        
        # Run once to test
        print("Running backup script once to verify...")
        stdin, stdout, stderr = ssh.exec_command(REMOTE_SCRIPT)
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        ssh.close()
        print("--- Backup System Setup Complete ---")
        
    except Exception as e:
        print(f"Setup Failed: {e}")

if __name__ == "__main__":
    setup_backup()
