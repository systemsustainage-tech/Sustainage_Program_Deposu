#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TSRS-GRI-SDG Entegrasyon Test Scripti
Entegrasyon özelliklerini test eder
"""

import logging
import os
import sys
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Proje kök dizinini Python path'e ekle
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def test_tsrs_integration() -> None:
    """TSRS-GRI-SDG entegrasyonunu test et"""
    logging.info("TSRS-GRI-SDG Entegrasyon Test Baslatiliyor...")
    logging.info("=" * 60)
    
    try:
        import sqlite3

        # Veritabanı bağlantısı
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        logging.info("1. TSRS-GRI Eslestirmeleri test ediliyor...")
        cursor.execute("SELECT COUNT(*) FROM map_tsrs_gri")
        tsrs_gri_count = cursor.fetchone()[0]
        logging.info(f"   Toplam TSRS-GRI eslestirmesi: {tsrs_gri_count}")
        
        if tsrs_gri_count > 0:
            cursor.execute("SELECT * FROM map_tsrs_gri LIMIT 3")
            rows = cursor.fetchall()
            logging.info("   Örnek eslestirmeler:")
            for row in rows:
                logging.info(f"     {row}")
        
        logging.info("\n2. TSRS-SDG Eslestirmeleri test ediliyor...")
        cursor.execute("SELECT COUNT(*) FROM map_tsrs_sdg")
        tsrs_sdg_count = cursor.fetchone()[0]
        logging.info(f"   Toplam TSRS-SDG eslestirmesi: {tsrs_sdg_count}")
        
        if tsrs_sdg_count > 0:
            cursor.execute("SELECT * FROM map_tsrs_sdg LIMIT 3")
            rows = cursor.fetchall()
            logging.info("   Örnek eslestirmeler:")
            for row in rows:
                logging.info(f"     {row}")
        
        logging.info("\n3. TSRS Standartlari test ediliyor...")
        cursor.execute("SELECT COUNT(*) FROM tsrs_standards")
        tsrs_standards_count = cursor.fetchone()[0]
        logging.info(f"   Toplam TSRS standart: {tsrs_standards_count}")
        
        logging.info("\n4. TSRS GOSTergeleri test ediliyor...")
        cursor.execute("SELECT COUNT(*) FROM tsrs_indicators")
        tsrs_indicators_count = cursor.fetchone()[0]
        logging.info(f"   Toplam TSRS gostergesi: {tsrs_indicators_count}")
        
        if tsrs_indicators_count > 0:
            cursor.execute("SELECT code, title, data_type FROM tsrs_indicators LIMIT 5")
            rows = cursor.fetchall()
            logging.info("   Örnek gostergeler:")
            for row in rows:
                logging.info(f"     {row[0]}: {row[1]} ({row[2]})")
        
        logging.info("\n5. Entegrasyon istatistikleri...")
        cursor.execute("""
            SELECT s.code, s.title, s.category,
                   COUNT(DISTINCT tg.gri_standard) as gri_count,
                   COUNT(DISTINCT tsd.sdg_goal_id) as sdg_count
            FROM tsrs_standards s
            LEFT JOIN map_tsrs_gri tg ON s.code = tg.tsrs_standard_code
            LEFT JOIN map_tsrs_sdg tsd ON s.code = tsd.tsrs_standard_code
            GROUP BY s.id, s.code, s.title, s.category
            ORDER BY s.code
        """)
        
        integration_stats = cursor.fetchall()
        logging.info("   TSRS Standart Entegrasyon Istatistikleri:")
        for stat in integration_stats:
            logging.info(f"     {stat[0]}: {stat[1]} - GRI: {stat[3]}, SDG: {stat[4]}")
        
        conn.close()
        
        logging.info("\n" + "=" * 60)
        logging.info("TSRS-GRI-SDG Entegrasyon Test Tamamlandi!")
        
        # Test sonuçları
        success_indicators = [
            tsrs_gri_count > 0,
            tsrs_sdg_count > 0,
            tsrs_standards_count > 0,
            tsrs_indicators_count > 0,
            len(integration_stats) > 0
        ]
        
        success_count = sum(success_indicators)
        total_tests = len(success_indicators)
        
        logging.info(f"Basarili Testler: {success_count}/{total_tests}")
        
        if success_count == total_tests:
            logging.info("Tum entegrasyon ozellikleri basariyla test edildi!")
            return True
        else:
            logging.info("Bazi entegrasyon ozellikleri test edilemedi.")
            return False
            
    except Exception as e:
        logging.error(f"TSRS-GRI-SDG entegrasyon test edilirken hata: {e}")
        return False

def test_tsrs_integration_gui() -> None:
    """TSRS entegrasyon GUI'sini test et"""
    logging.info("\nTSRS Entegrasyon GUI Test Baslatiliyor...")
    logging.info("=" * 60)
    
    try:
        import tkinter as tk

        from modules.tsrs.tsrs_integration_gui import TSRSIntegrationGUI

        # Test penceresi oluştur
        root = tk.Tk()
        root.withdraw()  # Pencereyi gizle
        
        # TSRS Entegrasyon GUI oluştur
        TSRSIntegrationGUI(root, 1)
        
        logging.info("TSRS Entegrasyon GUI basariyla olusturuldu")
        
        # Pencereyi kapat
        root.destroy()
        
        return True
        
    except Exception as e:
        logging.error(f"TSRS Entegrasyon GUI test edilirken hata: {e}")
        return False

def main() -> None:
    """Ana test fonksiyonu"""
    logging.info("TSRS-GRI-SDG Entegrasyon Test Baslatiliyor...")
    logging.info("=" * 60)
    
    success_count = 0
    total_tests = 2
    
    # 1. TSRS-GRI-SDG entegrasyon testi
    if test_tsrs_integration():
        success_count += 1
    
    # 2. TSRS entegrasyon GUI testi
    if test_tsrs_integration_gui():
        success_count += 1
    
    logging.info("\n" + "=" * 60)
    logging.info(f"TSRS-GRI-SDG Entegrasyon Test Tamamlandi: {success_count}/{total_tests} basarili")
    
    if success_count == total_tests:
        logging.info("Tum TSRS-GRI-SDG entegrasyon ozellikleri basariyla test edildi!")
        logging.info("\nEntegrasyon Ozellikleri:")
        logging.info("  - TSRS-GRI Eslestirmeleri")
        logging.info("  - TSRS-SDG Eslestirmeleri")
        logging.info("  - TSRS GOSTergeleri")
        logging.info("  - Entegrasyon GUI")
        logging.info("  - Entegrasyon Istatistikleri")
        logging.info("\nTSRS-GRI-SDG entegrasyonu kullanima hazir!")
        return True
    else:
        logging.info("Bazi ozellikler test edilemedi.")
        return False

if __name__ == "__main__":
    main()
