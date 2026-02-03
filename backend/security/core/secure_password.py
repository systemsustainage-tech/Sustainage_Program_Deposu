import logging
import hashlib
import json
import secrets
import sqlite3
import time
from typing import Tuple


def _ensure_users_columns(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    try:
        cur.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cur.fetchall()]
        
        if 'failed_attempts' not in columns:
            cur.execute("ALTER TABLE users ADD COLUMN failed_attempts INTEGER DEFAULT 0")
        
        if 'locked_until' not in columns:
            cur.execute("ALTER TABLE users ADD COLUMN locked_until INTEGER")
            
    except Exception as e:
        logging.error(f'Silent error in secure_password.py: {str(e)}')
    conn.commit()


def _now() -> int:
    return int(time.time())


def hash_password(password: str) -> str:
    """
    Hashes the password using Argon2.
    Format: argon2$<argon2_hash>
    Example: argon2$$argon2id$v=19$m=65536,t=3,p=4$...
    """
    try:
        from yonetim.security.core.crypto import hash_password as _hp
        h = _hp(password)
        # Ensure we store the algorithm identifier
        if h.startswith("$"):
            return "argon2$" + h
        return h
    except Exception:
        salt = secrets.token_hex(16)
        h = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
        return f"pbkdf2${salt}:{h}"


def verify_password(stored_hash: str, password: str) -> Tuple[bool, bool]:
    """
    Verifies a password against a stored hash.
    Returns (is_valid, needs_rehash)
    """
    try:
        # 1. Handle Migrated SHA-256 -> Argon2
        if stored_hash.startswith("argon2_sha256$"):
            # Format: argon2_sha256$$argon2id$...
            # The inner hash expects SHA-256 hex digest as the "password"
            inner_hash = stored_hash.replace("argon2_sha256$", "")
            # Remove redundant argon2$ if present (double prefix case)
            if inner_hash.startswith("argon2$"):
                inner_hash = inner_hash.replace("argon2$", "")
            
            hashed_input = hashlib.sha256(password.encode("utf-8")).hexdigest()
            
            from yonetim.security.core.crypto import verify_password as _vp
            if _vp(inner_hash, hashed_input):
                return True, False # It's secure enough, no need to rehash immediately unless we want to remove the SHA256 layer
            return False, False

        # 2. Standard Argon2 / Legacy Handling
        from yonetim.security.core.crypto import verify_password_compat
        s = stored_hash
        
        # Handle argon2$ prefix
        if s.startswith("argon2$") and s.count("$") >= 3:
            s = s.split("argon2$", 1)[1]
            
        ok = verify_password_compat(s, password)
        
        # Determine if rehash is needed (upgrade legacy to Argon2)
        needs = False
        if ok:
            # If it was not Argon2 (e.g. it was pbkdf2 or plain sha256), we need rehash
            if not stored_hash.startswith("argon2$") and not stored_hash.startswith("$argon2"):
                needs = True
                
        return ok, needs
    except Exception as e:
        logging.error(f"Password verification error: {e}")
        # Fallback manual verification logic (preserved from original)
        if stored_hash.startswith("argon2$"):
            s = stored_hash.split("argon2$", 1)[1]
        else:
            s = stored_hash
            
        if s.startswith("$argon2"):
            try:
                from argon2 import PasswordHasher
                ph = PasswordHasher()
                ph.verify(s, password)
                return True, False
            except Exception:
                return False, False
                
        if stored_hash.startswith("pbkdf2$"):
            payload = stored_hash.split("pbkdf2$", 1)[1]
        else:
            payload = stored_hash
            
        if ":" in payload:
            salt, h = payload.split(":", 1)
            calc = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
            return calc == h, True
            
        if len(payload) == 64 and all(c in "0123456789abcdefABCDEF" for c in payload):
            return hashlib.sha256(password.encode("utf-8")).hexdigest() == payload, True
            
        return False, False


