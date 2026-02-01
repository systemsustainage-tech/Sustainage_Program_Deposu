import paramiko
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def check_remote_lca():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        cmd = 'sqlite3 /var/www/sustainage/sustainage.db ".schema lca_products" ".schema lca_assessments" ".schema lca_entries"'
        print(f"Running: {cmd}")
        
        stdin, stdout, stderr = client.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        if output.strip():
            print("LCA Tables found:")
            print(output)
        else:
            print("LCA Tables NOT found or empty output.")
            
        if error:
            print(f"Error: {error}")

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_remote_lca()
