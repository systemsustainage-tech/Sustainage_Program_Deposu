import os
import paramiko

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_ed25519")

DB_PATH = "/var/www/sustainage/backend/data/sdg_desktop.sqlite"


def run() -> None:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)

    sql = f"""sqlite3 {DB_PATH} <<'SQL'
.mode list
.separator '|'
SELECT name, type, coalesce(sql,'') FROM sqlite_master WHERE sql LIKE '%roles_old%';
SELECT name, type, coalesce(sql,'') FROM sqlite_master WHERE name IN ('roles','roles_old');
SELECT count(*) FROM sqlite_master WHERE name='roles_old';
SQL
"""
    stdin, stdout, stderr = ssh.exec_command(sql)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode(errors="replace").strip()
    err = stderr.read().decode(errors="replace").strip()

    if exit_status != 0:
        ssh.close()
        raise RuntimeError(err or f"Remote command failed with exit code {exit_status}")

    print(out)

    sql2 = f"""sqlite3 {DB_PATH} <<'SQL'
SELECT count(*) FROM sqlite_master WHERE name='roles_old';
SQL
"""
    stdin, stdout, stderr = ssh.exec_command(sql2)
    exit_status = stdout.channel.recv_exit_status()
    exists_out = stdout.read().decode(errors="replace").strip()
    err2 = stderr.read().decode(errors="replace").strip()
    if exit_status != 0:
        ssh.close()
        raise RuntimeError(err2 or f"Remote command failed with exit code {exit_status}")

    roles_old_exists = exists_out.strip().endswith("1")
    if roles_old_exists:
        sql_type = f"""sqlite3 {DB_PATH} <<'SQL'
SELECT type FROM sqlite_master WHERE name='roles_old' LIMIT 1;
SQL
"""
        stdin, stdout, stderr = ssh.exec_command(sql_type)
        exit_status = stdout.channel.recv_exit_status()
        roles_old_type = stdout.read().decode(errors="replace").strip().lower()
        errt = stderr.read().decode(errors="replace").strip()
        if exit_status != 0:
            ssh.close()
            raise RuntimeError(errt or f"Remote command failed with exit code {exit_status}")
        if roles_old_type == 'table':
            ssh.close()
            return

    sql3 = f"""sqlite3 {DB_PATH} <<'SQL'
SELECT coalesce(sql,'') FROM sqlite_master WHERE name='roles';
SQL
"""
    stdin, stdout, stderr = ssh.exec_command(sql3)
    exit_status = stdout.channel.recv_exit_status()
    roles_sql = stdout.read().decode(errors="replace").strip()
    err3 = stderr.read().decode(errors="replace").strip()
    if exit_status != 0:
        ssh.close()
        raise RuntimeError(err3 or f"Remote command failed with exit code {exit_status}")

    if 'roles_old' in roles_sql:
        ssh.close()
        raise RuntimeError("roles nesnesi roles_old referansı içeriyor; otomatik düzeltme güvenli değil.")

    sql4 = f"""sqlite3 {DB_PATH} <<'SQL'
DROP VIEW IF EXISTS roles_old;
CREATE TABLE IF NOT EXISTS roles_old (
  id INTEGER PRIMARY KEY,
  name VARCHAR(50),
  display_name VARCHAR(100),
  description TEXT,
  is_system_role BOOLEAN,
  is_active BOOLEAN,
  created_at,
  updated_at,
  created_by INTEGER,
  updated_by INTEGER,
  company_id INTEGER
);
INSERT OR IGNORE INTO roles_old (id, name, display_name, description, is_system_role, is_active, created_at, updated_at, created_by, updated_by, company_id)
SELECT id, name, display_name, description, is_system_role, is_active, created_at, updated_at, created_by, updated_by, company_id
FROM roles;

CREATE TRIGGER IF NOT EXISTS roles_old_ai
AFTER INSERT ON roles
BEGIN
  INSERT OR REPLACE INTO roles_old (id, name, display_name, description, is_system_role, is_active, created_at, updated_at, created_by, updated_by, company_id)
  VALUES (new.id, new.name, new.display_name, new.description, new.is_system_role, new.is_active, new.created_at, new.updated_at, new.created_by, new.updated_by, new.company_id);
END;

CREATE TRIGGER IF NOT EXISTS roles_old_au
AFTER UPDATE ON roles
BEGIN
  UPDATE roles_old
     SET name=new.name,
         display_name=new.display_name,
         description=new.description,
         is_system_role=new.is_system_role,
         is_active=new.is_active,
         created_at=new.created_at,
         updated_at=new.updated_at,
         created_by=new.created_by,
         updated_by=new.updated_by,
         company_id=new.company_id
   WHERE id=old.id;
END;

CREATE TRIGGER IF NOT EXISTS roles_old_ad
AFTER DELETE ON roles
BEGIN
  DELETE FROM roles_old WHERE id=old.id;
END;

SELECT type, name FROM sqlite_master WHERE name='roles_old';
SQL
"""
    stdin, stdout, stderr = ssh.exec_command(sql4)
    exit_status = stdout.channel.recv_exit_status()
    out4 = stdout.read().decode(errors="replace").strip()
    err4 = stderr.read().decode(errors="replace").strip()
    ssh.close()

    if exit_status != 0:
        raise RuntimeError(err4 or f"Remote command failed with exit code {exit_status}")

    print(out4)


if __name__ == "__main__":
    run()
