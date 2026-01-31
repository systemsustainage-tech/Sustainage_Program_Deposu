import paramiko

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def check_nginx_and_fix():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USER, password=PASS)
        
        print("--- Checking Nginx Config ---")
        # List files first
        stdin, stdout, stderr = client.exec_command("ls /etc/nginx/sites-enabled/")
        files = stdout.read().decode().split()
        print(f"Config files: {files}")
        
        for f in files:
            print(f"--- Content of {f} ---")
            stdin, stdout, stderr = client.exec_command(f"cat /etc/nginx/sites-enabled/{f}")
            print(stdout.read().decode())

        print("\n--- Installing gevent ---")
        stdin, stdout, stderr = client.exec_command("/var/www/sustainage/venv/bin/pip install gevent")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("\n--- Restarting Service ---")
        # Stop manual process first
        client.exec_command("pkill -f 'python web_app.py'")
        client.exec_command("pkill -f 'python3 web_app.py'")
        
        # Restart systemd
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_code = stdout.channel.recv_exit_status()
        
        if exit_code == 0:
            print("Service restarted successfully.")
        else:
            print(f"Service restart failed: {stderr.read().decode()}")
            # Check status again
            stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
            print(stdout.read().decode())

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_nginx_and_fix()
