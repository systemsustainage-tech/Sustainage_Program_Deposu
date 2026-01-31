import paramiko

HOST = "72.62.150.207"
USER = "root"
PASS = "Z/2m?-JDp5VaX6q+HO(b"

def find_db():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        print("Checking for database file...")
        stdin, stdout, stderr = ssh.exec_command("find /var/www/sustainage -name '*.sqlite'")
        print(stdout.read().decode())
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_db()
