#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program içerisinde kullanılan eksik company_id'leri companies tablosuna ekle
"""

import logging
import os
import sqlite3
from datetime import datetime
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def add_missing_companies() -> None:
    """Program içerisinde kullanılan eksik company_id'leri companies tablosuna ekle"""
    
    db_path = DB_PATH
    if not os.path.exists(db_path):
        logging.info(f"Veritabani bulunamadi: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Mevcut company_id'leri kontrol et
        cursor.execute("SELECT id FROM companies")
        existing_ids = {row[0] for row in cursor.fetchall()}
        
        # Program içerisinde kullanılan company_id'ler
        used_ids = {1, 2, 3, 5, 6}
        missing_ids = used_ids - existing_ids
        
        logging.info(f"Mevcut company_id'ler: {sorted(existing_ids)}")
        logging.info(f"Kullanilan company_id'ler: {sorted(used_ids)}")
        logging.info(f"Eksik company_id'ler: {sorted(missing_ids)}")
        
        if not missing_ids:
            logging.info("Eksik company_id yok!")
            return True
        
        # Eksik company_id'leri ekle
        companies_to_add = []
        for cid in missing_ids:
            if cid == 2:
                companies_to_add.append((cid, 'Şirket 2', 'Teknoloji', 'Türkiye'))
            elif cid == 3:
                companies_to_add.append((cid, 'Şirket 3', 'Sanayi', 'Türkiye'))
            elif cid == 5:
                companies_to_add.append((cid, 'Şirket 5', 'Hizmet', 'Türkiye'))
            elif cid == 6:
                companies_to_add.append((cid, 'Şirket 6', 'Ticaret', 'Türkiye'))
            else:
                companies_to_add.append((cid, f'Şirket {cid}', 'Genel', 'Türkiye'))
        
        for company in companies_to_add:
            cursor.execute("""
                INSERT INTO companies (id, name, sector, country, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (*company, datetime.now().isoformat()))
        
        conn.commit()
        
        # Sonucu kontrol et
        cursor.execute("SELECT id, name, sector, country FROM companies ORDER BY id")
        companies = cursor.fetchall()
        
        logging.info(f"\nGuncellenmis companies tablosu ({len(companies)} adet):")
        for company in companies:
            try:
                logging.info(f"ID: {company[0]}, Name: {company[1]}, Sector: {company[2]}, Country: {company[3]}")
            except UnicodeEncodeError:
                logging.info(f"ID: {company[0]}, Name: {repr(company[1])}, Sector: {repr(company[2])}, Country: {repr(company[3])}")
        
        return True
        
    except Exception as e:
        logging.error(f"Hata: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = add_missing_companies()
    if success:
        logging.info("\nEksik company_id'ler basariyla eklendi!")
    else:
        logging.error("\nEksik company_id'ler eklenirken hata olustu!")
