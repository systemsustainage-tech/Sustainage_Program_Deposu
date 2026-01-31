import paramiko

def inspect_db():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        queries = [
            "SELECT id, username, email FROM users;",
            "SELECT id, name, user_id FROM companies;",
            "SELECT id, company_id, report_period FROM reports;"
        ]
        
        for q in queries:
            print(f"\nRunning: {q}")
            cmd = f'sqlite3 /var/www/sustainage/sustainage.db "{q}"'
            stdin, stdout, stderr = client.exec_command(cmd)
            print(stdout.read().decode())
            err = stderr.read().decode()
            if err:
                print(f"Error: {err}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    inspect_db()
