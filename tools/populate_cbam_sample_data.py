#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CBAM Örnek Veri Ekleme Scripti
"""

import logging
import os
import sqlite3
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Proje kök dizinini path'e ekle
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def populate_cbam_sample_data() -> None:
    """CBAM örnek verilerini ekle"""
    
    # Veritabanı yolu
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sdg_desktop.sqlite')
    
    if not os.path.exists(db_path):
        logging.info(f" Veritabanı bulunamadı: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Örnek şirket ID'si (varsayılan: 1)
        company_id = 1
        
        logging.info("CBAM ornek verileri ekleniyor...")
        
        # 1. CBAM Urunleri Ekle
        logging.info("CBAM urunleri ekleniyor...")
        
        cbam_products = [
            {
                'product_code': 'CEM001',
                'product_name': 'Portland Çimentosu',
                'hs_code': '2523.29.00',
                'cn_code': '2523 29 00',
                'sector': 'cement',
                'production_route': 'Dry Process'
            },
            {
                'product_code': 'STE001',
                'product_name': 'Sıcak Hadde Çelik',
                'hs_code': '7208.10.00',
                'cn_code': '7208 10 00',
                'sector': 'iron_steel',
                'production_route': 'Basic Oxygen Furnace'
            },
            {
                'product_code': 'ALU001',
                'product_name': 'Alüminyum İngot',
                'hs_code': '7601.20.00',
                'cn_code': '7601 20 00',
                'sector': 'aluminium',
                'production_route': 'Hall-Heroult Process'
            },
            {
                'product_code': 'FERT001',
                'product_name': 'Amonyum Nitrat',
                'hs_code': '3102.30.00',
                'cn_code': '3102 30 00',
                'sector': 'fertilizers',
                'production_route': 'Haber-Bosch Process'
            },
            {
                'product_code': 'ELEC001',
                'product_name': 'Elektrik',
                'hs_code': '2716.00.00',
                'cn_code': '2716 00 00',
                'sector': 'electricity',
                'production_route': 'Coal-Fired'
            }
        ]
        
        for product in cbam_products:
            cursor.execute("""
                INSERT OR REPLACE INTO cbam_products 
                (company_id, product_code, product_name, hs_code, cn_code, sector, production_route, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                product['product_code'],
                product['product_name'],
                product['hs_code'],
                product['cn_code'],
                product['sector'],
                product['production_route'],
                datetime.now().isoformat()
            ))
        
        logging.info(f"OK {len(cbam_products)} CBAM urunu eklendi")
        
        # 2. Emisyon Verileri Ekle
        logging.info("Emisyon verileri ekleniyor...")
        
        emission_data = [
            {
                'product_code': 'CEM001',
                'co2_emissions': 850.5,
                'n2o_emissions': 2.1,
                'pfc_emissions': 0.0,
                'calculation_method': 'Ölçüm',
                'period': '2024 Q4'
            },
            {
                'product_code': 'STE001',
                'co2_emissions': 1850.2,
                'n2o_emissions': 5.8,
                'pfc_emissions': 0.0,
                'calculation_method': 'Hesaplama',
                'period': '2024 Q4'
            },
            {
                'product_code': 'ALU001',
                'co2_emissions': 1250.8,
                'n2o_emissions': 1.2,
                'pfc_emissions': 45.6,
                'calculation_method': 'Ölçüm',
                'period': '2024 Q4'
            },
            {
                'product_code': 'FERT001',
                'co2_emissions': 2100.3,
                'n2o_emissions': 8.9,
                'pfc_emissions': 0.0,
                'calculation_method': 'Hesaplama',
                'period': '2024 Q4'
            },
            {
                'product_code': 'ELEC001',
                'co2_emissions': 950.7,
                'n2o_emissions': 0.8,
                'pfc_emissions': 0.0,
                'calculation_method': 'Varsayılan Değer',
                'period': '2024 Q4'
            }
        ]
        
        for emission in emission_data:
            # Önce product_id'yi bul
            cursor.execute("SELECT id FROM cbam_products WHERE product_code = ? AND company_id = ?", 
                         (emission['product_code'], company_id))
            product_row = cursor.fetchone()
            if not product_row:
                continue
            
            product_id = product_row[0]
            
            cursor.execute("""
                INSERT OR REPLACE INTO cbam_emissions 
                (product_id, reporting_period, emission_type, direct_emissions, indirect_emissions, 
                 embedded_emissions, total_emissions, calculation_method, data_quality, verification_status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                emission['period'],
                'Direct',
                emission['co2_emissions'],
                emission['n2o_emissions'],
                emission['pfc_emissions'],
                emission['co2_emissions'] + emission['n2o_emissions'] + emission['pfc_emissions'],
                emission['calculation_method'],
                'High',
                'Verified',
                datetime.now().isoformat()
            ))
        
        logging.info(f"OK {len(emission_data)} emisyon verisi eklendi")
        
        # 3. Ithalat Verileri Ekle
        logging.info("Ithalat verileri ekleniyor...")
        
        import_data = [
            {
                'product_code': 'CEM001',
                'period': '2024 Q4',
                'quantity': 1500.0,
                'country': 'Türkiye',
                'emissions': 1275.75,
                'cbam_cost': 6388.75
            },
            {
                'product_code': 'STE001',
                'period': '2024 Q4',
                'quantity': 2500.0,
                'country': 'Türkiye',
                'emissions': 4625.50,
                'cbam_cost': 23127.50
            },
            {
                'product_code': 'ALU001',
                'period': '2024 Q4',
                'quantity': 800.0,
                'country': 'Türkiye',
                'emissions': 1000.64,
                'cbam_cost': 5003.20
            },
            {
                'product_code': 'FERT001',
                'period': '2024 Q4',
                'quantity': 1200.0,
                'country': 'Türkiye',
                'emissions': 2520.36,
                'cbam_cost': 12601.80
            },
            {
                'product_code': 'ELEC001',
                'period': '2024 Q4',
                'quantity': 50000.0,
                'country': 'Türkiye',
                'emissions': 47535.0,
                'cbam_cost': 237675.0
            }
        ]
        
        for import_record in import_data:
            # Önce product_id'yi bul
            cursor.execute("SELECT id FROM cbam_products WHERE product_code = ? AND company_id = ?", 
                         (import_record['product_code'], company_id))
            product_row = cursor.fetchone()
            if not product_row:
                continue
            
            product_id = product_row[0]
            
            cursor.execute("""
                INSERT OR REPLACE INTO cbam_imports 
                (company_id, product_id, import_period, origin_country, quantity, quantity_unit, 
                 customs_value, currency, embedded_emissions, carbon_price_paid, cbam_certificate_required, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                product_id,
                import_record['period'],
                import_record['country'],
                import_record['quantity'],
                'ton',
                100000.0,  # Varsayılan gümrük değeri
                'EUR',
                import_record['emissions'],
                import_record['cbam_cost'],
                1,
                datetime.now().isoformat()
            ))
        
        logging.info(f"OK {len(import_data)} ithalat verisi eklendi")
        
        # 4. CBAM Kayit Durumu Ekle
        logging.info("CBAM kayit durumu ekleniyor...")
        
        # CBAM registration tablosu yoksa oluştur
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cbam_registration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                registration_number VARCHAR(50),
                status VARCHAR(50),
                registration_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        cursor.execute("""
            INSERT OR REPLACE INTO cbam_registration 
            (company_id, registration_number, status, registration_date, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            company_id,
            'TR-CBAM-2024-001',
            'Aktif',
            '2024-01-15',
            datetime.now().isoformat()
        ))
        
        logging.info("OK CBAM kayit durumu eklendi")
        
        # Degisiklikleri kaydet
        conn.commit()
        
        logging.info("\nCBAM ornek verileri basariyla eklendi!")
        logging.info("\nOzet:")
        logging.info(f"- Urun Sayisi: {len(cbam_products)}")
        logging.info(f"- Emisyon Kayitlari: {len(emission_data)}")
        logging.info(f"- Ithalat Kayitlari: {len(import_data)}")
        logging.info(f"- Toplam CBAM Yukumlulugu: {sum(i['cbam_cost'] for i in import_data):,.2f} EUR")
        
        return True
        
    except Exception as e:
        logging.error(f"CBAM ornek veri ekleme hatasi: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = populate_cbam_sample_data()
    if success:
        logging.info("\nCBAM ornek verileri basariyla eklendi!")
    else:
        logging.error("\nCBAM ornek verileri eklenirken hata olustu!")
        sys.exit(1)
