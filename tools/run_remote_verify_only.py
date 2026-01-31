import paramiko
import time
import sys

# Server details
HOST = "72.62.150.207"
USER = "root"
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def run_remote_verification():
    print(f"Connecting to {HOST}...")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=HOST, username=USER, password=PASSWORD)
        print("Connected successfully.")

        # Upload tools
        sftp = client.open_sftp()
        tools_to_upload = [
            (r'c:\SUSTAINAGESERVER\tools\verify_survey_counts_remote.py', '/var/www/sustainage/tools/verify_survey_counts_remote.py'),
            (r'c:\SUSTAINAGESERVER\tools\check_actual_schema.py', '/var/www/sustainage/tools/check_actual_schema.py')
        ]
        for local, remote in tools_to_upload:
            print(f"Uploading {local} to {remote}...")
            sftp.put(local, remote)
        sftp.close()

        # Define verification commands
        commands = [
            ("Checking Service Status...", "systemctl status sustainage --no-pager"),
            ("Checking Schema...", "python3 /var/www/sustainage/tools/check_actual_schema.py"),
            ("Verifying Survey Counts...", "python3 /var/www/sustainage/tools/verify_survey_counts_remote.py"),
            ("Checking ESRS Fix...", "python3 /var/www/sustainage/tools/fix_esrs_schema.py") # Running it again to see if it says 'already exists' or similar
        ]

        for desc, cmd in commands:
            print(f"\n--- {desc} ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            
            # Read output
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            
            if out:
                print("OUTPUT:")
                print(out)
            if err:
                print("ERROR:")
                print(err)

        client.close()
        print("\nVerification complete.")

    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_remote_verification()
