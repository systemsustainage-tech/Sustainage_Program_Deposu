import paramiko
import sys

HOSTNAME = "72.62.150.207"
USERNAME = "root"
PASSWORD = "Z/2m?-JDp5VaX6q+HO(b"

def main():
    try:
        print(f"Connecting to {HOSTNAME}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected.")
        
        # Check /var/www/sustainage
        print("\nListing /var/www/sustainage:")
        stdin, stdout, stderr = client.exec_command("ls -la /var/www/sustainage")
        print(stdout.read().decode())
        
        # Check /var/www/sustainage/SDG_WEB (if exists)
        print("\nListing /var/www/sustainage/SDG_WEB:")
        stdin, stdout, stderr = client.exec_command("ls -la /var/www/sustainage/SDG_WEB")
        out = stdout.read().decode()
        print(out)
        
        # Check service status
        print("\nChecking service status:")
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        print(stdout.read().decode())

        # Read service file
        print("\nReading /etc/systemd/system/sustainage.service:")
        stdin, stdout, stderr = client.exec_command("cat /etc/systemd/system/sustainage.service")
        print(stdout.read().decode())
        
        # Read /var/www/sustainage/web_app.py
        print("\nReading /var/www/sustainage/web_app.py (first 20 lines):")
        stdin, stdout, stderr = client.exec_command("head -n 20 /var/www/sustainage/web_app.py")
        print(stdout.read().decode())

        
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
