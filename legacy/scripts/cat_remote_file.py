import paramiko

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def cat_file():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        
        print("--- grep url_for /var/www/sustainage/templates/dashboard.html ---")
        stdin, stdout, stderr = client.exec_command("grep 'url_for' /var/www/sustainage/templates/dashboard.html")
        print(stdout.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    cat_file()