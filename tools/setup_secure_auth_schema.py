#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GÜVENLİ KİMLİK DOĞRULAMA ŞEMASI KURULUMU
- must_change_password, failed_attempts, locked_until ekler
- audit_logs tablosu oluşturur
- sessions tablosu oluşturur
"""

import logging
import sqlite3
import sys
from datetime import datetime
from config.icons import Icons

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_secure_auth_schema(db_path: str = "sdg.db") -> None:
    """Güvenli kimlik doğrulama şemasını kur"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    logging.info(" Güvenli Kimlik Doğrulama Şeması Kurulumu Başladı...")
    
    try:
        # 1. users tablosuna yeni kolonlar ekle
        logging.info("\n1️⃣ users tablosunu güncelleniyor...")
        
        # Mevcut kolonları kontrol et
        cur.execute("PRAGMA table_info(users)")
        existing_cols = {row[1] for row in cur.fetchall()}
        
        # Gerekli kolonları ekle
        new_columns = {
            'must_change_password': ('INTEGER', 'DEFAULT 1'),  # BOOLEAN -> INTEGER (SQLite)
            'failed_attempts': ('INTEGER', 'DEFAULT 0'),
            'locked_until': ('TEXT', 'DEFAULT NULL'),  # DATETIME -> TEXT (ISO format)
            'created_at': ('TEXT', f"DEFAULT '{datetime.now().isoformat()}'"),
            'last_login_at': ('TEXT', 'DEFAULT NULL'),
            'pw_hash_version': ('TEXT', "DEFAULT 'legacy'"),  # 'argon2', 'pbkdf2', 'legacy'
        }
        
        added_count = 0
        for col_name, (col_type, col_default) in new_columns.items():
            if col_name not in existing_cols:
                try:
                    cur.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type} {col_default}")
                    logging.info(f"    {col_name} kolonu eklendi")
                    added_count += 1
                except Exception as e:
                    logging.info(f"   ️ {col_name} eklenemedi: {e}")
        
        if added_count == 0:
            logging.info("   Icons.INFO Tüm kolonlar zaten mevcut")
        
        # 2. audit_logs tablosu oluştur
        logging.info("\n2️⃣ audit_logs tablosu oluşturuluyor...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                action TEXT NOT NULL,
                metadata TEXT,
                ip_address TEXT,
                user_agent TEXT,
                success INTEGER DEFAULT 1,
                ts TEXT DEFAULT (datetime('now')),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        logging.info("    audit_logs tablosu oluşturuldu")
        
        # Index ekle
        cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_logs(ts)")
        logging.info("    audit_logs indeksleri eklendi")
        
        # 3. sessions tablosu oluştur
        logging.info("\n3️⃣ sessions tablosu oluşturuluyor...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                expires_at TEXT NOT NULL,
                device_info TEXT,
                ip_address TEXT,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        logging.info("    sessions tablosu oluşturuldu")
        
        # Index ekle
        cur.execute("CREATE INDEX IF NOT EXISTS idx_session_token ON sessions(token)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_session_user ON sessions(user_id)")
        logging.info("    sessions indeksleri eklendi")
        
        # 4. user_password_history tablosu oluştur (opsiyonel - son 3 şifre)
        logging.info("\n4️⃣ user_password_history tablosu oluşturuluyor...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_password_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                pw_hash TEXT NOT NULL,
                changed_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        logging.info("    user_password_history tablosu oluşturuldu")
        
        # Index ekle
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pwd_history_user ON user_password_history(user_id)")
        logging.info("    user_password_history indeksleri eklendi")
        
        # 5. Mevcut kullanıcıları güncelle (legacy için)
        logging.info("\n5️⃣ Mevcut kullanıcılar güncelleniyor...")
        cur.execute("""
            UPDATE users 
            SET created_at = datetime('now'),
                pw_hash_version = 'legacy'
            WHERE created_at IS NULL
        """)
        updated = cur.rowcount
        logging.info(f"    {updated} kullanıcı güncellendi")
        
        conn.commit()
        
        # Özet
        logging.info("\n" + "="*60)
        logging.info(" GÜVENLİ KİMLİK DOĞRULAMA ŞEMASI BAŞARIYLA KURULDU!")
        logging.info("="*60)
        
        # Tablo sayıları
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM audit_logs")
        audit_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM sessions")
        session_count = cur.fetchone()[0]
        
        logging.info("\n Özet:")
        logging.info(f"    Kullanıcılar: {user_count}")
        logging.info(f"    Audit Log: {audit_count}")
        logging.info(f"    Aktif Oturumlar: {session_count}")
        
        return True
        
    except Exception as e:
        logging.error(f"\n HATA: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "sdg.db"
    logging.info(f" Veritabanı: {db_path}\n")
    
    success = setup_secure_auth_schema(db_path)
    sys.exit(0 if success else 1)

