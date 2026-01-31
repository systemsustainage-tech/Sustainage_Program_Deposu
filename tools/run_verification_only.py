import paramiko
import time

# Server details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_verification_only():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print(f"Connected to {HOSTNAME}")

        # Upload the fixed verify_full_system.py
        sftp = client.open_sftp()
        sftp.put(r"c:\SUSTAINAGESERVER\tools\verify_full_system.py", "/var/www/sustainage/tools/verify_full_system.py")
        sftp.close()
        print("Uploaded fixed verify_full_system.py")

        # 4. Create Test User
        print("Setting up test user...")
        stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/tools/setup_test_user.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Setup Error: {err}")

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
    run_verification_only()
