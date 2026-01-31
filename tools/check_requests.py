import paramiko

HOST = "72.62.150.207"
USER = "root"
KEY_PASS = "Z/2m?-JDp5VaX6q+HO(b"

def check_requests():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USER, password=KEY_PASS)
        
        cmd = "/var/www/sustainage/venv/bin/python -c \"import requests; print(requests.__version__)\""
        stdin, stdout, stderr = client.exec_command(cmd)
        
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_requests()
