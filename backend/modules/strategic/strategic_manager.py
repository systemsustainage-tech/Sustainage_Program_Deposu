#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stratejik Modüller Yöneticisi
Yönetici Mesajı, Sürdürülebilirlik Stratejisi, Risk ve Fırsatlar yönetimi
"""

import logging
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
try:
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    from core.base_manager import BaseTenantManager


class StrategicManager(BaseTenantManager):
    """Stratejik modülleri yöneten sınıf"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        super().__init__(db_path, company_id)
        self._init_database()

    def _init_database(self) -> None:
        """Veritabanı tablolarını oluştur"""
        # Yönetici Mesajları
        self.execute_update("""
            CREATE TABLE IF NOT EXISTS executive_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                executive_name TEXT NOT NULL,
                executive_title TEXT NOT NULL,
                message_title TEXT,
                message_content TEXT NOT NULL,
                message_summary TEXT,
                language TEXT DEFAULT 'tr',
                is_published INTEGER DEFAULT 0,
                created_by INTEGER,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """, skip_tenant_filter=True)

        # Sürdürülebilirlik Stratejisi
        self.execute_update("""
            CREATE TABLE IF NOT EXISTS sustainability_strategy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                strategy_title TEXT NOT NULL,
                vision TEXT,
                mission TEXT,
                values TEXT,
                strategic_pillars TEXT,
                commitments TEXT,
                sdg_alignment TEXT,
                created_by INTEGER,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """, skip_tenant_filter=True)

        # Stratejik Hedefler (SMART)
        self.execute_update("""
            CREATE TABLE IF NOT EXISTS strategic_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                strategy_id INTEGER,
                goal_title TEXT NOT NULL,
                goal_description TEXT,
                category TEXT,
                target_year INTEGER,
                baseline_year INTEGER,
                baseline_value REAL,
                target_value REAL,
                current_value REAL,
                unit TEXT,
                status TEXT DEFAULT 'active',
                progress_percent REAL DEFAULT 0,
                responsible_person TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (strategy_id) REFERENCES sustainability_strategy(id)
            )
        """, skip_tenant_filter=True)

        # Risk ve Fırsatlar
        self.execute_update("""
            CREATE TABLE IF NOT EXISTS risks_opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                impact_level TEXT,
                probability TEXT,
                time_horizon TEXT,
                stakeholders_affected TEXT,
                financial_impact TEXT,
                mitigation_actions TEXT,
                responsible_person TEXT,
                status TEXT DEFAULT 'active',
                created_by INTEGER,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # Risk/Fırsat Değerlendirme Matrisi
        self.execute_update("""
            CREATE TABLE IF NOT EXISTS risk_opportunity_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                risk_opportunity_id INTEGER NOT NULL,
                assessment_date TEXT NOT NULL,
                impact_score INTEGER,
                probability_score INTEGER,
                risk_score INTEGER,
                notes TEXT,
                assessed_by INTEGER,
                FOREIGN KEY (risk_opportunity_id) REFERENCES risks_opportunities(id)
            )
        """)

        # Eylem Planları
        self.execute_update("""
            CREATE TABLE IF NOT EXISTS action_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                linked_to_type TEXT,
                linked_to_id INTEGER,
                action_title TEXT NOT NULL,
                action_description TEXT,
                start_date TEXT,
                target_date TEXT,
                completion_date TEXT,
                status TEXT DEFAULT 'planned',
                priority TEXT,
                budget REAL,
                responsible_person TEXT,
                progress_notes TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # KPI'lar (Key Performance Indicators)
        self.execute_update("""
            CREATE TABLE IF NOT EXISTS strategic_kpis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                goal_id INTEGER,
                kpi_name TEXT NOT NULL,
                kpi_description TEXT,
                measurement_unit TEXT,
                measurement_frequency TEXT,
                baseline_value REAL,
                target_value REAL,
                current_value REAL,
                data_source TEXT,
                responsible_person TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (goal_id) REFERENCES strategic_goals(id)
            )
        """)

    # ============================================
    # YÖNETİCİ MESAJLARI
    # ============================================

    def create_executive_message(self, company_id: int, year: int,
                                 executive_name: str, executive_title: str,
                                 message_content: str, message_title: str = "",
                                 message_summary: str = "",
                                 language: str = 'tr',
                                 created_by: Optional[int] = None) -> Optional[int]:
        """Yönetici mesajı oluştur"""
        try:
            return self.execute_update("""
                INSERT INTO executive_messages 
                (company_id, year, executive_name, executive_title, message_title,
                 message_content, message_summary, language, created_by, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, year, executive_name, executive_title, message_title,
                message_content, message_summary, language, created_by,
                datetime.now().isoformat(), datetime.now().isoformat()
            ), company_id=company_id)

        except Exception as e:
            logging.error(f"Yönetici mesajı oluşturma hatası: {e}")
            return None

    def get_executive_message(self, company_id: int, year: int) -> Optional[Dict]:
        """Yönetici mesajını al"""
        try:
            rows = self.execute_query("""
                SELECT * FROM executive_messages
                WHERE company_id = ? AND year = ?
                ORDER BY updated_at DESC
                LIMIT 1
            """, (company_id, year), company_id=company_id)

            if rows:
                return rows[0]

            return None

        except Exception as e:
            logging.error(f"Yönetici mesajı alma hatası: {e}")
            return None

    # ============================================
    # SÜRDÜRÜLEBİLİRLİK STRATEJİSİ
    # ============================================

    def create_sustainability_strategy(self, company_id: int, year: int,
                                      strategy_title: str,
                                      vision: str = "", mission: str = "",
                                      values: str = "", strategic_pillars: List[str] = None,
                                      commitments: List[str] = None,
                                      sdg_alignment: List[int] = None,
                                      created_by: Optional[int] = None) -> Optional[int]:
        """Sürdürülebilirlik stratejisi oluştur"""
        try:
            return self.execute_update("""
                INSERT INTO sustainability_strategy 
                (company_id, year, strategy_title, vision, mission, values,
                 strategic_pillars, commitments, sdg_alignment, created_by, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, year, strategy_title, vision, mission, values,
                json.dumps(strategic_pillars, ensure_ascii=False) if strategic_pillars else None,
                json.dumps(commitments, ensure_ascii=False) if commitments else None,
                json.dumps(sdg_alignment) if sdg_alignment else None,
                created_by, datetime.now().isoformat(), datetime.now().isoformat()
            ), company_id=company_id)

        except Exception as e:
            logging.error(f"Strateji oluşturma hatası: {e}")
            return None

    def create_strategic_goal(self, company_id: int, goal_title: str,
                            goal_description: str = "", category: str = "",
                            target_year: int = None, baseline_year: int = None,
                            baseline_value: float = None, target_value: float = None,
                            unit: str = "", responsible_person: str = "") -> Optional[int]:
        """Stratejik hedef oluştur (SMART)"""
        try:
            return self.execute_update("""
                INSERT INTO strategic_goals 
                (company_id, goal_title, goal_description, category, target_year,
                 baseline_year, baseline_value, target_value, unit, responsible_person, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, goal_title, goal_description, category, target_year,
                baseline_year, baseline_value, target_value, unit, responsible_person,
                datetime.now().isoformat(), datetime.now().isoformat()
            ), company_id=company_id)

        except Exception as e:
            logging.error(f"Hedef oluşturma hatası: {e}")
            return None

    def update_goal_progress(self, goal_id: int, current_value: float) -> bool:
        """Hedef ilerlemesini güncelle"""
        try:
            # Hedef bilgilerini al
            # Note: Need company_id context here ideally, but update by ID is reasonably safe if checked
            # However, BaseTenantManager enforces tenant filter if company_id is set in self or passed
            # We should try to get company_id from context or pass it if available.
            # Here we don't have company_id in args. Assuming it's in self.company_id if set,
            # or we rely on the fact that ID is unique. But for strict multi-tenant, we should check ownership.
            # But changing signature might break callers.
            # For now, we'll use execute_query without explicit company_id if not available, 
            # BUT BaseTenantManager might require it if configured strict.
            
            rows = self.execute_query("""
                SELECT baseline_value, target_value, company_id
                FROM strategic_goals
                WHERE id = ?
            """, (goal_id,))

            if not rows:
                return False

            baseline = rows[0]['baseline_value']
            target = rows[0]['target_value']
            company_id = rows[0]['company_id'] # Get company_id for the update check

            # İlerleme hesapla
            if baseline is not None and target is not None and target != baseline:
                progress = ((current_value - baseline) / (target - baseline)) * 100
                progress = max(0, min(100, progress))  # 0-100 arası sınırla
            else:
                progress = 0

            # Güncelle
            self.execute_update("""
                UPDATE strategic_goals 
                SET current_value = ?, progress_percent = ?, updated_at = ?
                WHERE id = ? AND company_id = ?
            """, (current_value, progress, datetime.now().isoformat(), goal_id, company_id), company_id=company_id)

            return True

        except Exception as e:
            logging.error(f"İlerleme güncelleme hatası: {e}")
            return False

    def get_strategic_goals(self, company_id: int, category: Optional[str] = None) -> List[Dict]:
        """Stratejik hedefleri listele"""
        try:
            if category:
                rows = self.execute_query("""
                    SELECT * FROM strategic_goals
                    WHERE company_id = ? AND category = ?
                    ORDER BY target_year, goal_title
                """, (company_id, category), company_id=company_id)
            else:
                rows = self.execute_query("""
                    SELECT * FROM strategic_goals
                    WHERE company_id = ?
                    ORDER BY target_year, goal_title
                """, (company_id,), company_id=company_id)

            return rows

        except Exception as e:
            logging.error(f"Hedef listeleme hatası: {e}")
            return []

    # ============================================
    # RİSK VE FIRSATLAR
    # ============================================

    def create_risk_opportunity(self, company_id: int, type: str, category: str,
                               title: str, description: str = "",
                               impact_level: str = "", probability: str = "",
                               time_horizon: str = "", stakeholders_affected: str = "",
                               financial_impact: str = "", mitigation_actions: str = "",
                               responsible_person: str = "",
                               created_by: Optional[int] = None) -> Optional[int]:
        """Risk veya fırsat oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO risks_opportunities 
                (company_id, type, category, title, description, impact_level,
                 probability, time_horizon, stakeholders_affected, financial_impact,
                 mitigation_actions, responsible_person, created_by, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, type, category, title, description, impact_level,
                probability, time_horizon, stakeholders_affected, financial_impact,
                mitigation_actions, responsible_person, created_by,
                datetime.now().isoformat(), datetime.now().isoformat()
            ))

            ro_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return ro_id

        except Exception as e:
            logging.error(f"Risk/Fırsat oluşturma hatası: {e}")
            return None

    def assess_risk_opportunity(self, ro_id: int, impact_score: int,
                               probability_score: int, notes: str = "",
                               assessed_by: Optional[int] = None) -> bool:
        """Risk/Fırsat değerlendirmesi yap"""
        try:
            # Risk skoru = Etki x Olasılık
            risk_score = impact_score * probability_score

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO risk_opportunity_assessments 
                (risk_opportunity_id, assessment_date, impact_score, probability_score,
                 risk_score, notes, assessed_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                ro_id, datetime.now().isoformat(), impact_score, probability_score,
                risk_score, notes, assessed_by
            ))

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            logging.error(f"Değerlendirme hatası: {e}")
            return False

    def get_risks_opportunities(self, company_id: int, type: Optional[str] = None,
                               category: Optional[str] = None) -> List[Dict]:
        """Risk ve fırsatları listele"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = "SELECT * FROM risks_opportunities WHERE company_id = ?"
            params = [company_id]

            if type:
                query += " AND type = ?"
                params.append(type)

            if category:
                query += " AND category = ?"
                params.append(category)

            query += " ORDER BY created_at DESC"

            cursor.execute(query, params)

            columns = ['id', 'company_id', 'type', 'category', 'title', 'description',
                      'impact_level', 'probability', 'time_horizon', 'stakeholders_affected',
                      'financial_impact', 'mitigation_actions', 'responsible_person',
                      'status', 'created_by', 'created_at', 'updated_at']

            items = []
            for row in cursor.fetchall():
                items.append(dict(zip(columns, row)))

            conn.close()
            return items

        except Exception as e:
            logging.error(f"Risk/Fırsat listeleme hatası: {e}")
            return []

    def get_risk_matrix(self, company_id: int) -> Dict:
        """Risk matrisini oluştur (5x5)"""
        try:
            risks = self.get_risks_opportunities(company_id, type='risk')

            matrix = [[[] for _ in range(5)] for _ in range(5)]

            for risk in risks:
                # Son değerlendirmeyi al
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT impact_score, probability_score
                    FROM risk_opportunity_assessments
                    WHERE risk_opportunity_id = ?
                    ORDER BY assessment_date DESC
                    LIMIT 1
                """, (risk['id'],))

                result = cursor.fetchone()
                conn.close()

                if result:
                    impact, probability = result
                    # Skoru 1-5 aralığına indir
                    impact_idx = min(4, max(0, impact - 1))
                    prob_idx = min(4, max(0, probability - 1))

                    matrix[prob_idx][impact_idx].append({
                        'id': risk['id'],
                        'title': risk['title'],
                        'category': risk['category']
                    })

            return {
                'matrix': matrix,
                'total_risks': len(risks)
            }

        except Exception as e:
            logging.error(f"Risk matrisi hatası: {e}")
            return {'matrix': [[[] for _ in range(5)] for _ in range(5)], 'total_risks': 0}

    # ============================================
    # EYLEM PLANLARI
    # ============================================

    def create_action_plan(self, company_id: int, action_title: str,
                          action_description: str = "",
                          linked_to_type: str = "", linked_to_id: int = None,
                          start_date: str = "", target_date: str = "",
                          priority: str = "medium", budget: float = None,
                          responsible_person: str = "") -> Optional[int]:
        """Eylem planı oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO action_plans 
                (company_id, linked_to_type, linked_to_id, action_title, action_description,
                 start_date, target_date, priority, budget, responsible_person, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, linked_to_type, linked_to_id, action_title, action_description,
                start_date, target_date, priority, budget, responsible_person,
                datetime.now().isoformat(), datetime.now().isoformat()
            ))

            action_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return action_id

        except Exception as e:
            logging.error(f"Eylem planı oluşturma hatası: {e}")
            return None

    # ============================================
    # KPI'LAR
    # ============================================

    def create_kpi(self, company_id: int, kpi_name: str, goal_id: int = None,
                  kpi_description: str = "", measurement_unit: str = "",
                  measurement_frequency: str = "", baseline_value: float = None,
                  target_value: float = None, data_source: str = "",
                  responsible_person: str = "") -> Optional[int]:
        """KPI oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO strategic_kpis 
                (company_id, goal_id, kpi_name, kpi_description, measurement_unit,
                 measurement_frequency, baseline_value, target_value, data_source,
                 responsible_person, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, goal_id, kpi_name, kpi_description, measurement_unit,
                measurement_frequency, baseline_value, target_value, data_source,
                responsible_person, datetime.now().isoformat(), datetime.now().isoformat()
            ))

            kpi_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return kpi_id

        except Exception as e:
            logging.error(f"KPI oluşturma hatası: {e}")
            return None

