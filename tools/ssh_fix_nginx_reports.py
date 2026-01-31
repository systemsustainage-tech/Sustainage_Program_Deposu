
import paramiko

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def fix_nginx_reports():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        # Read current config
        stdin, stdout, stderr = client.exec_command('cat /etc/nginx/sites-available/sustainage')
        config = stdout.read().decode()
        
        # Define the block to remove (approximate)
        # We'll just replace the lines.
        # Be careful with whitespace.
        
        # Or better, we can filter it out line by line.
        new_lines = []
        skip = False
        for line in config.splitlines():
            if "location /reports {" in line:
                skip = True
                continue
            if skip and "}" in line:
                skip = False
                continue
            if not skip:
                new_lines.append(line)
        
        new_config = "\n".join(new_lines)
        
        # Write back (requires a bit more care with quoting if using echo, better use SFTP)
        sftp = client.open_sftp()
        with sftp.open('/etc/nginx/sites-available/sustainage', 'w') as f:
            f.write(new_config)
        sftp.close()
        
        print("Updated Nginx config.")
        
        # Test config
        stdin, stdout, stderr = client.exec_command('nginx -t')
        test_out = stdout.read().decode()
        test_err = stderr.read().decode()
        print(f"Config Test: {test_err}") # nginx -t usually outputs to stderr
        
        if "successful" in test_err:
            print("Reloading Nginx...")
            client.exec_command('systemctl reload nginx')
            print("Nginx reloaded.")
        else:
            print("Config test failed. Not reloading.")
            
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_nginx_reports()
