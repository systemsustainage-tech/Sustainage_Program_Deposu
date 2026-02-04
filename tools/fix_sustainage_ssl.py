import os
import subprocess
import time

# Configuration
REMOTE_HOST = "root@72.62.150.207"
LOCAL_CONF = "deploy/sustainage_ssl.nginx"
REMOTE_CONF = "/etc/nginx/sites-available/sustainage"
PATH_EXPORT = "export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin;"

def run_command(command, is_ssh=False):
    full_cmd = command
    if is_ssh:
        raw_cmd = command.replace(f"ssh {REMOTE_HOST} ", "").strip()
        if raw_cmd.startswith("'") and raw_cmd.endswith("'"):
            raw_cmd = raw_cmd[1:-1]
        elif raw_cmd.startswith('"') and raw_cmd.endswith('"'):
            raw_cmd = raw_cmd[1:-1]
            
        full_cmd = f'ssh {REMOTE_HOST} "{PATH_EXPORT} {raw_cmd}"'
    
    print(f"Running: {full_cmd}")
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Success: {result.stdout}")
    return True

def fix_ssl():
    print("--- Fixing SSL for sustainage.cloud ---")
    
    # 1. Upload new config
    print("Uploading Nginx config...")
    cmd = f"scp {LOCAL_CONF} {REMOTE_HOST}:{REMOTE_CONF}"
    if not run_command(cmd):
        print("Failed to upload config.")
        return

    # 2. Link if not exists (it should exist, but let's ensure)
    print("Ensuring symlink...")
    run_command(f"ssh {REMOTE_HOST} 'ln -sf {REMOTE_CONF} /etc/nginx/sites-enabled/sustainage'", is_ssh=True)

    # 3. Test Config
    print("Testing Nginx config...")
    if not run_command(f"ssh {REMOTE_HOST} 'nginx -t'", is_ssh=True):
        print("Config check failed! Aborting reload.")
        return

    # 4. Reload Nginx
    print("Reloading Nginx...")
    run_command(f"ssh {REMOTE_HOST} 'systemctl reload nginx'", is_ssh=True)
    
    print("Done. https://sustainage.cloud should now work.")

if __name__ == "__main__":
    fix_ssl()
