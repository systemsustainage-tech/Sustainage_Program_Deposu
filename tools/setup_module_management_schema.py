#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODÜL YÖNETİM ŞEMASI KURULUMU
- Modül tanımları tablosu
- Firma-modül ilişki tablosu
- Varsayılan modül verisi
"""

import logging
import sqlite3
import sys
from datetime import datetime
from config.icons import Icons

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_module_management_schema(db_path: str = "sdg.db") -> None:
    """Modül yönetim şemasını kur"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    logging.info(" Modül Yönetim Şeması Kurulumu Başladı...")
    
    try:
        # 1. Modül tanımları tablosu
        logging.info("\n1️⃣ modules tablosu oluşturuluyor...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_code TEXT UNIQUE NOT NULL,
                module_name TEXT NOT NULL,
                module_description TEXT,
                icon TEXT,
                category TEXT,
                is_core INTEGER DEFAULT 0,
                default_enabled INTEGER DEFAULT 1,
                display_order INTEGER DEFAULT 100,
                min_license_level TEXT DEFAULT 'basic',
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)
        logging.info("    modules tablosu oluşturuldu")
        
        # 2. Firma-modül ilişki tablosu
        logging.info("\n2️⃣ company_modules tablosu oluşturuluyor...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS company_modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                module_id INTEGER NOT NULL,
                is_enabled INTEGER DEFAULT 1,
                enabled_at TEXT,
                disabled_at TEXT,
                enabled_by_user_id INTEGER,
                license_expires_at TEXT,
                notes TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY(module_id) REFERENCES modules(id) ON DELETE CASCADE,
                FOREIGN KEY(enabled_by_user_id) REFERENCES users(id) ON DELETE SET NULL,
                UNIQUE(company_id, module_id)
            )
        """)
        logging.info("    company_modules tablosu oluşturuldu")
        
        # İndeksler ekle
        cur.execute("CREATE INDEX IF NOT EXISTS idx_company_modules_company ON company_modules(company_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_company_modules_module ON company_modules(module_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_company_modules_enabled ON company_modules(is_enabled)")
        logging.info("    İndeksler eklendi")
        
        # 3. Varsayılan modülleri ekle
        logging.info("\n3️⃣ Varsayılan modüller ekleniyor...")
        
        # Varsayılan modüller (kod, ad, açıklama, ikon, kategori, zorunlu_mu, aktif_mi, sıra)
        default_modules = [
            ('dashboard', 'Kontrol Paneli', 'Genel durum ve özet bilgiler', Icons.DASHBOARD, 'General', 1, 1, 10),
            ('esrs', 'ESRS Raporlama', 'Çevresel, Sosyal ve Yönetişim raporlaması', Icons.REPORT, 'Reporting', 0, 1, 20),
            ('sasb', 'SASB Standartları', 'Sektörel sürdürülebilirlik standartları', Icons.ANALYTICS, 'Reporting', 0, 1, 30),
            ('gri', 'GRI Standartları', 'Küresel Raporlama Girişimi standartları', Icons.DOCUMENTS, 'Reporting', 0, 1, 40),
            ('carbon', 'Karbon Ayak İzi', 'Karbon emisyon hesaplama ve takibi', Icons.CO2, 'Environment', 0, 1, 50),
            ('water', 'Su Ayak İzi', 'Su tüketimi ve yönetimi', Icons.WATER, 'Environment', 0, 1, 60),
            ('supply_chain', 'Tedarik Zinciri', 'Tedarikçi değerlendirme ve yönetimi', Icons.TRUCK, 'Social', 0, 1, 70),
            ('product_tech', 'Ürün & Teknoloji', 'İnovasyon, Kalite, Dijital Güvenlik, Acil Durum', Icons.STAR, 'Technology', 0, 1, 80),
            ('settings', 'Ayarlar', 'Sistem ve kullanıcı ayarları', Icons.SETTINGS, 'System', 1, 1, 999),
        ]
        
        inserted = 0
        for module_data in default_modules:
            try:
                cur.execute("""
                    INSERT OR IGNORE INTO modules 
                    (module_code, module_name, module_description, icon, category, 
                     is_core, default_enabled, display_order)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, module_data)
                if cur.rowcount > 0:
                    inserted += 1
            except Exception as e:
                logging.info(f"   ️ {module_data[0]} eklenemedi: {e}")
        
        logging.info(f"    {inserted} yeni modül eklendi")
        
        # 4. Mevcut firmalar için varsayılan modülleri aktifleştir
        logging.info("\n4️⃣ Mevcut firmalara modüller atanıyor...")
        
        # Tüm firmaları al (company_info veya companies tablosundan)
        try:
            cur.execute("SELECT DISTINCT company_id FROM company_info WHERE company_id IS NOT NULL")
            companies = cur.fetchall()
        except Exception:
            try:
                cur.execute("SELECT id FROM companies")
                companies = cur.fetchall()
            except Exception:
                companies = [(1,)]  # Varsayılan firma
                logging.info("   Icons.INFO Firma tablosu bulunamadı, varsayılan firma (ID=1) kullanılıyor")
        
        # Tüm modülleri al
        cur.execute("SELECT id, module_code, default_enabled FROM modules")
        all_modules = cur.fetchall()
        
        assigned = 0
        for company in companies:
            company_id = company[0]
            for module_id, module_code, default_enabled in all_modules:
                # Zaten kayıt var mı kontrol et
                cur.execute("""
                    SELECT id FROM company_modules 
                    WHERE company_id = ? AND module_id = ?
                """, (company_id, module_id))
                
                if not cur.fetchone():
                    # Yoksa ekle
                    cur.execute("""
                        INSERT INTO company_modules 
                        (company_id, module_id, is_enabled, enabled_at)
                        VALUES (?, ?, ?, ?)
                    """, (company_id, module_id, default_enabled, datetime.now().isoformat()))
                    assigned += 1
        
        logging.info(f"    {assigned} modül-firma ilişkisi oluşturuldu")
        
        conn.commit()
        
        # Özet
        logging.info("\n" + "="*60)
        logging.info(" MODÜL YÖNETİM ŞEMASI BAŞARIYLA KURULDU!")
        logging.info("="*60)
        
        # İstatistikler
        cur.execute("SELECT COUNT(*) FROM modules")
        module_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM company_modules")
        relation_count = cur.fetchone()[0]
        
        # Firma sayısını al
        try:
            cur.execute("SELECT COUNT(DISTINCT company_id) FROM company_info")
            company_count = cur.fetchone()[0]
        except Exception:
            try:
                cur.execute("SELECT COUNT(*) FROM companies")
                company_count = cur.fetchone()[0]
            except Exception:
                company_count = 1
        
        logging.info("\n Özet:")
        logging.info(f"    Tanımlı Modüller: {module_count}")
        logging.info(f"    Firmalar: {company_count}")
        logging.info(f"    Modül İlişkileri: {relation_count}")
        
        # Modül listesi
        logging.info("\n Tanımlı Modüller:")
        cur.execute("""
            SELECT module_code, module_name, category, is_core 
            FROM modules 
            ORDER BY display_order
        """)
        for row in cur.fetchall():
            core_badge = " [CORE]" if row[3] else ""
            logging.info(f"   • {row[0]}: {row[1]} ({row[2]}){core_badge}")
        
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
    
    success = setup_module_management_schema(db_path)
    sys.exit(0 if success else 1)

