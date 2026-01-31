#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
"""
GÜVENLİ KULLANICI OLUŞTURMA
- Admin tarafından geçici şifre ile kullanıcı oluşturma
- Argon2 hash ile güvenli saklama
- İlk girişte zorunlu şifre değiştirme (must_change_password=TRUE)
- Audit logging
"""

import secrets
import sqlite3
import string
from datetime import datetime
from typing import Dict, Optional, Tuple

from services.email_service import EmailService
from utils.language_manager import LanguageManager

lm = LanguageManager()

try:
    from yonetim.security.core.audit import write_audit
    from yonetim.security.core.crypto import hash_password
except Exception:
    from yonetim.security.core.audit import write_audit
    from yonetim.security.core.crypto import hash_password

try:
    from security.core.secure_password import PasswordPolicy as GlobalPasswordPolicy
except Exception:
    GlobalPasswordPolicy = None


class PasswordPolicy:
    def __init__(self):
        pass

    @staticmethod
    def validate(pw: str):
        if GlobalPasswordPolicy is not None:
            return GlobalPasswordPolicy.validate(pw)
        if not isinstance(pw, str):
            return False, lm.tr("err_password_not_string", "Şifre metin olmalı")
        pw = pw.strip()
        if len(pw) < 8:
            return False, lm.tr("err_password_too_short", "En az 8 karakter")
        has_upper = any(c.isupper() for c in pw)
        has_lower = any(c.islower() for c in pw)
        has_digit = any(c.isdigit() for c in pw)
        has_special = any(c in "!@#$%^&*" for c in pw)
        if not (has_upper and has_lower and has_digit and has_special):
            return False, lm.tr("err_password_complexity", "Büyük/küçük harf, rakam ve özel karakter olmalı")
        return True, None

def audit_log(db_path: str, action: str, **kwargs) -> None:
    actor = kwargs.get('username') or str(kwargs.get('user_id') or '-')
    details = kwargs.get('metadata') or {}
    details.update({
        'success': kwargs.get('success'),
        'user_id': kwargs.get('user_id'),
    })
    conn = sqlite3.connect(db_path)
    try:
        write_audit(conn, actor, action, details)
    finally:
        conn.close()


def generate_temp_password(length: int = 12) -> str:
    """
    Güvenli geçici şifre üret
    
    Politikaya uygun: En az 1 büyük, 1 küçük, 1 rakam, 1 özel karakter
    """
    # Karakter grupları
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*"

    # Her gruptan en az 1 karakter
    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(special)
    ]

    # Geri kalanı rastgele
    all_chars = lowercase + uppercase + digits + special
    password += [secrets.choice(all_chars) for _ in range(length - 4)]

    # Karıştır
    secrets.SystemRandom().shuffle(password)

    return ''.join(password)


