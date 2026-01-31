
import paramiko
import os
import sys

def fix_super_user_company():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    remote_db_path = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
    
    print(f"Connecting to {hostname}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        # Check if already exists (just in case)
        check_cmd = f"sqlite3 {remote_db_path} \"SELECT count(*) FROM user_companies WHERE user_id=1000;\""
        stdin, stdout, stderr = client.exec_command(check_cmd)
        count = int(stdout.read().decode().strip())
        
        if count > 0:
            print("User 1000 already has a company assigned.")
        else:
            print("Assigning Company 1 to User 1000...")
            insert_cmd = f"sqlite3 {remote_db_path} \"INSERT INTO user_companies (user_id, company_id, is_primary) VALUES (1000, 1, 1);\""
            stdin, stdout, stderr = client.exec_command(insert_cmd)
            err = stderr.read().decode()
            if err:
                print(f"Error executing insert: {err}")
            else:
                print("Successfully assigned company.")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fix_super_user_company()
