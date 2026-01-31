import paramiko

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Kayra_1507'

def run_verify():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    except:
        client.connect(HOSTNAME, username=USERNAME, password='Z/2m?-JDp5VaX6q+HO(b')

    print("Running verify_all_modules.py...")
    stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/tools/verify_all_modules.py")
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    client.close()

if __name__ == "__main__":
    run_verify()