def create_user_with_temp_password(
    db_path: str,
    username: str,
    email: str,
    display_name: str,
    role: str,
    temp_password: Optional[str] = None,
    created_by_user_id: Optional[int] = None,
    is_active: bool = True
) -> Tuple[bool, str, Optional[int], Optional[str]]:
    """
    Güvenli kullanıcı oluştur (geçici şifre ile)
    
    Args:
        db_path: Veritabanı yolu
        username: Kullanıcı adı (küçük harfe çevrilir)
        email: Email adresi
        display_name: Görünen ad
        role: Rol (admin, user, vb.)
        temp_password: Geçici şifre (verilmezse otomatik üretilir)
        created_by_user_id: Oluşturan admin ID
        is_active: Hesap aktif mi?
    
    Returns:
        (başarılı_mı, mesaj, user_id, geçici_şifre)
    """
    # Kullanıcı adını normalize et
    username = username.strip().lower()

    # Validasyon
    if not username:
        return False, lm.tr("err_username_empty", "Kullanıcı adı boş olamaz"), None, None

    if not email:
        return False, lm.tr("err_email_empty", "Email boş olamaz"), None, None

    # Email format kontrolü (basit)
    if '@' not in email:
        return False, lm.tr("err_email_invalid", "Geçerli bir email adresi girin"), None, None

    # Geçici şifre üret veya kontrol et
    if temp_password:
        # Verilen şifreyi kontrol et (minimum politika)
        is_valid, error = PasswordPolicy.validate(temp_password)
        if not is_valid:
            return False, lm.tr("err_temp_password_policy", "Geçici şifre politikaya uymuyor: {}").format(error), None, None
    else:
        # Otomatik üret
        temp_password = generate_temp_password()

    # Şifreyi hash'le
    password_hash = hash_password(temp_password)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        # Kullanıcı adı benzersizliği kontrol et
        cur.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?)", (username,))
        if cur.fetchone():
            return False, lm.tr("err_username_exists", "Kullanıcı adı '{}' zaten kullanılıyor").format(username), None, None

        # Email benzersizliği kontrol et
        cur.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (email,))
        if cur.fetchone():
            return False, lm.tr("err_email_exists", "Email '{}' zaten kullanılıyor").format(email), None, None

        # Get table info to check for columns
        cur.execute("PRAGMA table_info(users)")
        columns_info = cur.fetchall()
        column_names = [info[1] for info in columns_info]

        # Dynamic column availability
        has_display_name = 'display_name' in column_names
        has_first_name = 'first_name' in column_names
        has_last_name = 'last_name' in column_names
        has_role = 'role' in column_names
        has_must_change_password = 'must_change_password' in column_names
        has_failed_attempts = 'failed_attempts' in column_names
        has_login_attempts = 'login_attempts' in column_names
        has_pw_hash_version = 'pw_hash_version' in column_names
        
        # Base columns
        insert_cols = ['username', 'email', 'password_hash', 'created_at']
        insert_vals = [username, email, password_hash, datetime.now().isoformat()]

        # Active status
        if 'is_active' in column_names:
            insert_cols.append('is_active')
            insert_vals.append(1 if is_active else 0)

        # Name handling
        if has_display_name:
            insert_cols.append('display_name')
            insert_vals.append(display_name)
        elif has_first_name and has_last_name:
            # Split display_name or use defaults
            parts = display_name.split(' ', 1) if display_name else [username, '']
            first = parts[0]
            last = parts[1] if len(parts) > 1 else ''
            insert_cols.extend(['first_name', 'last_name'])
            insert_vals.extend([first, last])
            
        # Role
        if has_role:
            insert_cols.append('role')
            insert_vals.append(role)
            
        # Password change requirement
        if has_must_change_password:
            insert_cols.append('must_change_password')
            insert_vals.append(1)
            
        # Failed attempts
        if has_failed_attempts:
            insert_cols.append('failed_attempts')
            insert_vals.append(0)
        elif has_login_attempts:
            insert_cols.append('login_attempts')
            insert_vals.append(0)
            
        # Hash version
        if has_pw_hash_version:
            insert_cols.append('pw_hash_version')
            insert_vals.append('argon2' if password_hash.startswith('argon2$') else 'pbkdf2')

        placeholders = ', '.join(['?'] * len(insert_cols))
        col_str = ', '.join(insert_cols)
        
        query = f"INSERT INTO users ({col_str}) VALUES ({placeholders})"
        cur.execute(query, tuple(insert_vals))

        user_id = cur.lastrowid
        conn.commit()

        # Audit log
        audit_log(
            db_path,
            "USER_CREATE",
            user_id=created_by_user_id,
            username=f"admin_created_{username}",
            success=True,
            metadata={
                "created_user_id": user_id,
                "created_username": username,
                "role": role,
                "temp_password_used": True
            }
        )
        try:
            email_service = EmailService()
            email_service.send_new_user_welcome(
                to_email=email,
                user_name=(display_name or username),
                login_url="https://sustainage.cloud/login",
                program_name=lm.tr("app_name_sdg", "Sustainage SDG Platformu"),
                short_description=lm.tr("email_welcome_short_desc", "Hesabınız oluşturuldu ve Sustainage SDG programına erişim sağlandı."),
                reason=lm.tr("email_welcome_reason", "Admin tarafından kullanıcı oluşturuldu"),
                support_email="sdg@digage.tr",
            )
        except Exception as e:
            logging.error(f'Silent error in secure_user_create.py: {str(e)}')

        return True, lm.tr("msg_user_created_success", "Kullanıcı başarıyla oluşturuldu"), user_id, temp_password

    except Exception as e:
        conn.rollback()
        audit_log(
            db_path,
            "USER_CREATE",
            user_id=created_by_user_id,
            success=False,
            metadata={"error": str(e), "username": username}
        )
        return False, lm.tr("err_user_creation_failed", "Kullanıcı oluşturulamadı: {}").format(str(e)), None, None

    finally:
        conn.close()


