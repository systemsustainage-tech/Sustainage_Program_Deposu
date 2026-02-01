import paramiko

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

def check_lang_logs():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        
        # Grep for the specific log message in recent logs
        cmd = "journalctl -u sustainage.service --since '5 minutes ago' | grep 'Loading translations'"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        out = stdout.read().decode()
        if out:
            print("Found logs:")
            print(out)
        else:
            print("No translation logs found in the last 5 minutes.")
            
            # Show last 50 lines generally to see if it restarted
            cmd2 = "journalctl -u sustainage.service -n 50 --no-pager"
            stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
            print("\nRecent logs:")
            print(stdout2.read().decode())
        
        ssh.close()
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    check_lang_logs()
