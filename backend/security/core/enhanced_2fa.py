import logging
import io
import sqlite3
import os
from typing import List, Tuple
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load .env explicitly to ensure we get the key
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
ENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(ENV_PATH)

ENCRYPTION_KEY = os.getenv("TOTP_ENCRYPTION_KEY")
_fernet = Fernet(ENCRYPTION_KEY) if ENCRYPTION_KEY else None

def _encrypt_secret(secret: str) -> str:
    """Encrypts the TOTP secret using Fernet (AES)."""
    if not _fernet or not secret:
        return secret
    try:
        return _fernet.encrypt(secret.encode()).decode()
    except Exception as e:
        logging.error(f"Error encrypting TOTP secret: {e}")
        return secret

def _decrypt_secret(encrypted_secret: str) -> str:
    """Decrypts the TOTP secret. Returns original if decryption fails (backward compatibility)."""
    if not _fernet or not encrypted_secret:
        return encrypted_secret
    try:
        return _fernet.decrypt(encrypted_secret.encode()).decode()
    except Exception:
        # If decryption fails, it might be an old unencrypted secret or invalid key
        return encrypted_secret

def enable_totp_for_user(db_path: str, username: str) -> Tuple[bool, str, str, bytes]:
    from yonetim.security.core.auth import (enable_2fa, generate_totp_secret,
                                            get_otpauth_uri)
    secret = generate_totp_secret()
    
    # Encrypt secret before storing in DB
    encrypted_secret = _encrypt_secret(secret)
    
    conn = sqlite3.connect(db_path)
    try:
        _ensure_2fa_columns(conn)
        # Pass encrypted secret to enable_2fa (which saves it to DB)
        res = enable_2fa(conn, username, encrypted_secret)
        
        # Use PLAIN secret for QR code generation (so user can scan it)
        uri = get_otpauth_uri(username, secret)
        qr_bytes = _qr_bytes(uri)
        
        return bool(res.get("ok")), "2FA etkin", secret, qr_bytes
    finally:
        conn.close()

def verify_totp_code(db_path: str, username: str, code: str) -> Tuple[bool, str]:
    from yonetim.security.core.auth import verify_totp
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT totp_secret FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row or not row[0]:
        return False, "secret yok"
    
    # Decrypt secret before verifying
    secret = _decrypt_secret(row[0])
    
    ok = verify_totp(secret, str(code))
    return ok, "ok" if ok else "geçersiz"

def get_backup_codes(db_path: str, username: str) -> Tuple[bool, str, List[str]]:
    from yonetim.security.core.auth import regen_backup_codes
    conn = sqlite3.connect(db_path)
    try:
        res = regen_backup_codes(conn, username)
        return bool(res.get("ok")), "ok" if res.get("ok") else "hata", list(res.get("backup_plain") or [])
    finally:
        conn.close()

def verify_backup_code(db_path: str, username: str, code: str) -> Tuple[bool, str]:
    from yonetim.security.core.auth import consume_backup_code
    conn = sqlite3.connect(db_path)
    try:
        _ensure_2fa_columns(conn)
        ok = consume_backup_code(conn, username, code)
        return ok, "ok" if ok else "geçersiz"
    finally:
        conn.close()

def disable_2fa(db_path: str, username: str) -> Tuple[bool, str]:
    from yonetim.security.core.auth import disable_2fa
    conn = sqlite3.connect(db_path)
    try:
        _ensure_2fa_columns(conn)
        res = disable_2fa(conn, username)
        return bool(res.get("ok")), "ok" if res.get("ok") else "hata"
    finally:
        conn.close()

def regenerate_backup_codes(db_path: str, username: str) -> Tuple[bool, str, List[str]]:
    from yonetim.security.core.auth import regen_backup_codes
    conn = sqlite3.connect(db_path)
    try:
        _ensure_2fa_columns(conn)
        res = regen_backup_codes(conn, username)
        return bool(res.get("ok")), "ok" if res.get("ok") else "hata", list(res.get("backup_plain") or [])
    finally:
        conn.close()

def _qr_bytes(data: str) -> bytes:
    try:
        import qrcode
        img = qrcode.make(data)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        return data.encode("utf-8")

def _ensure_2fa_columns(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE users ADD COLUMN totp_secret TEXT")
    except Exception as e:
        logging.error(f'Silent error in enhanced_2fa.py: {str(e)}')
    try:
        cur.execute("ALTER TABLE users ADD COLUMN totp_enabled INTEGER DEFAULT 0")
    except Exception as e:
        logging.error(f'Silent error in enhanced_2fa.py: {str(e)}')
    try:
        cur.execute("ALTER TABLE users ADD COLUMN backup_codes TEXT")
    except Exception as e:
        logging.error(f'Silent error in enhanced_2fa.py: {str(e)}')
    conn.commit()
