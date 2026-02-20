import paramiko

def inspect_user_companies():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        db_path = "/var/www/sustainage/backend/data/sdg_desktop.sqlite"
        
        queries = [
            f"PRAGMA table_info(user_companies);",
            f"SELECT * FROM user_companies;"
        ]
        
        for q in queries:
            print(f"\nRunning: {q}")
            cmd = f'sqlite3 {db_path} "{q}"'
            stdin, stdout, stderr = client.exec_command(cmd)
            print(stdout.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    inspect_user_companies()
