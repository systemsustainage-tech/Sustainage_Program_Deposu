import paramiko

HOST = "72.62.150.207"
USER = "root"
PASS = "Z/2m?-JDp5VaX6q+HO(b"

def check_locales():
    print("--- Checking Locales ---")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        
        cmd = "grep 'energy_title' /var/www/sustainage/locales/tr.json"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        out = stdout.read().decode()
        if out:
            print("Found key in tr.json:")
            print(out)
        else:
            print("Key NOT found in tr.json")
            
        ssh.close()
        
    except Exception as e:
        print(f"Check Failed: {e}")

if __name__ == "__main__":
    check_locales()
