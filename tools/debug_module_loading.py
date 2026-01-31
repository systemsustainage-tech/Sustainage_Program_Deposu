#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modül Yükleme Debug
"""

import logging
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def debug_module_loading() -> None:
    """Modül yükleme sorununu debug et"""
    db_path = "sdg.db"
    
    logging.debug(" Modül Yükleme Debug")
    logging.info("="*50)
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # 1. Modules tablosunu kontrol et
        logging.info("\n1️⃣ Modules tablosu:")
        cur.execute("SELECT COUNT(*) FROM modules")
        module_count = cur.fetchone()[0]
        logging.info(f"   Toplam modül: {module_count}")
        
        if module_count > 0:
            cur.execute("SELECT module_code, module_name, is_core, default_enabled FROM modules ORDER BY display_order")
            modules = cur.fetchall()
            logging.info("   Modüller:")
            for code, name, is_core, default_enabled in modules:
                logging.info(f"      {code}: {name} (Core: {is_core}, Default: {default_enabled})")
        
        # 2. Company_modules tablosunu kontrol et
        logging.info("\n2️⃣ Company_modules tablosu:")
        cur.execute("SELECT COUNT(*) FROM company_modules")
        assignment_count = cur.fetchone()[0]
        logging.info(f"   Toplam atama: {assignment_count}")
        
        if assignment_count > 0:
            cur.execute("""
                SELECT cm.company_id, m.module_code, cm.is_enabled
                FROM company_modules cm
                JOIN modules m ON cm.module_id = m.id
                ORDER BY cm.company_id, m.display_order
            """)
            assignments = cur.fetchall()
            logging.info("   Atamalar:")
            for company_id, module_code, is_enabled in assignments:
                status = "" if is_enabled else ""
                logging.info(f"      Firma {company_id}: {status} {module_code}")
        
        # 3. Company_info tablosunu kontrol et
        logging.info("\n3️⃣ Company_info tablosu:")
        cur.execute("SELECT COUNT(*) FROM company_info")
        company_count = cur.fetchone()[0]
        logging.info(f"   Toplam firma: {company_count}")
        
        if company_count > 0:
            cur.execute("SELECT company_id, ticari_unvan, sirket_adi FROM company_info WHERE company_id IS NOT NULL")
            companies = cur.fetchall()
            logging.info("   Firmalar:")
            for company_id, ticari_unvan, sirket_adi in companies:
                name = ticari_unvan or sirket_adi or f"Firma {company_id}"
                logging.info(f"      {company_id}: {name}")
        
        # 4. Super admin paneli sorgusunu test et
        logging.info("\n4️⃣ Super Admin Panel Sorgusu Test:")
        company_id = 1  # Test için
        
        cur.execute("""
            SELECT 
                m.id,
                m.module_code,
                m.module_name,
                m.module_description,
                m.category,
                m.icon,
                m.is_core,
                COALESCE(cm.is_enabled, m.default_enabled) as is_enabled
            FROM modules m
            LEFT JOIN company_modules cm 
                ON m.id = cm.module_id AND cm.company_id = ?
            ORDER BY m.display_order, m.module_name
        """, (company_id,))
        
        results = cur.fetchall()
        logging.info(f"   Firma {company_id} için {len(results)} modül bulundu:")
        
        for module in results:
            module_id, code, name, desc, category, icon, is_core, is_enabled = module
            status = " CORE" if is_core else (" AÇIK" if is_enabled else " KAPALI")
            logging.info(f"      {icon} {name} ({code}) - {status}")
        
        # 5. Sorun tespiti
        logging.info("\n5️⃣ Sorun Tespiti:")
        
        if module_count == 0:
            logging.error("    HATA: Hiç modül yok!")
        elif assignment_count == 0:
            logging.error("    HATA: Hiç firma-modül ataması yok!")
        elif len(results) == 0:
            logging.error("    HATA: Sorgu sonucu boş!")
        else:
            logging.info("    Modül sistemi çalışıyor görünüyor")
        
    except Exception as e:
        logging.error(f" Hata: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    debug_module_loading()
