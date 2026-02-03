
import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def run_command(cmd):
    print(f"Executing remote command: {cmd}")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
        
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        exit_status = stdout.channel.recv_exit_status()
        
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        
        if out:
            print(f"[STDOUT]\n{out}")
        if err:
            print(f"[STDERR]\n{err}")
            
        if exit_status == 0:
            print("Command executed successfully.")
        else:
            print(f"Command failed with exit code {exit_status}")
            
        ssh.close()
    except Exception as e:
        print(f"Connection/Execution failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_command(" ".join(sys.argv[1:]))
    else:
        print("Usage: python run_remote_cmd.py <command>")
