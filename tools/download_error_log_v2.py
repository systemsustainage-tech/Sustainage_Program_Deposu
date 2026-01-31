import os
import paramiko

# FTP/SFTP Configuration
FTP_HOST = "72.62.150.207"
FTP_USER = "sustaina"
FTP_PASS = "Sustain_2024!"
LOCAL_LOG_PATH = "c:/SDG/temp_diagnose/server_error.log"

def explore_and_download_log():
    try:
        transport = paramiko.Transport((FTP_HOST, 22))
        transport.connect(username=FTP_USER, password=FTP_PASS)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        print("Connected to SFTP.")
        
        # Helper to list directory with error handling
        def list_dir(path):
            try:
                print(f"Listing {path}:")
                items = sftp.listdir(path)
                print(items)
                return items
            except Exception as e:
                print(f"Error listing {path}: {e}")
                return []

        # List root
        root_items = list_dir('.')
        
        # Check for 'logs' directory
        log_dir = None
        if 'logs' in root_items:
            log_dir = 'logs'
        elif 'statistics' in root_items:
            # Plesk often puts logs in statistics/logs
            stats_items = list_dir('statistics')
            if 'logs' in stats_items:
                log_dir = 'statistics/logs'
        
        target_log_file = None
        
        if log_dir:
            logs = list_dir(log_dir)
            # Look for error_log, error.log, proxy_error_log
            candidates = ['error_log', 'error.log', 'proxy_error_log']
            for cand in candidates:
                if cand in logs:
                    target_log_file = f"{log_dir}/{cand}"
                    break
        
        if target_log_file:
            print(f"Found log file at: {target_log_file}")
            os.makedirs(os.path.dirname(LOCAL_LOG_PATH), exist_ok=True)
            sftp.get(target_log_file, LOCAL_LOG_PATH)
            print(f"Downloaded to {LOCAL_LOG_PATH}")
            
            # Read last 50 lines
            with open(LOCAL_LOG_PATH, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                print("\n--- Last 50 lines ---")
                for line in lines[-50:]:
                    print(line.strip())
        else:
            print("Could not locate error log file automatically.")

        sftp.close()
        transport.close()
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    explore_and_download_log()
