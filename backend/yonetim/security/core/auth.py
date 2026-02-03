from __future__ import annotations
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Güvenlik Core - Authentication Modülü
SUSTAINAGE-SDG'den adapte edilmiş kimlik doğrulama sistemi
"""

import logging
import json
import time
from typing import Dict, List, Optional

import pyotp
from argon2.low_level import Type, hash_secret

from .crypto import hash_password, verify_password_compat

SUPER_ADMIN_USERNAME = "__super__"
# Sabit şifre KESİNLİKLE kullanılmaz; super-admin kurulum aracı ile oluşturulmalı.

# Brute-force ve hesap kilitleme parametreleri
LOCK_THRESHOLD = 5            # 5 başarısız denemeden sonra kilitle
BASE_LOCK_SECONDS = 15 * 60   # 15 dakika
MAX_BACKOFF_STEPS = 3         # 15m → 30m → 60m

# ------------ yardımcılar ------------
def _get_user_row(conn, username: str) -> None:
    cur = conn.cursor()
    cur.execute("""
        SELECT id, username, password_hash, is_superadmin, is_active,
               totp_secret_encrypted, totp_enabled, backup_codes,
               is_admin, last_login, must_change_password, deleted_at
          FROM users WHERE username=?
    """, (username,))
    return cur.fetchone()

def _create_user(conn, username: str, password_plain: str, *,
                 is_super: bool=False, is_admin: bool=False, is_active: bool=True, must_change: bool=False):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users(username,password_hash,is_superadmin,is_active,is_admin,must_change_password)
        VALUES (?,?,?,?,?,?)
    """, (username, hash_password(password_plain), 1 if is_super else 0, 1 if is_active else 0,
          1 if is_admin else 0, 1 if must_change else 0))
    conn.commit()

def _update_user_flags(conn, user_id: int, *, is_super: Optional[bool]=None, is_active: Optional[bool]=None,
                       is_admin: Optional[bool]=None, must_change: Optional[bool]=None):
    sets = []
    params = []
    if is_super is not None:
        sets.append("is_superadmin=?")
        params.append(1 if is_super else 0)
    if is_active is not None:
        sets.append("is_active=?")
        params.append(1 if is_active else 0)
    if is_admin is not None:
        sets.append("is_admin=?")
        params.append(1 if is_admin else 0)
    if must_change is not None:
        sets.append("must_change_password=?")
        params.append(1 if must_change else 0)
    if not sets:
        return
    params.append(user_id)
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET {', '.join(sets)} WHERE id=?", params)
    conn.commit()

def ensure_super_account_exists(conn) -> bool:
    """__super__ hesabının varlığını kontrol eder; otomatik oluşturma yapmaz."""
    row = _get_user_row(conn, SUPER_ADMIN_USERNAME)
    return bool(row)

def _ensure_lockout_columns(conn) -> None:
    """users tablosunda failed_attempts ve locked_until sütunlarını güvenli şekilde ekler."""
    try:
        cur = conn.cursor()
        # failed_attempts
        try:
            cur.execute("ALTER TABLE users ADD COLUMN failed_attempts INTEGER DEFAULT 0")
        except Exception as e:
            logging.error(f'Silent error in auth.py: {str(e)}')
        # locked_until (epoch seconds)
        try:
            cur.execute("ALTER TABLE users ADD COLUMN locked_until INTEGER")
        except Exception as e:
            logging.error(f'Silent error in auth.py: {str(e)}')
        conn.commit()
    except Exception:
        # Sessiz geç, login yine çalışsın; kilitleme özellikleri devre dışı kalır
        logging.error(f'Silent error in auth.py: {str(e)}')

