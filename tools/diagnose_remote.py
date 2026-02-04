import subprocess

REMOTE_HOST = "root@72.62.150.207"

def run_remote(cmd):
    full_cmd = f"ssh {REMOTE_HOST} '{cmd}'"
    print(f"Running: {cmd}")
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    print(f"STDOUT:\n{result.stdout}")
    print(f"STDERR:\n{result.stderr}")

if __name__ == "__main__":
    run_remote("uname -a")
    run_remote("echo $PATH")
    run_remote("ls -F /usr/bin/sys*")
    run_remote("ls -F /bin/sys*")
    run_remote("ls -F /usr/sbin/service")
    run_remote("ps aux | grep python")
    run_remote("ps aux | grep gunicorn")
