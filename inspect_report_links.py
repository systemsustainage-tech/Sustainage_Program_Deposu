import paramiko

def inspect_report_links():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        files_to_check = ['/var/www/sustainage/templates/dashboard.html', '/var/www/sustainage/templates/reports.html']
        
        for remote_path in files_to_check:
            print(f"\n--- Checking {remote_path} ---")
            try:
                with sftp.open(remote_path, 'r') as f:
                    content = f.read().decode()
                    lines = content.splitlines()
                    for i, line in enumerate(lines):
                        # Search for potential causes of https://sustainage.cloud/'#'
                        # Looking for href="'#'" or similar
                        if "'#'" in line or '"#"' in line or "href='#'" in line or 'href="#"' in line:
                            print(f"{i+1}: {line.strip()}")
                        # Also check for report detail links specifically
                        if 'report_detail' in line:
                            print(f"{i+1} [DETAIL]: {line.strip()}")
            except Exception as e:
                print(f"Could not read {remote_path}: {e}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    inspect_report_links()
