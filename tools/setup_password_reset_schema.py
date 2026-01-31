#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ŞİFRE SIFIRLAMA ŞEMASI KURULUMU
- reset_tokens tablosu
- OTP bazlı güvenli şifre sıfırlama
"""

import logging
import sqlite3
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_password_reset_schema(db_path: str = "sdg.db") -> None:
    """Şifre sıfırlama şemasını kur"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    logging.info(" Şifre Sıfırlama Şeması Kurulumu Başladı...")
    
    try:
        # reset_tokens tablosu
        logging.info("\n1️⃣ reset_tokens tablosu oluşturuluyor...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                code_hash TEXT NOT NULL,
                requested_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                attempts_left INTEGER NOT NULL DEFAULT 5,
                used_at TEXT,
                request_ip TEXT,
                sent_via TEXT DEFAULT 'email',
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id)
            )
        """)
        logging.info("    reset_tokens tablosu oluşturuldu")
        
        # İndeksler
        cur.execute("CREATE INDEX IF NOT EXISTS idx_reset_user ON reset_tokens(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_reset_expires ON reset_tokens(expires_at)")
        logging.info("    İndeksler eklendi")
        
        # Eski/süresi dolmuş tokenları temizle
        logging.info("\n2️⃣ Eski tokenlar temizleniyor...")
        cur.execute("""
            DELETE FROM reset_tokens 
            WHERE expires_at < datetime('now')
        """)
        deleted = cur.rowcount
        logging.info(f"    {deleted} eski token silindi")
        
        conn.commit()
        
        # Özet
        logging.info("\n" + "="*60)
        logging.info(" ŞİFRE SIFIRLAMA ŞEMASI BAŞARIYLA KURULDU!")
        logging.info("="*60)
        
        cur.execute("SELECT COUNT(*) FROM reset_tokens")
        token_count = cur.fetchone()[0]
        
        logging.info("\n Özet:")
        logging.info(f"    Aktif Reset Token: {token_count}")
        
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
    
    success = setup_password_reset_schema(db_path)
    sys.exit(0 if success else 1)

