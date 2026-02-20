import paramiko

def grep_remote():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    search_term = "company_edit_title"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        # grep -r "search_term" /path
        cmd = f"grep -r '{search_term}' /var/www/sustainage/templates/"
        print(f"Running: {cmd}")
        
        stdin, stdout, stderr = client.exec_command(cmd)
        
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        if output:
            print("Matches found:")
            print(output)
        else:
            print("No matches found.")
            
        if error:
            print("Errors:")
            print(error)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    grep_remote()
