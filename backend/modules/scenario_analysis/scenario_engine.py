#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Senaryo Analizi ve Modelleme Motoru - TAM VE EKSİKSİZ
TCFD senaryoları, BAU vs Net Zero, Risk modelleme, Finansal etki
"""

import logging
import json
import os
import sqlite3
from typing import Dict
from config.database import DB_PATH


class ScenarioEngine:
    """Senaryo analizi ve modelleme motoru"""

    # TCFD İklim Senaryoları (Türkçe)
    TCFD_SCENARIOS = {
        "2C": {
            "name": "2°C Senaryosu (Paris Anlaşması)",
            "description": "Küresel ısınma 2°C ile sınırlandırılır",
            "carbon_price_2030": 140,  # USD/tCO2
            "carbon_price_2050": 250,
            "renewable_share_2030": 0.60,  # %60
            "renewable_share_2050": 0.90,
            "physical_risk": "düşük",
            "transition_risk": "yüksek"
        },
        "4C": {
            "name": "4°C Senaryosu (Mevcut Politikalar)",
            "description": "Küresel ısınma 4°C'ye ulaşır",
            "carbon_price_2030": 30,
            "carbon_price_2050": 60,
            "renewable_share_2030": 0.30,
            "renewable_share_2050": 0.45,
            "physical_risk": "çok_yüksek",
            "transition_risk": "düşük"
        },
        "1_5C": {
            "name": "1.5°C Senaryosu (Net Zero 2050)",
            "description": "Küresel ısınma 1.5°C ile sınırlandırılır",
            "carbon_price_2030": 200,
            "carbon_price_2050": 400,
            "renewable_share_2030": 0.75,
            "renewable_share_2050": 0.95,
            "physical_risk": "çok_düşük",
            "transition_risk": "çok_yüksek"
        }
    }

    # Geçiş Riskleri (Türkçe)
    TRANSITION_RISKS = {
        "politika_duzenleyici": "Politika ve Düzenleyici Risk",
        "teknoloji": "Teknoloji Riski",
        "pazar": "Pazar Riski",
        "itibar": "İtibar Riski"
    }

    # Fiziksel Riskler (Türkçe)
    PHYSICAL_RISKS = {
        "ani": "Ani Fiziksel Riskler (Sel, Fırtına, Yangın)",
        "kronik": "Kronik Fiziksel Riskler (Deniz Seviyesi, Kuraklık, Sıcaklık)"
    }

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_scenario_tables()

    def _init_scenario_tables(self) -> None:
        """Senaryo tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Senaryo analizleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scenario_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    scenario_name TEXT NOT NULL,
                    scenario_type TEXT NOT NULL,
                    base_year INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    description TEXT,
                    assumptions TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Emisyon projeksiyonları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emission_projections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    scope1_emissions REAL DEFAULT 0,
                    scope2_emissions REAL DEFAULT 0,
                    scope3_emissions REAL DEFAULT 0,
                    total_emissions REAL DEFAULT 0,
                    emission_intensity REAL DEFAULT 0,
                    reduction_percentage REAL DEFAULT 0,
                    FOREIGN KEY (scenario_id) REFERENCES scenario_analyses(id)
                )
            """)

            # Geçiş riskleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transition_risks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_id INTEGER NOT NULL,
                    risk_category TEXT NOT NULL,
                    risk_description TEXT NOT NULL,
                    likelihood TEXT DEFAULT 'orta',
                    impact TEXT DEFAULT 'orta',
                    financial_impact_min REAL DEFAULT 0,
                    financial_impact_max REAL DEFAULT 0,
                    timeframe TEXT,
                    mitigation_strategy TEXT,
                    FOREIGN KEY (scenario_id) REFERENCES scenario_analyses(id)
                )
            """)

            # Fiziksel riskler
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS physical_risks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_id INTEGER NOT NULL,
                    risk_type TEXT NOT NULL,
                    risk_event TEXT NOT NULL,
                    affected_locations TEXT,
                    likelihood TEXT DEFAULT 'orta',
                    impact TEXT DEFAULT 'orta',
                    financial_impact_min REAL DEFAULT 0,
                    financial_impact_max REAL DEFAULT 0,
                    timeframe TEXT,
                    adaptation_measures TEXT,
                    FOREIGN KEY (scenario_id) REFERENCES scenario_analyses(id)
                )
            """)

            # Finansal etki simulasyonu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS financial_impact_simulation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    carbon_cost REAL DEFAULT 0,
                    energy_cost REAL DEFAULT 0,
                    capex_investment REAL DEFAULT 0,
                    opex_change REAL DEFAULT 0,
                    revenue_impact REAL DEFAULT 0,
                    net_financial_impact REAL DEFAULT 0,
                    roi_percentage REAL DEFAULT 0,
                    FOREIGN KEY (scenario_id) REFERENCES scenario_analyses(id)
                )
            """)

            # Senaryo karşılaştırmaları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scenario_comparisons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    comparison_name TEXT NOT NULL,
                    base_scenario_id INTEGER NOT NULL,
                    alternative_scenario_id INTEGER NOT NULL,
                    comparison_metrics TEXT,
                    recommendations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (base_scenario_id) REFERENCES scenario_analyses(id),
                    FOREIGN KEY (alternative_scenario_id) REFERENCES scenario_analyses(id)
                )
            """)

            conn.commit()
            logging.info("[OK] Senaryo analizi tablolari olusturuldu")

        except Exception as e:
            logging.error(f"[ERROR] Senaryo tablolari olusturulurken hata: {e}")
        finally:
            conn.close()

    # =====================================================
    # 1. TCFD SENARYO ANALİZİ
    # =====================================================

    def create_tcfd_scenario(self, company_id: int, scenario_key: str,
                            base_year: int, target_year: int,
                            current_emissions: float,
                            assumptions: Dict = None) -> int:
        """
        TCFD senaryosu oluştur (2°C, 4°C, 1.5°C)
        
        Args:
            scenario_key: "2C", "4C", "1_5C"
            current_emissions: Mevcut toplam emisyon (tCO2e)
            assumptions: Şirket varsayımları
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            scenario_info = self.TCFD_SCENARIOS[scenario_key]

            # Senaryo oluştur
            cursor.execute("""
                INSERT INTO scenario_analyses
                (company_id, scenario_name, scenario_type, base_year, target_year,
                 description, assumptions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                scenario_info["name"],
                "TCFD",
                base_year,
                target_year,
                scenario_info["description"],
                json.dumps(assumptions) if assumptions else None
            ))

            scenario_id = cursor.lastrowid

            # Emisyon projeksiyonları hesapla
            self._calculate_emission_projections(
                cursor, scenario_id, scenario_key,
                base_year, target_year, current_emissions
            )

            # Geçiş risklerini ekle
            self._add_transition_risks(cursor, scenario_id, scenario_key)

            # Fiziksel riskleri ekle
            self._add_physical_risks(cursor, scenario_id, scenario_key)

            # Finansal etki simülasyonu
            self._simulate_financial_impact(
                cursor, scenario_id, scenario_key,
                base_year, target_year, current_emissions
            )

            conn.commit()
            logging.info(f"[OK] TCFD senaryosu olusturuldu: {scenario_info['name']}")
            return scenario_id

        except Exception as e:
            logging.error(f"TCFD senaryo olusturma hatasi: {e}")
            return 0
        finally:
            conn.close()

    def _calculate_emission_projections(self, cursor, scenario_id: int,
                                       scenario_key: str, base_year: int,
                                       target_year: int,
                                       current_emissions: float) -> None:
        """Emisyon projeksiyonlarını hesapla"""
        self.TCFD_SCENARIOS[scenario_key]

        # Senaryoya göre azaltma hedefleri
        if scenario_key == "2C":
            target_reduction = 0.50  # %50 azaltım (2030)
            final_reduction = 0.80   # %80 azaltım (2050)
        elif scenario_key == "1_5C":
            target_reduction = 0.65  # %65 azaltım (2030)
            final_reduction = 0.95   # %95 azaltım (2050)
        else:  # 4C
            target_reduction = 0.10  # %10 azaltım (2030)
            final_reduction = 0.20   # %20 azaltım (2050)

        # Yıllık projeksiyonlar
        for year in range(base_year, target_year + 1):
            # Lineer interpolasyon
            progress = (year - base_year) / (target_year - base_year)

            if target_year == 2030:
                reduction = target_reduction * progress
            elif target_year == 2050:
                reduction = final_reduction * progress
            else:
                reduction = target_reduction * progress

            projected_emissions = current_emissions * (1 - reduction)

            # Scope dağılımı (varsayılan: Scope1: 40%, Scope2: 30%, Scope3: 30%)
            scope1 = projected_emissions * 0.40
            scope2 = projected_emissions * 0.30
            scope3 = projected_emissions * 0.30

            cursor.execute("""
                INSERT INTO emission_projections
                (scenario_id, year, scope1_emissions, scope2_emissions,
                 scope3_emissions, total_emissions, reduction_percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (scenario_id, year, scope1, scope2, scope3,
                  projected_emissions, reduction * 100))

    def _add_transition_risks(self, cursor, scenario_id: int, scenario_key: str) -> None:
        """Geçiş risklerini ekle"""
        scenario = self.TCFD_SCENARIOS[scenario_key]

        if scenario["transition_risk"] in ["yüksek", "çok_yüksek"]:
            risks = [
                {
                    "category": "politika_duzenleyici",
                    "description": "Karbon fiyatlama mekanizması ve emisyon sınırları",
                    "likelihood": "yüksek",
                    "impact": "yüksek",
                    "min": 5000000,
                    "max": 15000000
                },
                {
                    "category": "teknoloji",
                    "description": "Düşük karbonlu teknolojilere geçiş maliyeti",
                    "likelihood": "orta",
                    "impact": "yüksek",
                    "min": 10000000,
                    "max": 30000000
                },
                {
                    "category": "pazar",
                    "description": "Müşteri tercihlerinde değişim ve pazar kaybı",
                    "likelihood": "orta",
                    "impact": "orta",
                    "min": 2000000,
                    "max": 8000000
                }
            ]
        else:
            risks = [
                {
                    "category": "itibar",
                    "description": "İklim değişikliğine yönelik yetersiz eylem",
                    "likelihood": "düşük",
                    "impact": "düşük",
                    "min": 500000,
                    "max": 2000000
                }
            ]

        for risk in risks:
            cursor.execute("""
                INSERT INTO transition_risks
                (scenario_id, risk_category, risk_description, likelihood,
                 impact, financial_impact_min, financial_impact_max, timeframe)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (scenario_id, risk["category"], risk["description"],
                  risk["likelihood"], risk["impact"], risk["min"], risk["max"],
                  "2025-2030"))

    def _add_physical_risks(self, cursor, scenario_id: int, scenario_key: str) -> None:
        """Fiziksel riskleri ekle"""
        scenario = self.TCFD_SCENARIOS[scenario_key]

        if scenario["physical_risk"] in ["yüksek", "çok_yüksek"]:
            risks = [
                {
                    "type": "ani",
                    "event": "Aşırı hava olayları (sel, fırtına, yangın)",
                    "likelihood": "yüksek",
                    "impact": "yüksek",
                    "min": 8000000,
                    "max": 25000000
                },
                {
                    "type": "kronik",
                    "event": "Deniz seviyesi yükselmesi ve kıyı erozyonu",
                    "likelihood": "yüksek",
                    "impact": "orta",
                    "min": 5000000,
                    "max": 15000000
                },
                {
                    "type": "kronik",
                    "event": "Su stresi ve kuraklık",
                    "likelihood": "orta",
                    "impact": "yüksek",
                    "min": 3000000,
                    "max": 10000000
                }
            ]
        else:
            risks = [
                {
                    "type": "ani",
                    "event": "Hafif aşırı hava olayları",
                    "likelihood": "düşük",
                    "impact": "düşük",
                    "min": 1000000,
                    "max": 3000000
                }
            ]

        for risk in risks:
            cursor.execute("""
                INSERT INTO physical_risks
                (scenario_id, risk_type, risk_event, likelihood, impact,
                 financial_impact_min, financial_impact_max, timeframe)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (scenario_id, risk["type"], risk["event"], risk["likelihood"],
                  risk["impact"], risk["min"], risk["max"], "2025-2050"))

    def _simulate_financial_impact(self, cursor, scenario_id: int,
                                   scenario_key: str, base_year: int,
                                   target_year: int, current_emissions: float) -> None:
        """Finansal etki simülasyonu"""
        scenario = self.TCFD_SCENARIOS[scenario_key]

        # Yıllık finansal etki
        for year in range(base_year, target_year + 1):
            progress = (year - base_year) / (target_year - base_year)

            # Karbon maliyeti
            if target_year == 2030:
                carbon_price = scenario["carbon_price_2030"] * progress
            else:
                carbon_price = scenario["carbon_price_2050"] * progress

            # Emisyon azaltımı
            cursor.execute("""
                SELECT total_emissions FROM emission_projections
                WHERE scenario_id = ? AND year = ?
            """, (scenario_id, year))

            result = cursor.fetchone()
            emissions = result[0] if result else current_emissions

            carbon_cost = emissions * carbon_price

            # Enerji maliyeti (yenilenebilir enerji payı arttıkça azalır)
            renewable_share = scenario["renewable_share_2030"] * progress
            energy_cost_saving = 50000000 * renewable_share * 0.20  # %20 tasarruf

            # CAPEX (yatırım)
            capex = 20000000 * progress if scenario_key in ["2C", "1_5C"] else 5000000 * progress

            # Net finansal etki
            net_impact = carbon_cost + capex - energy_cost_saving

            # ROI
            roi = ((energy_cost_saving - carbon_cost) / capex * 100) if capex > 0 else 0

            cursor.execute("""
                INSERT INTO financial_impact_simulation
                (scenario_id, year, carbon_cost, energy_cost, capex_investment,
                 net_financial_impact, roi_percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (scenario_id, year, carbon_cost, energy_cost_saving,
                  capex, net_impact, roi))

    # =====================================================
    # 2. BAU vs NET ZERO KARŞILAŞTIRMASI
    # =====================================================

    def create_bau_vs_netzero_comparison(self, company_id: int,
                                        current_emissions: float) -> int:
        """
        İş Her Zamanki Gibi vs Net Zero karşılaştırması
        
        Returns:
            Karşılaştırma ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # BAU senaryosu (4°C)
            bau_id = self.create_tcfd_scenario(
                company_id, "4C", 2024, 2050, current_emissions,
                {"name": "İş Her Zamanki Gibi (BAU)", "intervention": "yok"}
            )

            # Net Zero senaryosu (1.5°C)
            netzero_id = self.create_tcfd_scenario(
                company_id, "1_5C", 2024, 2050, current_emissions,
                {"name": "Net Zero 2050", "intervention": "agresif"}
            )

            # Karşılaştırma kaydı
            cursor.execute("""
                INSERT INTO scenario_comparisons
                (company_id, comparison_name, base_scenario_id,
                 alternative_scenario_id, comparison_metrics)
                VALUES (?, ?, ?, ?, ?)
            """, (
                company_id,
                "BAU vs Net Zero 2050",
                bau_id,
                netzero_id,
                json.dumps({
                    "metric": "Emisyon Azaltımı, Finansal Etki, Risk Profili"
                })
            ))

            comparison_id = cursor.lastrowid
            conn.commit()

            logging.info("[OK] BAU vs Net Zero karsilastirmasi olusturuldu")
            return comparison_id

        except Exception as e:
            logging.error(f"Karsilastirma olusturma hatasi: {e}")
            return 0
        finally:
            conn.close()

    def get_scenario_comparison_summary(self, comparison_id: int) -> Dict:
        """Senaryo karşılaştırma özeti"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Karşılaştırma bilgileri
            cursor.execute("""
                SELECT base_scenario_id, alternative_scenario_id
                FROM scenario_comparisons WHERE id = ?
            """, (comparison_id,))

            result = cursor.fetchone()
            if not result:
                return {}

            bau_id, netzero_id = result

            summary = {
                "bau": self._get_scenario_summary(cursor, bau_id),
                "netzero": self._get_scenario_summary(cursor, netzero_id),
                "difference": {}
            }

            # Farkları hesapla
            summary["difference"] = {
                "emission_reduction": (
                    summary["netzero"]["total_reduction"] -
                    summary["bau"]["total_reduction"]
                ),
                "financial_impact": (
                    summary["netzero"]["total_cost"] -
                    summary["bau"]["total_cost"]
                ),
                "transition_risk_count": (
                    summary["netzero"]["transition_risks"] -
                    summary["bau"]["transition_risks"]
                ),
                "physical_risk_count": (
                    summary["bau"]["physical_risks"] -
                    summary["netzero"]["physical_risks"]
                )
            }

            conn.close()
            return summary

        except Exception as e:
            logging.error(f"Karsilastirma ozeti hatasi: {e}")
            return {}

    def _get_scenario_summary(self, cursor, scenario_id: int) -> Dict:
        """Senaryo özeti"""
        summary = {}

        # Toplam emisyon azaltımı (2050)
        cursor.execute("""
            SELECT reduction_percentage FROM emission_projections
            WHERE scenario_id = ? ORDER BY year DESC LIMIT 1
        """, (scenario_id,))

        result = cursor.fetchone()
        summary["total_reduction"] = result[0] if result else 0

        # Toplam maliyet
        cursor.execute("""
            SELECT SUM(net_financial_impact) FROM financial_impact_simulation
            WHERE scenario_id = ?
        """, (scenario_id,))

        result = cursor.fetchone()
        summary["total_cost"] = result[0] if result and result[0] else 0

        # Risk sayıları
        cursor.execute("SELECT COUNT(*) FROM transition_risks WHERE scenario_id = ?", (scenario_id,))
        summary["transition_risks"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM physical_risks WHERE scenario_id = ?", (scenario_id,))
        summary["physical_risks"] = cursor.fetchone()[0]

        return summary

    # =====================================================
    # 3. YARDIMCI FONKSİYONLAR
    # =====================================================

    def get_scenario_details(self, scenario_id: int) -> Dict:
        """Senaryo detaylarını getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Temel bilgiler
            cursor.execute("SELECT * FROM scenario_analyses WHERE id = ?", (scenario_id,))
            row = cursor.fetchone()

            if not row:
                return {}

            columns = [col[0] for col in cursor.description]
            details = dict(zip(columns, row))

            # Emisyon projeksiyonları
            cursor.execute("""
                SELECT year, total_emissions, reduction_percentage
                FROM emission_projections WHERE scenario_id = ?
                ORDER BY year
            """, (scenario_id,))

            details["emissions"] = [
                {"year": row[0], "emissions": row[1], "reduction": row[2]}
                for row in cursor.fetchall()
            ]

            # Riskler
            cursor.execute("SELECT COUNT(*) FROM transition_risks WHERE scenario_id = ?", (scenario_id,))
            details["transition_risk_count"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM physical_risks WHERE scenario_id = ?", (scenario_id,))
            details["physical_risk_count"] = cursor.fetchone()[0]

            conn.close()
            return details

        except Exception as e:
            logging.error(f"Senaryo detay hatasi: {e}")
            return {}
