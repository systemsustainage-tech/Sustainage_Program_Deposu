import paramiko
import os
import time

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'
remote_base = '/var/www/sustainage'

files_to_deploy = [
    ('c:/SUSTAINAGESERVER/backend/modules/sdg/sdg_data_validation.py', 'backend/modules/sdg/sdg_data_validation.py'),
    ('c:/SUSTAINAGESERVER/backend/modules/reporting/unified_report_docx.py', 'backend/modules/reporting/unified_report_docx.py'),
    ('c:/SUSTAINAGESERVER/tools/fix_sdg_validation.py', 'tools/fix_sdg_validation.py'),
    ('c:/SUSTAINAGESERVER/tools/test_unified_report_methodology.py', 'tools/test_unified_report_methodology.py'),
]

def deploy_and_run():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        sftp = ssh.open_sftp()
        
        for local_path, remote_rel_path in files_to_deploy:
            if not os.path.exists(local_path):
                print(f"Local file not found: {local_path}")
                continue
                
            remote_path = f"{remote_base}/{remote_rel_path}"
            print(f"Uploading {local_path} to {remote_path}...")
            sftp.put(local_path, remote_path)
            print("Success.")
                
        sftp.close()

        print("\n--- Running fix_sdg_validation.py ---")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/fix_sdg_validation.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Errors: {err}")

        print("\n--- Running test_unified_report_methodology.py ---")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/test_unified_report_methodology.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Errors: {err}")
        
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_and_run()
