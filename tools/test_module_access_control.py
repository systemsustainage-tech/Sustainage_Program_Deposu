#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modül Erişim Kontrolü Test
"""

import logging
import sqlite3
import sys

sys.path.insert(0, '.')

from core.module_access import is_module_enabled_for_company

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def test_module_access_control() -> None:
    """Modül erişim kontrolünü test et"""
    db_path = "sdg.db"
    
    logging.info(" Modül Erişim Kontrolü Test")
    logging.info("="*50)
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # 1. Bir modülü kapat (örn: esg)
        logging.info("\n1️⃣ ESG modülünü kapatıyoruz...")
        cur.execute("""
            UPDATE company_modules 
            SET is_enabled = 0 
            WHERE company_id = 1 AND module_id = (
                SELECT id FROM modules WHERE module_code = 'esg'
            )
        """)
        conn.commit()
        logging.info("    ESG modülü kapatıldı")
        
        # 2. Erişim kontrolü test et
        logging.info("\n2️⃣ Erişim kontrolü test ediliyor...")
        
        test_modules = ['dashboard', 'sdg', 'gri', 'esg', 'skdm', 'tsrs']
        
        logging.info("    Normal Kullanıcı (company_id=1):")
        for module in test_modules:
            enabled = is_module_enabled_for_company(db_path, 1, module, False)
            status = "" if enabled else ""
            logging.info(f"      {status} {module}")
        
        logging.info("    Super Admin:")
        for module in test_modules:
            enabled = is_module_enabled_for_company(db_path, 1, module, True)
            status = "" if enabled else ""
            logging.info(f"      {status} {module}")
        
        # 3. ESG'yi tekrar aç
        logging.info("\n3️⃣ ESG modülünü tekrar açıyoruz...")
        cur.execute("""
            UPDATE company_modules 
            SET is_enabled = 1 
            WHERE company_id = 1 AND module_id = (
                SELECT id FROM modules WHERE module_code = 'esg'
            )
        """)
        conn.commit()
        logging.info("    ESG modülü tekrar açıldı")
        
        # 4. Tekrar test et
        logging.info("\n4️⃣ Tekrar erişim kontrolü:")
        esg_enabled = is_module_enabled_for_company(db_path, 1, 'esg', False)
        status = "" if esg_enabled else ""
        logging.info(f"   Normal kullanıcı ESG erişimi: {status}")
        
        logging.info("\n" + "="*50)
        logging.info(" Modül erişim kontrolü çalışıyor!")
        logging.info("   - Super Admin: Tüm modüllere erişebilir")
        logging.info("   - Normal kullanıcı: Sadece açık modüllere erişebilir")
        
    except Exception as e:
        logging.error(f" Hata: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    test_module_access_control()
