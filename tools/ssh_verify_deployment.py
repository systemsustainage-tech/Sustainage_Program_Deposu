import paramiko

HOST = "72.62.150.207"
USER = "root"
PASS = "Z/2m?-JDp5VaX6q+HO(b"

FILES_TO_CHECK = [
    "/var/www/sustainage/server/templates/economic.html",
    "/var/www/sustainage/server/templates/biodiversity.html",
    "/var/www/sustainage/server/templates/tnfd.html",
    "/var/www/sustainage/server/templates/carbon.html",
    "/var/www/sustainage/server/templates/social.html",
    "/var/www/sustainage/server/templates/governance.html",
    "/var/www/sustainage/server/templates/data.html",
    "/var/www/sustainage/locales/tr.json"
]

def verify():
    print("--- Verifying Deployment ---")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        
        cmd = "ls -l " + " ".join(FILES_TO_CHECK)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        if output:
            print(output)
        if error:
            print(f"Error: {error}")
            
        ssh.close()
        
    except Exception as e:
        print(f"Verification Failed: {e}")

if __name__ == "__main__":
    verify()
