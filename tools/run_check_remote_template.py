import paramiko
import sys

# Remote server details
hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'
remote_base = '/var/www/sustainage'

def check_remote_template(template_id):
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        
        print(f"Checking template {template_id} on remote...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/check_remote_template.py {template_id}")
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print("STDOUT:")
        print(out)
        if err:
            print("STDERR:")
            print(err)
            
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_remote_template(sys.argv[1])
    else:
        print("Please provide template ID")