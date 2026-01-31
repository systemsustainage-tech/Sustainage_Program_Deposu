#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Risk ve Fırsatlar Yöneticisi
Sürdürülebilirlik riskleri ve fırsatları yönetimi
"""

import logging
import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List


class RiskOpportunityManager:
    """Risk ve fırsatlar yöneticisi"""

    def __init__(self, db_path: str = None) -> None:
        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Gerekli tabloları oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Riskler tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sustainability_risks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    risk_title TEXT NOT NULL,
                    description TEXT,
                    risk_category TEXT NOT NULL, -- 'environmental', 'social', 'economic', 'governance', 'operational'
                    risk_type TEXT NOT NULL, -- 'strategic', 'operational', 'financial', 'compliance', 'reputational'
                    impact_level TEXT NOT NULL, -- 'low', 'medium', 'high', 'critical'
                    probability_level TEXT NOT NULL, -- 'low', 'medium', 'high', 'very_high'
                    risk_score INTEGER, -- calculated from impact * probability
                    potential_impact TEXT,
                    root_causes TEXT, -- JSON array
                    affected_stakeholders TEXT, -- JSON array
                    current_controls TEXT, -- JSON array
                    mitigation_measures TEXT, -- JSON array
                    responsible_department TEXT,
                    risk_owner TEXT,
                    assessment_date TEXT NOT NULL,
                    next_assessment_date TEXT,
                    status TEXT DEFAULT 'active', -- 'active', 'mitigated', 'closed', 'transferred'
                    created_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT
                )
            """)

            # Fırsatlar tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sustainability_opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    opportunity_title TEXT NOT NULL,
                    description TEXT,
                    opportunity_category TEXT NOT NULL, -- 'environmental', 'social', 'economic', 'governance'
                    opportunity_type TEXT NOT NULL, -- 'innovation', 'market', 'partnership', 'efficiency', 'reputation'
                    potential_value TEXT, -- monetary or qualitative
                    probability_level TEXT NOT NULL, -- 'low', 'medium', 'high', 'very_high'
                    implementation_effort TEXT NOT NULL, -- 'low', 'medium', 'high'
                    opportunity_score INTEGER, -- calculated from value * probability / effort
                    expected_benefits TEXT,
                    required_resources TEXT, -- JSON array
                    implementation_plan TEXT, -- JSON array
                    success_metrics TEXT, -- JSON array
                    responsible_department TEXT,
                    opportunity_owner TEXT,
                    assessment_date TEXT NOT NULL,
                    target_implementation_date TEXT,
                    status TEXT DEFAULT 'identified', -- 'identified', 'evaluating', 'implementing', 'realized', 'cancelled'
                    created_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT
                )
            """)

            # Risk değerlendirmeleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS risk_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    risk_id INTEGER NOT NULL,
                    assessment_date TEXT NOT NULL,
                    assessor_name TEXT NOT NULL,
                    impact_level TEXT NOT NULL,
                    probability_level TEXT NOT NULL,
                    risk_score INTEGER NOT NULL,
                    assessment_rationale TEXT,
                    new_mitigation_measures TEXT, -- JSON array
                    status_change TEXT, -- if any
                    next_assessment_date TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (risk_id) REFERENCES sustainability_risks(id)
                )
            """)

            # Fırsat değerlendirmeleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS opportunity_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    opportunity_id INTEGER NOT NULL,
                    assessment_date TEXT NOT NULL,
                    assessor_name TEXT NOT NULL,
                    potential_value TEXT,
                    probability_level TEXT NOT NULL,
                    implementation_effort TEXT NOT NULL,
                    opportunity_score INTEGER NOT NULL,
                    assessment_rationale TEXT,
                    implementation_progress TEXT, -- percentage
                    status_change TEXT, -- if any
                    next_assessment_date TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (opportunity_id) REFERENCES sustainability_opportunities(id)
                )
            """)

            # Risk-Fırsat matrisi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS risk_opportunity_matrix (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    matrix_name TEXT NOT NULL,
                    description TEXT,
                    matrix_data TEXT NOT NULL, -- JSON matrix data
                    assessment_date TEXT NOT NULL,
                    created_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logging.info("[OK] Risk ve fırsat tabloları hazır")

        except Exception as e:
            logging.error(f"[HATA] Tablo oluşturma hatası: {e}")
        finally:
            conn.close()

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        stats = {
            'total_risks': 0,
            'high_risks': 0,
            'total_opportunities': 0,
            'high_value_opportunities': 0
        }
        try:
            cursor.execute("SELECT COUNT(*) FROM sustainability_risks WHERE company_id = ? AND status = 'active'", (company_id,))
            stats['total_risks'] = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM sustainability_risks WHERE company_id = ? AND status = 'active' AND (risk_score >= 9 OR impact_level IN ('high', 'critical'))", (company_id,))
            stats['high_risks'] = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM sustainability_opportunities WHERE company_id = ? AND status != 'cancelled'", (company_id,))
            stats['total_opportunities'] = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM sustainability_opportunities WHERE company_id = ? AND status != 'cancelled' AND (opportunity_score >= 9 OR potential_value IN ('high', 'very_high'))", (company_id,))
            stats['high_value_opportunities'] = cursor.fetchone()[0] or 0
            
            return stats
        except Exception as e:
            logging.error(f"Risk/Fırsat istatistikleri getirme hatası: {e}")
            return stats
        finally:
            conn.close()

    def calculate_risk_score(self, impact_level: str, probability_level: str) -> int:
        """Risk skorunu hesapla"""
        impact_scores = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        probability_scores = {'low': 1, 'medium': 2, 'high': 3, 'very_high': 4}

        impact_score = impact_scores.get(impact_level.lower(), 1)
        probability_score = probability_scores.get(probability_level.lower(), 1)

        return impact_score * probability_score

    def calculate_opportunity_score(self, potential_value: str, probability_level: str, implementation_effort: str) -> int:
        """Fırsat skorunu hesapla"""
        value_scores = {'low': 1, 'medium': 2, 'high': 3, 'very_high': 4}
        probability_scores = {'low': 1, 'medium': 2, 'high': 3, 'very_high': 4}
        effort_scores = {'low': 4, 'medium': 3, 'high': 2, 'very_high': 1}

        value_score = value_scores.get(potential_value.lower(), 1)
        probability_score = probability_scores.get(probability_level.lower(), 1)
        effort_score = effort_scores.get(implementation_effort.lower(), 1)

        return (value_score * probability_score * effort_score) // 2

    def create_risk(self, company_id: int, risk_title: str, description: str = "",
                   risk_category: str = "environmental", risk_type: str = "operational",
                   impact_level: str = "medium", probability_level: str = "medium",
                   potential_impact: str = "", root_causes: List[str] = None,
                   affected_stakeholders: List[str] = None, current_controls: List[str] = None,
                   mitigation_measures: List[str] = None, responsible_department: str = "",
                   risk_owner: str = "", created_by: int = None) -> int:
        """
        Yeni risk kaydı oluştur
        
        Args:
            company_id: Şirket ID
            risk_title: Risk başlığı
            description: Açıklama
            risk_category: Risk kategorisi
            risk_type: Risk türü
            impact_level: Etki seviyesi
            probability_level: Olasılık seviyesi
            potential_impact: Potansiyel etki
            root_causes: Kök nedenler listesi
            affected_stakeholders: Etkilenen paydaşlar listesi
            current_controls: Mevcut kontroller listesi
            mitigation_measures: Azaltma önlemleri listesi
            responsible_department: Sorumlu departman
            risk_owner: Risk sahibi
            created_by: Oluşturan kullanıcı ID
        
        Returns:
            Oluşturulan risk ID'si
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Risk skorunu hesapla
            risk_score = self.calculate_risk_score(impact_level, probability_level)

            # Sonraki değerlendirme tarihini hesapla (6 ay sonra)
            next_assessment = (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')

            cursor.execute("""
                INSERT INTO sustainability_risks 
                (company_id, risk_title, description, risk_category, risk_type, 
                 impact_level, probability_level, risk_score, potential_impact,
                 root_causes, affected_stakeholders, current_controls, mitigation_measures,
                 responsible_department, risk_owner, assessment_date, next_assessment_date, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, risk_title, description, risk_category, risk_type,
                impact_level, probability_level, risk_score, potential_impact,
                json.dumps(root_causes or []),
                json.dumps(affected_stakeholders or []),
                json.dumps(current_controls or []),
                json.dumps(mitigation_measures or []),
                responsible_department, risk_owner,
                datetime.now().strftime('%Y-%m-%d'),
                next_assessment,
                created_by
            ))

            risk_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] Risk kaydı oluşturuldu: {risk_title} (ID: {risk_id}, Skor: {risk_score})")
            return risk_id

        except Exception as e:
            conn.rollback()
            logging.error(f"[HATA] Risk oluşturma hatası: {e}")
            raise
        finally:
            conn.close()

    def create_opportunity(self, company_id: int, opportunity_title: str, description: str = "",
                          opportunity_category: str = "environmental", opportunity_type: str = "innovation",
                          potential_value: str = "medium", probability_level: str = "medium",
                          implementation_effort: str = "medium", expected_benefits: str = "",
                          required_resources: List[str] = None, implementation_plan: List[str] = None,
                          success_metrics: List[str] = None, responsible_department: str = "",
                          opportunity_owner: str = "", target_implementation_date: str = None,
                          created_by: int = None) -> int:
        """
        Yeni fırsat kaydı oluştur
        
        Args:
            company_id: Şirket ID
            opportunity_title: Fırsat başlığı
            description: Açıklama
            opportunity_category: Fırsat kategorisi
            opportunity_type: Fırsat türü
            potential_value: Potansiyel değer
            probability_level: Olasılık seviyesi
            implementation_effort: Uygulama çabası
            expected_benefits: Beklenen faydalar
            required_resources: Gerekli kaynaklar listesi
            implementation_plan: Uygulama planı listesi
            success_metrics: Başarı metrikleri listesi
            responsible_department: Sorumlu departman
            opportunity_owner: Fırsat sahibi
            target_implementation_date: Hedef uygulama tarihi
            created_by: Oluşturan kullanıcı ID
        
        Returns:
            Oluşturulan fırsat ID'si
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Fırsat skorunu hesapla
            opportunity_score = self.calculate_opportunity_score(potential_value, probability_level, implementation_effort)

            cursor.execute("""
                INSERT INTO sustainability_opportunities 
                (company_id, opportunity_title, description, opportunity_category, opportunity_type,
                 potential_value, probability_level, implementation_effort, opportunity_score,
                 expected_benefits, required_resources, implementation_plan, success_metrics,
                 responsible_department, opportunity_owner, assessment_date, target_implementation_date, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, opportunity_title, description, opportunity_category, opportunity_type,
                potential_value, probability_level, implementation_effort, opportunity_score,
                expected_benefits,
                json.dumps(required_resources or []),
                json.dumps(implementation_plan or []),
                json.dumps(success_metrics or []),
                responsible_department, opportunity_owner,
                datetime.now().strftime('%Y-%m-%d'),
                target_implementation_date,
                created_by
            ))

            opportunity_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] Fırsat kaydı oluşturuldu: {opportunity_title} (ID: {opportunity_id}, Skor: {opportunity_score})")
            return opportunity_id

        except Exception as e:
            conn.rollback()
            logging.error(f"[HATA] Fırsat oluşturma hatası: {e}")
            raise
        finally:
            conn.close()

    def get_risks(self, company_id: int, risk_category: str = None, status: str = None) -> List[Dict]:
        """Riskleri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            query = """
                SELECT * FROM sustainability_risks 
                WHERE company_id = ?
            """
            params = [company_id]

            if risk_category:
                query += " AND risk_category = ?"
                params.append(risk_category)

            if status:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY risk_score DESC, created_at DESC"

            cursor.execute(query, params)
            results = cursor.fetchall()

            risks = []
            for row in results:
                risks.append({
                    'id': row[0], 'company_id': row[1], 'risk_title': row[2], 'description': row[3],
                    'risk_category': row[4], 'risk_type': row[5], 'impact_level': row[6],
                    'probability_level': row[7], 'risk_score': row[8], 'potential_impact': row[9],
                    'root_causes': json.loads(row[10] or '[]'),
                    'affected_stakeholders': json.loads(row[11] or '[]'),
                    'current_controls': json.loads(row[12] or '[]'),
                    'mitigation_measures': json.loads(row[13] or '[]'),
                    'responsible_department': row[14], 'risk_owner': row[15],
                    'assessment_date': row[16], 'next_assessment_date': row[17],
                    'status': row[18], 'created_by': row[19], 'created_at': row[20], 'updated_at': row[21]
                })

            return risks

        except Exception as e:
            logging.error(f"[HATA] Riskler getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def get_opportunities(self, company_id: int, opportunity_category: str = None, status: str = None) -> List[Dict]:
        """Fırsatları getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            query = """
                SELECT * FROM sustainability_opportunities 
                WHERE company_id = ?
            """
            params = [company_id]

            if opportunity_category:
                query += " AND opportunity_category = ?"
                params.append(opportunity_category)

            if status:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY opportunity_score DESC, created_at DESC"

            cursor.execute(query, params)
            results = cursor.fetchall()

            opportunities = []
            for row in results:
                opportunities.append({
                    'id': row[0], 'company_id': row[1], 'opportunity_title': row[2], 'description': row[3],
                    'opportunity_category': row[4], 'opportunity_type': row[5], 'potential_value': row[6],
                    'probability_level': row[7], 'implementation_effort': row[8], 'opportunity_score': row[9],
                    'expected_benefits': row[10], 'required_resources': json.loads(row[11] or '[]'),
                    'implementation_plan': json.loads(row[12] or '[]'),
                    'success_metrics': json.loads(row[13] or '[]'),
                    'responsible_department': row[14], 'opportunity_owner': row[15],
                    'assessment_date': row[16], 'target_implementation_date': row[17],
                    'status': row[18], 'created_by': row[19], 'created_at': row[20], 'updated_at': row[21]
                })

            return opportunities

        except Exception as e:
            logging.error(f"[HATA] Fırsatlar getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def create_default_risks_opportunities(self, company_id: int, created_by: int = 1) -> None:
        """Varsayılan riskler ve fırsatlar oluştur"""
        try:
            # Varsayılan riskler
            default_risks = [
                {
                    'risk_title': 'İklim Değişikliği Riski',
                    'description': 'Aşırı hava olayları ve iklim değişikliği etkileri',
                    'risk_category': 'environmental',
                    'risk_type': 'strategic',
                    'impact_level': 'high',
                    'probability_level': 'high',
                    'potential_impact': 'Operasyonel kesintiler, maliyet artışları',
                    'root_causes': ['Küresel iklim değişikliği', 'Yetersiz adaptasyon planları'],
                    'affected_stakeholders': ['Çalışanlar', 'Müşteriler', 'Tedarikçiler', 'Toplum'],
                    'mitigation_measures': ['İklim risk analizi', 'Adaptasyon planları', 'Yeşil enerji geçişi'],
                    'responsible_department': 'Çevre',
                    'risk_owner': 'Çevre Müdürü'
                },
                {
                    'risk_title': 'Sosyal Sorumluluk Riski',
                    'description': 'İş güvenliği ve sosyal haklar ihlali riski',
                    'risk_category': 'social',
                    'risk_type': 'reputational',
                    'impact_level': 'critical',
                    'probability_level': 'medium',
                    'potential_impact': 'Marka değeri kaybı, yasal sorunlar',
                    'root_causes': ['Eğitim eksiklikleri', 'Kontrol mekanizmaları yetersizliği'],
                    'affected_stakeholders': ['Çalışanlar', 'Müşteriler', 'Yatırımcılar'],
                    'mitigation_measures': ['İSG eğitimleri', 'Denetim sistemleri', 'Şeffaf raporlama'],
                    'responsible_department': 'İnsan Kaynakları',
                    'risk_owner': 'İK Müdürü'
                },
                {
                    'risk_title': 'Tedarik Zinciri Riski',
                    'description': 'Tedarikçi sürdürülebilirlik standartları riski',
                    'risk_category': 'operational',
                    'risk_type': 'operational',
                    'impact_level': 'high',
                    'probability_level': 'medium',
                    'potential_impact': 'Tedarik kesintileri, kalite sorunları',
                    'root_causes': ['Tedarikçi denetimi eksikliği', 'Alternatif tedarikçi yokluğu'],
                    'affected_stakeholders': ['Müşteriler', 'Tedarikçiler', 'Toplum'],
                    'mitigation_measures': ['Tedarikçi değerlendirme', 'Çeşitlendirme', 'Sürdürülebilirlik standartları'],
                    'responsible_department': 'Satınalma',
                    'risk_owner': 'Satınalma Müdürü'
                }
            ]

            # Varsayılan fırsatlar
            default_opportunities = [
                {
                    'opportunity_title': 'Yeşil Enerji Geçişi',
                    'description': 'Yenilenebilir enerji kaynaklarına geçiş fırsatı',
                    'opportunity_category': 'environmental',
                    'opportunity_type': 'efficiency',
                    'potential_value': 'high',
                    'probability_level': 'high',
                    'implementation_effort': 'medium',
                    'expected_benefits': 'Enerji maliyetlerinde %30 tasarruf, karbon ayak izi azalması',
                    'required_resources': ['Yatırım bütçesi', 'Teknik uzmanlık', 'İzin süreçleri'],
                    'implementation_plan': ['Teknik fizibilite', 'Yatırım planı', 'Uygulama', 'İzleme'],
                    'success_metrics': ['Enerji maliyeti azalması', 'Karbon emisyon azalması', 'ROI'],
                    'responsible_department': 'Üretim',
                    'opportunity_owner': 'Üretim Müdürü'
                },
                {
                    'opportunity_title': 'Döngüsel Ekonomi Modeli',
                    'description': 'Atık yönetimi ve döngüsel ekonomi uygulamaları',
                    'opportunity_category': 'economic',
                    'opportunity_type': 'innovation',
                    'potential_value': 'medium',
                    'probability_level': 'medium',
                    'implementation_effort': 'high',
                    'expected_benefits': 'Atık maliyetlerinde azalma, yeni gelir kaynakları',
                    'required_resources': ['Teknoloji yatırımı', 'Eğitim', 'İş süreci değişikliği'],
                    'implementation_plan': ['Atık analizi', 'Teknoloji seçimi', 'Pilot uygulama', 'Yaygınlaştırma'],
                    'success_metrics': ['Atık azalması', 'Maliyet tasarrufu', 'Yeni gelir'],
                    'responsible_department': 'Çevre',
                    'opportunity_owner': 'Çevre Müdürü'
                },
                {
                    'opportunity_title': 'Dijital Sürdürülebilirlik Platformu',
                    'description': 'Dijital araçlarla sürdürülebilirlik yönetimi',
                    'opportunity_category': 'governance',
                    'opportunity_type': 'innovation',
                    'potential_value': 'high',
                    'probability_level': 'high',
                    'implementation_effort': 'medium',
                    'expected_benefits': 'Verimlilik artışı, şeffaflık, raporlama kolaylığı',
                    'required_resources': ['Yazılım geliştirme', 'Eğitim', 'Veri entegrasyonu'],
                    'implementation_plan': ['İhtiyaç analizi', 'Geliştirme', 'Test', 'Uygulama'],
                    'success_metrics': ['Süreç hızı', 'Veri kalitesi', 'Kullanıcı memnuniyeti'],
                    'responsible_department': 'IT',
                    'opportunity_owner': 'IT Müdürü'
                }
            ]

            # Riskleri oluştur
            for risk_data in default_risks:
                self.create_risk(company_id=company_id, created_by=created_by, **risk_data)

            # Fırsatları oluştur
            for opp_data in default_opportunities:
                self.create_opportunity(company_id=company_id, created_by=created_by, **opp_data)

            logging.info(f"[OK] {len(default_risks)} risk ve {len(default_opportunities)} fırsat oluşturuldu")

        except Exception as e:
            logging.error(f"[HATA] Varsayılan risk/fırsat oluşturma hatası: {e}")


if __name__ == "__main__":
    # Test
    manager = RiskOpportunityManager()
    manager.create_default_risks_opportunities(company_id=1, created_by=1)

    # Riskleri listele
    risks = manager.get_risks(company_id=1)
    logging.info(f"Toplam {len(risks)} risk bulundu:")
    for risk in risks:
        logging.info(f"- {risk['risk_title']} (Skor: {risk['risk_score']})")

    # Fırsatları listele
    opportunities = manager.get_opportunities(company_id=1)
    logging.info(f"Toplam {len(opportunities)} fırsat bulundu:")
    for opp in opportunities:
        logging.info(f"- {opp['opportunity_title']} (Skor: {opp['opportunity_score']})")
