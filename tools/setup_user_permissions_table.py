#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kullanıcı İzinleri Tablosu Oluşturma
"""

import logging
import os
import sqlite3
import sys
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ana dizini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_user_permissions_table() -> None:
    """Kullanıcı izinleri tablosunu oluştur"""
    
    logging.info("=" * 60)
    logging.info("KULLANICI IZINLERI TABLOSU OLUSTURMA")
    logging.info("=" * 60)
    
    # Veritabanı yolu
    db_path = DB_PATH
    
    if not os.path.exists(db_path):
        logging.error(f"HATA: Veritabanı bulunamadı: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Kullanıcı izinleri tablosu (zaten var, sadece kontrol et)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_permissions'")
        if not cursor.fetchone():
            logging.error("[HATA] user_permissions tablosu bulunamadı!")
            return False
        else:
            logging.info("[BILGI] user_permissions tablosu zaten mevcut")
        
        # İndeks oluştur
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_permissions_user_id 
            ON user_permissions(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_permissions_name 
            ON user_permissions(permission_name)
        """)
        
        conn.commit()
        
        logging.info("[BASARILI] Kullanıcı izinleri tablosu oluşturuldu!")
        
        # Mevcut admin kullanıcısına tüm izinleri ver
        cursor.execute("SELECT id FROM users WHERE username = '_super_' OR username = 'admin' LIMIT 1")
        admin_user = cursor.fetchone()
        
        if admin_user:
            admin_id = admin_user[0]
            
            # Tüm izinleri admin kullanıcısına ver
            all_permissions = [
                'General.Dışa Aktarma', 'General.İçe Aktarma', 'General.Admin',
                'Dijital Güvenlik.Görüntüleme', 'Dijital Güvenlik.Düzenleme', 'Dijital Güvenlik.Silme',
                'Dijital Güvenlik.Dışa Aktarma', 'Dijital Güvenlik.İçe Aktarma', 'Dijital Güvenlik.Admin',
                'GRI.Görüntüleme', 'GRI.Düzenleme', 'GRI.Silme', 'GRI.Dışa Aktarma',
                'TSRS.Görüntüleme', 'TSRS.Düzenleme', 'TSRS.Silme', 'TSRS.Dışa Aktarma', 'TSRS.İçe Aktarma',
                'SDG.Görüntüleme', 'SDG.Düzenleme', 'SDG.Silme', 'SDG.Dışa Aktarma', 'SDG.İçe Aktarma',
                'ESG.Görüntüleme', 'ESG.Düzenleme', 'ESG.Silme', 'ESG.Dışa Aktarma', 'ESG.İçe Aktarma',
                'SKDM.Görüntüleme', 'SKDM.Düzenleme', 'SKDM.Silme', 'SKDM.Dışa Aktarma',
                'Raporlama.Görüntüleme', 'Raporlama.Düzenleme', 'Raporlama.Silme', 'Raporlama.Dışa Aktarma', 'Raporlama.İçe Aktarma',
                'Yönetim.Görüntüleme', 'Yönetim.Düzenleme', 'Yönetim.Silme', 'Yönetim.Admin',
                'Eşleştirme.Görüntüleme', 'Eşleştirme.Düzenleme', 'Eşleştirme.Silme', 'Eşleştirme.Dışa Aktarma',
                'Önceliklendirme.Görüntüleme', 'Önceliklendirme.Düzenleme', 'Önceliklendirme.Silme', 'Önceliklendirme.Dışa Aktarma',
                'Su Yönetimi.Görüntüleme', 'Su Yönetimi.Düzenleme', 'Su Yönetimi.Silme', 'Su Yönetimi.Dışa Aktarma', 'Su Yönetimi.İçe Aktarma',
                'Atık Yönetimi.Görüntüleme', 'Atık Yönetimi.Düzenleme', 'Atık Yönetimi.Silme', 'Atık Yönetimi.Dışa Aktarma', 'Atık Yönetimi.İçe Aktarma',
                'Tedarik Zinciri.Görüntüleme', 'Tedarik Zinciri.Düzenleme', 'Tedarik Zinciri.Silme', 'Tedarik Zinciri.Dışa Aktarma'
            ]
            
            for permission in all_permissions:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO user_permissions 
                        (user_id, permission_name, granted_by)
                        VALUES (?, ?, ?)
                    """, (admin_id, permission, 'system'))
                except Exception as e:
                    logging.error(f"  [UYARI] {permission} izni eklenirken hata: {e}")
            
            conn.commit()
            logging.info(f"[BASARILI] Admin kullanıcısına ({admin_id}) tüm izinler verildi!")
        
        return True
        
    except Exception as e:
        logging.error(f"[HATA]: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = setup_user_permissions_table()
    if success:
        logging.info("\n[BASARILI] Islem tamamlandi!")
    else:
        logging.info("\n[BASARISIZ] Islem basarisiz!")
    
    input("\nDevam etmek icin Enter'a basin...")
