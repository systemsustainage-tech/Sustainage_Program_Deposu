import paramiko
import re

def grep_keys():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        # Grep for {{ _('...') }} or {{ _("...") }}
        cmd = "grep -r \"{{ _\" /var/www/sustainage/templates/"
        stdin, stdout, stderr = client.exec_command(cmd)
        output = stdout.read().decode()
        
        # Extract keys
        keys = set()
        matches = re.findall(r"{{ _\(['\"](.*?)['\"]\)", output)
        for m in matches:
            keys.add(m)
            
        print("Found keys:")
        for k in sorted(keys):
            print(k)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    grep_keys()
