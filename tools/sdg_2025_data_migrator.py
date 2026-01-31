import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG 2025 Veri Migrasyonu Aracı
Eklenen/çıkarılan/değiştirilen göstergeler için veri migrasyonu
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SDG2025DataMigrator:
    """SDG 2025 veri migrasyon yöneticisi"""
    
    def __init__(self, db_path: str):
        """
        Data Migrator'ı başlat
        
        Args:
            db_path: Veritabanı dosya yolu
        """
        self.db_path = db_path
        
        # Migrasyon kuralları
        self.migration_rules = {
            # Deprecated -> Replacement gösterge migrasyonları
            'deprecations': [
                {
                    'old_code': '17.18.2',
                    'new_code': '17.18.1',
                    'strategy': 'merge',
                    'note': 'Ulusal istatistik mevzuatı verileri 17.18.1\'e birleştirildi'
                },
                {
                    'old_code': '8.9.2',
                    'new_code': '8.9.1',
                    'strategy': 'merge',
                    'note': 'Turizm GSYİH verileri kapsamlı 8.9.1\'e birleştirildi'
                },
                {
                    'old_code': '10.c.1',
                    'new_code': '10.c.2',
                    'strategy': 'migrate',
                    'note': 'Para transferi maliyetleri 10.c.2\'ye taşındı'
                }
            ],
            # Güncellenen göstergeler (backward compatible)
            'modifications': [
                {
                    'code': '6.3.1',
                    'change_type': 'scope_expanded',
                    'action': 'keep_existing_data',
                    'note': 'Mevcut veriler geçerli, yeni kapsam için ek veri toplanabilir'
                },
                {
                    'code': '12.3.1',
                    'change_type': 'scope_expanded',
                    'action': 'data_quality_check',
                    'note': 'Tüketici israfı eklendi - mevcut verilerin uyumluluğu kontrol edilmeli'
                }
            ]
        }
    
    def get_connection(self) -> sqlite3.Connection:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)
    
    def backup_response_data(self, indicator_code: str) -> Dict:
        """
        Gösterge yanıt verilerini yedekle
        
        Args:
            indicator_code: Gösterge kodu
            
        Returns:
            Yedeklenen veri bilgileri
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Gösterge ID'sini al
            cursor.execute("SELECT id FROM sdg_indicators WHERE code = ?", (indicator_code,))
            result = cursor.fetchone()
            
            if not result:
                return {'status': 'indicator_not_found', 'count': 0}
            
            indicator_id = result[0]
            
            # Yanıtları al
            cursor.execute("""
                SELECT r.*, si.code, si.description
                FROM responses r
                JOIN sdg_indicators si ON r.indicator_id = si.id
                WHERE r.indicator_id = ?
            """, (indicator_id,))
            
            responses = cursor.fetchall()
            
            # Yedekleme dizini oluştur
            backup_dir = 'data/backups/sdg_2025_migration'
            os.makedirs(backup_dir, exist_ok=True)
            
            # Yedek dosyası
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(backup_dir, f'responses_{indicator_code}_{timestamp}.json')
            
            # JSON olarak kaydet
            backup_data = {
                'indicator_code': indicator_code,
                'indicator_id': indicator_id,
                'backup_date': datetime.now().isoformat(),
                'response_count': len(responses),
                'responses': [
                    {
                        'response_id': row[0],
                        'indicator_id': row[1],
                        'question_id': row[2] if len(row) > 2 else None,
                        'answer': row[3] if len(row) > 3 else None,
                        'created_at': row[4] if len(row) > 4 else None
                    }
                    for row in responses
                ]
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            logging.info(f" Yedek oluşturuldu: {backup_file} ({len(responses)} yanıt)")
            
            return {
                'status': 'success',
                'indicator_code': indicator_code,
                'count': len(responses),
                'backup_file': backup_file
            }
            
        except Exception as e:
            logging.error(f" Yedekleme hatası ({indicator_code}): {e}")
            return {'status': 'error', 'error': str(e), 'count': 0}
        finally:
            conn.close()
    
    def migrate_deprecated_data(self, old_code: str, new_code: str, strategy: str = 'merge') -> Dict:
        """
        Deprecated gösterge verilerini yeni göstergeye taşı
        
        Args:
            old_code: Eski gösterge kodu
            new_code: Yeni gösterge kodu
            strategy: Migrasyon stratejisi ('merge' veya 'migrate')
            
        Returns:
            Migrasyon sonucu
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        result = {
            'old_code': old_code,
            'new_code': new_code,
            'strategy': strategy,
            'migrated_count': 0,
            'errors': []
        }
        
        try:
            # Eski gösterge ID'sini al
            cursor.execute("SELECT id FROM sdg_indicators WHERE code = ?", (old_code,))
            old_result = cursor.fetchone()
            
            if not old_result:
                result['errors'].append(f"Eski gösterge bulunamadı: {old_code}")
                return result
            
            old_indicator_id = old_result[0]
            
            # Yeni gösterge ID'sini al
            cursor.execute("SELECT id FROM sdg_indicators WHERE code = ?", (new_code,))
            new_result = cursor.fetchone()
            
            if not new_result:
                result['errors'].append(f"Yeni gösterge bulunamadı: {new_code}")
                return result
            
            new_indicator_id = new_result[0]
            
            # Yedek al
            self.backup_response_data(old_code)
            
            if strategy == 'merge':
                # Yanıtları birleştir (yeni göstergeye kopyala, eskisini deprecated işaretle)
                cursor.execute("""
                    INSERT INTO responses (indicator_id, question_id, answer, created_at, migrated_from)
                    SELECT ?, question_id, answer, created_at, ?
                    FROM responses
                    WHERE indicator_id = ?
                """, (new_indicator_id, old_indicator_id, old_indicator_id))
                
                result['migrated_count'] = cursor.rowcount
                
                # Eski göstergeyi deprecated işaretle
                cursor.execute("""
                    UPDATE sdg_indicators
                    SET is_deprecated = 1,
                        deprecation_reason = ?,
                        replacement_indicator = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    f"2025 revizyonunda {new_code} ile birleştirildi",
                    new_code,
                    old_indicator_id
                ))
                
            elif strategy == 'migrate':
                # Yanıtları taşı (eski göstergeyi yenisine güncelle)
                cursor.execute("""
                    UPDATE responses
                    SET indicator_id = ?,
                        migrated_from = ?,
                        migrated_at = CURRENT_TIMESTAMP
                    WHERE indicator_id = ?
                """, (new_indicator_id, old_indicator_id, old_indicator_id))
                
                result['migrated_count'] = cursor.rowcount
                
                # Eski göstergeyi deprecated işaretle
                cursor.execute("""
                    UPDATE sdg_indicators
                    SET is_deprecated = 1,
                        deprecation_reason = ?,
                        replacement_indicator = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    f"2025 revizyonunda {new_code}'ye taşındı",
                    new_code,
                    old_indicator_id
                ))
            
            conn.commit()
            logging.info(f" Migrasyon tamamlandı: {old_code} → {new_code} ({result['migrated_count']} yanıt)")
            
        except Exception as e:
            conn.rollback()
            result['errors'].append(str(e))
            logging.error(f" Migrasyon hatası: {e}")
        finally:
            conn.close()
        
        return result
    
    def validate_modified_data(self, indicator_code: str) -> Dict:
        """
        Güncellenmiş gösterge verilerinin tutarlılığını kontrol et
        
        Args:
            indicator_code: Gösterge kodu
            
        Returns:
            Validasyon sonucu
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        validation = {
            'indicator_code': indicator_code,
            'total_responses': 0,
            'issues': [],
            'quality_score': 0
        }
        
        try:
            # Gösterge ID'sini al
            cursor.execute("SELECT id FROM sdg_indicators WHERE code = ?", (indicator_code,))
            result = cursor.fetchone()
            
            if not result:
                validation['issues'].append("Gösterge bulunamadı")
                return validation
            
            indicator_id = result[0]
            
            # Yanıt sayısını al
            cursor.execute("""
                SELECT COUNT(*) FROM responses WHERE indicator_id = ?
            """, (indicator_id,))
            validation['total_responses'] = cursor.fetchone()[0]
            
            # Boş yanıtları kontrol et
            cursor.execute("""
                SELECT COUNT(*) FROM responses 
                WHERE indicator_id = ? AND (answer IS NULL OR answer = '')
            """, (indicator_id,))
            empty_count = cursor.fetchone()[0]
            
            if empty_count > 0:
                validation['issues'].append(f"Boş yanıt: {empty_count}")
            
            # Veri kalite skoru hesapla (0-100)
            if validation['total_responses'] > 0:
                empty_ratio = empty_count / validation['total_responses']
                validation['quality_score'] = int((1 - empty_ratio) * 100)
            
        except Exception as e:
            validation['issues'].append(str(e))
        finally:
            conn.close()
        
        return validation
    
    def execute_all_migrations(self, dry_run: bool = True) -> Dict:
        """
        Tüm migrasyonları çalıştır
        
        Args:
            dry_run: Test modu (değişiklik yapmaz)
            
        Returns:
            Migrasyon özeti
        """
        logging.info("\n" + "="*80)
        logging.info("SDG 2025 VERİ MİGRASYONU")
        logging.info("="*80 + "\n")
        
        summary = {
            'deprecations': [],
            'modifications': [],
            'total_migrated': 0,
            'total_errors': 0,
            'dry_run': dry_run
        }
        
        if dry_run:
            logging.info("️  DRY RUN - Değişiklikler uygulanmayacak\n")
        
        # Deprecated gösterge migrasyonları
        logging.info(" Deprecated Gösterge Migrasyonları:\n")
        for rule in self.migration_rules['deprecations']:
            logging.info(f"  {rule['old_code']} → {rule['new_code']} ({rule['strategy']})")
            
            if not dry_run:
                result = self.migrate_deprecated_data(
                    rule['old_code'],
                    rule['new_code'],
                    rule['strategy']
                )
                summary['deprecations'].append(result)
                summary['total_migrated'] += result['migrated_count']
                summary['total_errors'] += len(result['errors'])
            else:
                logging.info("    → DRY RUN: Migrasyon simüle edildi")
                summary['deprecations'].append({
                    'old_code': rule['old_code'],
                    'new_code': rule['new_code'],
                    'strategy': rule['strategy'],
                    'status': 'simulated'
                })
        
        # Güncellenmiş gösterge validasyonları
        logging.info("\n Güncellenmiş Gösterge Validasyonları:\n")
        for rule in self.migration_rules['modifications']:
            logging.info(f"  {rule['code']} - {rule['change_type']}")
            
            validation = self.validate_modified_data(rule['code'])
            summary['modifications'].append(validation)
            
            if validation['issues']:
                logging.info(f"    ️  Sorunlar: {', '.join(validation['issues'])}")
            else:
                logging.info(f"     Kalite skoru: {validation['quality_score']}/100")
        
        return summary
    
    def generate_migration_report(self, summary: Dict, output_path: str = None) -> str:
        """
        Migrasyon raporu oluştur
        
        Args:
            summary: Migrasyon özeti
            output_path: Çıktı dosya yolu
            
        Returns:
            Rapor dosya yolu
        """
        if not output_path:
            output_dir = 'reports/sdg_2025_migration'
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(output_dir, f'sdg_2025_data_migration_{timestamp}.txt')
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("SDG 2025 VERI MIGRASYONU RAPORU\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Rapor Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Veritabani: {self.db_path}\n")
                f.write(f"Dry Run: {'Evet' if summary['dry_run'] else 'Hayir'}\n\n")
                
                # Özet
                f.write("-" * 80 + "\n")
                f.write("OZET\n")
                f.write("-" * 80 + "\n\n")
                
                f.write(f"Toplam Migrate Edilen Yanit: {summary['total_migrated']}\n")
                f.write(f"Toplam Hata: {summary['total_errors']}\n")
                f.write(f"Deprecation Migrasyonu: {len(summary['deprecations'])}\n")
                f.write(f"Modifikasyon Validasyonu: {len(summary['modifications'])}\n\n")
                
                # Deprecation detayları
                if summary['deprecations']:
                    f.write("-" * 80 + "\n")
                    f.write("DEPRECATION MIGRASYONLARI\n")
                    f.write("-" * 80 + "\n\n")
                    
                    for dep in summary['deprecations']:
                        f.write(f"{dep['old_code']} -> {dep['new_code']}\n")
                        if 'migrated_count' in dep:
                            f.write(f"  Migrate edilen: {dep['migrated_count']} yanit\n")
                        if 'strategy' in dep:
                            f.write(f"  Strateji: {dep['strategy']}\n")
                        if 'errors' in dep and dep['errors']:
                            f.write(f"  Hatalar: {', '.join(dep['errors'])}\n")
                        f.write("\n")
                
                # Modifikasyon detayları
                if summary['modifications']:
                    f.write("-" * 80 + "\n")
                    f.write("MODIFIKASYON VALIDASYONLARI\n")
                    f.write("-" * 80 + "\n\n")
                    
                    for mod in summary['modifications']:
                        f.write(f"{mod['indicator_code']}\n")
                        f.write(f"  Toplam yanit: {mod['total_responses']}\n")
                        f.write(f"  Kalite skoru: {mod['quality_score']}/100\n")
                        if mod['issues']:
                            f.write(f"  Sorunlar: {', '.join(mod['issues'])}\n")
                        f.write("\n")
                
                f.write("=" * 80 + "\n")
            
            logging.info(f"\n Migrasyon raporu oluşturuldu: {output_path}")
            return output_path
            
        except Exception as e:
            logging.error(f"Rapor oluşturma hatası: {e}")
            return None
    
    def add_migration_columns(self) -> None:
        """Migrasyon için gerekli kolonları ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # responses tablosuna migrasyon kolonları
            try:
                cursor.execute("""
                    ALTER TABLE responses 
                    ADD COLUMN migrated_from INTEGER
                """)
                logging.info(" migrated_from kolonu eklendi")
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
            
            try:
                cursor.execute("""
                    ALTER TABLE responses 
                    ADD COLUMN migrated_at TIMESTAMP
                """)
                logging.info(" migrated_at kolonu eklendi")
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
            
            conn.commit()
            
        except Exception as e:
            logging.error(f"Kolon ekleme hatası: {e}")
            conn.rollback()
        finally:
            conn.close()

