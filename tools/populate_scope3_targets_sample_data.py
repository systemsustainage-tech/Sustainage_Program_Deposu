#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scope 3 Hedef Örnek Veri Ekleme Scripti
"""

import logging
import os
import sqlite3
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Proje kök dizinini path'e ekle
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def populate_scope3_targets_sample_data() -> None:
    """Scope 3 hedef örnek verilerini ekle"""
    
    # Veritabanı yolu
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sdg_desktop.sqlite')
    
    if not os.path.exists(db_path):
        logging.info(f"Veritabani bulunamadi: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Örnek şirket ID'si (varsayılan: 1)
        company_id = 1
        
        logging.info("Scope 3 hedef ornek verileri ekleniyor...")
        
        # Kategori ID'lerini al
        cursor.execute("SELECT id, category_number FROM scope3_categories")
        category_mapping = {row[1]: row[0] for row in cursor.fetchall()}
        
        # 1. Scope 3 Hedef Verileri Ekle
        logging.info("Scope 3 hedef verileri ekleniyor...")
        
        targets_data = [
            {
                'category_id': category_mapping[1],
                'target_type': 'Mutlak Emisyon Azaltımı',
                'baseline_year': 2024,
                'target_year': 2030,
                'baseline_emissions': 750.0,
                'target_emissions': 450.0,
                'reduction_percentage': 40.0,
                'target_description': 'Satın alınan mal ve hizmetlerde %40 emisyon azaltımı hedefleniyor'
            },
            {
                'category_id': category_mapping[3],
                'target_type': 'Yenilenebilir Enerji Oranı',
                'baseline_year': 2024,
                'target_year': 2026,
                'baseline_emissions': 600.0,
                'target_emissions': 300.0,
                'reduction_percentage': 50.0,
                'target_description': 'Yakıt ve enerji faaliyetlerinde %50 yenilenebilir enerji kullanımı'
            },
            {
                'category_id': category_mapping[4],
                'target_type': 'Yoğunluk Azaltımı',
                'baseline_year': 2024,
                'target_year': 2028,
                'baseline_emissions': 500.0,
                'target_emissions': 350.0,
                'reduction_percentage': 30.0,
                'target_description': 'Nakliye ve dağıtımda km başına emisyon yoğunluğunu azaltma'
            },
            {
                'category_id': category_mapping[6],
                'target_type': 'Sürdürülebilir Satın Alma',
                'baseline_year': 2024,
                'target_year': 2025,
                'baseline_emissions': 600.0,
                'target_emissions': 480.0,
                'reduction_percentage': 20.0,
                'target_description': 'İş seyahatlerinde sürdürülebilir ulaşım seçenekleri'
            },
            {
                'category_id': category_mapping[7],
                'target_type': 'Karbon Nötr',
                'baseline_year': 2024,
                'target_year': 2035,
                'baseline_emissions': 12000.0,
                'target_emissions': 0.0,
                'reduction_percentage': 100.0,
                'target_description': 'Çalışanların işe gidiş-gelişlerinde karbon nötr hedefi'
            },
            {
                'category_id': category_mapping[5],
                'target_type': 'Döngüsel Ekonomi',
                'baseline_year': 2024,
                'target_year': 2030,
                'baseline_emissions': 1500.0,
                'target_emissions': 750.0,
                'reduction_percentage': 50.0,
                'target_description': 'Üretilen ürünlerin kullanımında döngüsel ekonomi prensipleri'
            },
            {
                'category_id': category_mapping[2],
                'target_type': 'Tedarikçi Uyumluluğu',
                'baseline_year': 2024,
                'target_year': 2027,
                'baseline_emissions': 600.0,
                'target_emissions': 360.0,
                'reduction_percentage': 40.0,
                'target_description': 'Sermaye mallarında sürdürülebilir tedarikçi seçimi'
            },
            {
                'category_id': category_mapping[8],
                'target_type': 'Net Sıfır',
                'baseline_year': 2024,
                'target_year': 2040,
                'baseline_emissions': 240.0,
                'target_emissions': 0.0,
                'reduction_percentage': 100.0,
                'target_description': 'Kiralanan varlıklarda net sıfır emisyon hedefi'
            }
        ]
        
        for target in targets_data:
            cursor.execute("""
                INSERT OR IGNORE INTO scope3_targets 
                (company_id, category_id, target_type, baseline_year, target_year,
                 baseline_emissions, target_emissions, reduction_percentage, 
                 target_description, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                target['category_id'],
                target['target_type'],
                target['baseline_year'],
                target['target_year'],
                target['baseline_emissions'],
                target['target_emissions'],
                target['reduction_percentage'],
                target['target_description'],
                'Active',
                datetime.now().isoformat()
            ))
        
        logging.info(f"OK {len(targets_data)} Scope 3 hedef verisi eklendi")
        
        # Degisiklikleri kaydet
        conn.commit()
        
        logging.info("\nScope 3 hedef ornek verileri basariyla eklendi!")
        logging.info("\nOzet:")
        logging.info(f"- Hedef Verileri: {len(targets_data)}")
        logging.info("- Hedef Yılları: 2025-2040")
        logging.info("- Azaltım Hedefleri: %20-100")
        
        return True
        
    except Exception as e:
        logging.error(f"Scope 3 hedef ornek veri ekleme hatasi: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = populate_scope3_targets_sample_data()
    if success:
        logging.info("\nScope 3 hedef ornek verileri basariyla eklendi!")
    else:
        logging.error("\nScope 3 hedef ornek verileri eklenirken hata olustu!")
        sys.exit(1)
