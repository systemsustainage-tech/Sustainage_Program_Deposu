#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sürdürülebilirlik Stratejisi Yöneticisi
Stratejik sürdürülebilirlik planları ve hedefler
"""

import logging
import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List


class SustainabilityStrategyManager:
    """Sürdürülebilirlik stratejisi yöneticisi"""

    def __init__(self, db_path: str = None) -> None:
        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Gerekli tabloları oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Sürdürülebilirlik stratejileri
            cursor.execute("""
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
                    status TEXT DEFAULT 'draft', -- 'draft', 'active', 'completed', 'archived'
                    approval_date TEXT,
                    approved_by INTEGER,
                    created_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT
                )
            """)

            # Stratejik hedefler
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS strategic_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                    FOREIGN KEY (strategy_id) REFERENCES sustainability_strategies(id)
                )
            """)

            # Hedef ilerlemeleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS goal_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                    FOREIGN KEY (goal_id) REFERENCES strategic_goals(id)
                )
            """)

            # Stratejik girişimler
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS strategic_initiatives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_id INTEGER NOT NULL,
                    initiative_name TEXT NOT NULL,
                    description TEXT,
                    category TEXT, -- 'program', 'project', 'partnership', 'investment'
                    priority TEXT DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
                    start_date TEXT,
                    end_date TEXT,
                    budget REAL,
                    responsible_department TEXT,
                    expected_outcomes TEXT, -- JSON array
                    success_metrics TEXT, -- JSON array
                    status TEXT DEFAULT 'planned', -- 'planned', 'active', 'completed', 'cancelled'
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (strategy_id) REFERENCES sustainability_strategies(id)
                )
            """)

            # Stratejik değerlendirmeler
            cursor.execute("""
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
            """)

            conn.commit()
            logging.info("[OK] Sürdürülebilirlik stratejisi tabloları hazır")

        except Exception as e:
            logging.error(f"[HATA] Tablo oluşturma hatası: {e}")
        finally:
            conn.close()

    def create_strategy(self, company_id: int, strategy_name: str, description: str = "",
                       vision: str = "", mission: str = "", core_values: List[str] = None,
                       strategic_pillars: List[str] = None, time_horizon: int = 5,
                       start_year: int = None, end_year: int = None, created_by: int = None) -> int:
        """
        Yeni sürdürülebilirlik stratejisi oluştur
        
        Args:
            company_id: Şirket ID
            strategy_name: Strateji adı
            description: Açıklama
            vision: Vizyon
            mission: Misyon
            core_values: Temel değerler listesi
            strategic_pillars: Stratejik sütunlar listesi
            time_horizon: Zaman ufku (yıl)
            start_year: Başlangıç yılı
            end_year: Bitiş yılı
            created_by: Oluşturan kullanıcı ID
        
        Returns:
            Oluşturulan strateji ID'si
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Varsayılan değerler
            if start_year is None:
                start_year = datetime.now().year
            if end_year is None:
                end_year = start_year + time_horizon - 1

            # Aynı isimde strateji kontrolü
            cursor.execute("""
                SELECT id FROM sustainability_strategies 
                WHERE company_id = ? AND strategy_name = ?
            """, (company_id, strategy_name))

            if cursor.fetchone():
                raise ValueError(f"Bu isimde strateji zaten mevcut: {strategy_name}")

            cursor.execute("""
                INSERT INTO sustainability_strategies 
                (company_id, strategy_name, description, vision, mission, core_values, 
                 strategic_pillars, time_horizon, start_year, end_year, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, strategy_name, description, vision, mission,
                json.dumps(core_values or []),
                json.dumps(strategic_pillars or []),
                time_horizon, start_year, end_year, created_by
            ))

            strategy_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] Sürdürülebilirlik stratejisi oluşturuldu: {strategy_name} (ID: {strategy_id})")
            return strategy_id

        except Exception as e:
            conn.rollback()
            logging.error(f"[HATA] Strateji oluşturma hatası: {e}")
            raise
        finally:
            conn.close()

    def add_strategic_goal(self, strategy_id: int, goal_category: str, goal_title: str,
                          description: str = "", target_year: int = None, baseline_year: int = None,
                          baseline_value: float = None, target_value: float = None, unit: str = "",
                          measurement_frequency: str = "annual", responsible_department: str = "",
                          kpi_formula: str = "", is_critical: bool = False) -> int:
        """
        Stratejiye hedef ekle
        
        Args:
            strategy_id: Strateji ID
            goal_category: Hedef kategorisi ('environmental', 'social', 'economic', 'governance')
            goal_title: Hedef başlığı
            description: Açıklama
            target_year: Hedef yıl
            baseline_year: Baz yıl
            baseline_value: Baz değer
            target_value: Hedef değer
            unit: Birim
            measurement_frequency: Ölçüm sıklığı
            responsible_department: Sorumlu departman
            kpi_formula: KPI formülü
            is_critical: Kritik hedef mi
        
        Returns:
            Oluşturulan hedef ID'si
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO strategic_goals 
                (strategy_id, goal_category, goal_title, description, target_year, 
                 baseline_year, baseline_value, target_value, unit, measurement_frequency,
                 responsible_department, kpi_formula, is_critical)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                strategy_id, goal_category, goal_title, description, target_year,
                baseline_year, baseline_value, target_value, unit, measurement_frequency,
                responsible_department, kpi_formula, 1 if is_critical else 0
            ))

            goal_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] Stratejik hedef eklendi: {goal_title} (ID: {goal_id})")
            return goal_id

        except Exception as e:
            conn.rollback()
            logging.error(f"[HATA] Hedef ekleme hatası: {e}")
            raise
        finally:
            conn.close()

    def record_goal_progress(self, goal_id: int, reporting_period: str, actual_value: float,
                           target_value: float = None, progress_narrative: str = "",
                           challenges: List[str] = None, actions_taken: List[str] = None,
                           next_steps: List[str] = None, reported_by: int = None) -> int:
        """
        Hedef ilerlemesini kaydet
        
        Args:
            goal_id: Hedef ID
            reporting_period: Raporlama dönemi ('YYYY-MM' or 'YYYY')
            actual_value: Gerçekleşen değer
            target_value: Hedef değer
            progress_narrative: İlerleme açıklaması
            challenges: Zorluklar listesi
            actions_taken: Alınan aksiyonlar listesi
            next_steps: Sonraki adımlar listesi
            reported_by: Raporlayan kullanıcı ID
        
        Returns:
            Oluşturulan ilerleme kaydı ID'si
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Hedef bilgilerini al
            cursor.execute("""
                SELECT target_value FROM strategic_goals WHERE id = ?
            """, (goal_id,))

            goal_result = cursor.fetchone()
            if not goal_result:
                raise ValueError(f"Hedef bulunamadı: ID {goal_id}")

            # Hedef değer belirlenmemişse parametreden al
            if target_value is None:
                target_value = goal_result[0]

            # Başarı oranını hesapla
            achievement_rate = (actual_value / target_value * 100) if target_value and target_value != 0 else 0

            cursor.execute("""
                INSERT INTO goal_progress 
                (goal_id, reporting_period, actual_value, target_value, achievement_rate,
                 progress_narrative, challenges, actions_taken, next_steps, reported_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                goal_id, reporting_period, actual_value, target_value, achievement_rate,
                progress_narrative,
                json.dumps(challenges or []),
                json.dumps(actions_taken or []),
                json.dumps(next_steps or []),
                reported_by
            ))

            progress_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] Hedef ilerlemesi kaydedildi: Hedef ID {goal_id}, Dönem {reporting_period}")
            return progress_id

        except Exception as e:
            conn.rollback()
            logging.error(f"[HATA] İlerleme kaydetme hatası: {e}")
            raise
        finally:
            conn.close()

    def get_strategies(self, company_id: int, status: str = None) -> List[Dict]:
        """Sürdürülebilirlik stratejilerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            query = """
                SELECT * FROM sustainability_strategies 
                WHERE company_id = ?
            """
            params = [company_id]

            if status:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY start_year DESC, created_at DESC"

            cursor.execute(query, params)
            results = cursor.fetchall()

            strategies = []
            for row in results:
                strategies.append({
                    'id': row[0], 'company_id': row[1], 'strategy_name': row[2], 'description': row[3],
                    'vision': row[4], 'mission': row[5], 'core_values': json.loads(row[6] or '[]'),
                    'strategic_pillars': json.loads(row[7] or '[]'), 'time_horizon': row[8],
                    'start_year': row[9], 'end_year': row[10], 'status': row[11],
                    'approval_date': row[12], 'approved_by': row[13], 'created_by': row[14],
                    'created_at': row[15], 'updated_at': row[16]
                })

            return strategies

        except Exception as e:
            logging.error(f"[HATA] Stratejiler getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def get_strategy_goals(self, strategy_id: int) -> List[Dict]:
        """Stratejik hedefleri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM strategic_goals 
                WHERE strategy_id = ? AND status != 'cancelled'
                ORDER BY goal_category, is_critical DESC, goal_title
            """, (strategy_id,))

            results = cursor.fetchall()
            goals = []

            for row in results:
                goals.append({
                    'id': row[0], 'strategy_id': row[1], 'goal_category': row[2], 'goal_title': row[3],
                    'description': row[4], 'target_year': row[5], 'baseline_year': row[6],
                    'baseline_value': row[7], 'target_value': row[8], 'unit': row[9],
                    'measurement_frequency': row[10], 'responsible_department': row[11],
                    'kpi_formula': row[12], 'progress_tracking_method': row[13], 'is_critical': row[14],
                    'status': row[15], 'created_at': row[16]
                })

            return goals

        except Exception as e:
            logging.error(f"[HATA] Hedefler getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def get_goal_progress(self, goal_id: int = None, strategy_id: int = None) -> List[Dict]:
        """Hedef ilerlemelerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if goal_id:
                cursor.execute("""
                    SELECT gp.*, sg.goal_title, sg.goal_category
                    FROM goal_progress gp
                    JOIN strategic_goals sg ON gp.goal_id = sg.id
                    WHERE gp.goal_id = ?
                    ORDER BY gp.reporting_period DESC
                """, (goal_id,))
            elif strategy_id:
                cursor.execute("""
                    SELECT gp.*, sg.goal_title, sg.goal_category
                    FROM goal_progress gp
                    JOIN strategic_goals sg ON gp.goal_id = sg.id
                    WHERE sg.strategy_id = ?
                    ORDER BY gp.goal_id, gp.reporting_period DESC
                """, (strategy_id,))
            else:
                cursor.execute("""
                    SELECT gp.*, sg.goal_title, sg.goal_category
                    FROM goal_progress gp
                    JOIN strategic_goals sg ON gp.goal_id = sg.id
                    ORDER BY gp.reporting_period DESC
                """)

            results = cursor.fetchall()
            progress_records = []

            for row in results:
                progress_records.append({
                    'id': row[0], 'goal_id': row[1], 'reporting_period': row[2],
                    'actual_value': row[3], 'target_value': row[4], 'achievement_rate': row[5],
                    'progress_narrative': row[6], 'challenges': json.loads(row[7] or '[]'),
                    'actions_taken': json.loads(row[8] or '[]'), 'next_steps': json.loads(row[9] or '[]'),
                    'reported_by': row[10], 'reported_at': row[11], 'goal_title': row[12], 'goal_category': row[13]
                })

            return progress_records

        except Exception as e:
            logging.error(f"[HATA] İlerleme kayıtları getirme hatası: {e}")
            return []
        finally:
            conn.close()

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
