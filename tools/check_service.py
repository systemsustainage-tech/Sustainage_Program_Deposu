import paramiko

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def check_service():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, username=USER, password=PASS)
        
        cmds = [
            "cat /etc/systemd/system/sustainage.service",
            "systemctl status sustainage --no-pager"
        ]
        
        for cmd in cmds:
            print(f"--- {cmd} ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            print(stdout.read().decode())
            print(stderr.read().decode())
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_service()