def main():
    """Ana fonksiyon"""
    logging.info(" SDG 2025 Veri Migrasyonu Aracı")
    logging.info("=" * 60 + "\n")
    
    # Veritabanı yolu
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
    
    if not os.path.exists(db_path):
        logging.info(f" Veritabanı bulunamadı: {db_path}")
        return
    
    # Migrator oluştur
    migrator = SDG2025DataMigrator(db_path)
    
    # Migrasyon kolonları ekle
    logging.info(" Migrasyon kolonları kontrol ediliyor...")
    migrator.add_migration_columns()
    
    # Dry run
    logging.info("\n DRY RUN - Migrasyon Simülasyonu...")
    summary_dry = migrator.execute_all_migrations(dry_run=True)
    
    logging.info("\n Dry Run Özeti:")
    logging.info(f"  Deprecation migrasyonu: {len(summary_dry['deprecations'])}")
    logging.info(f"  Modifikasyon validasyonu: {len(summary_dry['modifications'])}")
    
    # Gerçek migrasyon onayı
    logging.info("\n Migrasyonları uygulamak istiyor musunuz?")
    response = input("(y/n): ").lower()
    
    if response == 'y':
        logging.info("\n Migrasyon Uygulanıyor...")
        summary = migrator.execute_all_migrations(dry_run=False)
        
        # Rapor oluştur
        logging.info("\n Migrasyon Raporu Oluşturuluyor...")
        report_path = migrator.generate_migration_report(summary)
        
        logging.info("\n" + "=" * 60)
        logging.info(" Migrasyon Tamamlandı!")
        if report_path:
            logging.info(f"\n Rapor: {report_path}")
    else:
        logging.info("\n İşlem iptal edildi.")

if __name__ == '__main__':
    main()

