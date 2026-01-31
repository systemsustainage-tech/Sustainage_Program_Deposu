import paramiko

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Kayra_1507'

def check_csrd():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    except:
        client.connect(HOSTNAME, username=USERNAME, password='Z/2m?-JDp5VaX6q+HO(b')

    print("Checking /csrd status...")
    # Using cookie jar to maintain session if login needed, but verify_all_modules uses __super__ login.
    # Here we just check if the page returns 500 or redirects (302) or 200.
    # Since /csrd requires login, it should redirect to /login (302) if not logged in.
    # If it returns 500, it's broken.
    
    stdin, stdout, stderr = client.exec_command("curl -k -I https://localhost/csrd")
    output = stdout.read().decode()
    print(output)
    
    client.close()

if __name__ == "__main__":
    check_csrd()