# ------------ login ------------
def login(conn, username: str, password: str) -> Dict:
    uname = (username or "").strip()
    row = _get_user_row(conn, uname)
    if not row:
        # Super-admin otomatik oluşturulmaz; kurulum aracı kullanılmalı
        return {"ok": False, "reason": "invalid"}

    (_id, _username, pw_hash, is_super, is_active,
     totp_secret, totp_enabled, _backup,
     is_admin, last_login, must_change, deleted_at) = row

    if deleted_at:
        return {"ok": False, "reason": "inactive"}
    if int(is_active) != 1:
        return {"ok": False, "reason": "inactive"}
    # Kilit kontrolü
    _ensure_lockout_columns(conn)
    try:
        cur = conn.cursor()
        cur.execute("SELECT locked_until, failed_attempts FROM users WHERE id=?", (_id,))
        lk = cur.fetchone()
        if lk and lk[0]:
            now = int(time.time())
            if int(lk[0]) > now:
                return {"ok": False, "reason": "locked", "until": int(lk[0])}
    except Exception as e:
        logging.error(f'Silent error in auth.py: {str(e)}')
    if not verify_password_compat(pw_hash, password or ""):
        # Başarısız deneme sayacı ve kilitleme
        try:
            _ensure_lockout_columns(conn)
            cur = conn.cursor()
            cur.execute("SELECT failed_attempts FROM users WHERE id=?", (_id,))
            row_fail = cur.fetchone()
            current = int(row_fail[0] or 0) if row_fail else 0
            new_fail = current + 1
            lock_until = None
            if new_fail >= LOCK_THRESHOLD:
                steps = min(new_fail - LOCK_THRESHOLD, MAX_BACKOFF_STEPS)
                lock_secs = BASE_LOCK_SECONDS * (2 ** steps)
                lock_until = int(time.time()) + lock_secs
            cur.execute("UPDATE users SET failed_attempts=?, locked_until=? WHERE id=?",
                        (new_fail, lock_until, _id))
            conn.commit()
        except Exception as e:
            logging.error(f'Silent error in auth.py: {str(e)}')
        try:
            from .audit import audit_security_event
            audit_security_event(conn, actor=uname, event="login_failed", details={"user_id": _id})
        except Exception as e:
            logging.error(f'Silent error in auth.py: {str(e)}')
        return {"ok": False, "reason": "invalid"}

    _touch_last_login(conn, _id)
    # Başarılı girişte sayaçları sıfırla
    try:
        _ensure_lockout_columns(conn)
        cur = conn.cursor()
        cur.execute("UPDATE users SET failed_attempts=0, locked_until=NULL WHERE id=?", (_id,))
        conn.commit()
    except Exception as e:
        logging.error(f'Silent error in auth.py: {str(e)}')
    try:
        from .audit import audit_user_action
        audit_user_action(conn, actor=uname, action="login", target_user=uname)
    except Exception as e:
        logging.error(f'Silent error in auth.py: {str(e)}')
    return {"ok": True,
            "user_id": _id,
            "is_super": bool(int(is_super)==1),
            "is_admin": bool(int(is_admin)==1),
            "needs_2fa": bool(int(totp_enabled)==1),
            "must_change_password": bool(int(must_change)==1)}

def _touch_last_login(conn, user_id: int) -> None:
    cur = conn.cursor()
    cur.execute("UPDATE users SET last_login=? WHERE id=?", (int(time.time()), user_id))
    conn.commit()

# ------------ 2FA / TOTP ------------
def generate_totp_secret() -> str:
    return pyotp.random_base32()

def get_otpauth_uri(username: str, secret: str, issuer: str="SUSTAINAGE-SDG") -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name=issuer)

def verify_totp(secret: str, code: str, valid_window: int=1) -> bool:
    if not secret:
        return False
    totp = pyotp.TOTP(secret)
    try:
        return totp.verify(code, valid_window=valid_window)
    except Exception:
        return False

def _argon2_hash(s: str) -> str:
    return hash_secret(s.encode("utf-8"), b"SUSTAINAGE_SALT",
                       time_cost=2, memory_cost=512, parallelism=2, hash_len=32, type=Type.I).hex()

def _generate_backup_codes(n: int=10) -> None:
    import random
    import string
    plain = ["".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) for __ in range(n)]
    hashed = [_argon2_hash(p) for p in plain]
    return plain, hashed

