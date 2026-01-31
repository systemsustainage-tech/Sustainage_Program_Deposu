#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SASB Manager - Backend İş Mantığı
- Sektör yönetimi
- Metrik yönetimi
- SASB-GRI mapping
- Veri import/export
"""

import logging
import json
import os
import sqlite3
from typing import Dict, List, Optional
from config.database import DB_PATH


class SASBManager:
    """SASB Modülü Backend Manager"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        """Init"""
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)

        self.db_path = db_path
        self.module_dir = os.path.dirname(os.path.abspath(__file__))

        # Veritabanı başlat
        self.init_database()

        # Veri yükle
        self.load_sector_data()

    def init_database(self) -> None:
        """SASB tablolarını oluştur"""
        schema_path = os.path.join(self.module_dir, 'sasb_schema.sql')

        if not os.path.exists(schema_path):
            logging.info("️ SASB schema bulunamadı!")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = f.read()

            cursor.executescript(schema)
            conn.commit()
            logging.info("[OK] SASB tablolari olusturuldu")
        except Exception as e:
            logging.error(f"[HATA] Tablo olusturma hatasi: {e}")
        finally:
            conn.close()

    def load_sector_data(self) -> bool:
        """Sektör verilerini JSON'dan yükle (Yeni yapı - Data dizini)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            data_dir = os.path.join(self.module_dir, 'data')
            
            # 1. Sektörleri Yükle (sasb_sectors.json)
            sectors_file = os.path.join(data_dir, 'sasb_sectors.json')
            if os.path.exists(sectors_file):
                with open(sectors_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for sector in data.get('sasb_sectors', []):
                        cursor.execute("""
                            INSERT OR IGNORE INTO sasb_sectors 
                            (sector_code, sector_name, industry_group, description)
                            VALUES (?, ?, ?, ?)
                        """, (sector['sector_code'], sector['sector_name'], 
                              sector['industry_group'], sector.get('sector_description', '')))
            
            # GLOBAL Sektör (IFRS S1/S2 gibi genel standartlar için)
            cursor.execute("SELECT id FROM sasb_sectors WHERE sector_code = 'GLOBAL'")
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO sasb_sectors (sector_code, sector_name, industry_group, description) 
                    VALUES ('GLOBAL', 'Global Standards', 'General', 'Cross-industry standards like IFRS S1/S2')
                """)
            
            # 2. Topics Yükle (sasb_disclosure_topics.json)
            topics_file = os.path.join(data_dir, 'sasb_disclosure_topics.json')
            if os.path.exists(topics_file):
                with open(topics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for topic in data.get('sasb_disclosure_topics', []):
                        sector_code = topic.get('sector_code')
                        
                        # Sector ID bul
                        if sector_code == 'ALL':
                            cursor.execute("SELECT id FROM sasb_sectors WHERE sector_code = 'GLOBAL'")
                        else:
                            cursor.execute("SELECT id FROM sasb_sectors WHERE sector_code = ?", (sector_code,))
                        
                        res = cursor.fetchone()
                        if res:
                            sector_id = res[0]
                            
                            # Check existence
                            cursor.execute("SELECT id FROM sasb_disclosure_topics WHERE sector_id = ? AND topic_code = ?", (sector_id, topic['topic_code']))
                            if not cursor.fetchone():
                                cursor.execute("""
                                    INSERT INTO sasb_disclosure_topics 
                                    (sector_id, topic_code, topic_name, category, is_material, description)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                """, (sector_id, topic['topic_code'], topic['topic_name'],
                                     topic['topic_category'], topic['is_financial_material'], topic.get('topic_description', '')))

            # 3. Metrics Yükle (sasb_metrics.json)
            metrics_file = os.path.join(data_dir, 'sasb_metrics.json')
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for metric in data.get('sasb_metrics', []):
                         # Topic ID bul (Code ile)
                         cursor.execute("SELECT id FROM sasb_disclosure_topics WHERE topic_code = ?", (metric['topic_code'],))
                         topics = cursor.fetchall()
                         
                         for topic_row in topics:
                             topic_id = topic_row[0]
                             
                             # Check existence
                             cursor.execute("SELECT id FROM sasb_metrics WHERE disclosure_topic_id = ? AND metric_code = ?", (topic_id, metric['metric_code']))
                             if not cursor.fetchone():
                                 cursor.execute("""
                                    INSERT INTO sasb_metrics
                                    (disclosure_topic_id, metric_code, metric_name, metric_type, unit, reporting_guidance)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                """, (topic_id, metric['metric_code'], metric['metric_name'],
                                     metric['metric_type'], metric.get('unit_of_measure', ''), metric.get('calculation_method', '')))

            # 4. GRI Mapping (sasb_gri_mapping.json)
            mapping_file = os.path.join(data_dir, 'sasb_gri_mapping.json')
            if os.path.exists(mapping_file):
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    mappings_list = data.get('sasb_gri_mapping', data.get('sasb_gri_mappings', []))
                    for mapping in mappings_list:
                        # Key uyumlulugu
                        sasb_code = mapping.get('sasb_metric_code', mapping.get('sasb_code'))
                        gri_ind = mapping.get('gri_indicator', mapping.get('gri_disclosure'))
                        notes = mapping.get('mapping_notes', mapping.get('notes', ''))
                        
                        # Check existence
                        cursor.execute("SELECT id FROM sasb_gri_mapping WHERE sasb_metric_code = ? AND gri_disclosure = ?", (sasb_code, gri_ind))
                        if not cursor.fetchone():
                            cursor.execute("""
                                INSERT INTO sasb_gri_mapping 
                                (sasb_metric_code, gri_standard, gri_disclosure, mapping_strength, notes)
                                VALUES (?, ?, ?, ?, ?)
                            """, (sasb_code, mapping['gri_standard'], gri_ind, 
                                  mapping['mapping_strength'], notes))

            conn.commit()
            logging.info("[OK] SASB verileri yeni JSON yapisindan yuklendi (Data folder)")
            return True

        except Exception as e:
            logging.error(f"[HATA] SASB veri yukleme hatasi: {e}")
            return False
        finally:
            conn.close()

    def _import_sectors(self, cursor, sectors: List[Dict]) -> None:
        """Eski import metodu - Artik kullanilmiyor ama referans icin tutulabilir"""
        pass

    def get_all_sectors(self) -> List[Dict]:
        """Tüm sektörleri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, sector_code, sector_name, industry_group, description
                FROM sasb_sectors
                ORDER BY industry_group, sector_name
            """)

            sectors = []
            for row in cursor.fetchall():
                sectors.append({
                    'id': row[0],
                    'sector_code': row[1],
                    'sector_name': row[2],
                    'industry_group': row[3],
                    'description': row[4]
                })

            return sectors
        finally:
            conn.close()

    def get_sector_topics(self, sector_id: int) -> List[Dict]:
        """Sektör disclosure topics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, topic_code, topic_name, category, description
                FROM sasb_disclosure_topics
                WHERE sector_id = ? AND is_material = 1
                ORDER BY category, topic_name
            """, (sector_id,))

            topics = []
            for row in cursor.fetchall():
                topics.append({
                    'id': row[0],
                    'topic_code': row[1],
                    'topic_name': row[2],
                    'category': row[3],
                    'description': row[4]
                })

            return topics
        finally:
            conn.close()

    def get_topic_metrics(self, topic_id: int) -> List[Dict]:
        """Topic metrikleri"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, metric_code, metric_name, metric_type, unit, reporting_guidance
                FROM sasb_metrics
                WHERE disclosure_topic_id = ?
                ORDER BY metric_code
            """, (topic_id,))

            metrics = []
            for row in cursor.fetchall():
                metrics.append({
                    'id': row[0],
                    'metric_code': row[1],
                    'metric_name': row[2],
                    'metric_type': row[3],
                    'unit': row[4],
                    'reporting_guidance': row[5]
                })

            return metrics
        finally:
            conn.close()

    def select_company_sector(self, company_id: int, year: int, sector_id: int) -> bool:
        """Şirket sektörü seç"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO company_sasb_data (company_id, year, sector_id)
                VALUES (?, ?, ?)
            """, (company_id, year, sector_id))

            conn.commit()
            return True
        except Exception as e:
            logging.error(f"[HATA] Sektor secim hatasi: {e}")
            return False
        finally:
            conn.close()

    def save_metric_response(self, company_id: int, year: int, metric_id: int,
                            response_value: str, numerical_value: Optional[float] = None,
                            unit: Optional[str] = None, notes: Optional[str] = None) -> bool:
        """Metrik yanıtı kaydet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO sasb_metric_responses
                (company_id, year, metric_id, response_value, numerical_value, unit, notes, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (company_id, year, metric_id, response_value, numerical_value, unit, notes))

            conn.commit()
            return True
        except Exception as e:
            logging.error(f"[HATA] Yanit kaydetme hatasi: {e}")
            return False
        finally:
            conn.close()

    def get_sasb_gri_mappings(self) -> List[Dict]:
        """SASB-GRI mapping listesi"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT sasb_metric_code, gri_standard, gri_disclosure, 
                       mapping_strength, notes
                FROM sasb_gri_mapping
                ORDER BY sasb_metric_code
            """)

            mappings = []
            for row in cursor.fetchall():
                mappings.append({
                    'sasb_code': row[0],
                    'gri_standard': row[1],
                    'gri_disclosure': row[2],
                    'strength': row[3],
                    'notes': row[4]
                })

            return mappings
        finally:
            conn.close()

    def get_metric_responses(self, company_id: int, year: int) -> Dict:
        """Şirketin belirli bir yıldaki metrik yanıtlarını getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT metric_id, response_value, numerical_value, unit, notes
                FROM sasb_metric_responses
                WHERE company_id = ? AND year = ?
            """, (company_id, year))

            responses = {}
            for row in cursor.fetchall():
                responses[row[0]] = {
                    'response_value': row[1],
                    'numerical_value': row[2],
                    'unit': row[3],
                    'notes': row[4]
                }
            return responses
        finally:
            conn.close()

    def get_company_sector(self, company_id: int, year: int) -> Optional[Dict]:
        """Şirketin seçili sektörünü getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT s.id, s.sector_code, s.sector_name, s.industry_group
                FROM company_sasb_data csd
                JOIN sasb_sectors s ON csd.sector_id = s.id
                WHERE csd.company_id = ? AND csd.year = ?
            """, (company_id, year))

            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'sector_code': row[1],
                    'sector_name': row[2],
                    'industry_group': row[3]
                }
            return None
        finally:
            conn.close()

    def get_company_disclosures(self, company_id: int, year: int) -> List[Dict]:
        """Rapor için detaylı disclosure verilerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT 
                    dt.topic_code, dt.topic_name,
                    m.metric_code, m.metric_name, m.unit,
                    r.response_value, r.notes
                FROM sasb_metric_responses r
                JOIN sasb_metrics m ON r.metric_id = m.id
                JOIN sasb_disclosure_topics dt ON m.disclosure_topic_id = dt.id
                WHERE r.company_id = ? AND r.year = ?
                ORDER BY dt.topic_code, m.metric_code
            """, (company_id, year))

            disclosures = []
            for row in cursor.fetchall():
                disclosures.append({
                    'topic_code': row[0],
                    'topic_name': row[1],
                    'metric_code': row[2],
                    'metric_name': row[3],
                    'unit_of_measure': row[4],
                    'metric_value': row[5],
                    'notes': row[6],
                    'data_source': 'Manual Entry'
                })
            return disclosures
        finally:
            conn.close()

    def get_completion_status(self, company_id: int, year: int) -> Dict:
        """Tamamlanma durumu"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT s.sector_name, COUNT(DISTINCT m.id) as total_metrics,
                       COUNT(DISTINCT r.metric_id) as completed_metrics
                FROM company_sasb_data csd
                JOIN sasb_sectors s ON csd.sector_id = s.id
                LEFT JOIN sasb_disclosure_topics dt ON dt.sector_id = s.id
                LEFT JOIN sasb_metrics m ON m.disclosure_topic_id = dt.id
                LEFT JOIN sasb_metric_responses r ON r.metric_id = m.id 
                    AND r.company_id = csd.company_id AND r.year = csd.year
                WHERE csd.company_id = ? AND csd.year = ?
                GROUP BY s.sector_name
            """, (company_id, year))

            result = cursor.fetchone()
            if result:
                total = result[1] or 0
                completed = result[2] or 0
                percentage = (completed / total * 100) if total > 0 else 0

                return {
                    'sector': result[0],
                    'total_metrics': total,
                    'completed_metrics': completed,
                    'completion_percentage': round(percentage, 1)
                }

            return {'total_metrics': 0, 'completed_metrics': 0, 'completion_percentage': 0}
        finally:
            conn.close()


if __name__ == "__main__":
    # Test
    logging.info(" SASB Manager Test...")

    manager = SASBManager()

    # Sektörleri listele
    sectors = manager.get_all_sectors()
    logging.info(f"[OK] {len(sectors)} sektor yuklendi")

    # İlk 5 sektörü göster
    for i, sector in enumerate(sectors[:5], 1):
        logging.info(f"{i}. {sector['sector_code']} - {sector['sector_name']}")

    # GRI Mapping
    mappings = manager.get_sasb_gri_mappings()
    logging.info(f"[OK] {len(mappings)} SASB-GRI mapping")

    logging.info("[OK] Test tamamlandi!")
