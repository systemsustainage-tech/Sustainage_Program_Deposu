import paramiko

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def check():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected.")
        
        print("Checking reportlab...")
        stdin, stdout, stderr = client.exec_command('python3 -c "import reportlab; print(reportlab.__version__)"')
        out = stdout.read().decode()
        err = stderr.read().decode()
        print(f"STDOUT: {out}")
        print(f"STDERR: {err}")
        
        client.close()
    except Exception as e:
        print(f"Check failed: {e}")

if __name__ == '__main__':
    check()
