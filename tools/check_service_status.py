import subprocess

REMOTE_HOST = "root@72.62.150.207"
PATH_EXPORT = "export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin;"

def run_remote(cmd):
    full_cmd = f'ssh {REMOTE_HOST} "{PATH_EXPORT} {cmd}"'
    print(f"Running: {full_cmd}")
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")

if __name__ == "__main__":
    run_remote("systemctl status sustainage --no-pager")
    run_remote("journalctl -u sustainage -n 20 --no-pager")
