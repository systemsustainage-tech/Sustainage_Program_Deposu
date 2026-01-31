#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TSRS Modülü Kurulum Scripti
TSRS tablolarını oluşturur ve varsayılan verileri yükler
"""

import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Proje kök dizinini Python path'e ekle
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def setup_tsrs_tables() -> None:
    """TSRS tablolarını oluştur"""
    logging.info("TSRS tablolari olusturuluyor...")
    try:
        from tsrs.tsrs_manager import TSRSManager
        manager = TSRSManager()
        success = manager.create_tables()
        if success:
            logging.info("TSRS tablolari basariyla olusturuldu")
            return True
        else:
            logging.info("TSRS tablolari olusturulamadi")
            return False
    except Exception as e:
        logging.error(f"TSRS tablolari olusturulurken hata: {e}")
        return False

def setup_tsrs_default_data() -> None:
    """Varsayılan TSRS verilerini oluştur"""
    logging.info("Varsayilan TSRS verileri olusturuluyor...")
    try:
        from tsrs.tsrs_manager import TSRSManager
        manager = TSRSManager()
        success = manager.create_default_tsrs_data()
        if success:
            logging.info("Varsayilan TSRS verileri basariyla olusturuldu")
            return True
        else:
            logging.info("Varsayilan TSRS verileri olusturulamadi")
            return False
    except Exception as e:
        logging.error(f"Varsayilan TSRS verileri olusturulurken hata: {e}")
        return False

def test_tsrs_functionality() -> None:
    """TSRS fonksiyonalitesini test et"""
    logging.info("TSRS fonksiyonalitesi test ediliyor...")
    try:
        from tsrs.tsrs_manager import TSRSManager
        manager = TSRSManager()
        
        # Kategorileri test et
        categories = manager.get_tsrs_categories()
        logging.info(f"TSRS kategorileri: {len(categories)} adet")
        
        # Standartları test et
        standards = manager.get_tsrs_standards()
        logging.info(f"TSRS standartlari: {len(standards)} adet")
        
        # İstatistikleri test et
        stats = manager.get_tsrs_statistics(1)
        logging.info(f"TSRS istatistikleri: {stats}")
        
        logging.info("TSRS fonksiyonalitesi test edildi")
        return True
        
    except Exception as e:
        logging.error(f"TSRS fonksiyonalitesi test edilirken hata: {e}")
        return False

def main() -> None:
    """Ana kurulum fonksiyonu"""
    logging.info("TSRS Modulu Kurulum Baslatiliyor...")
    logging.info("=" * 50)
    
    success_count = 0
    total_tasks = 3
    
    # 1. TSRS tablolarını oluştur
    if setup_tsrs_tables():
        success_count += 1
    
    # 2. Varsayılan verileri oluştur
    if setup_tsrs_default_data():
        success_count += 1
    
    # 3. Fonksiyonaliteyi test et
    if test_tsrs_functionality():
        success_count += 1
    
    logging.info("=" * 50)
    logging.info(f"TSRS Modulu Kurulum Tamamlandi: {success_count}/{total_tasks} basarili")
    
    if success_count == total_tasks:
        logging.info("Tum TSRS ozellikleri basariyla kuruldu!")
        logging.info("\nTSRS Ozellikleri:")
        logging.info("  - TSRS Standartlari ve Kategorileri")
        logging.info("  - TSRS GOSTergeleri ve Metrikleri")
        logging.info("  - TSRS Yanitlari ve Raporlama")
        logging.info("  - TSRS-GRI-SDG Eslestirmeleri")
        logging.info("\nTSRS Modulu kullanima hazir!")
        return True
    else:
        logging.error("Bazi ozellikler kurulamadi. Lutfen hatalari kontrol edin.")
        return False

if __name__ == "__main__":
    main()
