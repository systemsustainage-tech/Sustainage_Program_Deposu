#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modül Erişim Kontrolü Test
"""

import logging
import sqlite3
import sys

sys.path.insert(0, '.')

from core.module_access import (get_enabled_modules_for_company,
                                is_module_enabled_for_company)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


from config.database import DB_PATH

def test_module_access() -> None:
    """Modül erişim kontrolünü test et"""
    db_path = DB_PATH
    
    logging.info(" Modül Erişim Kontrolü Test")
    logging.info("="*50)
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # 1. Modülleri listele
        cur.execute("SELECT module_code, module_name, is_core, default_enabled FROM modules ORDER BY display_order")
        modules = cur.fetchall()
        
        logging.info(f"\n Toplam {len(modules)} modül:")
        for module_code, module_name, is_core, default_enabled in modules:
            logging.info(f"   {module_code}: {module_name} (Core: {is_core}, Default: {default_enabled})")
        
        # 2. Firma modüllerini kontrol et
        cur.execute("SELECT DISTINCT company_id FROM company_info WHERE company_id IS NOT NULL")
        companies = cur.fetchall()
        
        if not companies:
            companies = [(1,)]  # Varsayılan firma
        
        logging.info(f"\n {len(companies)} firma bulundu")
        
        for company_id, in companies:
            logging.info(f"\n Firma {company_id} modül durumu:")
            
            # Normal kullanıcı için
            logging.info("    Normal Kullanıcı:")
            for module_code, module_name, is_core, default_enabled in modules:
                enabled = is_module_enabled_for_company(db_path, company_id, module_code, False)
                status = "" if enabled else ""
                logging.info(f"      {status} {module_code}: {module_name}")
            
            # Super admin için
            logging.info("    Super Admin:")
            for module_code, module_name, is_core, default_enabled in modules:
                enabled = is_module_enabled_for_company(db_path, company_id, module_code, True)
                status = "" if enabled else ""
                logging.info(f"      {status} {module_code}: {module_name}")
            
            # Etkin modülleri getir
            enabled_modules = get_enabled_modules_for_company(db_path, company_id, False)
            logging.info(f"    Etkin modül sayısı: {len(enabled_modules)}")
        
        # 3. Company_modules tablosunu kontrol et
        logging.info("\n Company_modules atamaları:")
        cur.execute("""
            SELECT cm.company_id, m.module_code, cm.is_enabled
            FROM company_modules cm
            JOIN modules m ON cm.module_id = m.id
            ORDER BY cm.company_id, m.display_order
        """)
        
        assignments = cur.fetchall()
        for company_id, module_code, is_enabled in assignments:
            status = "" if is_enabled else ""
            logging.info(f"   Firma {company_id}: {status} {module_code}")
        
        return True
        
    except Exception as e:
        logging.error(f" Hata: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    success = test_module_access()
    logging.info(f"\n{' Test başarılı!' if success else ' Test başarısız!'}")
    sys.exit(0 if success else 1)
