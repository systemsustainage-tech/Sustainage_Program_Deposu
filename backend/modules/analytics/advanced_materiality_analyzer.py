#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
İleri Seviye Materialite Analizi
Paydaş önceliklendirme, işletme etkisi değerlendirmesi, matris görselleştirme
"""

import logging
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List
from config.database import DB_PATH
from backend.modules.prioritization.prioritization_manager import PrioritizationManager


@dataclass
class StakeholderWeight:
    """Paydaş ağırlık sınıfı"""
    stakeholder_type: str
    weight: float
    influence_level: str
    engagement_frequency: str

@dataclass
class BusinessImpact:
    """İşletme etkisi sınıfı"""
    topic_name: str
    financial_impact: float
    operational_impact: float
    reputational_impact: float
    regulatory_impact: float
    total_impact: float

class AdvancedMaterialityAnalyzer:
    """İleri Seviye Materialite Analizi Yöneticisi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        
        # Bağımlı tabloların varlığını garantiye al
        try:
            PrioritizationManager(db_path)
        except Exception as e:
            logging.error(f"PrioritizationManager baslatilamadi: {e}")

        self._init_advanced_tables()
        self._init_stakeholder_weights()

    def _init_advanced_tables(self) -> None:
        """İleri seviye materialite tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Paydaş ağırlık tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stakeholder_weights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    stakeholder_type TEXT NOT NULL,
                    weight REAL NOT NULL,
                    influence_level TEXT NOT NULL,
                    engagement_frequency TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # İşletme etkisi değerlendirmesi tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS business_impact_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    topic_id INTEGER NOT NULL,
                    assessment_year INTEGER NOT NULL,
                    financial_impact REAL NOT NULL,
                    operational_impact REAL NOT NULL,
                    reputational_impact REAL NOT NULL,
                    regulatory_impact REAL NOT NULL,
                    total_impact REAL NOT NULL,
                    assessment_method TEXT,
                    confidence_level TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (topic_id) REFERENCES materiality_topics(id)
                )
            """)

            # Paydaş önceliklendirme skorları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stakeholder_prioritization_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    topic_id INTEGER NOT NULL,
                    stakeholder_type TEXT NOT NULL,
                    priority_score REAL NOT NULL,
                    weighted_score REAL NOT NULL,
                    assessment_year INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (topic_id) REFERENCES materiality_topics(id)
                )
            """)

            # Materialite matrisi tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS materiality_matrix (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    topic_id INTEGER NOT NULL,
                    assessment_year INTEGER NOT NULL,
                    stakeholder_priority REAL NOT NULL,
                    business_impact REAL NOT NULL,
                    materiality_level TEXT NOT NULL,
                    quadrant TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (topic_id) REFERENCES materiality_topics(id)
                )
            """)

            # Otomatik materialite güncellemeleri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS materiality_updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    update_type TEXT NOT NULL,
                    previous_score REAL,
                    new_score REAL,
                    change_reason TEXT,
                    update_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            conn.commit()
            logging.info("[OK] İleri seviye materialite tablolari olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] İleri seviye materialite tablolari olusturulamadi: {e}")
        finally:
            conn.close()

    def _init_stakeholder_weights(self) -> None:
        """Varsayılan paydaş ağırlıklarını oluştur"""
        default_weights = [
            ("Müşteriler", 0.25, "Yüksek", "Günlük"),
            ("Çalışanlar", 0.20, "Yüksek", "Günlük"),
            ("Yatırımcılar", 0.15, "Yüksek", "Aylık"),
            ("Tedarikçiler", 0.12, "Orta", "Haftalık"),
            ("Yerel Toplum", 0.10, "Orta", "Aylık"),
            ("Regülatörler", 0.08, "Yüksek", "Çeyreklik"),
            ("Medya", 0.05, "Orta", "Haftalık"),
            ("Sivil Toplum", 0.03, "Düşük", "Aylık"),
            ("Rakip Firmalar", 0.02, "Düşük", "Çeyreklik")
        ]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            for stakeholder_type, weight, influence_level, engagement_frequency in default_weights:
                cursor.execute("""
                    INSERT OR IGNORE INTO stakeholder_weights 
                    (company_id, stakeholder_type, weight, influence_level, engagement_frequency)
                    VALUES (1, ?, ?, ?, ?)
                """, (stakeholder_type, weight, influence_level, engagement_frequency))

            conn.commit()
            logging.info("[OK] Varsayilan paydas agirliklari olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] Varsayilan paydas agirliklari olusturulamadi: {e}")
        finally:
            conn.close()

    def calculate_stakeholder_prioritization_scores(self, company_id: int, year: int = None) -> Dict[str, float]:
        """Paydaş önceliklendirme skorlarını hesapla"""
        if year is None:
            year = datetime.now().year

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Paydaş ağırlıklarını al
            cursor.execute("""
                SELECT stakeholder_type, weight, influence_level, engagement_frequency
                FROM stakeholder_weights 
                WHERE company_id = ?
            """, (company_id,))

            stakeholder_weights = cursor.fetchall()

            # Materialite konularını al
            cursor.execute("""
                SELECT id, topic_name FROM materiality_topics 
                WHERE company_id = ?
            """, (company_id,))

            topics = cursor.fetchall()

            prioritization_scores = {}

            for topic_id, topic_name in topics:
                topic_scores = {}

                for stakeholder_type, weight, influence_level, engagement_frequency in stakeholder_weights:
                    # Öncelik skorunu hesapla (1-10 arası)
                    base_score = self._calculate_base_priority_score(
                        stakeholder_type, influence_level, engagement_frequency
                    )

                    # Ağırlıklı skor
                    weighted_score = base_score * weight

                    topic_scores[stakeholder_type] = {
                        'base_score': base_score,
                        'weighted_score': weighted_score,
                        'weight': weight
                    }

                    # Veritabanına kaydet
                    cursor.execute("""
                        INSERT OR REPLACE INTO stakeholder_prioritization_scores
                        (company_id, topic_id, stakeholder_type, priority_score, weighted_score, assessment_year)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (company_id, topic_id, stakeholder_type, base_score, weighted_score, year))

                # Toplam ağırlıklı skor
                total_weighted_score = sum(score['weighted_score'] for score in topic_scores.values())
                prioritization_scores[topic_name] = {
                    'total_score': total_weighted_score,
                    'stakeholder_scores': topic_scores
                }

            conn.commit()
            return prioritization_scores

        except Exception as e:
            logging.error(f"[HATA] Paydas onceliklendirme skorlari hesaplanamadi: {e}")
            return {}
        finally:
            conn.close()

    def _calculate_base_priority_score(self, stakeholder_type: str, influence_level: str, engagement_frequency: str) -> float:
        """Temel öncelik skorunu hesapla"""
        # Etki seviyesi skoru
        influence_scores = {"Yüksek": 8, "Orta": 5, "Düşük": 2}
        influence_score = influence_scores.get(influence_level, 5)

        # Etkileşim sıklığı skoru
        frequency_scores = {"Günlük": 9, "Haftalık": 7, "Aylık": 5, "Çeyreklik": 3}
        frequency_score = frequency_scores.get(engagement_frequency, 5)

        # Paydaş tipine göre özel ağırlık
        stakeholder_multipliers = {
            "Müşteriler": 1.2,
            "Çalışanlar": 1.1,
            "Yatırımcılar": 1.0,
            "Tedarikçiler": 0.9,
            "Yerel Toplum": 0.8,
            "Regülatörler": 1.3,
            "Medya": 0.7,
            "Sivil Toplum": 0.6,
            "Rakip Firmalar": 0.5
        }

        multiplier = stakeholder_multipliers.get(stakeholder_type, 1.0)

        # Final skor (1-10 arası)
        base_score = (influence_score + frequency_score) / 2 * multiplier
        return min(max(base_score, 1.0), 10.0)

    def assess_business_impact(self, company_id: int, year: int = None) -> Dict[str, BusinessImpact]:
        """İşletme etkisi değerlendirmesi yap"""
        if year is None:
            year = datetime.now().year

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Materialite konularını al
            cursor.execute("""
                SELECT id, topic_name FROM materiality_topics 
                WHERE company_id = ?
            """, (company_id,))

            topics = cursor.fetchall()
            business_impacts = {}

            for topic_id, topic_name in topics:
                # Etki skorlarını hesapla (1-10 arası)
                financial_impact = self._calculate_financial_impact(topic_name)
                operational_impact = self._calculate_operational_impact(topic_name)
                reputational_impact = self._calculate_reputational_impact(topic_name)
                regulatory_impact = self._calculate_regulatory_impact(topic_name)

                # Toplam etki (ağırlıklı ortalama)
                total_impact = (
                    financial_impact * 0.3 +
                    operational_impact * 0.25 +
                    reputational_impact * 0.25 +
                    regulatory_impact * 0.2
                )

                business_impact = BusinessImpact(
                    topic_name=topic_name,
                    financial_impact=financial_impact,
                    operational_impact=operational_impact,
                    reputational_impact=reputational_impact,
                    regulatory_impact=regulatory_impact,
                    total_impact=total_impact
                )

                business_impacts[topic_name] = business_impact

                # Veritabanına kaydet
                cursor.execute("""
                    INSERT OR REPLACE INTO business_impact_assessments
                    (company_id, topic_id, assessment_year, financial_impact, operational_impact,
                     reputational_impact, regulatory_impact, total_impact, assessment_method, confidence_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (company_id, topic_id, year, financial_impact, operational_impact,
                      reputational_impact, regulatory_impact, total_impact, "Otomatik Hesaplama", "Yüksek"))

            conn.commit()
            return business_impacts

        except Exception as e:
            logging.error(f"[HATA] İsletme etkisi degerlendirmesi yapilamadi: {e}")
            return {}
        finally:
            conn.close()

    def _calculate_financial_impact(self, topic_name: str) -> float:
        """Finansal etki skorunu hesapla"""
        financial_keywords = {
            "maliyet": 8, "gelir": 7, "kar": 8, "yatırım": 6, "finansal": 7,
            "ekonomik": 6, "fiyat": 5, "bütçe": 6, "kâr": 8, "zarar": 9
        }

        topic_lower = topic_name.lower()
        max_score = 1.0

        for keyword, score in financial_keywords.items():
            if keyword in topic_lower:
                max_score = max(max_score, score)

        return max_score

    def _calculate_operational_impact(self, topic_name: str) -> float:
        """Operasyonel etki skorunu hesapla"""
        operational_keywords = {
            "üretim": 8, "operasyon": 7, "süreç": 6, "verimlilik": 7,
            "kalite": 8, "kapasite": 6, "lojistik": 5, "tedarik": 6,
            "dağıtım": 5, "hizmet": 6, "işletme": 7
        }

        topic_lower = topic_name.lower()
        max_score = 1.0

        for keyword, score in operational_keywords.items():
            if keyword in topic_lower:
                max_score = max(max_score, score)

        return max_score

    def _calculate_reputational_impact(self, topic_name: str) -> float:
        """İtibar etkisi skorunu hesapla"""
        reputational_keywords = {
            "itibar": 9, "marka": 8, "güven": 8, "şeffaflık": 7,
            "etik": 8, "sosyal": 7, "çevre": 8, "sürdürülebilirlik": 8,
            "sorumluluk": 7, "değer": 6, "kültür": 6
        }

        topic_lower = topic_name.lower()
        max_score = 1.0

        for keyword, score in reputational_keywords.items():
            if keyword in topic_lower:
                max_score = max(max_score, score)

        return max_score

    def _calculate_regulatory_impact(self, topic_name: str) -> float:
        """Regülatif etki skorunu hesapla"""
        regulatory_keywords = {
            "yasal": 8, "mevzuat": 8, "düzenleme": 7, "uyum": 7,
            "denetim": 8, "sertifika": 6, "standart": 7, "kural": 6,
            "politika": 6, "yönetmelik": 8, "kanun": 9
        }

        topic_lower = topic_name.lower()
        max_score = 1.0

        for keyword, score in regulatory_keywords.items():
            if keyword in topic_lower:
                max_score = max(max_score, score)

        return max_score

    def get_materiality_summary(self, company_id: int) -> Dict[str, Any]:
        """Materialite özeti getir (web_app uyumluluğu için)"""
        try:
            # Matris verilerini oluştur
            matrix_result = self.generate_materiality_matrix(company_id)
            
            # Web app'in beklediği formata dönüştür
            return {
                'total_topics': matrix_result.get('total_topics', 0),
                'high_materiality_count': matrix_result.get('high_materiality', 0),
                'medium_materiality_count': matrix_result.get('medium_materiality', 0),
                'low_materiality_count': matrix_result.get('low_materiality', 0),
                'matrix_data': matrix_result.get('matrix_data', [])
            }
        except Exception as e:
            logging.error(f"Materialite özeti hatası: {e}")
            return {
                'total_topics': 0,
                'high_materiality_count': 0,
                'medium_materiality_count': 0,
                'low_materiality_count': 0,
                'matrix_data': []
            }

    def generate_materiality_matrix(self, company_id: int, year: int = None) -> Dict[str, Any]:
        """Materialite matrisi oluştur"""
        if year is None:
            year = datetime.now().year

        # Paydaş önceliklendirme skorlarını al
        stakeholder_scores = self.calculate_stakeholder_prioritization_scores(company_id, year)

        # İşletme etkisi değerlendirmesini al
        business_impacts = self.assess_business_impact(company_id, year)

        # Matris verilerini hazırla
        matrix_data = []

        for topic_name, stakeholder_data in stakeholder_scores.items():
            if topic_name in business_impacts:
                stakeholder_priority = stakeholder_data['total_score']
                business_impact = business_impacts[topic_name].total_impact

                # Materialite seviyesini belirle
                materiality_level = self._determine_materiality_level(stakeholder_priority, business_impact)
                quadrant = self._determine_quadrant(stakeholder_priority, business_impact)

                matrix_data.append({
                    'topic_name': topic_name,
                    'stakeholder_priority': stakeholder_priority,
                    'business_impact': business_impact,
                    'materiality_level': materiality_level,
                    'quadrant': quadrant
                })

                # Veritabanına kaydet
                self._save_materiality_matrix_entry(company_id, topic_name, year,
                                                  stakeholder_priority, business_impact,
                                                  materiality_level, quadrant)

        return {
            'matrix_data': matrix_data,
            'year': year,
            'total_topics': len(matrix_data),
            'high_materiality': len([d for d in matrix_data if d['materiality_level'] == 'Yüksek']),
            'medium_materiality': len([d for d in matrix_data if d['materiality_level'] == 'Orta']),
            'low_materiality': len([d for d in matrix_data if d['materiality_level'] == 'Düşük'])
        }

    def _determine_materiality_level(self, stakeholder_priority: float, business_impact: float) -> str:
        """Materialite seviyesini belirle"""
        # Ortalama skor
        average_score = (stakeholder_priority + business_impact) / 2

        if average_score >= 7.5:
            return "Yüksek"
        elif average_score >= 5.0:
            return "Orta"
        else:
            return "Düşük"

    def _determine_quadrant(self, stakeholder_priority: float, business_impact: float) -> str:
        """Quadrant'ı belirle"""
        if stakeholder_priority >= 5 and business_impact >= 5:
            return "Yüksek Öncelik"
        elif stakeholder_priority >= 5 and business_impact < 5:
            return "Paydaş Odaklı"
        elif stakeholder_priority < 5 and business_impact >= 5:
            return "İşletme Odaklı"
        else:
            return "Düşük Öncelik"

    def _save_materiality_matrix_entry(self, company_id: int, topic_name: str, year: int,
                                     stakeholder_priority: float, business_impact: float,
                                     materiality_level: str, quadrant: str) -> None:
        """Materialite matrisi girişini kaydet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Topic ID'yi al
            cursor.execute("""
                SELECT id FROM materiality_topics 
                WHERE company_id = ? AND topic_name = ?
            """, (company_id, topic_name))

            result = cursor.fetchone()
            if result:
                topic_id = result[0]

                cursor.execute("""
                    INSERT OR REPLACE INTO materiality_matrix
                    (company_id, topic_id, assessment_year, stakeholder_priority, business_impact,
                     materiality_level, quadrant)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (company_id, topic_id, year, stakeholder_priority, business_impact,
                      materiality_level, quadrant))

                conn.commit()

        except Exception as e:
            logging.error(f"[HATA] Materialite matrisi kaydedilemedi: {e}")
        finally:
            conn.close()

    def get_automatic_materiality_topics(self, company_id: int) -> List[str]:
        """Otomatik materialite konu belirleme"""
        # Sektör bazlı önerilen konular
        sector_topics = {
            "Teknoloji": [
                "Veri Gizliliği ve Güvenliği",
                "Yapay Zeka Etik Kuralları",
                "Dijital Erişilebilirlik",
                "E-atık Yönetimi",
                "Enerji Verimliliği",
                "İnsan Hakları ve Çalışma Koşulları"
            ],
            "Üretim": [
                "Çevresel Etki",
                "İş Sağlığı ve Güvenliği",
                "Tedarik Zinciri Sürdürülebilirliği",
                "Su Yönetimi",
                "Atık Azaltma",
                "Enerji Verimliliği"
            ],
            "Finans": [
                "Finansal Şeffaflık",
                "Risk Yönetimi",
                "Müşteri Koruma",
                "Dijital Güvenlik",
                "Sürdürülebilir Yatırım",
                "Etik Yatırım"
            ]
        }

        # Varsayılan olarak tüm sektörlerden konuları al
        all_topics = []
        for topics in sector_topics.values():
            all_topics.extend(topics)

        return list(set(all_topics))  # Tekrarları kaldır

    def update_materiality_annually(self, company_id: int, year: int) -> Dict[str, Any]:
        """Yıllık materialite güncellemesi"""
        try:
            # Önceki yıl verilerini al
            prev_year = year - 1
            current_matrix = self.generate_materiality_matrix(company_id, year)

            # Değişiklikleri analiz et
            changes = self._analyze_materiality_changes(company_id, prev_year, year)

            # Güncelleme kaydı oluştur
            self._log_materiality_update(company_id, "Yıllık Güncelleme",
                                       changes['previous_avg_score'],
                                       changes['current_avg_score'],
                                       f"Yıllık materialite güncellemesi - {year}")

            return {
                'current_matrix': current_matrix,
                'changes': changes,
                'update_status': 'Başarılı',
                'update_date': datetime.now().isoformat()
            }

        except Exception as e:
            logging.error(f"[HATA] Yillik materialite guncellemesi yapilamadi: {e}")
            return {'update_status': 'Hatalı', 'error': str(e)}

    def _analyze_materiality_changes(self, company_id: int, prev_year: int, current_year: int) -> Dict[str, Any]:
        """Materialite değişikliklerini analiz et"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Önceki yıl verilerini al
            cursor.execute("""
                SELECT topic_name, stakeholder_priority, business_impact, materiality_level
                FROM materiality_matrix 
                WHERE company_id = ? AND assessment_year = ?
            """, (company_id, prev_year))

            prev_data = {row[0]: {'stakeholder_priority': row[1], 'business_impact': row[2], 'materiality_level': row[3]}
                        for row in cursor.fetchall()}

            # Mevcut yıl verilerini al
            cursor.execute("""
                SELECT topic_name, stakeholder_priority, business_impact, materiality_level
                FROM materiality_matrix 
                WHERE company_id = ? AND assessment_year = ?
            """, (company_id, current_year))

            current_data = {row[0]: {'stakeholder_priority': row[1], 'business_impact': row[2], 'materiality_level': row[3]}
                           for row in cursor.fetchall()}

            # Değişiklikleri hesapla
            changes = {
                'new_topics': [],
                'removed_topics': [],
                'priority_changes': [],
                'level_changes': [],
                'previous_avg_score': 0,
                'current_avg_score': 0
            }

            # Yeni konular
            changes['new_topics'] = [topic for topic in current_data.keys() if topic not in prev_data]

            # Kaldırılan konular
            changes['removed_topics'] = [topic for topic in prev_data.keys() if topic not in current_data]

            # Ortak konulardaki değişiklikler
            common_topics = set(prev_data.keys()) & set(current_data.keys())

            for topic in common_topics:
                prev_score = (prev_data[topic]['stakeholder_priority'] + prev_data[topic]['business_impact']) / 2
                current_score = (current_data[topic]['stakeholder_priority'] + current_data[topic]['business_impact']) / 2

                if abs(current_score - prev_score) > 1.0:  # Önemli değişiklik
                    changes['priority_changes'].append({
                        'topic': topic,
                        'previous_score': prev_score,
                        'current_score': current_score,
                        'change': current_score - prev_score
                    })

                if prev_data[topic]['materiality_level'] != current_data[topic]['materiality_level']:
                    changes['level_changes'].append({
                        'topic': topic,
                        'previous_level': prev_data[topic]['materiality_level'],
                        'current_level': current_data[topic]['materiality_level']
                    })

            # Ortalama skorları hesapla
            if prev_data:
                changes['previous_avg_score'] = sum(
                    (data['stakeholder_priority'] + data['business_impact']) / 2
                    for data in prev_data.values()
                ) / len(prev_data)

            if current_data:
                changes['current_avg_score'] = sum(
                    (data['stakeholder_priority'] + data['business_impact']) / 2
                    for data in current_data.values()
                ) / len(current_data)

            return changes

        except Exception as e:
            logging.error(f"[HATA] Materialite degisiklikleri analiz edilemedi: {e}")
            return {}
        finally:
            conn.close()

    def _log_materiality_update(self, company_id: int, update_type: str,
                               previous_score: float, new_score: float, change_reason: str) -> None:
        """Materialite güncelleme kaydını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO materiality_updates
                (company_id, update_type, previous_score, new_score, change_reason, updated_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, update_type, previous_score, new_score, change_reason, "Sistem"))

            conn.commit()

        except Exception as e:
            logging.error(f"[HATA] Materialite guncelleme kaydi olusturulamadi: {e}")
        finally:
            conn.close()

    def get_materiality_summary(self, company_id: int, year: int = None) -> Dict[str, Any]:
        """Materialite özetini al"""
        if year is None:
            year = datetime.now().year

        matrix_data = self.generate_materiality_matrix(company_id, year)

        return {
            'year': year,
            'total_topics': matrix_data['total_topics'],
            'high_materiality_count': matrix_data['high_materiality'],
            'medium_materiality_count': matrix_data['medium_materiality'],
            'low_materiality_count': matrix_data['low_materiality'],
            'matrix_data': matrix_data['matrix_data'],
            'quadrant_distribution': self._get_quadrant_distribution(matrix_data['matrix_data'])
        }

    def _get_quadrant_distribution(self, matrix_data: List[Dict]) -> Dict[str, int]:
        """Quadrant dağılımını hesapla"""
        distribution = {
            "Yüksek Öncelik": 0,
            "Paydaş Odaklı": 0,
            "İşletme Odaklı": 0,
            "Düşük Öncelik": 0
        }

        for data in matrix_data:
            quadrant = data['quadrant']
            if quadrant in distribution:
                distribution[quadrant] += 1

        return distribution
