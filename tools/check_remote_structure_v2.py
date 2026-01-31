import paramiko

def check_structure():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    
    paths = [
        '/var/www/sustainage/mapping/sdg_gri_mapping.py',
        '/var/www/sustainage/mapping/__init__.py'
    ]
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        for p in paths:
            stdin, stdout, stderr = client.exec_command(f"ls -l {p}")
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            if out:
                print(f"OK: {out}")
            else:
                print(f"MISSING: {p} ({err})")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_structure()
