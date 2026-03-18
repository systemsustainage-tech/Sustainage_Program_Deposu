import os
import sys
import paramiko

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_ed25519")

DB_PATH = "/var/www/sustainage/backend/data/sdg_desktop.sqlite"
SUPER_USERNAME = "__super__"


def update_email(new_email: str) -> int:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)

    sql = f"""sqlite3 {DB_PATH} <<'SQL'
UPDATE users SET email='{new_email}' WHERE username='{SUPER_USERNAME}';
SELECT changes();
SELECT email FROM users WHERE username='{SUPER_USERNAME}';
SQL
"""
    stdin, stdout, stderr = ssh.exec_command(sql)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode(errors="replace").strip()
    err = stderr.read().decode(errors="replace").strip()
    ssh.close()

    if exit_status != 0:
        raise RuntimeError(err or f"Remote command failed with exit code {exit_status}")

    print(out)

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    if not lines:
        return 0
    try:
        return int(lines[0])
    except Exception:
        return 0


if __name__ == "__main__":
    new_email = "kivanc.kasoglu@sustainage.tr"
    if len(sys.argv) > 1:
        new_email = sys.argv[1].strip()

    changed = update_email(new_email)
    if changed <= 0:
        sys.exit(2)
