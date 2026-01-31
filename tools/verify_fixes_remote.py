import paramiko
import time

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def verify():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected to server.")

        # Python script to run on server
        verify_script = """
import requests
import sys

# Login to get session
session = requests.Session()
login_url = 'http://localhost:5000/login'
# Assuming we have a test user or can bypass login for localhost if configured, 
# but usually we need to login.
# Let's try to access login page first to see if it's up.
try:
    r = session.get(login_url)
    print(f"Login Page: {r.status_code}")
except Exception as e:
    print(f"Login Page Error: {e}")
    sys.exit(1)

# URLs to check
urls = [
    '/dashboard',
    '/prioritization',
    '/targets',
    '/eu_taxonomy'
]

# Note: Without valid login credentials, these might redirect to /login (302).
# We just want to ensure they don't error out (500).
# If we can, let's try to login.
# Do we have credentials? 'testuser' / 'password' or similar?
# Memories say '__super__' / 'Kayra_1507'

try:
    login_data = {'username': '__super__', 'password': 'Kayra_1507'}
    r = session.post(login_url, data=login_data)
    print(f"Login Attempt: {r.status_code}")
    if r.url.endswith('/dashboard') or r.status_code == 200:
        print("Login Successful")
    else:
        print("Login Failed or Redirected unexpected")
except Exception as e:
    print(f"Login POST Error: {e}")

for url in urls:
    full_url = f'http://localhost:5000{url}'
    try:
        r = session.get(full_url)
        print(f"{url}: {r.status_code}")
        if r.status_code == 500:
            print(f"ERROR 500 on {url}")
    except Exception as e:
        print(f"{url} Error: {e}")

"""
        
        # Write script to remote file
        stdin, stdout, stderr = client.exec_command('cat > /tmp/verify_script.py')
        stdin.write(verify_script)
        stdin.channel.shutdown_write() # Send EOF
        
        # Run script
        print("Running verification script on server...")
        stdin, stdout, stderr = client.exec_command('/var/www/sustainage/venv/bin/python3 /tmp/verify_script.py')
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print("Output:\n", out)
        if err:
            print("Errors:\n", err)
            
        client.close()

    except Exception as e:
        print(f"Verification failed: {e}")

if __name__ == '__main__':
    verify()
