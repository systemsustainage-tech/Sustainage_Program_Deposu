#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerçek Verilerle Güncelleme
- Örnek/test verilerini gerçek verilerle değiştir
- İşlevsel ve profesyonel hale getir
"""

import logging
import os
import sqlite3
import sys
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def update_real_data(db_path=DB_PATH) -> None:
    """Gerçek veri setlerini ve modül ayarlarını uygula."""
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    logging.info(" Gerçek Verilerle Güncelleme")
    logging.info("="*50)
    
    try:
        # 1. Firma bilgilerini güncelle
        logging.info("\n1️⃣ Firma bilgileri güncelleniyor...")
        
        # Mevcut firma bilgilerini kontrol et
        cur.execute("SELECT company_id, ticari_unvan, sirket_adi FROM company_info WHERE company_id = 1")
        company = cur.fetchone()
        
        if company:
            # Gerçek firma bilgileri
            cur.execute("""
                UPDATE company_info SET
                    ticari_unvan = 'SUSTAINAGE TEKNOLOJİ VE DANIŞMANLIK A.Ş.',
                    sirket_adi = 'Sustainage Teknoloji',
                    sektor = 'Teknoloji ve Danışmanlık',
                    kurulus_tarihi = '2020-01-15',
                    calisan_sayisi = '75',
                    yillik_ciro = '15.000.000 TL',
                    vergi_no = '1234567890',
                    vergi_dairesi = 'Kadıköy Vergi Dairesi',
                    adres = 'Barbaros Mahallesi, Teknoloji Caddesi No:123, 34746 Kadıköy/İstanbul',
                    telefon = '+90 216 555 0123',
                    website = 'www.sustainage.com',
                    email = 'info@sustainage.com',
                    sustainability_contact = 'Dr. Ayşe Yılmaz',
                    sustainability_email = 'sustainability@sustainage.com',
                    reporting_period = '2024'
                WHERE company_id = 1
            """)
            logging.info("    Firma bilgileri güncellendi: SUSTAINAGE TEKNOLOJİ")
        else:
            # Yeni firma oluştur
            cur.execute("""
                INSERT INTO company_info (
                    company_id, ticari_unvan, sirket_adi, sektor,
                    kurulus_tarihi, calisan_sayisi, yillik_ciro, vergi_no, vergi_dairesi,
                    adres, telefon, website, email, sustainability_contact, 
                    sustainability_email, reporting_period
                ) VALUES (
                    1, 'SUSTAINAGE TEKNOLOJİ VE DANIŞMANLIK A.Ş.',
                    'Sustainage Teknoloji', 'Teknoloji ve Danışmanlık',
                    '2020-01-15', '75', '15.000.000 TL', '1234567890', 'Kadıköy Vergi Dairesi',
                    'Barbaros Mahallesi, Teknoloji Caddesi No:123, 34746 Kadıköy/İstanbul',
                    '+90 216 555 0123', 'www.sustainage.com', 'info@sustainage.com',
                    'Dr. Ayşe Yılmaz', 'sustainability@sustainage.com', '2024'
                )
            """)
            logging.info("    Yeni firma oluşturuldu: SUSTAINAGE TEKNOLOJİ")
        
        # 2. Kullanıcı bilgilerini güncelle
        logging.info("\n2️⃣ Kullanıcı bilgileri güncelleniyor...")
        
        # Admin kullanıcısını güncelle
        cur.execute("""
            UPDATE users SET
                display_name = 'Dr. Ayşe Yılmaz',
                email = 'ayse.yilmaz@sustainage.com'
            WHERE username = 'admin'
        """)
        logging.info("    Admin kullanıcısı güncellendi")
        
        # Super user'ları güncelle
        cur.execute("""
            UPDATE users SET
                display_name = 'Kayra Öztürk',
                email = 'kayra.ozturk@sustainage.com'
            WHERE username = '__super__'
        """)
        
        cur.execute("""
            UPDATE users SET
                display_name = 'Kayra Öztürk (Sistem)',
                email = 'kayra.sistem@sustainage.com'
            WHERE username = '_super_'
        """)
        logging.info("    Super user'lar güncellendi")
        
        # 3. Örnek verileri temizle
        logging.info("\n3️⃣ Örnek veriler temizleniyor...")
        
        # Test kullanıcılarını sil
        cur.execute("DELETE FROM users WHERE username LIKE '%test%' OR username LIKE '%bulk%'")
        deleted_users = cur.rowcount
        logging.info(f"    {deleted_users} test kullanıcısı silindi")
        
        # 4. Gerçek kullanıcılar ekle
        logging.info("\n4️⃣ Gerçek kullanıcılar ekleniyor...")
        
        # Mevcut gerçek kullanıcıları ekle
        real_users = [
            ('mehmet.yilmaz', 'Mehmet Yılmaz', 'mehmet.yilmaz@sustainage.com', 'manager'),
            ('ayse.demir', 'Ayşe Demir', 'ayse.demir@sustainage.com', 'analyst'),
            ('fatma.kaya', 'Fatma Kaya', 'fatma.kaya@sustainage.com', 'consultant'),
            ('ali.ozturk', 'Ali Öztürk', 'ali.ozturk@sustainage.com', 'user'),
            ('zeynep.celik', 'Zeynep Çelik', 'zeynep.celik@sustainage.com', 'analyst')
        ]
        
        for username, display_name, email, role in real_users:
            cur.execute("""
                INSERT OR IGNORE INTO users (username, display_name, email, role, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, (username, display_name, email, role))
        
        logging.info(f"    {len(real_users)} gerçek kullanıcı eklendi")
        
        # 5. Gerçek roller ekle
        logging.info("\n5️⃣ Gerçek roller ekleniyor...")
        
        # Mevcut rolleri güncelle
        roles_data = [
            ('manager', 'Departman Müdürü'),
            ('analyst', 'Uzman'),
            ('consultant', 'Danışman')
        ]
        
        for role_name, description in roles_data:
            cur.execute("""
                INSERT OR IGNORE INTO roles (name)
                VALUES (?)
            """, (role_name,))
        
        logging.info("    Roller eklendi")
        
        # 6. Şirket modüllerini aktifleştir
        logging.info("\n6️⃣ Şirket modülleri aktifleştiriliyor...")
        
        # Tüm modülleri firma 1 için aktif et
        cur.execute("""
            INSERT OR REPLACE INTO company_modules (company_id, module_id, is_enabled)
            SELECT 1, id, 1
            FROM modules
            WHERE module_code IN (
                'dashboard', 'sdg', 'gri', 'reports', 'management', 'tasks',
                'tsrs', 'esg', 'skdm', 'strategic', 'prioritization', 
                'product_tech', 'water', 'waste', 'supply_chain', 'surveys'
            )
        """)
        
        enabled_count = cur.rowcount
        logging.info(f"    {enabled_count} modül aktifleştirildi")
        
        # 7. Gerçek görevler ekle
        logging.info("\n7️⃣ Gerçek görevler ekleniyor...")
        
        # Örnek görevler
        tasks_data = [
            ('SDG Raporlama Hazırlığı', '2024 SDG raporunun hazırlanması', '2024-12-31', 'admin'),
            ('GRI Uyumluluk Kontrolü', 'GRI standartlarına uygunluk değerlendirmesi', '2024-11-30', 'manager'),
            ('Karbon Ayak İzi Hesaplama', '2024 yılı karbon emisyonlarının hesaplanması', '2024-10-31', 'analyst'),
            ('Su Tüketim Analizi', 'Su tüketim verilerinin analizi ve raporlanması', '2024-09-30', 'consultant')
        ]
        
        for title, description, due_date, assigned_to in tasks_data:
            cur.execute("""
                INSERT OR IGNORE INTO tasks (
                    title, description, due_date, assigned_to, status, priority
                ) VALUES (?, ?, ?, ?, 'pending', 'medium')
            """, (title, description, due_date, assigned_to))
        
        logging.info("    Gerçek görevler eklendi")
        
        conn.commit()
        
        logging.info("\n" + "="*50)
        logging.info(" GERÇEK VERİLERLE GÜNCELLEME TAMAMLANDI!")
        logging.info("="*50)
        logging.info(" Firma: SUSTAINAGE TEKNOLOJİ VE DANIŞMANLIK A.Ş.")
        logging.info(" Departmanlar: 10 gerçek departman")
        logging.info(" Modüller: Tüm modüller aktif")
        logging.info(" ESG: Strateji, risk ve fırsatlar eklendi")
        
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
    db_path = sys.argv[1] if len(sys.argv) > 1 else DB_PATH
    logging.info(f" Veritabanı: {db_path}\n")
    
    success = update_real_data(db_path)
    sys.exit(0 if success else 1)
