import paramiko
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def install():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected.")
        
        # Try apt first
        print("Installing python3-reportlab via apt...")
        stdin, stdout, stderr = client.exec_command('apt-get update && apt-get install -y python3-reportlab')
        out = stdout.read().decode()
        err = stderr.read().decode()
        print(out)
        if "E:" in err and "Unable to locate package" not in err: # Some error occurred
             print(f"Apt error: {err}")
             # Fallback to pip
             print("Falling back to pip...")
             stdin, stdout, stderr = client.exec_command('pip3 install reportlab --break-system-packages')
             print(stdout.read().decode())
             print(stderr.read().decode())
        else:
             print("Apt install finished (or tried).")
             # Check if installed
             stdin, stdout, stderr = client.exec_command('python3 -c "import reportlab; print(reportlab.__version__)"')
             ver = stdout.read().decode().strip()
             if ver:
                 print(f"Reportlab version: {ver}")
             else:
                 print("Reportlab not found, forcing pip install...")
                 stdin, stdout, stderr = client.exec_command('pip3 install reportlab --break-system-packages')
                 print(stdout.read().decode())
                 print(stderr.read().decode())

        # Restart Gunicorn again just in case
        print("Restarting Gunicorn...")
        client.exec_command("pkill -HUP gunicorn")
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    install()