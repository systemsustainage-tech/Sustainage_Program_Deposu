import paramiko
import sys
import time

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def run_server_and_stream():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        
        # Stop existing service first
        print("Stopping existing sustainage service...")
        client.exec_command("systemctl stop sustainage")
        print("Killing existing gunicorn processes...")
        client.exec_command("pkill -f gunicorn")
        time.sleep(2)
        
        # Try pip installing gunicorn/gevent first if missing, then run
        print("Checking/Installing gunicorn/gevent...")
        stdin, stdout, stderr = client.exec_command("/var/www/sustainage/venv/bin/pip install gunicorn gevent")
        # Wait for install
        stdout.channel.recv_exit_status()
        
        # Start server manually and stream output
        print("\n" + "="*60)
        print("   SUSTAINAGE REMOTE SERVER - LIVE MONITOR SCREEN")
        print("   Server: 72.62.150.207")
        print("   Status: RUNNING")
        print("="*60 + "\n")
        
        # Run gunicorn and bind to 0.0.0.0:5000, logging to stdout
        cmd = (
            "cd /var/www/sustainage && "
            "/var/www/sustainage/venv/bin/gunicorn "
            "--workers 1 "
            "--worker-class gevent "
            "--bind 0.0.0.0:5000 "
            "--timeout 300 "
            "--log-level info "
            "--access-logfile - "
            "--error-logfile - "
            "web_app:app"
        )
        stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
        
        # Stream output
        last_print = time.time()
        while True:
            if stdout.channel.recv_ready():
                output = stdout.channel.recv(1024).decode('utf-8', errors='ignore')
                sys.stdout.write(output)
                sys.stdout.flush()
                last_print = time.time()
            
            if stdout.channel.exit_status_ready():
                break
            
            # Heartbeat every 10 seconds if silence
            if time.time() - last_print > 10:
                # sys.stdout.write(".")
                # sys.stdout.flush()
                last_print = time.time()
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping server...")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    run_server_and_stream()