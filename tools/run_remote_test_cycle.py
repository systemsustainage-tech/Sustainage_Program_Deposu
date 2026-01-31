import paramiko
import time
import os

# Server details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_remote_verification():
    try:
        # 1. Connect
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print(f"Connected to {HOSTNAME}")

        # 2. Upload Files
        sftp = client.open_sftp()
        
        # Ensure target directories exist
        stdin, stdout, stderr = client.exec_command("mkdir -p /var/www/sustainage/backend/modules/quality /var/www/sustainage/tools")
        stdout.channel.recv_exit_status()

        # Upload unified_report_docx.py (Code Fix)
        local_report = r"c:\SUSTAINAGESERVER\backend\modules\reporting\unified_report_docx.py"
        remote_report = "/var/www/sustainage/backend/modules/reporting/unified_report_docx.py"
        print(f"Uploading {local_report}...")
        sftp.put(local_report, remote_report)
        
        # Upload DataQualityScorer (Dependency)
        local_scorer = r"c:\SUSTAINAGESERVER\backend\modules\quality\data_quality_scorer.py"
        remote_scorer = "/var/www/sustainage/backend/modules/quality/data_quality_scorer.py"
        print(f"Uploading {local_scorer}...")
        sftp.put(local_scorer, remote_scorer)

        # Upload verify_full_system.py (Test Script)
        local_test = r"c:\SUSTAINAGESERVER\tools\verify_full_system.py"
        remote_test = "/var/www/sustainage/tools/verify_full_system.py"
        print(f"Uploading {local_test}...")
        sftp.put(local_test, remote_test)

        # Upload setup_test_user.py
        local_setup = r"c:\SUSTAINAGESERVER\tools\setup_test_user.py"
        remote_setup = "/var/www/sustainage/tools/setup_test_user.py"
        print(f"Uploading {local_setup}...")
        sftp.put(local_setup, remote_setup)

        sftp.close()

        # 3. Restart Service (to apply code changes)
        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Error restarting service: {stderr.read().decode()}")

        time.sleep(5) # Wait for service to come up

        # 4. Create Test User
        print("Setting up test user...")
        stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/tools/setup_test_user.py")
        print(stdout.read().decode())
        print(stderr.read().decode())

        # 5. Run Verification
        print("Running full system verification...")
        stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/tools/verify_full_system.py")
        
        # Stream output
        output = stdout.read().decode()
        errors = stderr.read().decode()
        
        print("\n--- TEST RESULTS ---")
        print(output)
        if errors:
            print("\n--- ERRORS ---")
            print(errors)

        client.close()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_remote_verification()
