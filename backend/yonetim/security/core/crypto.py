#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Güvenlik Core - Şifreleme Modülü
SUSTAINAGE-SDG'den adapte edilmiş şifreleme sistemi
"""

from __future__ import annotations

import base64
import ctypes
import hashlib
import string
import sys
import os
try:
    from ctypes import wintypes
except ValueError:
    # Linux/Mac üzerinde wintypes bulunmayabilir
    wintypes = None
from typing import Optional

# -------------------------
#  Parola Karma (Argon2)
# -------------------------
try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError
except Exception as _:
    # argon2-cffi yoksa anlamlı bir hata verelim
    PasswordHasher = None
    VerifyMismatchError = Exception

# Varsayılan güvenli ayarlar (argon2id)
_PH: Optional["PasswordHasher"] = None
def _ph() -> "PasswordHasher":
    global _PH
    if _PH is None:
        if PasswordHasher is None:
            raise RuntimeError("argon2-cffi paketi kurulu değil. `pip install argon2-cffi`")
        # İstersen burada time_cost/memory_cost/parallelism ayarlarını özelleştirebilirsin
        _PH = PasswordHasher()
    return _PH

def hash_password(plain: str) -> str:
    """
    Kullanıcı parolalarını güvenli şekilde karmalar.
    DÖNÜŞ: Argon2 karması (ör. '$argon2id$v=19$...')
    """
    if not isinstance(plain, str):
        raise TypeError("plain must be str")
    return _ph().hash(plain)

def verify_password(stored_hash: str, plain: str) -> bool:
    """
    Argon2 karmasını doğrular. Doğruysa True, değilse False.
    """
    try:
        _ph().verify(stored_hash, plain)
        return True
    except VerifyMismatchError:
        return False
    except Exception:
        # Her ihtimale karşı tüm diğer hataları da başarısız sayalım
        return False


def verify_password_compat(stored_hash: str, plain: str) -> bool:
    """
    Geriye dönük uyumluluk:
    - Argon2 ('$argon2...')
    - PBKDF2-SHA256 ('salt:hexhash')
    - Düz SHA-256 hex (64 haneli)
    """
    if not stored_hash:
        return False
    try:
        # Argon2
        if stored_hash.startswith("$argon2"):
            return verify_password(stored_hash, plain)
        if stored_hash.startswith("argon2$"):
            try:
                s = stored_hash.split("argon2$", 1)[1]
            except Exception:
                s = stored_hash
            return verify_password(s, plain)
        # Werkzeug (pbkdf2:...)
        if stored_hash.startswith("pbkdf2:") or stored_hash.startswith("scrypt:"):
            try:
                from werkzeug.security import check_password_hash
                return check_password_hash(stored_hash, plain)
            except ImportError:
                pass
        # PBKDF2-SHA256 (salt:hash)
        if ":" in stored_hash:
            salt, hash_hex = stored_hash.split(":", 1)
            calc = hashlib.pbkdf2_hmac('sha256', (plain or "").encode('utf-8'), salt.encode('utf-8'), 100000).hex()
            return calc == hash_hex
        # Düz SHA-256 hex
        hexdigits = set(string.hexdigits)
        if len(stored_hash) == 64 and all(c in hexdigits for c in stored_hash):
            return hashlib.sha256((plain or "").encode('utf-8')).hexdigest() == stored_hash
    except Exception:
        return False
    return False


# -------------------------
#  DPAPI ile Şifreleme
# -------------------------
def _win_protect(data: bytes) -> bytes:
    CRYPTPROTECT_UI_FORBIDDEN = 0x1

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [
            ("cbData", wintypes.DWORD),
            ("pbData", ctypes.POINTER(ctypes.c_byte)),
        ]

    pDataIn = DATA_BLOB(
        len(data),
        ctypes.cast(ctypes.create_string_buffer(data), ctypes.POINTER(ctypes.c_byte)),
    )
    pDataOut = DATA_BLOB()
    if not ctypes.windll.crypt32.CryptProtectData(
        ctypes.byref(pDataIn),
        None,
        None,
        None,
        None,
        CRYPTPROTECT_UI_FORBIDDEN,
        ctypes.byref(pDataOut),
    ):
        raise OSError("CryptProtectData failed")

    try:
        buf = ctypes.string_at(pDataOut.pbData, pDataOut.cbData)
        ctypes.windll.kernel32.LocalFree(pDataOut.pbData)
        return buf
    except Exception:
        ctypes.windll.kernel32.LocalFree(pDataOut.pbData)
        raise

def _win_unprotect(data: bytes) -> bytes:
    CRYPTPROTECT_UI_FORBIDDEN = 0x1

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [
            ("cbData", wintypes.DWORD),
            ("pbData", ctypes.POINTER(ctypes.c_byte)),
        ]

    pDataIn = DATA_BLOB(
        len(data),
        ctypes.cast(ctypes.create_string_buffer(data), ctypes.POINTER(ctypes.c_byte)),
    )
    pDataOut = DATA_BLOB()
    if not ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(pDataIn),
        None,
        None,
        None,
        None,
        CRYPTPROTECT_UI_FORBIDDEN,
        ctypes.byref(pDataOut),
    ):
        raise OSError("CryptUnprotectData failed")

    try:
        buf = ctypes.string_at(pDataOut.pbData, pDataOut.cbData)
        ctypes.windll.kernel32.LocalFree(pDataOut.pbData)
        return buf
    except Exception:
        ctypes.windll.kernel32.LocalFree(pDataOut.pbData)
        raise

def protect_str(plain: str) -> str:
    """
    Metni şifreler ve Base64-url olarak döner.
    Windows'ta DPAPI, diğer OS'lerde yalnız Base64 (uyarı: korumasız).
    """
    data = plain.encode("utf-8")
    if sys.platform.startswith("win"):
        enc = _win_protect(data)
    else:
        # Non-Windows için güçlü koruma istenirse bir KMS/keystore entegre edilebilir.
        enc = data
    return base64.urlsafe_b64encode(enc).decode("ascii")

def unprotect_str(enc_b64: str) -> str:
    """
    Base64-url şifreli metni çözer.
    Windows'ta DPAPI çözümü, diğer OS'lerde Base64 çözümü yapılır.
    """
    if not enc_b64:
        return ""
    raw = base64.urlsafe_b64decode(enc_b64.encode("ascii"))
    if sys.platform.startswith("win"):
        dec = _win_unprotect(raw)
    else:
        dec = raw
    return dec.decode("utf-8", errors="ignore")
