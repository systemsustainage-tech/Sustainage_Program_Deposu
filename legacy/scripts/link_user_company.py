import paramiko

def link_user_company():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        db_path = "/var/www/sustainage/backend/data/sdg_desktop.sqlite"
        
        # 1. Get test_user ID
        print("Getting test_user ID...")
        cmd = f'sqlite3 {db_path} "SELECT id FROM users WHERE email=\'test@sustainage.com\';"'
        stdin, stdout, stderr = client.exec_command(cmd)
        user_id = stdout.read().decode().strip()
        print(f"User ID: {user_id}")
        
        # 2. Get Kivanc company ID
        print("Getting Kivanc company ID...")
        cmd = f'sqlite3 {db_path} "SELECT id FROM companies WHERE name LIKE \'%Kıvanç%\';"'
        stdin, stdout, stderr = client.exec_command(cmd)
        company_id = stdout.read().decode().strip()
        print(f"Company ID: {company_id}")
        
        if user_id and company_id:
            # 3. Insert link
            print(f"Linking User {user_id} to Company {company_id}...")
            cmd = f'sqlite3 {db_path} "INSERT INTO user_companies (user_id, company_id, is_primary) VALUES ({user_id}, {company_id}, 1);"'
            stdin, stdout, stderr = client.exec_command(cmd)
            err = stderr.read().decode()
            if err:
                print(f"Error inserting: {err}")
            else:
                print("Link created successfully.")
        else:
            print("Could not find user or company.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    link_user_company()
