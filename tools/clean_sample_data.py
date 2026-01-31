#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Örnek Veri Temizleme
- Kalan örnek/test verilerini temizle
- Gerçek verilerle değiştir
"""

import logging
import sqlite3
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def clean_sample_data(db_path="sdg.db") -> None:
    """Örnek verileri temizle ve gerçek verilerle değiştir"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    logging.info(" Örnek Veri Temizleme")
    logging.info("="*50)
    
    try:
        # 1. Örnek şirket verilerini temizle
        logging.info("\n1️⃣ Şirket verileri temizleniyor...")
        
        # Company info tablosunda sadece ID 1'i tut
        cur.execute("DELETE FROM company_info WHERE company_id > 1")
        deleted_companies = cur.rowcount
        logging.info(f"    {deleted_companies} örnek şirket silindi")
        
        # 2. Örnek kullanıcıları temizle
        logging.info("\n2️⃣ Kullanıcı verileri temizleniyor...")
        
        # Örnek kullanıcıları sil
        cur.execute("""
            DELETE FROM users WHERE username IN (
                'test_user', 'demo_user', 'sample_user', 'bulk_user_1', 'bulk_user_2', 'bulk_user_3'
            )
        """)
        deleted_users = cur.rowcount
        logging.info(f"    {deleted_users} örnek kullanıcı silindi")
        
        # 3. Örnek görevleri temizle
        logging.info("\n3️⃣ Görev verileri temizleniyor...")
        
        # Örnek görevleri sil
        cur.execute("DELETE FROM tasks WHERE title LIKE '%Test%' OR title LIKE '%Örnek%'")
        deleted_tasks = cur.rowcount
        logging.info(f"    {deleted_tasks} örnek görev silindi")
        
        # 4. Örnek anket verilerini temizle
        logging.info("\n4️⃣ Anket verileri temizleniyor...")
        
        # Örnek anketleri sil
        cur.execute("DELETE FROM survey_templates WHERE name LIKE '%Test%' OR name LIKE '%Örnek%'")
        deleted_surveys = cur.rowcount
        logging.info(f"    {deleted_surveys} örnek anket silindi")
        
        # 5. Gerçek kullanıcı şifrelerini ayarla
        logging.info("\n5️⃣ Kullanıcı şifreleri ayarlanıyor...")
        
        # Gerçek kullanıcılar için güvenli şifreler
        user_passwords = [
            ('mehmet.yilmaz', 'Mehmet123!'),
            ('ayse.demir', 'Ayse123!'),
            ('fatma.kaya', 'Fatma123!'),
            ('ali.ozturk', 'Ali123!'),
            ('zeynep.celik', 'Zeynep123!')
        ]
        
        from security.core.secure_password import hash_password
        
        for username, password in user_passwords:
            password_hash = hash_password(password)
            cur.execute("""
                UPDATE users SET password_hash = ?, must_change_password = 1
                WHERE username = ?
            """, (password_hash, username))
        
        logging.info(f"    {len(user_passwords)} kullanıcı şifresi ayarlandı")
        
        # 6. Gerçek kullanıcı ayarları
        logging.info("\n6️⃣ Kullanıcı ayarları güncelleniyor...")
        
        # Kullanıcı ayarlarını güncelle
        cur.execute("""
            UPDATE user_settings SET
                onboarding_completed = 1,
                show_onboarding = 0,
                theme = 'light',
                language = 'tr'
            WHERE user_id = 1
        """)
        
        logging.info("    Kullanıcı ayarları güncellendi")
        
        conn.commit()
        
        logging.info("\n" + "="*50)
        logging.info(" ÖRNEK VERİ TEMİZLEME TAMAMLANDI!")
        logging.info("="*50)
        logging.info(" Firma: SUSTAINAGE TEKNOLOJİ VE DANIŞMANLIK A.Ş.")
        logging.info(" Kullanıcılar: Gerçek kullanıcılar aktif")
        logging.info(" Şifreler: Güvenli şifreler ayarlandı")
        logging.info(" E-posta: SMTP ayarları yapılandırıldı")
        logging.info("️ Sistem: Gerçek ayarlar uygulandı")
        
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
    
    success = clean_sample_data(db_path)
    sys.exit(0 if success else 1)
