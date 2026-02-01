import paramiko
import time

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"  # Varsayılan şifre, güvenlik için ssh key tercih edilmeli ama mevcut akışta bu kullanılıyor

def check_and_kill_port():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        print("Connected.")
        
        # 1. Check what's running on port 5000
        print("Checking port 5000 usage...")
        # using netstat or lsof. trying lsof first, usually available. if not, netstat.
        cmd = "lsof -i :5000"
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode().strip()
        
        if out:
            print("Processes found on port 5000:")
            print(out)
            
            # Extract PIDs and kill them
            lines = out.split('\n')[1:] # Skip header
            pids = set()
            for line in lines:
                parts = line.split()
                if len(parts) > 1:
                    pids.add(parts[1])
            
            if pids:
                print(f"Killing PIDs: {', '.join(pids)}")
                kill_cmd = f"kill -9 {' '.join(pids)}"
                client.exec_command(kill_cmd)
                print("Kill command sent.")
                time.sleep(2)
            else:
                print("Could not parse PIDs.")
        else:
            print("No process found explicitly listening on port 5000 via lsof.")
            
            # Try netstat just in case
            cmd = "netstat -nlp | grep 5000"
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode().strip()
            if out:
                print("Netstat found usage:")
                print(out)
                # Parse PID/Program name (e.g., "1234/python")
                import re
                pids = re.findall(r'(\d+)/', out)
                if pids:
                     print(f"Killing PIDs from netstat: {', '.join(pids)}")
                     kill_cmd = f"kill -9 {' '.join(pids)}"
                     client.exec_command(kill_cmd)

        # 2. Check for any stray python or gunicorn processes that might be related but not bound yet
        # Be careful not to kill system processes. 
        # For now, let's just focus on the port conflict.

        # 3. Restart service
        print("Restarting sustainage service...")
        client.exec_command("systemctl restart sustainage")
        time.sleep(5) # Wait for boot
        
        # 4. Check status
        print("Checking service status...")
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        status = stdout.read().decode()
        print(status)
        
        if "active (running)" in status:
            print("SUCCESS: Service is active and running.")
        else:
            print("FAILURE: Service is not running. Fetching recent logs...")
            # Get logs
            stdin, stdout, stderr = client.exec_command("journalctl -u sustainage.service -n 50 --no-pager")
            logs = stdout.read().decode()
            print("--- LOGS ---")
            print(logs)
            print("--- END LOGS ---")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_and_kill_port()
