#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GÜVENLİK YÖNETİM ARACI
- Komut satırından güvenlik işlemleri
- Kullanıcı yönetimi
- 2FA yönetimi
- Token yönetimi
- Audit log inceleme
"""

import logging
import argparse
import os
import sys

# Path ayarı
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3

from security.core.enhanced_2fa import (disable_2fa, enable_totp_for_user,
                                        get_backup_codes,
                                        regenerate_backup_codes)
from security.core.file_permissions import secure_critical_files
from security.core.secure_password import (PasswordPolicy, audit_log,
                                           hash_password,
                                           reset_failed_attempts)
from security.core.temp_access_token import (generate_temp_token,
                                             list_active_tokens)
from config.icons import Icons
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    parser = argparse.ArgumentParser(
        description="SUSTAINAGE SDG Güvenlik Yönetim Aracı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  # Şifre sıfırlama
  python security_admin_tool.py reset-password admin --password "NewPassword123!"
  
  # 2FA etkinleştirme
  python security_admin_tool.py enable-2fa admin
  
  # Geçici token oluşturma
  python security_admin_tool.py create-token admin --duration 60 --uses 3
  
  # Hesap kilidi açma
  python security_admin_tool.py unlock-account admin
  
  # Audit logları görüntüleme
  python security_admin_tool.py show-logs --username admin --limit 50
"""
    )
    
    parser.add_argument(
        '--db',
        default=DB_PATH,
        help='Veritabanı yolu (varsayılan: data/sdg_desktop.sqlite)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Komutlar')
    
    # ========================================
    # PAROLA YÖNETİMİ
    # ========================================
    
    reset_pwd = subparsers.add_parser('reset-password', help='Kullanıcı şifresini sıfırla')
    reset_pwd.add_argument('username', help='Kullanıcı adı')
    reset_pwd.add_argument('--password', required=True, help='Yeni şifre')
    
    unlock = subparsers.add_parser('unlock-account', help='Hesap kilidini aç')
    unlock.add_argument('username', help='Kullanıcı adı')
    
    # ========================================
    # 2FA YÖNETİMİ
    # ========================================
    
    enable_2fa = subparsers.add_parser('enable-2fa', help='2FA etkinleştir')
    enable_2fa.add_argument('username', help='Kullanıcı adı')
    
    disable_2fa = subparsers.add_parser('disable-2fa', help='2FA devre dışı bırak')
    disable_2fa.add_argument('username', help='Kullanıcı adı')
    
    backup_codes = subparsers.add_parser('show-backup-codes', help='Yedek kodları göster')
    backup_codes.add_argument('username', help='Kullanıcı adı')
    
    regen_codes = subparsers.add_parser('regenerate-backup-codes', help='Yedek kodları yenile')
    regen_codes.add_argument('username', help='Kullanıcı adı')
    
    # ========================================
    # TOKEN YÖNETİMİ
    # ========================================
    
    create_token = subparsers.add_parser('create-token', help='Geçici token oluştur')
    create_token.add_argument('username', help='Kullanıcı adı')
    create_token.add_argument('--duration', type=int, default=30, help='Süre (dakika)')
    create_token.add_argument('--uses', type=int, default=1, help='Maksimum kullanım')
    create_token.add_argument('--purpose', default='Uzaktan destek', help='Amaç')
    
    list_tokens = subparsers.add_parser('list-tokens', help='Aktif tokenları listele')
    list_tokens.add_argument('--username', help='Kullanıcı adı (opsiyonel)')
    
    # ========================================
    # AUDIT LOG
    # ========================================
    
    show_logs = subparsers.add_parser('show-logs', help='Audit logları göster')
    show_logs.add_argument('--username', help='Kullanıcı adı filtresi')
    show_logs.add_argument('--action', help='Aksiyon filtresi')
    show_logs.add_argument('--limit', type=int, default=100, help='Maksimum kayıt')
    
    # ========================================
    # DOSYA GÜVENLİĞİ
    # ========================================
    
    subparsers.add_parser('secure-files', help='Kritik dosyaları güvenli hale getir')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Komutları çalıştır
    try:
        if args.command == 'reset-password':
            cmd_reset_password(args.db, args.username, args.password)
        
        elif args.command == 'unlock-account':
            cmd_unlock_account(args.db, args.username)
        
        elif args.command == 'enable-2fa':
            cmd_enable_2fa(args.db, args.username)
        
        elif args.command == 'disable-2fa':
            cmd_disable_2fa(args.db, args.username)
        
        elif args.command == 'show-backup-codes':
            cmd_show_backup_codes(args.db, args.username)
        
        elif args.command == 'regenerate-backup-codes':
            cmd_regenerate_backup_codes(args.db, args.username)
        
        elif args.command == 'create-token':
            cmd_create_token(args.db, args.username, args.duration, args.uses, args.purpose)
        
        elif args.command == 'list-tokens':
            cmd_list_tokens(args.db, args.username)
        
        elif args.command == 'show-logs':
            cmd_show_logs(args.db, args.username, args.action, args.limit)
        
        elif args.command == 'secure-files':
            cmd_secure_files()
        
    except Exception as e:
        logging.error(f"\n HATA: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# ============================================================================
# KOMUT FONKSİYONLARI
# ============================================================================

def cmd_reset_password(db_path, username, password):
    """Kullanıcı şifresini sıfırla"""
    logging.info(f"\n Şifre Sıfırlama: {username}")
    logging.info("=" * 60)
    
    # Şifre politikası kontrolü
    is_valid, error = PasswordPolicy.validate(password)
    if not is_valid:
        logging.error(f" Şifre politikaya uymuyor: {error}")
        return
    
    # Şifreyi hashle
    hashed = hash_password(password)
    
    # Veritabanına kaydet
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE users
        SET password_hash = ?,
            pw_hash_version = 'argon2',
            must_change_password = 0,
            failed_attempts = 0,
            locked_until = NULL
        WHERE username = ?
    """, (hashed, username))
    
    if cur.rowcount == 0:
        logging.info(f" Kullanıcı bulunamadı: {username}")
        conn.close()
        return
    
    conn.commit()
    conn.close()
    
    # Audit log
    audit_log(db_path, "PWD_RESET_BY_ADMIN", username=username, success=True)
    
    logging.info(" Şifre başarıyla sıfırlandı")


def cmd_unlock_account(db_path, username):
    """Hesap kilidini aç"""
    logging.info(f"\n Hesap Kilidi Açma: {username}")
    logging.info("=" * 60)
    
    reset_failed_attempts(db_path, username)
    
    logging.info(" Hesap kilidi açıldı")


def cmd_enable_2fa(db_path, username):
    """2FA etkinleştir"""
    logging.info(f"\n 2FA Etkinleştirme: {username}")
    logging.info("=" * 60)
    
    success, msg, secret, qr_bytes = enable_totp_for_user(db_path, username)
    
    if not success:
        logging.info(f" {msg}")
        return
    
    # QR kodu kaydet
    qr_file = f"2fa_qr_{username}.png"
    with open(qr_file, 'wb') as f:
        f.write(qr_bytes)
    
    logging.info(f" {msg}")
    logging.info(f"\nSecret Key: {secret}")
    logging.info(f"QR Kod: {qr_file}")
    logging.info("\nKullanıcıya QR kodu gönderin veya secret key'i paylaşın")


def cmd_disable_2fa(db_path, username):
    """2FA devre dışı bırak"""
    logging.info(f"\n 2FA Devre Dışı Bırakma: {username}")
    logging.info("=" * 60)
    
    success, msg = disable_2fa(db_path, username)
    
    if success:
        logging.info(f" {msg}")
    else:
        logging.info(f" {msg}")


def cmd_show_backup_codes(db_path, username):
    """Yedek kodları göster"""
    logging.info(f"\n Yedek Kodlar: {username}")
    logging.info("=" * 60)
    
    success, msg, codes = get_backup_codes(db_path, username)
    
    if not success:
        logging.info(f" {msg}")
        return
    
    logging.info(f"\nToplam: {len(codes)} kod\n")
    for i, code in enumerate(codes, 1):
        logging.info(f"  {i:2}. {code}")


def cmd_regenerate_backup_codes(db_path, username):
    """Yedek kodları yenile"""
    logging.info(f"\n Yedek Kod Yenileme: {username}")
    logging.info("=" * 60)
    
    success, msg, codes = regenerate_backup_codes(db_path, username)
    
    if not success:
        logging.info(f" {msg}")
        return
    
    logging.info(f" {msg}\n")
    logging.info("Yeni yedek kodlar:\n")
    for i, code in enumerate(codes, 1):
        logging.info(f"  {i:2}. {code}")


def cmd_create_token(db_path, username, duration, uses, purpose):
    """Geçici token oluştur"""
    logging.info(f"\nIcons.TIME Geçici Token Oluşturma: {username}")
    logging.info("=" * 60)
    
    success, msg, token = generate_temp_token(
        db_path,
        username,
        duration_minutes=duration,
        max_uses=uses,
        purpose=purpose
    )
    
    if not success:
        logging.info(f" {msg}")
        return
    
    logging.info(f" {msg}\n")
    logging.info(f"Token: {token}\n")
    logging.info(f"Süre: {duration} dakika")
    logging.info(f"Maksimum kullanım: {uses}")
    logging.info(f"Amaç: {purpose}")


def cmd_list_tokens(db_path, username=None):
    """Aktif tokenları listele"""
    logging.info("\n Aktif Tokenlar")
    logging.info("=" * 60)
    
    tokens = list_active_tokens(db_path, username)
    
    if not tokens:
        logging.info("Aktif token bulunamadı")
        return
    
    logging.info(f"\nToplam: {len(tokens)} token\n")
    for i, t in enumerate(tokens, 1):
        logging.info(f"{i}. {t['username']} - {t['purpose']}")
        logging.info(f"   Oluşturulma: {t['created_at']}")
        logging.info(f"   Son kullanım: {t['last_used_at'] or 'Henüz kullanılmadı'}")
        logging.info(f"   Kullanım: {t['use_count']}/{t['max_uses']}")
        logging.info()


def cmd_show_logs(db_path, username=None, action=None, limit=100):
    """Audit logları göster"""
    logging.info("\n Audit Logları")
    logging.info("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    query = "SELECT * FROM security_logs WHERE 1=1"
    params = []
    
    if username:
        query += " AND username = ?"
        params.append(username)
    
    if action:
        query += " AND action = ?"
        params.append(action)
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    cur.execute(query, params)
    logs = cur.fetchall()
    conn.close()
    
    if not logs:
        logging.info("Log bulunamadı")
        return
    
    logging.info(f"\nToplam: {len(logs)} kayıt\n")
    for log in logs:
        log_id, user_id, username, action, ip, user_agent, success, details, created_at = log
        status = "" if success else ""
        logging.info(f"{status} {created_at} | {username or 'N/A'} | {action}")
        if details:
            logging.info(f"   Detay: {details}")
        logging.info()


def cmd_secure_files():
    """Kritik dosyaları güvenli hale getir"""
    logging.info("\n Kritik Dosyaları Güvenli Hale Getirme")
    logging.info("=" * 60)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    secure_critical_files(base_dir)


if __name__ == "__main__":
    main()

