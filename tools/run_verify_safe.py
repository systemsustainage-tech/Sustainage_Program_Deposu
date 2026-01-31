import paramiko
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Kayra_1507'

def run_verify_safe():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    except:
        client.connect(HOSTNAME, username=USERNAME, password='Z/2m?-JDp5VaX6q+HO(b')

    print("Running verify_all_modules.py (redirected output)...")
    client.exec_command("python3 /var/www/sustainage/tools/verify_all_modules.py > /tmp/verify_out.txt 2>&1")
    
    # Give it a moment to finish (it should be fast, but exec_command returns immediately if backgrounded? No, it waits if not backgrounded)
    # But wait, exec_command returns channels. If I don't read from them, does it block?
    # Better to read from the command execution itself.
    
    stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/tools/verify_all_modules.py")
    out = stdout.read().decode()
    err = stderr.read().decode()
    
    print("--- STDOUT ---")
    print(out)
    print("--- STDERR ---")
    print(err)
    
    client.close()

if __name__ == "__main__":
    run_verify_safe()
