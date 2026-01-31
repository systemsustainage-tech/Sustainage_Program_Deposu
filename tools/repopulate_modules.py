#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modül Verilerini Yeniden Doldur
"""

import logging
import sqlite3
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def repopulate_modules(db_path="sdg.db") -> None:
    """Modül verilerini yeniden doldur"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    logging.info(" Modül Verilerini Yeniden Doldurma")
    logging.info("="*50)
    
    try:
        # Mevcut modülleri temizle
        cur.execute("DELETE FROM modules")
        cur.execute("DELETE FROM company_modules")
        logging.info(" Eski modül verileri temizlendi")
        
        # Modül verilerini ekle
        modules = [
            # CORE MODULES (is_core = 1)
            ('dashboard', 'Dashboard', 'Ana kontrol paneli', '', 'core', 1, 1, 1, 'basic'),
            ('sdg', 'SDG Hedefleri', 'Sürdürülebilir Kalkınma Hedefleri', '', 'core', 1, 1, 2, 'basic'),
            ('gri', 'GRI Standartları', 'Global Reporting Initiative', '', 'core', 1, 1, 3, 'basic'),
            ('reports', 'Raporlama', 'Entegre raporlama sistemi', '', 'core', 1, 1, 4, 'basic'),
            ('management', 'Yönetim', 'Kullanıcı ve sistem yönetimi', '️', 'core', 1, 1, 5, 'basic'),
            ('tasks', 'Görev Yönetimi', 'Proje ve görev takibi', '', 'core', 1, 1, 6, 'basic'),
            
            # OPTIONAL MODULES (is_core = 0)
            ('tsrs', 'TSRS', 'Türkiye Sürdürülebilirlik Raporlama Standartları', '🇹🇷', 'reporting', 0, 1, 7, 'standard'),
            ('esg', 'ESG Yönetimi', 'Environmental, Social, Governance', '', 'management', 0, 1, 8, 'standard'),
            ('skdm', 'SKDM', 'Sürdürülebilir Karbon Değişim Yönetimi', '', 'environment', 0, 1, 9, 'premium'),
            ('strategic', 'Stratejik Planlama', 'Kurumsal strateji ve planlama', '', 'strategy', 0, 1, 10, 'premium'),
            ('prioritization', 'Önceliklendirme', 'Materyalite ve öncelik analizi', '', 'analysis', 0, 1, 11, 'standard'),
            ('product_tech', 'Ürün/Teknoloji', 'Ürün ve teknoloji yönetimi', '', 'innovation', 0, 1, 12, 'premium'),
            ('water', 'Su Yönetimi', 'Su kaynakları ve su ayak izi', '', 'environment', 0, 1, 13, 'standard'),
            ('waste', 'Atık Yönetimi', 'Atık azaltma ve döngüsel ekonomi', '️', 'environment', 0, 1, 14, 'standard'),
            ('supply_chain', 'Tedarik Zinciri', 'Sürdürülebilir tedarik zinciri', '', 'management', 0, 1, 15, 'premium'),
            ('surveys', 'Anket Yönetimi', 'Stakeholder anketleri', '', 'engagement', 0, 1, 16, 'basic'),
        ]
        
        for module in modules:
            cur.execute("""
                INSERT INTO modules (
                    module_code, module_name, module_description, icon, category,
                    is_core, default_enabled, display_order, min_license_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, module)
        
        logging.info(f" {len(modules)} modül eklendi")
        
        # Tüm firmalara CORE modülleri ata
        cur.execute("SELECT DISTINCT company_id FROM company_info WHERE company_id IS NOT NULL")
        companies = cur.fetchall()
        
        if not companies:
            # Varsayılan firma ekle
            cur.execute("INSERT OR IGNORE INTO company_info (company_id, company_name) VALUES (1, 'Varsayılan Firma')")
            companies = [(1,)]
        
        core_modules = [m[0] for m in modules if m[5] == 1]  # is_core = 1 olanlar
        
        for company_id, in companies:
            for module_code in core_modules:
                # Module ID'sini bul
                cur.execute("SELECT id FROM modules WHERE module_code = ?", (module_code,))
                module_row = cur.fetchone()
                if module_row:
                    module_id = module_row[0]
                    cur.execute("""
                        INSERT OR IGNORE INTO company_modules (company_id, module_id, is_enabled)
                        VALUES (?, ?, 1)
                    """, (company_id, module_id))
        
        logging.info(f" {len(companies)} firmaya CORE modülleri atandı")
        
        conn.commit()
        
        # Özet
        cur.execute("SELECT COUNT(*) FROM modules")
        module_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM company_modules")
        assignment_count = cur.fetchone()[0]
        
        logging.info("\n" + "="*50)
        logging.info(" MODÜL VERİLERİ YENİDEN DOLDURULDU!")
        logging.info("="*50)
        logging.info(f" Toplam Modül: {module_count}")
        logging.info(f" Toplam Atama: {assignment_count}")
        logging.info(f" Etkilenen Firma: {len(companies)}")
        
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
    
    success = repopulate_modules(db_path)
    sys.exit(0 if success else 1)
