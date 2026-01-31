#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EU Taxonomy Faaliyetlerini İçe Aktarma Aracı
"""

import logging
import io
import json
import os
import sys

# Windows terminal için UTF-8 desteği
if os.name == 'nt' and not os.getenv('PYTEST_CURRENT_TEST'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Proje kök dizinini path'e ekle
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules.eu_taxonomy.taxonomy_manager import EUTaxonomyManager
from config.icons import Icons

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def import_activities(db_path: str, activities_file: str) -> None:
    """Faaliyetleri içe aktar"""
    logging.info(f"{Icons.EU_FLAG} EU Taxonomy Faaliyetleri İçe Aktarılıyor...")
    logging.info("=" * 60)
    
    # Manager oluştur
    manager = EUTaxonomyManager(db_path)
    
    # JSON dosyasını oku
    try:
        with open(activities_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logging.info(f" JSON dosyası okunamadı: {e}")
        return False
    
    # Faaliyetleri ekle
    activities = data.get('activities', [])
    success_count = 0
    error_count = 0
    
    for activity in activities:
        try:
            result = manager.add_taxonomy_activity(activity)
            if result:
                logging.info(f" {activity['activity_code']}: {activity['activity_name_tr']}")
                success_count += 1
            else:
                logging.error(f"️  {activity['activity_code']}: Zaten mevcut veya hata")
                error_count += 1
        except Exception as e:
            logging.error(f" {activity['activity_code']}: Hata - {e}")
            error_count += 1
    
    logging.info("\n" + "=" * 60)
    logging.info(" Özet:")
    logging.info(f"   Başarılı: {success_count}")
    logging.error(f"   Hatalı: {error_count}")
    logging.info(f"   Toplam: {len(activities)}")
    
    # Framework eşleştirmelerini ekle
    mappings = data.get('framework_mappings', [])
    if mappings:
        logging.info("\n Framework Eşleştirmeleri Ekleniyor...")
        mapping_success = 0
        
        for mapping in mappings:
            try:
                activity_code = mapping['activity_code']
                objective_code = mapping['objective_code']
                
                # SDG eşleştirmeleri
                for sdg_target in mapping.get('sdg_targets', []):
                    manager.map_to_frameworks(
                        activity_code=activity_code,
                        objective_code=objective_code,
                        sdg_target=sdg_target,
                        rationale=f"SDG Target {sdg_target} alignment"
                    )
                
                # GRI eşleştirmeleri
                for gri_disclosure in mapping.get('gri_disclosures', []):
                    manager.map_to_frameworks(
                        activity_code=activity_code,
                        objective_code=objective_code,
                        gri_disclosure=gri_disclosure,
                        rationale=f"GRI Disclosure {gri_disclosure} alignment"
                    )
                
                # TSRS eşleştirmeleri
                for tsrs_metric in mapping.get('tsrs_metrics', []):
                    manager.map_to_frameworks(
                        activity_code=activity_code,
                        objective_code=objective_code,
                        tsrs_metric=tsrs_metric,
                        rationale=f"TSRS Metric {tsrs_metric} alignment"
                    )
                
                mapping_success += 1
                logging.info(f" {activity_code} eşleştirmeleri eklendi")
                
            except Exception as e:
                logging.error(f" {mapping.get('activity_code', '?')}: Eşleştirme hatası - {e}")
        
        logging.info(f"\n Eşleştirme Özeti: {mapping_success}/{len(mappings)}")
    
    logging.info("\n İçe aktarma tamamlandı!")
    return True

def main() -> None:
    """Ana fonksiyon"""
    # Varsayılan yollar
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
    activities_file = os.path.join(base_dir, 'data', 'eu_taxonomy_activities.json')
    
    # Komut satırı argümanları
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    if len(sys.argv) > 2:
        activities_file = sys.argv[2]
    
    logging.info(f" Veritabanı: {db_path}")
    logging.info(f" Faaliyetler: {activities_file}")
    logging.info()
    
    # İçe aktar
    import_activities(db_path, activities_file)

if __name__ == '__main__':
    main()
