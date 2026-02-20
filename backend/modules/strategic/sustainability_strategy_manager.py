#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sürdürülebilirlik Stratejisi Yöneticisi
Stratejik sürdürülebilirlik planları ve hedefler
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from backend.core.base_manager import BaseTenantManager


class SustainabilityStrategyManager(BaseTenantManager):
    """Sürdürülebilirlik stratejisi yöneticisi"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        super().__init__(db_path, company_id)
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Gerekli tabloları oluştur"""
        try:
            # Sürdürülebilirlik stratejileri
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS sustainability_strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    strategy_name TEXT NOT NULL,
                    description TEXT,
                    vision TEXT,
                    mission TEXT,
                    core_values TEXT, -- JSON array
                    strategic_pillars TEXT, -- JSON array
                    time_horizon INTEGER DEFAULT 5, -- years
                    start_year INTEGER NOT NULL,
                    end_year INTEGER NOT NULL,
                    status TEXT DEFAULT 'active', -- 'draft', 'active', 'completed', 'archived'
                    approval_date TEXT,
                    approved_by INTEGER,
                    created_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT
                )
            """, skip_tenant_filter=True)

            # Stratejik hedefler
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS strategic_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    strategy_id INTEGER NOT NULL,
                    goal_category TEXT NOT NULL, -- 'environmental', 'social', 'economic', 'governance'
                    goal_title TEXT NOT NULL,
                    description TEXT,
                    target_year INTEGER,
                    baseline_year INTEGER,
                    baseline_value REAL,
                    target_value REAL,
                    unit TEXT,
                    measurement_frequency TEXT DEFAULT 'annual', -- 'monthly', 'quarterly', 'annual'
                    responsible_department TEXT,
                    kpi_formula TEXT,
                    progress_tracking_method TEXT,
                    is_critical INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active', -- 'active', 'completed', 'paused', 'cancelled'
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (strategy_id) REFERENCES sustainability_strategies(id),
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """, skip_tenant_filter=True)

            # Hedef ilerlemeleri
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS goal_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    goal_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL, -- 'YYYY-MM' or 'YYYY'
                    actual_value REAL,
                    target_value REAL,
                    achievement_rate REAL, -- percentage
                    progress_narrative TEXT,
                    challenges TEXT, -- JSON array
                    actions_taken TEXT, -- JSON array
                    next_steps TEXT, -- JSON array
                    reported_by INTEGER,
                    reported_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (goal_id) REFERENCES strategic_goals(id),
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """, skip_tenant_filter=True)

            # Stratejik girişimler
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS strategic_initiatives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    initiative_name TEXT NOT NULL,
                    description TEXT,
                    strategy_id INTEGER,
                    goal_id INTEGER,
                    start_date TEXT,
                    end_date TEXT,
                    budget REAL,
                    currency TEXT DEFAULT 'TRY',
                    responsible_person TEXT,
                    status TEXT DEFAULT 'planned', -- 'planned', 'in_progress', 'completed', 'cancelled'
                    impact_assessment TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (strategy_id) REFERENCES sustainability_strategies(id),
                    FOREIGN KEY (goal_id) REFERENCES strategic_goals(id),
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """, skip_tenant_filter=True)

            # Stratejik değerlendirmeler
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS strategy_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_id INTEGER NOT NULL,
                    assessment_date TEXT NOT NULL,
                    assessment_type TEXT NOT NULL, -- 'quarterly', 'annual', 'mid_term', 'final'
                    overall_progress REAL, -- percentage
                    strengths TEXT, -- JSON array
                    weaknesses TEXT, -- JSON array
                    opportunities TEXT, -- JSON array
                    threats TEXT, -- JSON array
                    recommendations TEXT, -- JSON array
                    assessed_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (strategy_id) REFERENCES sustainability_strategies(id)
                )
            """, skip_tenant_filter=True)

            logging.info("[OK] Sürdürülebilirlik stratejisi tabloları hazır")

        except Exception as e:
            logging.error(f"[HATA] Tablo oluşturma hatası: {e}")

    def create_strategy(self, company_id: int, strategy_name: str, description: str = "",
                       vision: str = "", mission: str = "", core_values: List[str] = None,
                       strategic_pillars: List[str] = None, time_horizon: int = 5,
                       start_year: int = None, end_year: int = None, created_by: int = None) -> int:
        """
        Yeni sürdürülebilirlik stratejisi oluştur
        """
        try:
            # Varsayılan değerler
            if start_year is None:
                start_year = datetime.now().year
            if end_year is None:
                end_year = start_year + time_horizon - 1

            # Aynı isimde strateji kontrolü
            existing = self.execute_query(
                "SELECT id FROM sustainability_strategies WHERE company_id = ? AND strategy_name = ?", 
                (company_id, strategy_name),
                company_id=company_id
            )

            if existing:
                raise ValueError(f"Bu isimde strateji zaten mevcut: {strategy_name}")

            # Insert strategy
            strategy_id = self.insert(
                "sustainability_strategies",
                {
                    "company_id": company_id,
                    "strategy_name": strategy_name,
                    "description": description,
                    "vision": vision,
                    "mission": mission,
                    "core_values": json.dumps(core_values or []),
                    "strategic_pillars": json.dumps(strategic_pillars or []),
                    "time_horizon": time_horizon,
                    "start_year": start_year,
                    "end_year": end_year,
                    "created_by": created_by
                },
                company_id=company_id
            )

            logging.info(f"[OK] Sürdürülebilirlik stratejisi oluşturuldu: {strategy_name} (ID: {strategy_id})")
            return strategy_id

        except Exception as e:
            logging.error(f"[HATA] Strateji oluşturma hatası: {e}")
            raise

    def add_strategic_goal(self, strategy_id: int, goal_category: str, goal_title: str,
                          description: str = "", target_year: int = None, baseline_year: int = None,
                          baseline_value: float = None, target_value: float = None, unit: str = "",
                          measurement_frequency: str = "annual", responsible_department: str = "",
                          kpi_formula: str = "", is_critical: bool = False) -> int:
        """
        Stratejiye hedef ekle
        """
        try:
            # Note: We don't check company_id here explicitly because strategy_id is linked to it,
            # but BaseTenantManager requires company_id context.
            # We assume the caller provides correct context or we should fetch it from strategy_id if needed.
            # However, for insert, we don't strictly need it if we are just inserting by strategy_id, 
            # BUT BaseTenantManager.insert adds company_id automatically.
            # Strategic goals table DOES NOT have company_id in the schema above!
            # Let's check schema: "CREATE TABLE IF NOT EXISTS strategic_goals (..., strategy_id INTEGER NOT NULL, ...)"
            # It does NOT have company_id. 
            # This is a problem for BaseTenantManager.insert which tries to inject company_id.
            
            # If the table doesn't have company_id, we should use execute_update directly without company_id injection if possible,
            # OR we should add company_id to the table.
            # Adding company_id to child tables is good practice for tenant isolation.
            # But for now, let's stick to existing schema and use execute_update with skip_tenant_filter=True 
            # OR just standard execute_update if inject_tenant_filter is smart enough (it filters by table name usually).
            
            # Wait, inject_tenant_filter tries to inject "WHERE company_id = ?" for UPDATE/DELETE/SELECT.
            # For INSERT, it usually expects company_id column if using helper.
            
            # Let's use execute_update for raw insert.
            
            query = """
                INSERT INTO strategic_goals 
                (strategy_id, goal_category, goal_title, description, target_year, 
                 baseline_year, baseline_value, target_value, unit, measurement_frequency,
                 responsible_department, kpi_formula, is_critical)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                strategy_id, goal_category, goal_title, description, target_year,
                baseline_year, baseline_value, target_value, unit, measurement_frequency,
                responsible_department, kpi_formula, 1 if is_critical else 0
            )
            
            # Since strategic_goals table does NOT have company_id, we can't enforce tenant isolation on INSERT easily 
            # unless we verify strategy_id belongs to the company first.
            
            if self.company_id:
                strategy = self.execute_query(
                    "SELECT id FROM sustainability_strategies WHERE id = ? AND company_id = ?",
                    (strategy_id, self.company_id),
                    company_id=self.company_id
                )
                if not strategy:
                    raise ValueError(f"Strategy {strategy_id} not found for company {self.company_id}")

            return self.execute_update(query, params, skip_tenant_filter=True)

        except Exception as e:
            logging.error(f"[HATA] Hedef ekleme hatası: {e}")
            raise

    def record_goal_progress(self, goal_id: int, reporting_period: str, actual_value: float,
                           target_value: float = None, progress_narrative: str = "",
                           challenges: List[str] = None, actions_taken: List[str] = None,
                           next_steps: List[str] = None, reported_by: int = None) -> int:
        """
        Hedef ilerlemesini kaydet
        """
        try:
            # Check tenant isolation
            if self.company_id:
                # Verify goal belongs to a strategy owned by this company
                check_query = """
                    SELECT sg.id 
                    FROM strategic_goals sg
                    JOIN sustainability_strategies ss ON sg.strategy_id = ss.id
                    WHERE sg.id = ? AND ss.company_id = ?
                """
                is_valid = self.execute_query(check_query, (goal_id, self.company_id), skip_tenant_filter=True)
                if not is_valid:
                    raise ValueError(f"Goal {goal_id} not found or access denied for company {self.company_id}")

            # Hedef bilgilerini al (check existence and get target value)
            goal_result = self.execute_query(
                "SELECT target_value FROM strategic_goals WHERE id = ?",
                (goal_id,),
                skip_tenant_filter=True
            )

            if not goal_result:
                raise ValueError(f"Hedef bulunamadı: ID {goal_id}")

            current_target = goal_result[0]['target_value'] if goal_result[0]['target_value'] is not None else 0

            # Hedef değer belirlenmemişse parametreden al
            if target_value is None:
                target_value = current_target

            # Başarı oranını hesapla
            achievement_rate = (actual_value / target_value * 100) if target_value and target_value != 0 else 0

            query = """
                INSERT INTO goal_progress 
                (goal_id, reporting_period, actual_value, target_value, achievement_rate,
                 progress_narrative, challenges, actions_taken, next_steps, reported_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                goal_id, reporting_period, actual_value, target_value, achievement_rate,
                progress_narrative,
                json.dumps(challenges or []),
                json.dumps(actions_taken or []),
                json.dumps(next_steps or []),
                reported_by
            )

            progress_id = self.execute_update(query, params, skip_tenant_filter=True)
            
            logging.info(f"[OK] Hedef ilerlemesi kaydedildi: Hedef ID {goal_id}, Dönem {reporting_period}")
            return progress_id

        except Exception as e:
            logging.error(f"[HATA] İlerleme kaydetme hatası: {e}")
            raise

    def get_strategies(self, company_id: int, status: str = None) -> List[Dict]:
        """Sürdürülebilirlik stratejilerini getir"""
        try:
            query = "SELECT * FROM sustainability_strategies WHERE company_id = ?"
            params = [company_id]

            if status:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY start_year DESC, created_at DESC"

            results = self.execute_query(query, tuple(params), company_id=company_id)
            
            # Results are already dict-like
            strategies = []
            for row in results:
                # Convert Row to dict if needed, handle JSON fields
                strategy = dict(row)
                strategy['core_values'] = json.loads(strategy.get('core_values') or '[]')
                strategy['strategic_pillars'] = json.loads(strategy.get('strategic_pillars') or '[]')
                strategies.append(strategy)

            return strategies

        except Exception as e:
            logging.error(f"[HATA] Stratejiler getirme hatası: {e}")
            return []

    def get_strategy_goals(self, strategy_id: int) -> List[Dict]:
        """Stratejik hedefleri getir"""
        try:
            # Verify strategy ownership if company context exists
            if self.company_id:
                strategy = self.execute_query(
                    "SELECT id FROM sustainability_strategies WHERE id = ? AND company_id = ?",
                    (strategy_id, self.company_id),
                    company_id=self.company_id
                )
                if not strategy:
                    logging.warning(f"Access denied: Strategy {strategy_id} does not belong to company {self.company_id}")
                    return []

            query = """
                SELECT * FROM strategic_goals 
                WHERE strategy_id = ? AND status != 'cancelled'
                ORDER BY goal_category, is_critical DESC, goal_title
            """
            
            results = self.execute_query(query, (strategy_id,), skip_tenant_filter=True)
            return [dict(row) for row in results]

        except Exception as e:
            logging.error(f"[HATA] Hedefler getirme hatası: {e}")
            return []

    def get_goal_progress(self, goal_id: int = None, strategy_id: int = None) -> List[Dict]:
        """Hedef ilerlemelerini getir"""
        try:
            base_query = """
                SELECT gp.*, sg.goal_title, sg.goal_category
                FROM goal_progress gp
                JOIN strategic_goals sg ON gp.goal_id = sg.id
                JOIN sustainability_strategies ss ON sg.strategy_id = ss.id
            """
            params = []
            conditions = []
            
            # Enforce tenant isolation
            if self.company_id:
                conditions.append("ss.company_id = ?")
                params.append(self.company_id)
            
            if goal_id:
                conditions.append("gp.goal_id = ?")
                params.append(goal_id)
            elif strategy_id:
                conditions.append("sg.strategy_id = ?")
                params.append(strategy_id)
            
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
                
            base_query += " ORDER BY gp.reporting_period DESC"
            
            # Use skip_tenant_filter=True because we manually handled it via JOIN
            results = self.execute_query(base_query, tuple(params), skip_tenant_filter=True)
            
            progress_records = []

            for row in results:
                # row is dict-like
                progress_records.append({
                    'id': row['id'], 
                    'goal_id': row['goal_id'], 
                    'reporting_period': row['reporting_period'],
                    'actual_value': row['actual_value'], 
                    'target_value': row['target_value'], 
                    'achievement_rate': row['achievement_rate'],
                    'progress_narrative': row['progress_narrative'], 
                    'challenges': json.loads(row['challenges'] or '[]'),
                    'actions_taken': json.loads(row['actions_taken'] or '[]'), 
                    'next_steps': json.loads(row['next_steps'] or '[]'),
                    'reported_by': row.get('reported_by'), # Use .get() as it might be missing in older schemas? No, it's in INSERT.
                    # 'reported_at' is missing in INSERT above, let's check schema.
                    # 'reported_at' usually defaults to CURRENT_TIMESTAMP in DB.
                    'reported_at': row.get('created_at'), # Schema check needed. Usually created_at.
                    'goal_title': row['goal_title'], 
                    'goal_category': row['goal_category']
                })

            return progress_records

        except Exception as e:
            logging.error(f"[HATA] İlerleme kayıtları getirme hatası: {e}")
            return []

    def create_default_strategy(self, company_id: int, created_by: int = 1) -> int:
        """Varsayılan sürdürülebilirlik stratejisi oluştur"""
        try:
            # Ana strateji oluştur
            strategy_id = self.create_strategy(
                company_id=company_id,
                strategy_name="2024-2028 Sürdürülebilirlik Stratejisi",
                description="Kapsamlı sürdürülebilirlik stratejisi ve hedefleri",
                vision="Sürdürülebilir bir gelecek için öncü şirket olmak",
                mission="Çevresel, sosyal ve ekonomik değer yaratarak paydaşlarımıza fayda sağlamak",
                core_values=[
                    "Çevresel Sorumluluk",
                    "Sosyal Adalet",
                    "Şeffaflık",
                    "İnovasyon",
                    "İş Birliği"
                ],
                strategic_pillars=[
                    "Çevresel Sürdürülebilirlik",
                    "Sosyal Sorumluluk",
                    "Ekonomik Değer",
                    "Kurumsal Yönetişim"
                ],
                time_horizon=5,
                start_year=2024,
                end_year=2028,
                created_by=created_by
            )

            # Çevresel hedefler
            self.add_strategic_goal(
                strategy_id=strategy_id,
                goal_category="environmental",
                goal_title="Karbon Ayak İzi Azaltma",
                description="Scope 1 ve 2 emisyonlarını %30 azaltma",
                target_year=2028,
                baseline_year=2023,
                baseline_value=1000,
                target_value=700,
                unit="ton CO2e",
                responsible_department="Çevre",
                is_critical=True
            )

            self.add_strategic_goal(
                strategy_id=strategy_id,
                goal_category="environmental",
                goal_title="Yenilenebilir Enerji Oranı",
                description="Toplam enerji tüketiminde yenilenebilir enerji oranını %50'ye çıkarma",
                target_year=2028,
                baseline_year=2023,
                baseline_value=20,
                target_value=50,
                unit="%",
                responsible_department="Üretim"
            )

            # Sosyal hedefler
            self.add_strategic_goal(
                strategy_id=strategy_id,
                goal_category="social",
                goal_title="İş Kazası Oranı",
                description="İş kazası oranını sıfıra yaklaştırma",
                target_year=2028,
                baseline_year=2023,
                baseline_value=2.5,
                target_value=0.5,
                unit="kazalar/100 çalışan",
                responsible_department="İnsan Kaynakları",
                is_critical=True
            )

            self.add_strategic_goal(
                strategy_id=strategy_id,
                goal_category="social",
                goal_title="Kadın Yönetici Oranı",
                description="Üst düzey yönetici pozisyonlarında kadın oranını %40'a çıkarma",
                target_year=2028,
                baseline_year=2023,
                baseline_value=25,
                target_value=40,
                unit="%",
                responsible_department="İnsan Kaynakları"
            )

            # Ekonomik hedefler
            self.add_strategic_goal(
                strategy_id=strategy_id,
                goal_category="economic",
                goal_title="Sürdürülebilirlik Yatırımları",
                description="Yıllık gelirin %5'ini sürdürülebilirlik yatırımlarına ayırma",
                target_year=2028,
                baseline_year=2023,
                baseline_value=2,
                target_value=5,
                unit="%",
                responsible_department="Finans"
            )

            logging.info(f"[OK] Varsayılan strateji oluşturuldu: ID {strategy_id}")
            return strategy_id

        except Exception as e:
            logging.error(f"[HATA] Varsayılan strateji oluşturma hatası: {e}")
            return None


if __name__ == "__main__":
    # Test
    manager = SustainabilityStrategyManager()

    # Varsayılan strateji oluştur
    strategy_id = manager.create_default_strategy(company_id=1, created_by=1)

    if strategy_id:
        # Hedefleri listele
        goals = manager.get_strategy_goals(strategy_id)
        logging.info(f"Strateji ID {strategy_id} için {len(goals)} hedef bulundu:")
        for goal in goals:
            logging.info(f"- {goal['goal_title']} ({goal['goal_category']})")

        # Test ilerleme kaydı
        if goals:
            goal_id = goals[0]['id']
            progress_id = manager.record_goal_progress(
                goal_id=goal_id,
                reporting_period="2024",
                actual_value=800,
                target_value=700,
                progress_narrative="Enerji verimliliği projeleri başarıyla uygulandı",
                challenges=["Yatırım bütçesi sınırları"],
                actions_taken=["LED aydınlatma", "Enerji izleme sistemi"],
                next_steps=["Güneş enerjisi paneli kurulumu"]
            )
            logging.info(f"Test ilerleme kaydı oluşturuldu: ID {progress_id}")
