import paramiko

HOST = "72.62.150.207"
USER = "root"
PASS = "Z/2m?-JDp5VaX6q+HO(b"

def check_template():
    print("--- Checking Template Content ---")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        
        # Check energy.html content
        cmd = "grep '{{ _(' /var/www/sustainage/server/templates/energy.html | head -n 5"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        out = stdout.read().decode()
        if out:
            print("Found translation tags in energy.html:")
            print(out)
        else:
            print("No translation tags found in energy.html (or file empty)")
            
        ssh.close()
        
    except Exception as e:
        print(f"Check Failed: {e}")

if __name__ == "__main__":
    check_template()
