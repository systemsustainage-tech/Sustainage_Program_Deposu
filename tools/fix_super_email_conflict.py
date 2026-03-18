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


def _ssh() -> paramiko.SSHClient:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
    return ssh


def run_sql(ssh: paramiko.SSHClient, sql: str) -> str:
    cmd = f"""sqlite3 {DB_PATH} <<'SQL'
.bail on
{sql}
SQL
"""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode(errors="replace").strip()
    err = stderr.read().decode(errors="replace").strip()
    if exit_status != 0:
        raise RuntimeError(err or f"Remote command failed with exit code {exit_status}")
    return out


def fix_super_email(target_email: str, fallback_email: str) -> None:
    ssh = _ssh()
    try:
        before = run_sql(
            ssh,
            f"""
.mode list
.separator '|'
SELECT id, username, email FROM users WHERE username='{SUPER_USERNAME}';
SELECT id, username, email FROM users WHERE email='{target_email}' AND username<>'{SUPER_USERNAME}';
SELECT id, username, email FROM users WHERE email='{fallback_email}' AND username<>'{SUPER_USERNAME}';
""",
        )
        print("BEFORE")
        print(before or "(no rows)")

        changes = run_sql(
            ssh,
            f"""
BEGIN;

UPDATE users
   SET email='{fallback_email}'
 WHERE email='{target_email}'
   AND username<>'{SUPER_USERNAME}';

UPDATE users
   SET email='{target_email}'
 WHERE username='{SUPER_USERNAME}';

COMMIT;

.mode list
.separator '|'
SELECT changes();
SELECT id, username, email FROM users WHERE username='{SUPER_USERNAME}';
SELECT id, username, email FROM users WHERE email='{target_email}';
""",
        )
        print("AFTER")
        print(changes or "(no output)")
    finally:
        ssh.close()


if __name__ == "__main__":
    target = "kivanc.kasoglu@sustainage.tr"
    if len(sys.argv) > 1:
        target = sys.argv[1].strip()

    fallback = "super.admin@sustainage.app"
    if len(sys.argv) > 2:
        fallback = sys.argv[2].strip()

    fix_super_email(target, fallback)
