import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program içerisindeki gerçek şirket verilerini kontrol et
"""

import os
import re
import sqlite3
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def check_company_data() -> None:
    """Program içerisindeki gerçek şirket verilerini kontrol et"""
    
    db_path = DB_PATH
    if not os.path.exists(db_path):
        logging.info(f"Veritabani bulunamadi: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Company_id içeren tabloları bul
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = cursor.fetchall()
        
        company_tables = []
        for table in all_tables:
            table_name = table[0]
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name or ""):
                continue
            try:
                cursor.execute("PRAGMA table_info(" + table_name + ")")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                if 'company_id' in column_names:
                    company_tables.append(table_name)
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        
        logging.info("Company_id iceren tablolar:")
        for table in company_tables:
            logging.info(f"- {table}")
        
        logging.info("\n" + "="*50)
        
        # Her tabloda hangi company_id'lerin kullanıldığını kontrol et
        for table in company_tables:
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table or ""):
                logging.info(f"{table} tablosu kontrol edilemedi: geçersiz tablo adı")
                continue
            try:
                cursor.execute(
                    "SELECT DISTINCT company_id FROM " + table + " WHERE company_id IS NOT NULL ORDER BY company_id"
                )
                company_ids = cursor.fetchall()
                if company_ids:
                    logging.info(f"\n{table} tablosunda kullanılan company_id'ler:")
                    for cid in company_ids:
                        logging.info(f"  - {cid[0]}")
            except Exception as e:
                logging.info(f"{table} tablosu kontrol edilemedi: {e}")
        
        logging.info("\n" + "="*50)
        
        cursor.execute(
            "SELECT company_id, COALESCE(ticari_unvan, sirket_adi), sektor FROM company_info ORDER BY company_id"
        )
        companies = cursor.fetchall()
        logging.info(f"\nCompany_info tablosundaki mevcut veriler ({len(companies)} adet):")
        for company in companies:
            logging.info(f"ID: {company[0]}, Name: {repr(company[1])}, Sector: {repr(company[2])}")
        
        # Hangi company_id'lerin gerçekten kullanıldığını bul
        used_company_ids = set()
        for table in company_tables:
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table or ""):
                continue
            try:
                cursor.execute("SELECT DISTINCT company_id FROM " + table + " WHERE company_id IS NOT NULL")
                ids = cursor.fetchall()
                for cid in ids:
                    used_company_ids.add(cid[0])
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        
        logging.info(f"\nProgram icerisinde gercek kullanilan company_id'ler: {sorted(used_company_ids)}")
        
        # Eksik olan company_id'leri bul
        existing_ids = {company[0] for company in companies}
        missing_ids = used_company_ids - existing_ids
        if missing_ids:
            logging.info(f"\nEksik company_id'ler (company_info'ta yok): {sorted(missing_ids)}")
        else:
            logging.info("\nTum kullanilan company_id'ler company_info tablosunda mevcut.")
            
    except Exception as e:
        logging.error(f"Hata: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_company_data()
