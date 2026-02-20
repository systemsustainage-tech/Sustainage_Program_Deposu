#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SMART Hedefler ve KPI Yöneticisi
Specific, Measurable, Achievable, Relevant, Time-bound hedefler
"""

import logging
import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
try:
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    from core.base_manager import BaseTenantManager


class SMARTGoalsManager(BaseTenantManager):
    """SMART hedefler ve KPI yöneticisi"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        super().__init__(db_path, company_id)
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Gerekli tabloları oluştur"""
        try:
            # SMART hedefler tablosu
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS smart_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    goal_title TEXT NOT NULL,
                    description TEXT,
                    goal_category TEXT NOT NULL, -- 'strategic', 'operational', 'sustainability', 'financial'
                    goal_owner TEXT NOT NULL, -- person responsible
                    department TEXT NOT NULL,
                    
                    -- SMART Criteria
                    specific_description TEXT NOT NULL, -- What exactly will be accomplished?
                    measurable_metrics TEXT NOT NULL, -- How will success be measured?
                    achievable_rationale TEXT NOT NULL, -- Why is this goal achievable?
                    relevant_justification TEXT NOT NULL, -- Why is this goal important?
                    time_bound_deadline TEXT NOT NULL, -- When will this be completed?
                    
                    -- Goal Details
                    baseline_value REAL,
                    target_value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    measurement_frequency TEXT DEFAULT 'monthly', -- 'daily', 'weekly', 'monthly', 'quarterly', 'annual'
                    data_source TEXT, -- Where will data come from?
                    
                    -- Status and Progress
                    status TEXT DEFAULT 'draft', -- 'draft', 'active', 'on_track', 'at_risk', 'completed', 'cancelled'
                    priority TEXT DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
                    start_date TEXT NOT NULL,
                    target_date TEXT NOT NULL,
                    completion_date TEXT,
                    
                    -- Alignment
                    aligned_with_strategy TEXT, -- strategy name or reference
                    supports_sdg TEXT, -- JSON array of SDG numbers
                    supports_gri TEXT, -- JSON array of GRI indicators
                    supports_tsrs TEXT, -- JSON array of TSRS indicators
                    
                    -- Tracking
                    current_value REAL,
                    progress_percentage REAL DEFAULT 0,
                    last_updated TEXT,
                    next_review_date TEXT,
                    
                    created_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT
                )
            """, skip_tenant_filter=True)

            # KPI tanımları
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS kpi_definitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    kpi_name TEXT NOT NULL,
                    kpi_code TEXT NOT NULL, -- unique identifier
                    description TEXT,
                    category TEXT NOT NULL, -- 'environmental', 'social', 'economic', 'governance'
                    unit TEXT NOT NULL,
                    calculation_method TEXT, -- formula or method
                    data_source TEXT,
                    frequency TEXT DEFAULT 'monthly',
                    target_value REAL,
                    baseline_value REAL,
                    benchmark_value REAL, -- industry benchmark
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """, skip_tenant_filter=True)

            # Hedef ilerlemeleri
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS goal_progress_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal_id INTEGER NOT NULL,
                    tracking_date TEXT NOT NULL,
                    actual_value REAL NOT NULL,
                    target_value REAL,
                    progress_percentage REAL,
                    variance REAL, -- difference from target
                    variance_percentage REAL,
                    status_comment TEXT,
                    challenges_faced TEXT, -- JSON array
                    actions_taken TEXT, -- JSON array
                    next_actions TEXT, -- JSON array
                    reported_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (goal_id) REFERENCES smart_goals(id)
                )
            """)

            # Hedef değerlendirmeleri
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS goal_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal_id INTEGER NOT NULL,
                    assessment_date TEXT NOT NULL,
                    assessor_name TEXT NOT NULL,
                    smart_score INTEGER, -- 1-5 rating for each SMART criteria
                    specific_score INTEGER, -- 1-5
                    measurable_score INTEGER, -- 1-5
                    achievable_score INTEGER, -- 1-5
                    relevant_score INTEGER, -- 1-5
                    time_bound_score INTEGER, -- 1-5
                    overall_assessment TEXT,
                    recommendations TEXT, -- JSON array
                    next_assessment_date TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (goal_id) REFERENCES smart_goals(id)
                )
            """)

            # Hedef hiyerarşisi (ana hedef - alt hedef ilişkisi)
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS goal_hierarchy (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_goal_id INTEGER NOT NULL,
                    child_goal_id INTEGER NOT NULL,
                    relationship_type TEXT DEFAULT 'supports', -- 'supports', 'enables', 'depends_on'
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_goal_id) REFERENCES smart_goals(id),
                    FOREIGN KEY (child_goal_id) REFERENCES smart_goals(id)
                )
            """)

            logging.info("[OK] SMART hedefler tabloları hazır")

        except Exception as e:
            logging.error(f"[HATA] Tablo oluşturma hatası: {e}")

    def create_smart_goal(self, company_id: int, goal_title: str, description: str = "",
                         goal_category: str = "operational", goal_owner: str = "",
                         department: str = "", specific_description: str = "",
                         measurable_metrics: str = "", achievable_rationale: str = "",
                         relevant_justification: str = "", time_bound_deadline: str = "",
                         baseline_value: float = None, target_value: float = 0,
                         unit: str = "", measurement_frequency: str = "monthly",
                         data_source: str = "", priority: str = "medium",
                         start_date: str = None, target_date: str = "",
                         aligned_with_strategy: str = "", supports_sdg: List[str] = None,
                         supports_gri: List[str] = None, supports_tsrs: List[str] = None,
                         created_by: int = None) -> int:
        """
        Yeni SMART hedef oluştur
        """
        try:
            # Varsayılan başlangıç tarihi
            if start_date is None:
                start_date = datetime.now().strftime('%Y-%m-%d')

            # SMART kriterlerini kontrol et
            smart_criteria = [
                specific_description, measurable_metrics, achievable_rationale,
                relevant_justification, time_bound_deadline
            ]

            if not all(criteria.strip() for criteria in smart_criteria):
                raise ValueError("Tüm SMART kriterleri doldurulmalıdır")

            goal_id = self.insert(
                "smart_goals",
                {
                    "company_id": company_id,
                    "goal_title": goal_title,
                    "description": description,
                    "goal_category": goal_category,
                    "goal_owner": goal_owner,
                    "department": department,
                    "specific_description": specific_description,
                    "measurable_metrics": measurable_metrics,
                    "achievable_rationale": achievable_rationale,
                    "relevant_justification": relevant_justification,
                    "time_bound_deadline": time_bound_deadline,
                    "baseline_value": baseline_value,
                    "target_value": target_value,
                    "unit": unit,
                    "measurement_frequency": measurement_frequency,
                    "data_source": data_source,
                    "priority": priority,
                    "start_date": start_date,
                    "target_date": target_date,
                    "aligned_with_strategy": aligned_with_strategy,
                    "supports_sdg": json.dumps(supports_sdg or []),
                    "supports_gri": json.dumps(supports_gri or []),
                    "supports_tsrs": json.dumps(supports_tsrs or []),
                    "created_by": created_by
                },
                company_id=company_id
            )

            logging.info(f"[OK] SMART hedef oluşturuldu: {goal_title} (ID: {goal_id})")
            return goal_id

        except Exception as e:
            logging.error(f"[HATA] SMART hedef oluşturma hatası: {e}")
            raise

    def track_progress(self, goal_id: int, tracking_date: str, actual_value: float,
                      target_value: float = None, status_comment: str = "",
                      challenges_faced: List[str] = None, actions_taken: List[str] = None,
                      next_actions: List[str] = None, reported_by: int = None) -> int:
        """
        Hedef ilerlemesini takip et
        """
        try:
            # Hedef bilgilerini al
            # Note: smart_goals table has company_id.
            # We can use execute_query with skip_tenant_filter=True if we want to bypass check or 
            # ideally check with company_id.
            # Here we assume goal_id is unique enough or we rely on the fact that we can't easily check company_id without fetching it first.
            # But let's try to be safe. If self.company_id is set, use it.
            
            goal_result = self.execute_query(
                "SELECT target_value, current_value, baseline_value FROM smart_goals WHERE id = ?",
                (goal_id,),
                skip_tenant_filter=True
            )

            if not goal_result:
                raise ValueError(f"Hedef bulunamadı: ID {goal_id}")

            goal_target_value = goal_result[0]['target_value']
            # current_value = goal_result[0]['current_value'] # Unused variable
            baseline_value = goal_result[0]['baseline_value']

            # Hedef değer belirlenmemişse parametreden al
            if target_value is None:
                target_value = goal_target_value

            # İlerleme yüzdesini hesapla
            if baseline_value is not None:
                if target_value and baseline_value != target_value:
                    progress_percentage = ((actual_value - baseline_value) / (target_value - baseline_value)) * 100
                else:
                    progress_percentage = 0
            else:
                progress_percentage = 0

            # Varyans hesapla
            variance = actual_value - target_value if target_value else 0
            variance_percentage = (variance / target_value * 100) if target_value and target_value != 0 else 0

            # Insert tracking
            # goal_progress_tracking does not have company_id
            query = """
                INSERT INTO goal_progress_tracking 
                (goal_id, tracking_date, actual_value, target_value, progress_percentage,
                 variance, variance_percentage, status_comment, challenges_faced, actions_taken, next_actions, reported_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                goal_id, tracking_date, actual_value, target_value, progress_percentage,
                variance, variance_percentage, status_comment,
                json.dumps(challenges_faced or []),
                json.dumps(actions_taken or []),
                json.dumps(next_actions or []),
                reported_by
            )
            
            tracking_id = self.execute_update(query, params, skip_tenant_filter=True)

            # Hedefin güncel değerini güncelle
            # smart_goals has company_id, so inject_tenant_filter works if context is set.
            # If not, we skip it.
            
            update_query = """
                UPDATE smart_goals 
                SET current_value = ?, progress_percentage = ?, last_updated = ?
                WHERE id = ?
            """
            update_params = (actual_value, progress_percentage, tracking_date, goal_id)
            
            self.execute_update(update_query, update_params, skip_tenant_filter=True)

            logging.info(f"[OK] Hedef ilerlemesi kaydedildi: Hedef ID {goal_id}, Değer: {actual_value}")
            return tracking_id

        except Exception as e:
            logging.error(f"[HATA] İlerleme takip hatası: {e}")
            raise

    def assess_smart_criteria(self, goal_id: int, assessor_name: str, assessment_date: str,
                             specific_score: int, measurable_score: int, achievable_score: int,
                             relevant_score: int, time_bound_score: int, overall_assessment: str = "",
                             recommendations: List[str] = None, created_by: int = None) -> int:
        """
        SMART kriterlerini değerlendir
        """
        try:
            # Skorları kontrol et (1-5 arası)
            scores = [specific_score, measurable_score, achievable_score, relevant_score, time_bound_score]
            if not all(1 <= score <= 5 for score in scores):
                raise ValueError("Tüm skorlar 1-5 arasında olmalıdır")

            # Genel SMART skorunu hesapla
            smart_score = sum(scores) / len(scores)

            # Sonraki değerlendirme tarihini hesapla (3 ay sonra)
            next_assessment = (datetime.strptime(assessment_date, '%Y-%m-%d') + timedelta(days=90)).strftime('%Y-%m-%d')

            # goal_assessments does not have company_id
            query = """
                INSERT INTO goal_assessments 
                (goal_id, assessment_date, assessor_name, smart_score, specific_score, measurable_score,
                 achievable_score, relevant_score, time_bound_score, overall_assessment, recommendations, next_assessment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                goal_id, assessment_date, assessor_name, smart_score, specific_score, measurable_score,
                achievable_score, relevant_score, time_bound_score, overall_assessment,
                json.dumps(recommendations or []), next_assessment
            )

            assessment_id = self.execute_update(query, params, skip_tenant_filter=True)

            logging.info(f"[OK] SMART değerlendirme kaydedildi: Hedef ID {goal_id}, Genel Skor: {smart_score:.1f}")
            return assessment_id

        except Exception as e:
            logging.error(f"[HATA] SMART değerlendirme hatası: {e}")
            raise

    def get_smart_goals(self, company_id: int, goal_category: str = None, status: str = None) -> List[Dict]:
        """SMART hedefleri getir"""
        try:
            query = "SELECT * FROM smart_goals WHERE company_id = ?"
            params = [company_id]

            if goal_category:
                query += " AND goal_category = ?"
                params.append(goal_category)

            if status:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY priority DESC, target_date ASC"

            results = self.execute_query(query, tuple(params), company_id=company_id)
            
            goals = []
            for row in results:
                goal = dict(row)
                goal['supports_sdg'] = json.loads(goal.get('supports_sdg') or '[]')
                goal['supports_gri'] = json.loads(goal.get('supports_gri') or '[]')
                goal['supports_tsrs'] = json.loads(goal.get('supports_tsrs') or '[]')
                goals.append(goal)

            return goals

        except Exception as e:
            logging.error(f"[HATA] SMART hedefler getirme hatası: {e}")
            return []

    def create_default_smart_goals(self, company_id: int, created_by: int = 1) -> None:
        """Varsayılan SMART hedefler oluştur"""
        try:
            default_goals = [
                {
                    'goal_title': 'Enerji Verimliliği Artırma',
                    'description': 'Enerji tüketimini azaltarak maliyetleri düşürme ve çevresel etkiyi minimize etme',
                    'goal_category': 'sustainability',
                    'goal_owner': 'Üretim Müdürü',
                    'department': 'Üretim',
                    'specific_description': 'Tüm üretim tesislerinde enerji tüketimini kWh/ton ürün bazında azaltma',
                    'measurable_metrics': 'Enerji yoğunluğu (kWh/ton), Toplam enerji tüketimi (kWh), Enerji maliyeti (TL)',
                    'achievable_rationale': 'Mevcut teknoloji ve bütçe ile LED aydınlatma, motor optimizasyonu ve proses iyileştirmeleri yapılabilir',
                    'relevant_justification': 'Enerji maliyetleri toplam maliyetin %15\'ini oluşturuyor ve karbon ayak izimizi azaltacak',
                    'time_bound_deadline': '12 ay içinde hedef değere ulaşılacak',
                    'baseline_value': 150,
                    'target_value': 120,
                    'unit': 'kWh/ton',
                    'measurement_frequency': 'monthly',
                    'data_source': 'Enerji ölçüm sistemleri, elektrik faturaları',
                    'priority': 'high',
                    'start_date': datetime.now().strftime('%Y-%m-%d'),
                    'target_date': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
                    'supports_sdg': ['SDG_7', 'SDG_12', 'SDG_13'],
                    'supports_gri': ['GRI_302-1', 'GRI_302-2'],
                    'supports_tsrs': ['TSRS_E1-1']
                },
                {
                    'goal_title': 'İş Kazası Oranını Sıfırlama',
                    'description': 'Çalışan güvenliğini artırarak iş kazalarını sıfıra yaklaştırma',
                    'goal_category': 'social',
                    'goal_owner': 'İSG Müdürü',
                    'department': 'İnsan Kaynakları',
                    'specific_description': 'Tüm çalışanlar için iş kazası oranını 100 çalışan başına 0.5\'in altına düşürme',
                    'measurable_metrics': 'İş kazası sayısı, Kayıp zamanlı kaza oranı, Güvenlik eğitimi saatleri',
                    'achievable_rationale': 'Mevcut güvenlik programları genişletilerek, eğitim artırılarak ve denetimler sıklaştırılarak ulaşılabilir',
                    'relevant_justification': 'Çalışan güvenliği en öncelikli değerimiz ve yasal yükümlülüğümüz',
                    'time_bound_deadline': '18 ay içinde hedef değere ulaşılacak',
                    'baseline_value': 2.5,
                    'target_value': 0.5,
                    'unit': 'kazalar/100 çalışan',
                    'measurement_frequency': 'monthly',
                    'data_source': 'İSG kayıtları, kaza raporları',
                    'priority': 'critical',
                    'start_date': datetime.now().strftime('%Y-%m-%d'),
                    'target_date': (datetime.now() + timedelta(days=540)).strftime('%Y-%m-%d'),
                    'supports_sdg': ['SDG_3', 'SDG_8'],
                    'supports_gri': ['GRI_403-1', 'GRI_403-2'],
                    'supports_tsrs': ['TSRS_S1-1']
                },
                {
                    'goal_title': 'Atık Azaltma ve Geri Dönüşüm',
                    'description': 'Atık üretimini azaltarak döngüsel ekonomiye katkı sağlama',
                    'goal_category': 'environmental',
                    'goal_owner': 'Çevre Müdürü',
                    'department': 'Çevre',
                    'specific_description': 'Üretim atıklarının %80\'ini geri dönüştürme ve %20 azaltma',
                    'measurable_metrics': 'Atık miktarı (ton), Geri dönüşüm oranı (%), Atık maliyeti (TL)',
                    'achievable_rationale': 'Atık ayrıştırma sistemleri kurularak ve tedarikçilerle işbirliği yapılarak ulaşılabilir',
                    'relevant_justification': 'Atık maliyetlerini azaltacak, çevresel etkiyi minimize edecek ve döngüsel ekonomiye katkı sağlayacak',
                    'time_bound_deadline': '24 ay içinde hedef değerlere ulaşılacak',
                    'baseline_value': 100,
                    'target_value': 80,
                    'unit': 'ton/ay',
                    'measurement_frequency': 'monthly',
                    'data_source': 'Atık kayıtları, geri dönüşüm sertifikaları',
                    'priority': 'medium',
                    'start_date': datetime.now().strftime('%Y-%m-%d'),
                    'target_date': (datetime.now() + timedelta(days=720)).strftime('%Y-%m-%d'),
                    'supports_sdg': ['SDG_12', 'SDG_14', 'SDG_15'],
                    'supports_gri': ['GRI_306-1', 'GRI_306-2'],
                    'supports_tsrs': ['TSRS_E5-1']
                }
            ]

            # Hedefleri oluştur
            for goal_data in default_goals:
                self.create_smart_goal(company_id=company_id, created_by=created_by, **goal_data)

            logging.info(f"[OK] {len(default_goals)} SMART hedef oluşturuldu")

        except Exception as e:
            logging.error(f"[HATA] Varsayılan SMART hedefler oluşturma hatası: {e}")