def enable_2fa(conn, username: str, secret: str) -> dict:
    cur = conn.cursor()
    plain, hashed = _generate_backup_codes()
    cur.execute("UPDATE users SET totp_secret_encrypted=?, totp_enabled=1, backup_codes=? WHERE username=?",
                (secret, json.dumps(hashed), username))
    conn.commit()
    return {"ok": True, "backup_plain": plain}

def disable_2fa(conn, username: str) -> dict:
    cur = conn.cursor()
    cur.execute("UPDATE users SET totp_secret_encrypted=NULL, totp_enabled=0, backup_codes=NULL WHERE username=?", (username,))
    conn.commit()
    return {"ok": True}

def consume_backup_code(conn, username: str, code_plain: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT backup_codes FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    if not row or not row[0]:
        return False
    try:
        codes = json.loads(row[0])
    except Exception:
        return False
    h = _argon2_hash(code_plain)
    if h not in codes:
        return False
    codes.remove(h)
    cur.execute("UPDATE users SET backup_codes=? WHERE username=?", (json.dumps(codes), username))
    conn.commit()
    return True

def regen_backup_codes(conn, username: str) -> dict:
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username=?", (username,))
    if not cur.fetchone():
        return {"ok": False, "reason": "not_found"}
    plain, hashed = _generate_backup_codes()
    cur.execute("UPDATE users SET backup_codes=? WHERE username=?", (json.dumps(hashed), username))
    conn.commit()
    return {"ok": True, "backup_plain": plain}

def is_force_2fa(conn) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key='force_2fa'")
    row = cur.fetchone()
    return bool(row and row[0] == "1")

def set_force_2fa(conn, on: bool) -> None:
    cur = conn.cursor()
    cur.execute("INSERT INTO settings(key,value) VALUES('force_2fa',?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value", ("1" if on else "0",))
    conn.commit()

# ------------ parola işlemleri ------------
def _random_token(n: int=6) -> str:
    import random
    import string
    return "".join(random.choice(string.digits) for _ in range(n))

def create_reset_token(conn, username: str, ttl_seconds: int=900) -> dict:
    cur = conn.cursor()
    cur.execute("SELECT id, is_active FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    if not row:
        return {"ok": False, "reason": "not_found"}
    if int(row[1]) != 1:
        return {"ok": False, "reason": "inactive"}
    token = _random_token(6)
    expires = int(time.time()) + int(ttl_seconds)
    cur.execute("INSERT INTO password_resets(username, token, expires_at, used) VALUES (?,?,?,0)",
                (username, token, expires))
    conn.commit()
    return {"ok": True, "token": token, "expires_at": expires}

def reset_password_with_token(conn, username: str, token: str, new_password: str) -> dict:
    cur = conn.cursor()
    now = int(time.time())
    cur.execute("SELECT id FROM password_resets WHERE username=? AND token=? AND used=0 AND expires_at>?",
                (username, token, now))
    row = cur.fetchone()
    if not row:
        return {"ok": False, "reason": "invalid_or_expired"}
    cur.execute("UPDATE users SET password_hash=?, must_change_password=0 WHERE username=?",
                (hash_password(new_password), username))
    cur.execute("UPDATE password_resets SET used=1 WHERE id=?", (row[0],))
    conn.commit()
    return {"ok": True}

def change_own_password(conn, username: str, old_password: str, new_password: str) -> dict:
    row = _get_user_row(conn, username)
    if not row:
        return {"ok": False, "reason": "not_found"}
    if not verify_password_compat(row[2], old_password or ""):
        return {"ok": False, "reason": "invalid_old"}
    cur = conn.cursor()
    cur.execute("UPDATE users SET password_hash=?, must_change_password=0 WHERE id=?",
                (hash_password(new_password), row[0]))
    conn.commit()
    return {"ok": True}

# ------------ admin işlemleri ------------
def _admin_count(conn) -> int:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE is_admin=1 AND is_active=1 AND deleted_at IS NULL")
    return int(cur.fetchone()[0])

def create_user_by_admin(conn, actor_is_super: bool, actor_is_admin: bool,
                         username: str, temp_password: str, make_admin: bool=False) -> dict:
    if not (actor_is_super or actor_is_admin):
        return {"ok": False, "reason": "forbidden"}
    if username == SUPER_ADMIN_USERNAME:
        return {"ok": False, "reason": "forbidden"}
    if _get_user_row(conn, username):
        return {"ok": False, "reason": "exists"}
    _create_user(conn, username, temp_password, is_super=False, is_admin=make_admin, is_active=True, must_change=True)
    return {"ok": True}

def admin_reset_password(conn, actor_is_super: bool, actor_is_admin: bool,
                         target_username: str, new_temp_password: str) -> dict:
    if not (actor_is_super or actor_is_admin):
        return {"ok": False, "reason": "forbidden"}
    row = _get_user_row(conn, target_username)
    if not row:
        return {"ok": False, "reason": "not_found"}
    if int(row[3]) == 1 and not actor_is_super:
        return {"ok": False, "reason": "forbidden"}
    cur = conn.cursor()
    cur.execute("UPDATE users SET password_hash=?, must_change_password=1 WHERE id=?",
                (hash_password(new_temp_password), row[0]))
    conn.commit()
    return {"ok": True}

def set_user_active(conn, actor_is_super: bool, actor_is_admin: bool, username: str, active: bool) -> dict:
    if not (actor_is_super or actor_is_admin):
        return {"ok": False, "reason": "forbidden"}
    row = _get_user_row(conn, username)
    if not row:
        return {"ok": False, "reason": "not_found"}
    if row[1] == SUPER_ADMIN_USERNAME:
        return {"ok": False, "reason": "forbidden"}
    if int(row[8]) == 1 and not active and _admin_count(conn) <= 1:
        return {"ok": False, "reason": "last_admin"}
    _update_user_flags(conn, row[0], is_active=active)
    return {"ok": True}

def set_user_admin(conn, actor_is_super: bool, actor_is_admin: bool, username: str, make_admin: bool) -> dict:
    if not (actor_is_super or actor_is_admin):
        return {"ok": False, "reason": "forbidden"}
    row = _get_user_row(conn, username)
    if not row:
        return {"ok": False, "reason": "not_found"}
    if row[1] == SUPER_ADMIN_USERNAME:
        return {"ok": False, "reason": "forbidden"}
    if int(row[8]) == 1 and (not make_admin) and _admin_count(conn) <= 1:
        return {"ok": False, "reason": "last_admin"}
    _update_user_flags(conn, row[0], is_admin=make_admin)
    return {"ok": True}

def soft_delete_user(conn, actor_is_super: bool, actor_is_admin: bool, username: str) -> dict:
    if not (actor_is_super or actor_is_admin):
        return {"ok": False, "reason": "forbidden"}
    row = _get_user_row(conn, username)
    if not row:
        return {"ok": False, "reason": "not_found"}
    if row[1] == SUPER_ADMIN_USERNAME:
        return {"ok": False, "reason": "forbidden"}
    if int(row[8]) == 1 and _admin_count(conn) <= 1:
        return {"ok": False, "reason": "last_admin"}
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_active=0, deleted_at=? WHERE id=?", (int(time.time()), row[0]))
    conn.commit()
    return {"ok": True}

def list_users_for_admin(conn, include_super: bool=False) -> List[dict]:
    """
    include_super=False iken __super__ kayıtları listeden düşer.
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT username, is_admin, is_active, totp_enabled, last_login, must_change_password, deleted_at, is_superadmin
          FROM users
         ORDER BY (username=?) DESC, username
    """, (SUPER_ADMIN_USERNAME,))
    out = []
    for u, is_admin, is_active, t2, last_login, must, deleted_at, is_super in cur.fetchall():
        if (not include_super) and (u == SUPER_ADMIN_USERNAME):
            continue
        out.append({
            "username": u,
            "is_admin": bool(int(is_admin)==1),
            "is_active": bool(int(is_active)==1),
            "totp": bool(int(t2)==1),
            "last_login": last_login or 0,
            "must_change_password": bool(int(must)==1),
            "deleted": bool(deleted_at is not None),
            "is_super": bool(int(is_super)==1),
        })
    return out
