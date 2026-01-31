import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG 2025 Revizyon Senkronizasyon Aracı
2025 SDG gösterge revizyonu ile mevcut verilerin senkronizasyonu
"""

import io
import json
import os
import sqlite3
import sys
from datetime import datetime
from typing import Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Windows terminal için UTF-8 desteği
if os.name == 'nt' and not os.getenv('PYTEST_CURRENT_TEST'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError) as e:
        logging.error(f'Silent error in sdg_2025_sync.py: {str(e)}')

class SDG2025Sync:
    """SDG 2025 senkronizasyon yöneticisi"""
    
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        
        # 2025 revizyonu değişiklikleri
        self.revision_2025 = {
            'added_indicators': [
                # Yeni eklenen göstergeler
                {
                    'code': '1.1.2',
                    'goal_id': 1,
                    'target': '1.1',
                    'description': 'Ulusal yoksulluk sınırının altında yaşayan nüfusun oranı',
                    'revision_note': '2025 revizyonunda eklendi',
                    'status': 'new'
                },
                {
                    'code': '13.2.3',
                    'goal_id': 13,
                    'target': '13.2',
                    'description': 'İklim değişikliği uyum planlarının uygulanma durumu',
                    'revision_note': '2025 revizyonunda eklendi',
                    'status': 'new'
                }
            ],
            'modified_indicators': [
                # Güncellenen göstergeler
                {
                    'code': '6.3.1',
                    'old_description': 'Güvenli arıtılmış atık su oranı',
                    'new_description': 'Güvenli arıtılmış evsel ve endüstriyel atık su oranı',
                    'revision_note': 'Tanım genişletildi - 2025',
                    'status': 'modified'
                },
                {
                    'code': '12.3.1',
                    'old_description': 'Küresel gıda kaybı endeksi',
                    'new_description': 'Gıda kaybı ve israfı endeksi (üretimden tüketime)',
                    'revision_note': 'Kapsam genişletildi - 2025',
                    'status': 'modified'
                }
            ],
            'deprecated_indicators': [
                # Kaldırılan veya birleştirilen göstergeler
                {
                    'code': '17.18.2',
                    'reason': '17.18.1 ile birleştirildi',
                    'replacement': '17.18.1',
                    'revision_note': '2025 revizyonunda birleştirildi',
                    'status': 'deprecated'
                }
            ],
            'tier_changes': [
                # Tier değişiklikleri (Tier III -> Tier II vb.)
                {
                    'code': '11.6.2',
                    'old_tier': 'III',
                    'new_tier': 'II',
                    'reason': 'Veri metodolojisi geliştirildi',
                    'status': 'tier_upgraded'
                }
            ]
        }
    
    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)
    
    def backup_database(self) -> str:
        """Veritabanını yedekle"""
        try:
            import shutil
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = 'data/backups/sdg_2025_sync'
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_path = os.path.join(backup_dir, f'sdg_desktop_pre_2025_sync_{timestamp}.sqlite')
            shutil.copy2(self.db_path, backup_path)
            
            logging.info(f" Veritabanı yedeklendi: {backup_path}")
            return backup_path
            
        except Exception as e:
            logging.error(f" Yedekleme hatası: {e}")
            return None
    
    def analyze_current_data(self) -> Dict:
        """Mevcut veri durumunu analiz et"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        analysis = {
            'total_indicators': 0,
            'total_responses': 0,
            'indicators_by_goal': {},
            'response_coverage': {},
            'potential_conflicts': []
        }
        
        try:
            # Toplam gösterge sayısı
            cursor.execute("SELECT COUNT(*) FROM sdg_indicators")
            analysis['total_indicators'] = cursor.fetchone()[0]
            
            # Toplam yanıt sayısı
            cursor.execute("SELECT COUNT(*) FROM responses")
            analysis['total_responses'] = cursor.fetchone()[0]
            
            # Hedef bazlı gösterge sayıları
            cursor.execute("""
                SELECT goal_id, COUNT(*) as count
                FROM sdg_indicators
                GROUP BY goal_id
                ORDER BY goal_id
            """)
            
            for row in cursor.fetchall():
                analysis['indicators_by_goal'][row[0]] = row[1]
            
            # Yanıt kapsama oranı
            cursor.execute("""
                SELECT 
                    i.goal_id,
                    COUNT(DISTINCT i.id) as total_indicators,
                    COUNT(DISTINCT r.indicator_id) as answered_indicators
                FROM sdg_indicators i
                LEFT JOIN responses r ON i.id = r.indicator_id
                GROUP BY i.goal_id
            """)
            
            for row in cursor.fetchall():
                goal_id, total, answered = row
                coverage = (answered / total * 100) if total > 0 else 0
                analysis['response_coverage'][goal_id] = {
                    'total': total,
                    'answered': answered,
                    'percentage': coverage
                }
            
            # 2025 revizyonunda etkilenecek göstergeleri kontrol et
            for indicator in self.revision_2025['modified_indicators']:
                cursor.execute("""
                    SELECT COUNT(*) FROM responses 
                    WHERE indicator_id = (
                        SELECT id FROM sdg_indicators WHERE code = ?
                    )
                """, (indicator['code'],))
                
                response_count = cursor.fetchone()[0]
                if response_count > 0:
                    analysis['potential_conflicts'].append({
                        'indicator_code': indicator['code'],
                        'response_count': response_count,
                        'issue': 'Güncellenen gösterge için mevcut yanıtlar var'
                    })
            
        except Exception as e:
            logging.error(f"Analiz hatası: {e}")
        finally:
            conn.close()
        
        return analysis
    
    def apply_2025_revision(self, dry_run: bool = True) -> Dict:
        """2025 revizyonunu uygula"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        results = {
            'added': [],
            'modified': [],
            'deprecated': [],
            'tier_changes': [],
            'errors': []
        }
        
        try:
            # 1. Yeni göstergeleri ekle
            logging.info("\n Yeni Göstergeler Ekleniyor...")
            for indicator in self.revision_2025['added_indicators']:
                try:
                    if not dry_run:
                        cursor.execute("""
                            INSERT OR IGNORE INTO sdg_indicators 
                            (code, goal_id, target, description, revision_note)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            indicator['code'],
                            indicator['goal_id'],
                            indicator['target'],
                            indicator['description'],
                            indicator['revision_note']
                        ))
                    
                    results['added'].append(indicator['code'])
                    logging.info(f"   {indicator['code']}: {indicator['description'][:50]}...")
                    
                except Exception as e:
                    results['errors'].append(f"Ekleme hatası ({indicator['code']}): {e}")
                    logging.info(f"   {indicator['code']}: {e}")
            
            # 2. Mevcut göstergeleri güncelle
            logging.info("\n Göstergeler Güncelleniyor...")
            for indicator in self.revision_2025['modified_indicators']:
                try:
                    if not dry_run:
                        cursor.execute("""
                            UPDATE sdg_indicators 
                            SET description = ?,
                                revision_note = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE code = ?
                        """, (
                            indicator['new_description'],
                            indicator['revision_note'],
                            indicator['code']
                        ))
                    
                    results['modified'].append(indicator['code'])
                    logging.info(f"   {indicator['code']}: Güncellendi")
                    
                except Exception as e:
                    results['errors'].append(f"Güncelleme hatası ({indicator['code']}): {e}")
                    logging.info(f"   {indicator['code']}: {e}")
            
            # 3. Eski göstergeleri işaretle
            logging.info("\n️  Eski Göstergeler İşaretleniyor...")
            for indicator in self.revision_2025['deprecated_indicators']:
                try:
                    if not dry_run:
                        cursor.execute("""
                            UPDATE sdg_indicators 
                            SET is_deprecated = 1,
                                deprecation_reason = ?,
                                replacement_indicator = ?,
                                revision_note = ?
                            WHERE code = ?
                        """, (
                            indicator['reason'],
                            indicator['replacement'],
                            indicator['revision_note'],
                            indicator['code']
                        ))
                    
                    results['deprecated'].append(indicator['code'])
                    logging.info(f"   {indicator['code']}: Deprecated olarak işaretlendi")
                    
                except Exception as e:
                    # Kolon yoksa ekle
                    if 'no such column' in str(e).lower():
                        self._add_revision_columns(cursor)
                        # Tekrar dene
                        if not dry_run:
                            cursor.execute("""
                                UPDATE sdg_indicators 
                                SET is_deprecated = 1,
                                    deprecation_reason = ?,
                                    replacement_indicator = ?,
                                    revision_note = ?
                                WHERE code = ?
                            """, (
                                indicator['reason'],
                                indicator['replacement'],
                                indicator['revision_note'],
                                indicator['code']
                            ))
                        results['deprecated'].append(indicator['code'])
                        logging.info(f"   {indicator['code']}: Deprecated olarak işaretlendi")
                    else:
                        results['errors'].append(f"Deprecation hatası ({indicator['code']}): {e}")
                        logging.info(f"   {indicator['code']}: {e}")
            
            # 4. Tier değişikliklerini uygula
            logging.info("\n Tier Değişiklikleri Uygulanıyor...")
            for change in self.revision_2025['tier_changes']:
                try:
                    if not dry_run:
                        cursor.execute("""
                            UPDATE sdg_indicators 
                            SET tier = ?,
                                tier_change_note = ?
                            WHERE code = ?
                        """, (
                            change['new_tier'],
                            f"Tier {change['old_tier']} -> {change['new_tier']}: {change['reason']}",
                            change['code']
                        ))
                    
                    results['tier_changes'].append(change['code'])
                    logging.info(f"   {change['code']}: Tier {change['old_tier']} → {change['new_tier']}")
                    
                except Exception as e:
                    results['errors'].append(f"Tier değişiklik hatası ({change['code']}): {e}")
                    logging.info(f"   {change['code']}: {e}")
            
            if not dry_run:
                conn.commit()
                logging.info("\n Değişiklikler veritabanına kaydedildi")
            else:
                logging.info("\n️  DRY RUN - Değişiklikler uygulanmadı")
            
        except Exception as e:
            logging.error(f"\n Revizyon uygulama hatası: {e}")
            conn.rollback()
        finally:
            conn.close()
        
        return results
    
    def _add_revision_columns(self, cursor) -> None:
        """Revizyon kolonlarını ekle"""
        try:
            cursor.execute("""
                ALTER TABLE sdg_indicators 
                ADD COLUMN is_deprecated BOOLEAN DEFAULT 0
            """)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        
        try:
            cursor.execute("""
                ALTER TABLE sdg_indicators 
                ADD COLUMN deprecation_reason TEXT
            """)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        
        try:
            cursor.execute("""
                ALTER TABLE sdg_indicators 
                ADD COLUMN replacement_indicator VARCHAR(20)
            """)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        
        try:
            cursor.execute("""
                ALTER TABLE sdg_indicators 
                ADD COLUMN revision_note TEXT
            """)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        
        try:
            cursor.execute("""
                ALTER TABLE sdg_indicators 
                ADD COLUMN tier_change_note TEXT
            """)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        
        try:
            cursor.execute("""
                ALTER TABLE sdg_indicators 
                ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
    
    def generate_migration_report(self, analysis: Dict, results: Dict, output_path: str = None) -> str:
        """Migrasyon raporu oluştur"""
        if not output_path:
            output_dir = 'reports/sdg_2025_sync'
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(output_dir, f'sdg_2025_migration_report_{timestamp}.txt')
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("SDG 2025 REVİZYON MİGRASYON RAPORU\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Rapor Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Veritabanı: {self.db_path}\n\n")
                
                # Mevcut durum
                f.write("-" * 80 + "\n")
                f.write("MEVCUT DURUM ANALİZİ\n")
                f.write("-" * 80 + "\n\n")
                
                f.write(f"Toplam Gösterge: {analysis['total_indicators']}\n")
                f.write(f"Toplam Yanıt: {analysis['total_responses']}\n\n")
                
                f.write("Hedef Bazlı Gösterge Dağılımı:\n")
                for goal_id, count in sorted(analysis['indicators_by_goal'].items()):
                    f.write(f"  SDG {goal_id}: {count} gösterge\n")
                
                f.write("\nYanıt Kapsama Oranları:\n")
                for goal_id, coverage in sorted(analysis['response_coverage'].items()):
                    f.write(f"  SDG {goal_id}: %{coverage['percentage']:.1f} ({coverage['answered']}/{coverage['total']})\n")
                
                # Revizyon değişiklikleri
                f.write("\n" + "-" * 80 + "\n")
                f.write("2025 REVİZYON DEĞİŞİKLİKLERİ\n")
                f.write("-" * 80 + "\n\n")
                
                f.write(f" Eklenen Gösterge: {len(results['added'])}\n")
                for code in results['added']:
                    f.write(f"  - {code}\n")
                
                f.write(f"\n Güncellenen Gösterge: {len(results['modified'])}\n")
                for code in results['modified']:
                    f.write(f"  - {code}\n")
                
                f.write(f"\n️  Deprecated Gösterge: {len(results['deprecated'])}\n")
                for code in results['deprecated']:
                    f.write(f"  - {code}\n")
                
                f.write(f"\n Tier Değişikliği: {len(results['tier_changes'])}\n")
                for code in results['tier_changes']:
                    f.write(f"  - {code}\n")
                
                # Potansiyel çakışmalar
                if analysis['potential_conflicts']:
                    f.write("\n" + "-" * 80 + "\n")
                    f.write("POTANSİYEL ÇAKIŞMALAR\n")
                    f.write("-" * 80 + "\n\n")
                    
                    for conflict in analysis['potential_conflicts']:
                        f.write(f"️  {conflict['indicator_code']}\n")
                        f.write(f"   Mevcut yanıt: {conflict['response_count']}\n")
                        f.write(f"   Sorun: {conflict['issue']}\n\n")
                
                # Hatalar
                if results['errors']:
                    f.write("\n" + "-" * 80 + "\n")
                    f.write("HATALAR\n")
                    f.write("-" * 80 + "\n\n")
                    
                    for error in results['errors']:
                        f.write(f" {error}\n")
                
                # Öneriler
                f.write("\n" + "-" * 80 + "\n")
                f.write("ÖNERİLER\n")
                f.write("-" * 80 + "\n\n")
                
                f.write("1. Deprecated göstergelerin yanıtlarını yeni göstergelere taşıyın\n")
                f.write("2. Güncellenmiş tanımları kullanıcılara bildirin\n")
                f.write("3. Yeni göstergeleri yanıtlamaya başlayın\n")
                f.write("4. Tier yükseltmelerinden yararlanın\n")
                
                f.write("\n" + "=" * 80 + "\n")
            
            logging.info(f"\n Migrasyon raporu oluşturuldu: {output_path}")
            return output_path
            
        except Exception as e:
            logging.error(f"Rapor oluşturma hatası: {e}")
            return None
    
    def create_revision_metadata(self) -> None:
        """Revizyon metadata tablosu oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sdg_revision_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    revision_year INTEGER NOT NULL,
                    revision_date DATE,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    applied_by VARCHAR(100),
                    backup_path TEXT,
                    changes_summary TEXT,
                    notes TEXT
                )
            """)
            
            conn.commit()
            logging.info("[OK] Revizyon metadata tablosu oluşturuldu")
            
        except Exception as e:
            logging.error(f"[HATA] Metadata tablosu oluşturma hatası: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def record_revision_application(self, backup_path: str, results: Dict) -> None:
        """Revizyon uygulamasını kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            changes_summary = json.dumps({
                'added': len(results['added']),
                'modified': len(results['modified']),
                'deprecated': len(results['deprecated']),
                'tier_changes': len(results['tier_changes']),
                'errors': len(results['errors'])
            }, ensure_ascii=False)
            
            cursor.execute("""
                INSERT INTO sdg_revision_metadata 
                (revision_year, revision_date, backup_path, changes_summary, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (
                2025,
                '2025-01-01',
                backup_path,
                changes_summary,
                'SDG 2025 gösterge revizyonu uygulandı'
            ))
            
            conn.commit()
            logging.info("[OK] Revizyon kaydı oluşturuldu")
            
        except Exception as e:
            logging.error(f"[HATA] Revizyon kaydı oluşturma hatası: {e}")
            conn.rollback()
        finally:
            conn.close()

def main() -> None:
    """Ana fonksiyon"""
    logging.info(" SDG 2025 Revizyon Senkronizasyon Aracı")
    logging.info("=" * 60)
    
    # Veritabanı yolu
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
    
    if not os.path.exists(db_path):
        logging.info(f" Veritabanı bulunamadı: {db_path}")
        return
    
    # Sync manager oluştur
    sync = SDG2025Sync(db_path)
    
    # Metadata tablosu oluştur
    sync.create_revision_metadata()
    
    # Mevcut durumu analiz et
    logging.info("\n Mevcut Durum Analiz Ediliyor...")
    analysis = sync.analyze_current_data()
    
    logging.info("\n Analiz Sonuçları:")
    logging.info(f"  Toplam Gösterge: {analysis['total_indicators']}")
    logging.info(f"  Toplam Yanıt: {analysis['total_responses']}")
    logging.info(f"  Potansiyel Çakışma: {len(analysis['potential_conflicts'])}")
    
    # Kullanıcıya sor
    logging.info("\n️  DİKKAT: Bu işlem veritabanını değiştirecektir!")
    logging.info("1. Önce DRY RUN yapılacak (değişiklik uygulanmaz)")
    logging.info("2. Sonra gerçek uygulama için onay istenecek")
    
    input("\nDevam etmek için Enter'a basın...")
    
    # Dry run
    logging.info("\n DRY RUN - Değişiklikler Simüle Ediliyor...")
    results_dry = sync.apply_2025_revision(dry_run=True)
    
    logging.info("\n Dry Run Özeti:")
    logging.info(f"   Eklenecek: {len(results_dry['added'])}")
    logging.info(f"   Güncellenecek: {len(results_dry['modified'])}")
    logging.info(f"  ️  Deprecated: {len(results_dry['deprecated'])}")
    logging.info(f"   Tier Değişikliği: {len(results_dry['tier_changes'])}")
    logging.error(f"   Hata: {len(results_dry['errors'])}")
    
    # Gerçek uygulama onayı
    logging.info("\n Değişiklikleri uygulamak istiyor musunuz?")
    response = input("(y/n): ").lower()
    
    if response == 'y':
        # Yedek al
        logging.info("\n Veritabanı Yedekleniyor...")
        backup_path = sync.backup_database()
        
        if not backup_path:
            logging.info(" Yedekleme başarısız! İşlem iptal edildi.")
            return
        
        # Gerçek uygulama
        logging.info("\n Değişiklikler Uygulanıyor...")
        results = sync.apply_2025_revision(dry_run=False)
        
        # Revizyon kaydı
        sync.record_revision_application(backup_path, results)
        
        # Rapor oluştur
        logging.info("\n Migrasyon Raporu Oluşturuluyor...")
        report_path = sync.generate_migration_report(analysis, results)
        
        logging.info("\n" + "=" * 60)
        logging.info(" SDG 2025 Revizyonu Başarıyla Uygulandı!")
        logging.info("\n Raporlar:")
        logging.info(f"  - Yedek: {backup_path}")
        if report_path:
            logging.info(f"  - Rapor: {report_path}")
    else:
        logging.info("\n İşlem iptal edildi.")

if __name__ == '__main__':
    main()