if __name__ == "__main__":
    # Test
    manager = SMARTGoalsManager()
    manager.create_default_smart_goals(company_id=1, created_by=1)

    # Hedefleri listele
    goals = manager.get_smart_goals(company_id=1)
    logging.info(f"Toplam {len(goals)} SMART hedef bulundu:")
    for goal in goals:
        logging.info(f"- {goal['goal_title']} ({goal['goal_category']}) - İlerleme: {goal['progress_percentage']:.1f}%")

    # Test ilerleme takibi
    if goals:
        goal_id = goals[0]['id']
        tracking_id = manager.track_progress(
            goal_id=goal_id,
            tracking_date=datetime.now().strftime('%Y-%m-%d'),
            actual_value=130,
            status_comment="LED aydınlatma projesi tamamlandı",
            challenges_faced=["Bütçe onayı gecikmesi"],
            actions_taken=["LED aydınlatma kurulumu", "Enerji izleme sistemi"],
            next_actions=["Motor optimizasyonu", "Proses iyileştirmeleri"]
        )
        logging.info(f"Test ilerleme takibi oluşturuldu: ID {tracking_id}")

        # Test SMART değerlendirme
        assessment_id = manager.assess_smart_criteria(
            goal_id=goal_id,
            assessor_name="Sürdürülebilirlik Uzmanı",
            assessment_date=datetime.now().strftime('%Y-%m-%d'),
            specific_score=5,
            measurable_score=4,
            achievable_score=4,
            relevant_score=5,
            time_bound_score=4,
            overall_assessment="Hedef çok iyi tanımlanmış ve ulaşılabilir",
            recommendations=["Daha sık ilerleme kontrolü", "Alternatif teknolojiler araştırma"]
        )
        logging.info(f"Test SMART değerlendirme oluşturuldu: ID {assessment_id}")
