#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-posta kimlik bilgilerini güvenli şekilde saklama aracı
- Parolayı Argon2 ile hash'ler (geri döndürülemez)
- İsteğe bağlı olarak parolayı Fernet (AES-128) ile şifreler (geri çözülebilir)
- Çıktıyı config/email_credentials.json dosyasına yazar

GÜVENLİK
- Parola ve anahtar sadece ortam değişkenlerinden okunur: SENDER_EMAIL, SENDER_PASSWORD, SENDER_PASSWORD_KEY
- Parola/anahtar asla ekrana yazdırılmaz, loglanmaz
"""

import logging
import base64
import json
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Argon2 hashing
try:
    from argon2 import PasswordHasher
    from argon2.low_level import Type
    ARGON2_AVAILABLE = True
except Exception:
    ARGON2_AVAILABLE = False
    import hashlib

# Fernet encryption
try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except Exception:
    CRYPTO_AVAILABLE = False

OUTPUT_PATH = os.path.join('config', 'email_credentials.json')


def mask_email(email: str) -> str:
    try:
        user, domain = email.split('@', 1)
        if len(user) <= 2:
            masked_user = user[0] + '*' * max(0, len(user) - 1)
        else:
            masked_user = user[0] + '*' * (len(user) - 2) + user[-1]
        return f"{masked_user}@{domain}"
    except Exception:
        return email[:1] + '***'


def hash_password_argon2(password: str) -> str:
    if ARGON2_AVAILABLE:
        ph = PasswordHasher(time_cost=3, memory_cost=64 * 1024, parallelism=2, type=Type.ID)
        return ph.hash(password)
    # Fallback: PBKDF2-SHA256 (salt + iterations)
    salt = os.urandom(16)
    iterations = 200_000
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    return f"pbkdf2_sha256${iterations}${base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"


def encrypt_password(password: str, key_b64: str | None) -> str | None:
    if not CRYPTO_AVAILABLE or not key_b64:
        return None
    try:
        # Eğer KEY verilmemişse, kullanıcı dışarıda üretsin (örn. Fernet.generate_key())
        f = Fernet(key_b64.encode('utf-8'))
        token = f.encrypt(password.encode('utf-8'))
        return token.decode('utf-8')
    except Exception:
        return None


def main() -> None:
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    key_b64 = os.getenv('SENDER_PASSWORD_KEY')  # Opsiyonel: Fernet key (base64)

    if not sender_email or not sender_password:
        logging.error('[HATA] SENDER_EMAIL ve SENDER_PASSWORD ortam değişkenlerini ayarlayın.')
        logging.info('Örnek (PowerShell):')
        logging.info('$env:SENDER_EMAIL = "system@digage.tr"')
        logging.info('$env:SENDER_PASSWORD = "<SMTP_SIFRENIZ>"')
        logging.info('Opsiyonel: $env:SENDER_PASSWORD_KEY = "<FERNET_BASE64_KEY>"')
        return

    # Hash ve opsiyonel şifreleme
    password_hash = hash_password_argon2(sender_password)
    password_enc = encrypt_password(sender_password, key_b64)

    record = {
        'sender_email': sender_email,
        'email_mask': mask_email(sender_email),
        'password_hash': password_hash,
        'hash_alg': 'argon2id' if ARGON2_AVAILABLE else 'pbkdf2_sha256',
        'password_enc': password_enc,  # None olabilir; sadece KEY verilirse yazılır
        'enc_alg': 'fernet' if password_enc else None,
        'updated_at': datetime.now().isoformat(timespec='seconds'),
        'notes': 'Parola hiçbir zaman düz metin olarak saklanmaz. Şifreleme için KEY env kullanın.'
    }

    os.makedirs('config', exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

    logging.info('[OK] Kimlik bilgileri güvenli şekilde saklandı: config/email_credentials.json')
    if password_enc:
        logging.info('[INFO] Şifreli parola yazıldı (Fernet). Çözmek için SENDER_PASSWORD_KEY gerekli.')
    else:
        logging.info('[INFO] Şifreleme anahtarı verilmedi, sadece hash kaydedildi.')


if __name__ == '__main__':
    main()