def bulk_create_users_from_list(
    db_path: str,
    users_data: list,
    created_by_user_id: Optional[int] = None
) -> Dict[str, list]:
    """
    Toplu kullanıcı oluşturma
    
    Args:
        users_data: [{"username": "...", "email": "...", "display_name": "...", "role": "..."}, ...]
    
    Returns:
        {
            "success": [{"username": "...", "temp_password": "..."}, ...],
            "failed": [{"username": "...", "error": "..."}, ...]
        }
    """
    results = {
        "success": [],
        "failed": []
    }

    for user_data in users_data:
        success, message, user_id, temp_password = create_user_with_temp_password(
            db_path,
            username=user_data.get('username'),
            email=user_data.get('email'),
            display_name=user_data.get('display_name', user_data.get('username')),
            role=user_data.get('role', 'user'),
            temp_password=user_data.get('temp_password'),  # Opsiyonel
            created_by_user_id=created_by_user_id,
            is_active=user_data.get('is_active', True)
        )

        if success:
            results["success"].append({
                "username": user_data.get('username'),
                "user_id": user_id,
                "temp_password": temp_password
            })
        else:
            results["failed"].append({
                "username": user_data.get('username'),
                "error": message
            })

    return results


# Test/Demo
if __name__ == "__main__":
    logging.info(" Güvenli Kullanıcı Oluşturma - Test")
    logging.info("="*60)

    db_path = "sdg.db"

    # 1. Otomatik geçici şifre ile kullanıcı oluştur
    logging.info("\n1️⃣ Otomatik Geçici Şifre ile Kullanıcı Oluşturma:")

    success, message, user_id, temp_password = create_user_with_temp_password(
        db_path,
        username=f"test_user_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        email=f"test{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
        display_name="Test User",
        role="user",
        created_by_user_id=1  # Admin ID
    )

    if success:
        logging.info(f"    {message}")
        logging.info(f"    User ID: {user_id}")
        logging.info(f"    Geçici Şifre: {temp_password}")
        logging.info("   ️ İlk girişte şifre değiştirilmeli!")
    else:
        logging.info(f"    {message}")

    # 2. Manuel geçici şifre ile
    logging.info("\n2️⃣ Manuel Geçici Şifre ile Kullanıcı Oluşturma:")

    manual_password = "ManuelTest123!"
    success2, message2, user_id2, _ = create_user_with_temp_password(
        db_path,
        username=f"manual_user_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        email=f"manual{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
        display_name="Manual Test User",
        role="user",
        temp_password=manual_password,
        created_by_user_id=1
    )

    if success2:
        logging.info(f"    {message2}")
        logging.info(f"    User ID: {user_id2}")
        logging.info(f"    Manuel Şifre: {manual_password}")
    else:
        logging.info(f"    {message2}")

    # 3. Toplu oluşturma örneği
    logging.info("\n3️⃣ Toplu Kullanıcı Oluşturma:")

    bulk_users = [
        {"username": f"bulk1_{datetime.now().strftime('%H%M%S')}", "email": f"bulk1{datetime.now().strftime('%H%M%S')}@example.com", "display_name": "Bulk User 1", "role": "user"},
        {"username": f"bulk2_{datetime.now().strftime('%H%M%S')}", "email": f"bulk2{datetime.now().strftime('%H%M%S')}@example.com", "display_name": "Bulk User 2", "role": "admin"},
    ]

    results = bulk_create_users_from_list(db_path, bulk_users, created_by_user_id=1)

    logging.info(f"    Başarılı: {len(results['success'])}")
    for user in results['success']:
        logging.info(f"      - {user['username']}: {user['temp_password']}")

    if results['failed']:
        logging.error(f"    Başarısız: {len(results['failed'])}")
        for user in results['failed']:
            logging.error(f"      - {user['username']}: {user['error']}")

    logging.info("\n" + "="*60)
    logging.info(" Test tamamlandı!")
