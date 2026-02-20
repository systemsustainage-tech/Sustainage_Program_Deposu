import paramiko
import os

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
REMOTE_DIR = '/var/www/sustainage'

def check_structure():
    try:
        print(f"Connecting to {HOST}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USER, password=PASS)
        
        # Check specific directories
        dirs_to_check = [
            'yonetim',
            'yonetim/kullanici_yonetimi',
            'yonetim/security',
            'yonetim/security/core',
            'utils',
            'services'
        ]
        
        for d in dirs_to_check:
            path = f"{REMOTE_DIR}/{d}"
            stdin, stdout, stderr = client.exec_command(f"ls -F {path}")
            out = stdout.read().decode()
            err = stderr.read().decode()
            if err:
                print(f"DIR {d}: NOT FOUND or Error: {err.strip()}")
            else:
                print(f"DIR {d}:\n{out}")
                
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_structure()
