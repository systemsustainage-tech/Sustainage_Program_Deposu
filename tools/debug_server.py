import paramiko
import time

# Server Details
HOSTNAME = '213.142.148.170'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def debug():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected to server.")

        # Check Syntax
        print("\n--- Checking Syntax of web_app.py ---")
        stdin, stdout, stderr = client.exec_command('python3 -m py_compile /var/www/sustainage/web_app.py')
        out = stdout.read().decode()
        err = stderr.read().decode()
        if err:
            print(f"SYNTAX ERROR:\n{err}")
        else:
            print("Syntax OK.")

        # Check Gunicorn Process
        print("\n--- Checking Gunicorn Process ---")
        stdin, stdout, stderr = client.exec_command('ps aux | grep gunicorn')
        print(stdout.read().decode())

        # Check Logs (assuming standard output/error might be captured somewhere or just check syslog)
        # Since it's pkill -HUP, it might be running under supervisor or systemd still.
        # Let's try to find where it logs.
        print("\n--- Checking /var/log/syslog (Tail 50) ---")
        stdin, stdout, stderr = client.exec_command('tail -n 50 /var/log/syslog')
        print(stdout.read().decode())
        
        print("\n--- Checking Nginx Error Log (Tail 20) ---")
        stdin, stdout, stderr = client.exec_command('tail -n 20 /var/log/nginx/error.log')
        print(stdout.read().decode())

        client.close()
        
    except Exception as e:
        print(f"Debug failed: {e}")

if __name__ == '__main__':
    debug()
