import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def check_status():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Use the same logic as restart_service.py
        key_filename = KEY_FILE if os.path.exists(KEY_FILE) else None
        client.connect(HOST, username=USER, key_filename=key_filename)
        
        print(f"Connected to {HOST}. Checking service status...")
        
        # Check status
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage --no-pager")
        status_out = stdout.read().decode()
        status_err = stderr.read().decode()
        print("\n--- Service Status ---")
        print(status_out)
        print(status_err)
        
        # Check recent logs
        stdin, stdout, stderr = client.exec_command("journalctl -u sustainage -n 50 --no-pager")
        logs_out = stdout.read().decode()
        logs_err = stderr.read().decode()
        print("\n--- Recent Logs ---")
        print(logs_out)
        print(logs_err)
        
        # Persist to local file for detailed inspection (including Gunicorn error log tail)
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            out_path = os.path.join(base_dir, 'tools', 'remote_service_status.log')
            # Also try to read Gunicorn error log tail
            gunicorn_out = ""
            gunicorn_err = ""
            try:
                stdin, stdout, stderr = client.exec_command("tail -n 80 /var/www/sustainage/logs/error.log")
                gunicorn_out = stdout.read().decode()
                gunicorn_err = stderr.read().decode()
            except Exception as ge:
                gunicorn_err = f"Failed to read gunicorn error log: {ge}"
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write("--- Service Status ---\n")
                f.write(status_out)
                if status_err:
                    f.write("\n[stderr]\n")
                    f.write(status_err)
                f.write("\n\n--- Recent Logs ---\n")
                f.write(logs_out)
                if logs_err:
                    f.write("\n[stderr]\n")
                    f.write(logs_err)
                if gunicorn_out or gunicorn_err:
                    f.write("\n\n--- Gunicorn error.log (tail) ---\n")
                    if gunicorn_out:
                        f.write(gunicorn_out)
                    if gunicorn_err:
                        f.write("\n[stderr]\n")
                        f.write(gunicorn_err)
        except Exception as file_e:
            print(f"Failed to write local status log: {file_e}")
        
        client.close()
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_status()
