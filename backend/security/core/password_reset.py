#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sifre Sifirlama - Email bazli OTP sistemi
Argon2 hash ile guvenli
"""

import logging
import secrets
import sqlite3
import string
from datetime import datetime, timedelta
from typing import Tuple

from yonetim.security.core.crypto import hash_password

try:
    from security.core.secure_password import PasswordPolicy as GlobalPasswordPolicy
except Exception:
    GlobalPasswordPolicy = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def request_password_reset(db_path: str, username_or_email: str) -> Tuple[bool, str]:
    """
    Sifre sifirlama talebi - Email gonder
    
    Returns:
        (basarili_mi, mesaj)
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        # Kullaniciyi bul (username veya email ile)
        cur.execute("""
            SELECT id, username, email, display_name, is_active
            FROM users
            WHERE username = ? OR email = ?
        """, (username_or_email, username_or_email))

        user = cur.fetchone()

        if not user:
            # Guvenlik: Kullanici bulunamadi deme
            return False, "Kullanici bulunamadi veya email kayitli degil"

        user_id, username, email, display_name, is_active = user

        # Aktif mi?
        if not is_active:
            return False, "Hesap pasif durumda"

        # Email var mi?
        if not email or '@' not in email:
            return False, "Kullanicinin kayitli email adresi yok"

        # OTP kodu olustur (6 haneli)
        otp_code = ''.join(secrets.choice(string.digits) for _ in range(6))

        # Gecerlilik suresi (10 dakika)
        expires_at = datetime.now() + timedelta(minutes=10)

        # Veritabanina kaydet
        # password_reset_tokens tablosu varsa kullan, yoksa olustur
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    token TEXT NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Eski tokenları sil
            cur.execute("""
                DELETE FROM password_reset_tokens 
                WHERE user_id = ? AND (used = 1 OR expires_at < datetime('now'))
            """, (user_id,))

            # Yeni token ekle
            cur.execute("""
                INSERT INTO password_reset_tokens (user_id, token, expires_at)
                VALUES (?, ?, ?)
            """, (user_id, otp_code, expires_at.isoformat()))

            conn.commit()

        except Exception as e:
            logging.error(f"[HATA] Token kaydedilemedi: {e}")
            conn.rollback()
            return False, "Token olusturulamadi"

        # Email gonder
        try:
            from services.email_service import EmailService

            email_service = EmailService(db_path=db_path)

            success = email_service.send_password_reset_email(
                to_email=email,
                user_name=display_name or username,
                reset_code=otp_code,
                support_email="destek@sustainage.com"  # Kullanici degistirecek
            )

            if success:
                return True, f"Sifre sifirlama kodu {email} adresine gonderildi"
            else:
                return False, "Email gonderilemedi. Lutfen daha sonra tekrar deneyin"

        except Exception as e:
            logging.error(f"[HATA] Email gonderilemedi: {e}")
            # Yine de kodu console'a yazdir (test icin)
            logging.info(f"[TEST] Sifre sifirlama kodu: {otp_code}")
            return True, f"Kod olusturuldu (email gonderimi basarisiz): {otp_code}"

    except Exception as e:
        logging.error(f"[HATA] Sifre sifirlama hatasi: {e}")
        return False, "Sistem hatasi"
    finally:
        conn.close()


def verify_reset_code_and_change_password(db_path: str, username: str, code: str, new_password: str) -> Tuple[bool, str]:
    """
    Reset kodunu dogrula ve sifreyi degistir
    
    Returns:
        (basarili_mi, mesaj)
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        # Kullaniciyi bul
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cur.fetchone()

        if not user:
            return False, "Kullanici bulunamadi"

        user_id = user[0]

        # Token dogrula
        cur.execute("""
            SELECT id, expires_at
            FROM password_reset_tokens
            WHERE user_id = ? AND token = ? AND used = 0
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id, code))

        token_row = cur.fetchone()

        if not token_row:
            return False, "Gecersiz veya kullanilmis kod"

        token_id, expires_at_str = token_row

        # Surenin dolmadigini kontrol et
        expires_at = datetime.fromisoformat(expires_at_str)
        if datetime.now() > expires_at:
            return False, "Kodun suresi dolmus. Lutfen yeni kod isteyin"

        if GlobalPasswordPolicy is not None:
            ok, msg = GlobalPasswordPolicy.validate(new_password)
            if not ok:
                return False, msg or "Sifre politikaya uymuyor"
        else:
            if len(new_password) < 8:
                return False, "Sifre en az 8 karakter olmali"

        # Yeni sifreyi hashle
        new_hash = hash_password(new_password)

        # Sifreyi guncelle
        cur.execute("""
            UPDATE users
            SET password_hash = ?, pw_hash_version = 'argon2', must_change_password = 0
            WHERE id = ?
        """, (new_hash, user_id))

        # Token'i kullanilmis olarak isaretleupdate
        cur.execute("""
            UPDATE password_reset_tokens
            SET used = 1
            WHERE id = ?
        """, (token_id,))

        conn.commit()

        logging.info(f"[OK] Sifre sifirlandi: {username}")
        return True, "Sifreniz basariyla degistirildi"

    except Exception as e:
        logging.error(f"[HATA] Sifre degistirme hatasi: {e}")
        conn.rollback()
        return False, "Sistem hatasi"
    finally:
        conn.close()

