import os
import subprocess
import sys

# Remote paths
BACKUP_SCRIPT = "/var/www/sustainage/tools/backup_manager.py"
PYTHON_CMD = "/usr/bin/python3"
LOG_FILE = "/var/www/sustainage/logs/backup.log"

# Create logs directory if it doesn't exist
LOG_DIR = os.path.dirname(LOG_FILE)
if not os.path.exists(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
        print(f"Created log directory: {LOG_DIR}")
    except Exception as e:
        print(f"Error creating log directory: {e}")

CRON_CMD = f"0 3 * * * {PYTHON_CMD} {BACKUP_SCRIPT} >> {LOG_FILE} 2>&1"

def setup_cron():
    print("Checking crontab for backup job...")
    
    # List current cron jobs
    try:
        # crontab -l returns exit code 1 if no crontab exists for user
        current_crontab = subprocess.check_output(["crontab", "-l"], text=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        current_crontab = "" # No crontab for user
    except Exception as e:
        print(f"Error reading crontab: {e}")
        return

    if "backup_manager.py" in current_crontab:
        print("Backup cron job already exists.")
        print(f"Current entry matching script: {[line for line in current_crontab.splitlines() if 'backup_manager.py' in line]}")
        return

    # Append new job
    new_crontab = current_crontab.strip() + "\n" + CRON_CMD + "\n"
    
    print(f"Adding cron job: {CRON_CMD}")
    
    # Write back
    try:
        process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(input=new_crontab)
        
        if process.returncode == 0:
            print("Backup cron job added successfully.")
        else:
            print(f"Failed to add backup cron job. Error: {stderr}")
    except Exception as e:
        print(f"Error writing crontab: {e}")

if __name__ == "__main__":
    setup_cron()
