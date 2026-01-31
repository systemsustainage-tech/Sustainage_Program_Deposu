import paramiko
import time

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_remote_init():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        
        print("Running init_missing_tables.py on remote...")
        stdin, stdout, stderr = ssh.exec_command("python3 /var/www/sustainage/tools/init_missing_tables.py")
        
        # Wait for command to finish and get output
        exit_status = stdout.channel.recv_exit_status()
        out = stdout.read().decode('utf-8')
        err = stderr.read().decode('utf-8')
        
        print("Output:")
        print(out)
        
        if exit_status != 0:
            print("Error:")
            print(err)
        else:
            print("Success.")

        # Also restart service just in case
        print("Restarting service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        stdout.channel.recv_exit_status()
        print("Service restarted.")

    except Exception as e:
        print(f"Failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    run_remote_init()
