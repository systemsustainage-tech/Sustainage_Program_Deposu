#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG 2025 Veri Tutarlılık Kontrol Aracı
2025 revizyonu sonrası veri kalitesi ve tutarlılık kontrolleri
"""

import logging
import os
import sqlite3
from typing import Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SDG2025DataValidator:
    """SDG 2025 veri validasyon sınıfı"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
    
    def validate_all(self) -> Dict:
        """Tüm validasyon kontrollerini yap"""
        logging.info("\n" + "="*80)
        logging.info("SDG 2025 VERİ TUTARLILIK KONTROLÜ")
        logging.info("="*80 + "\n")
        
        results = {
            'deprecated_checks': self.check_deprecated_indicators(),
            'revision_labels': self.check_revision_labels(),
            'data_completeness': self.check_data_completeness(),
            'tier_consistency': self.check_tier_consistency(),
            'migration_integrity': self.check_migration_integrity()
        }
        
        return results
    
    def check_deprecated_indicators(self) -> Dict:
        """Deprecated göstergeleri kontrol et"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT code, is_deprecated, replacement_indicator
                FROM sdg_indicators
                WHERE is_deprecated = 1
            """)
            
            deprecated = cursor.fetchall()
            
            # Deprecated göstergelerin yanıtlarını kontrol et
            issues = []
            for code, is_dep, replacement in deprecated:
                cursor.execute("""
                    SELECT COUNT(*) FROM responses r
                    JOIN sdg_indicators si ON r.indicator_id = si.id
                    WHERE si.code = ?
                """, (code,))
                
                response_count = cursor.fetchone()[0]
                if response_count > 0 and not replacement:
                    issues.append(f"{code}: {response_count} yanıt var ama replacement yok")
            
            logging.info(f" Deprecated göstergeler: {len(deprecated)}")
            if issues:
                logging.info(f"  ️  Sorunlar: {len(issues)}")
            
            return {
                'total_deprecated': len(deprecated),
                'issues': issues
            }
            
        finally:
            conn.close()
    
    def check_revision_labels(self) -> Dict:
        """Revizyon etiketlerini kontrol et"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM sdg_indicators
                WHERE revision_note IS NOT NULL AND revision_note LIKE '%2025%'
            """)
            
            labeled_count = cursor.fetchone()[0]
            
            logging.info(f" 2025 etiketli göstergeler: {labeled_count}")
            
            return {'labeled_count': labeled_count}
            
        finally:
            conn.close()
    
    def check_data_completeness(self) -> Dict:
        """Veri eksiksizliğini kontrol et"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN description IS NULL OR description = '' THEN 1 ELSE 0 END) as missing_desc
                FROM sdg_indicators
            """)
            
            total, missing_desc = cursor.fetchone()
            
            logging.info(f" Veri eksiksizliği: {total - missing_desc}/{total} gösterge tamam")
            
            return {
                'total_indicators': total,
                'missing_description': missing_desc
            }
            
        finally:
            conn.close()
    
    def check_tier_consistency(self) -> Dict:
        """Tier tutarlılığını kontrol et"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT tier, COUNT(*) as count
                FROM sdg_indicators
                WHERE tier IS NOT NULL
                GROUP BY tier
            """)
            
            tier_dist = {row[0]: row[1] for row in cursor.fetchall()}
            
            logging.info(f" Tier dağılımı: {tier_dist}")
            
            return {'tier_distribution': tier_dist}
            
        finally:
            conn.close()
    
    def check_migration_integrity(self) -> Dict:
        """Migrasyon bütünlüğünü kontrol et"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Migrated responses kontrolü
            cursor.execute("""
                SELECT COUNT(*) FROM responses
                WHERE migrated_from IS NOT NULL
            """)
            
            migrated_count = cursor.fetchone()[0]
            
            logging.info(f" Migrate edilmiş yanıtlar: {migrated_count}")
            
            return {'migrated_responses': migrated_count}
            
        except Exception:
            return {'migrated_responses': 0, 'note': 'Migration columns not found'}
        finally:
            conn.close()

def main():
    """Ana fonksiyon"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
    
    validator = SDG2025DataValidator(db_path)
    validator.validate_all()
    
    logging.info("\n" + "="*80)
    logging.info(" Validasyon tamamlandı!")
    logging.info("="*80)

if __name__ == '__main__':
    main()

