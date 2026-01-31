
import paramiko
import sys

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def create_test_user():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        
        # Python script to create user
        py_script = """
import sys
sys.path.append('/var/www/sustainage')
from backend.yonetim.kullanici_yonetimi.models.user_manager import UserManager
from backend.yonetim.security.core.crypto import hash_password

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

try:
    mgr = UserManager(DB_PATH)
    # Check if exists
    user = mgr.get_user_by_username('test_user')
    if user:
        print('User test_user already exists.')
        # Reset password just in case
        # mgr.update_password(user['id'], 'test12345') # update_password method might differ too
        print('User already exists, skipping creation.')
    else:
        user_data = {
            'username': 'test_user',
            'password': 'test12345',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True,
            'is_verified': True
        }
        user_id = mgr.create_user(user_data)
        if user_id > 0:
            print(f'User test_user created with ID {user_id}.')
        else:
            print('Failed to create user.')
except Exception as e:
    print(f'Error: {e}')
"""
        # Escape for shell
        safe_script = py_script.replace('"', '\\"')
        
        # We can't easily pass multi-line script via command line argument if it has complex quotes.
        # Better to upload it.
        
        sftp = client.open_sftp()
        with sftp.file('/tmp/create_test_user.py', 'w') as f:
            f.write(py_script)
        sftp.close()
        
        print("Executing creation script...")
        stdin, stdout, stderr = client.exec_command("python3 /tmp/create_test_user.py")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"SSH Error: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    create_test_user()
