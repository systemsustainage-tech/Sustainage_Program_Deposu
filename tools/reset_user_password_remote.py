import os
import sys
import paramiko
from werkzeug.security import generate_password_hash

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_ed25519")

DB_PATH = "/var/www/sustainage/backend/data/sdg_desktop.sqlite"


def reset_password(username: str, new_password: str) -> None:
    password_hash = generate_password_hash(new_password, method="pbkdf2:sha256")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)

    sql = f"""sqlite3 {DB_PATH} <<'SQL'
.bail on
UPDATE users
   SET password_hash='{password_hash}',
       is_active=1,
       login_attempts=0,
       failed_attempts=0,
       locked_until=NULL,
       must_change_password=0,
       updated_at=CURRENT_TIMESTAMP
 WHERE username='{username}';
SELECT changes();
SELECT username, email, is_active, login_attempts, failed_attempts, locked_until, length(password_hash) FROM users WHERE username='{username}';
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


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tools/reset_user_password_remote.py <username> <new_password>")
        raise SystemExit(2)

    reset_password(sys.argv[1].strip(), sys.argv[2])
