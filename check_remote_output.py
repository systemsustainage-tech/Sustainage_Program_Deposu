import subprocess
import sys

print("Starting script...")
KEY_PATH = r"c:\sdg\deploy\id_rsa"
HOST = "root@178.156.163.125"

def run_ssh(cmd):
    print(f"Running: {cmd}")
    ssh_cmd = ["ssh", "-i", KEY_PATH, "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", HOST, cmd]
    try:
        # Use run instead of check_output to capture everything
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return f"Error (Code {result.returncode}):\nStdout: {result.stdout}\nStderr: {result.stderr}"
        return result.stdout
    except Exception as e:
        return f"Exception: {e}"

commands = [
    "ls -la /var/www/sustainage/static/",
    "cat /etc/nginx/sites-enabled/default",
    "python3 /var/www/sustainage/generate_kivanc_report.py"
]

try:
    with open("remote_debug.log", "w", encoding="utf-8") as f:
        for cmd in commands:
            f.write(f"--- CMD: {cmd} ---\n")
            out = run_ssh(cmd)
            f.write(out)
            f.write("\n\n")
            print(f"Finished {cmd}")
except Exception as e:
    print(f"File Error: {e}")

print("Debug log written to remote_debug.log")
