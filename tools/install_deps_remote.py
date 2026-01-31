import paramiko
import os
import sys

# Remote server details
hostname = '72.62.150.207'
username = 'root'
password = os.environ.get('REMOTE_PASS', 'Sustainage123.')

def install_deps():
    print(f"Connecting to {hostname}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        print("Installing dependencies...")
        stdin, stdout, stderr = client.exec_command('pip3 install pyotp qrcode python-docx openpyxl argon2-cffi pandas openai schedule matplotlib --break-system-packages')
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        if out: print(f"Output: {out}")
        if err: print(f"Error: {err}")
        
    except Exception as e:
        print(f"Installation failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    install_deps()
