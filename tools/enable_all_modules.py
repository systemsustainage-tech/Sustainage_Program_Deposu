#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tüm Modülleri Aktifleştir
- Firma 1 için tüm modülleri aktif hale getir
"""

import logging
import sqlite3
import sys
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def enable_all_modules(db_path=DB_PATH, company_id=1) -> None:
    """Tüm modülleri belirtilen firma için aktifleştir"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    logging.info(" Tüm Modülleri Aktifleştirme")
    logging.info("="*50)
    
    try:
        # Şema tespiti
        cur.execute("PRAGMA table_info(modules)")
        mod_cols = {c[1] for c in cur.fetchall()}
        code_col = 'module_code' if 'module_code' in mod_cols else ('code' if 'code' in mod_cols else None)
        if not code_col:
            raise Exception("modules tablosunda module_code/code kolonu bulunamadı")
        
        # Tüm modülleri getir
        cur.execute(f"SELECT {code_col} FROM modules WHERE {code_col} IS NOT NULL")
        modules = cur.fetchall()
        
        logging.info(f" Toplam {len(modules)} modül bulundu")
        
        # company_modules şema tespiti
        cur.execute("PRAGMA table_info(company_modules)")
        cm_cols = {c[1] for c in cur.fetchall()}
        use_code = 'module_code' in cm_cols
        
        # Her modülü firma için aktifleştir
        for (module_code,) in modules:
            if use_code:
                cur.execute("""
                    INSERT OR REPLACE INTO company_modules (company_id, module_code, is_enabled)
                    VALUES (?, ?, 1)
                """, (company_id, module_code))
            else:
                # Eski şema: module_id
                cur.execute("SELECT id FROM modules WHERE {0} = ?".format(code_col), (module_code,))
                row = cur.fetchone()
                if row:
                    cur.execute("""
                        INSERT OR REPLACE INTO company_modules (company_id, module_id, is_enabled)
                        VALUES (?, ?, 1)
                    """, (company_id, row[0]))
        
        conn.commit()
        
        logging.info(f" {len(modules)} modül firma {company_id} için aktifleştirildi")
        
        # Sonuçları göster
        logging.info("\n Aktif Modüller:")
        if use_code:
            cur.execute("""
                SELECT m.module_name, m.module_code, m.category, m.is_core
                FROM modules m
                JOIN company_modules cm ON m.module_code = cm.module_code
                WHERE cm.company_id = ? AND cm.is_enabled = 1
                ORDER BY m.display_order
            """, (company_id,))
        else:
            cur.execute("""
                SELECT m.module_name, m.module_code, m.category, m.is_core
                FROM modules m
                JOIN company_modules cm ON m.id = cm.module_id
                WHERE cm.company_id = ? AND cm.is_enabled = 1
                ORDER BY m.display_order
            """, (company_id,))
        
        active_modules = cur.fetchall()
        for name, code, category, is_core in active_modules:
            core_text = " (CORE)" if is_core else ""
            logging.info(f"    {name} ({code}) - {category}{core_text}")
        
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
    company_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    logging.info(f" Veritabanı: {db_path}")
    logging.info(f" Firma ID: {company_id}\n")
    
    success = enable_all_modules(db_path, company_id)
    sys.exit(0 if success else 1)
