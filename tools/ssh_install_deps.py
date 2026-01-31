import paramiko

HOST = "72.62.150.207"
USER = "root"
PASS = "Z/2m?-JDp5VaX6q+HO(b"

def install_deps():
    print("--- Installing Python Dependencies ---")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        
        print("Installing python-docx, openpyxl, reportlab...")
        stdin, stdout, stderr = ssh.exec_command("pip3 install python-docx openpyxl reportlab --break-system-packages")
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print(out)
        if err:
            print("STDERR (might be warnings):", err)
            
        ssh.close()
        print("--- Installation Complete ---")
        
    except Exception as e:
        print(f"Installation Failed: {e}")

if __name__ == "__main__":
    install_deps()
