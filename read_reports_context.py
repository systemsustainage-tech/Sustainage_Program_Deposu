import paramiko

def read_reports_context():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        # Read reports.html around the loop
        print("--- reports.html context ---")
        with sftp.open('/var/www/sustainage/templates/reports.html', 'r') as f:
            content = f.read().decode()
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if 25 <= i <= 45:  # Around the found lines 34-36
                    print(f"{i+1}: {line}")

        # Read dashboard.html around the buttons
        print("\n--- dashboard.html buttons ---")
        with sftp.open('/var/www/sustainage/templates/dashboard.html', 'r') as f:
            content = f.read().decode()
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if 320 <= i <= 360:
                    print(f"{i+1}: {line}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    read_reports_context()