def record_failed_login(db_path: str, username: str, max_attempts=None, lock_seconds=None) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    _ensure_users_columns(conn)
    cur.execute("SELECT id, failed_attempts FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return
    attempts = int(row[1] or 0) + 1
    lock_until = None
    try:
        threshold = int(max_attempts) if max_attempts is not None else 5
    except (TypeError, ValueError):
        threshold = 5
    if threshold < 1:
        threshold = 5
    try:
        base = int(lock_seconds) if lock_seconds is not None else 15 * 60
    except (TypeError, ValueError):
        base = 15 * 60
    if base < 1:
        base = 15 * 60
    if attempts >= threshold:
        steps = max(0, attempts - threshold)
        lock_until = _now() + base * (2 ** min(steps, 3))
    cur.execute("UPDATE users SET failed_attempts=?, locked_until=? WHERE id=?", (attempts, lock_until, row[0]))
    try:
        _ensure_security_logs(conn)
        _insert_security_log(cur, "LOGIN_FAIL", username, False, None, {}, user_id=row[0])
        conn.commit()
    except Exception:
        conn.commit()
    conn.close()


def reset_failed_attempts(db_path: str, username: str) -> None:
    conn = sqlite3.connect(db_path)
    _ensure_users_columns(conn)
    cur = conn.cursor()
    cur.execute("UPDATE users SET failed_attempts=0, locked_until=NULL WHERE username=?", (username,))
    conn.commit()
    conn.close()


def lockout_check(db_path: str, username: str) -> Tuple[bool, int]:
    conn = sqlite3.connect(db_path)
    _ensure_users_columns(conn)
    cur = conn.cursor()
    cur.execute("SELECT locked_until FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row or not row[0]:
        return True, 0
    until = int(row[0])
    now = _now()
    if until > now:
        return False, max(0, until - now)
    return True, 0


def _ensure_security_logs(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS security_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            event_type TEXT,
            success INTEGER,
            ip_address TEXT,
            user_agent TEXT,
            details TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def _insert_security_log(cur: sqlite3.Cursor, action: str, username: str, success: bool, ip_address: str, metadata: dict, user_id: int = None) -> None:
    try:
        cur.execute(
            "INSERT INTO security_logs(user_id, username, event_type, action, ip_address, user_agent, success, details) VALUES(?,?,?,?,?,?,?,?)",
            (user_id, username, action, action, ip_address, None, 1 if success else 0, json.dumps(metadata or {}, ensure_ascii=False)),
        )
    except sqlite3.OperationalError:
        cur.execute(
            "INSERT INTO security_logs(user_id, username, event_type, ip_address, user_agent, success, details) VALUES(?,?,?,?,?,?,?)",
            (user_id, username, action, ip_address, None, 1 if success else 0, json.dumps(metadata or {}, ensure_ascii=False)),
        )


def audit_log(db_path: str, action: str, **kwargs) -> None:
    conn = sqlite3.connect(db_path)
    _ensure_security_logs(conn)
    cur = conn.cursor()
    username = kwargs.get("username")
    success = bool(kwargs.get("success")) if kwargs.get("success") is not None else None
    ip_address = kwargs.get("ip_address")
    metadata = kwargs.get("metadata") or {}
    user_id = kwargs.get("user_id")
    _insert_security_log(cur, action, username or "-", bool(success) if success is not None else False, ip_address, metadata, user_id=user_id)
    conn.commit()
    conn.close()


def _get_system_setting_int(key: str, default: int) -> int:
    try:
        conn = sqlite3.connect("backend/data/sdg_desktop.sqlite")
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                category TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute("SELECT value FROM system_settings WHERE key=?", (key,))
        row = cur.fetchone()
        conn.close()
        if row and row[0] is not None:
            try:
                val = int(str(row[0]).strip())
                if val > 0:
                    return val
            except ValueError:
                return default
    except Exception as e:
        logging.error(f"Password policy system setting read error for {key}: {e}")
    return default


def _get_system_setting_str(key: str) -> str:
    try:
        conn = sqlite3.connect("backend/data/sdg_desktop.sqlite")
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                category TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute("SELECT value FROM system_settings WHERE key=?", (key,))
        row = cur.fetchone()
        conn.close()
        if row and row[0] is not None:
            return str(row[0]).strip()
    except Exception as e:
        logging.error(f"Password policy system setting read error for {key}: {e}")
    return ""


class PasswordPolicy:
    def __init__(self):
        pass

    @staticmethod
    def validate(pw: str):
        if not isinstance(pw, str):
            return False, "Şifre metin olmalı"
        s = pw.strip()
        min_len = _get_system_setting_int("sec_password_min_length", 8)
        if min_len <= 0:
            min_len = 8
        if len(s) < min_len:
            return False, f"En az {min_len} karakter"
        require_special = _get_system_setting_str("sec_password_require_special") == "1"
        if not any(c.isupper() for c in s):
            return False, "Büyük harf olmalı"
        if not any(c.islower() for c in s):
            return False, "Küçük harf olmalı"
        if not any(c.isdigit() for c in s):
            return False, "Rakam olmalı"
        if require_special and not any(c in "!@#$%^&*" for c in s):
            return False, "Özel karakter olmalı"
        return True, None


def check_password_history(db_path: str, username: str, new_password: str, max_history: int = 5) -> bool:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS password_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password_hash TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("SELECT password_hash FROM password_history WHERE username=? ORDER BY id DESC LIMIT ?", (username, max_history))
    rows = [r[0] for r in cur.fetchall()]
    ok, _ = verify_password(rows[0], new_password) if rows else (True, False)
    conn.close()
    return not ok
