
import paramiko

# Server Credentials
HOST = "72.62.150.207"
USER = "root"
PASS = "Z/2m?-JDp5VaX6q+HO(b"

def check_paths():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        
        paths = [
            "/var/www/sustainage/backend/data/sdg_desktop.sqlite",
            "/var/www/sustainage/data/sdg_desktop.sqlite",
            "/var/www/sustainage/database.db"
        ]
        
        for p in paths:
            print(f"Checking {p}...")
            stdin, stdout, stderr = ssh.exec_command(f"ls -l {p}")
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            if out:
                print(f"[EXISTS] {out}")
            else:
                print(f"[MISSING] {err}")
        
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_paths()
