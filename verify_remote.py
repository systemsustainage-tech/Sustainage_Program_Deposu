
import paramiko
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def verify():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    
    print("Running populate_full_test_data.py...")
    stdin, stdout, stderr = client.exec_command('python3 /var/www/sustainage/populate_full_test_data.py')
    out = stdout.read().decode()
    err = stderr.read().decode()
    print("Output:")
    print(out)
    if err:
        print("Error:")
        print(err)
        
    print("Checking if report_registry has entries...")
    stdin, stdout, stderr = client.exec_command('sqlite3 /var/www/sustainage/backend/data/sdg_desktop.sqlite "SELECT COUNT(*) FROM report_registry;"')
    print("Report Registry Count:", stdout.read().decode())

    print("Checking waste_generation columns...")
    stdin, stdout, stderr = client.exec_command('sqlite3 /var/www/sustainage/backend/data/sdg_desktop.sqlite "PRAGMA table_info(waste_generation);"')
    print(stdout.read().decode())
    
    print("Testing PDF Generation...")
    # Create a small script to import web_app and run generate_report_file
    test_script = """
import sys
sys.path.append('/var/www/sustainage')
from web_app import generate_report_file
try:
    path, size = generate_report_file(1, 'carbon', 'Test Report', 'PDF', '2024-01', 'Test Description')
    print(f'Success: {path} ({size} bytes)')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
"""
    stdin, stdout, stderr = client.exec_command(f'python3 -c "{test_script}"')
    print("PDF Gen Output:", stdout.read().decode())
    print("PDF Gen Error:", stderr.read().decode())
    
    client.close()

if __name__ == '__main__':
    verify()
