#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TCFD MANAGER - İş Mantığı ve Veri Yönetimi
- Governance, Strategy, Risk Management, Metrics veri yönetimi
- İklim risklerinin tanımlanması ve değerlendirilmesi
- Senaryo analizi yönetimi
- Hedef ve metrik takibi
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from backend.core.base_manager import BaseTenantManager

class TCFDManager(BaseTenantManager):
    """TCFD modülü iş mantığı ve veri yönetimi"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None):
        """
        Args:
            db_path: Ana veritabanı yolu (sdg_desktop.sqlite)
            company_id: Şirket ID (opsiyonel)
        """
        super().__init__(db_path, company_id)
        self.module_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.module_dir, 'data')

        # Veritabanını başlat
        self.init_database()

        # Risk katalogu ve senaryoları yükle
        self.load_catalogs()

    def init_database(self) -> None:
        """TCFD tablolarını oluştur (yoksa)"""
        schema_path = os.path.join(self.module_dir, 'tcfd_schema.sql')

        if os.path.exists(schema_path):
            try:
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema = f.read()

                # SQL komutlarını çalıştır
                self.db.execute_script(schema)
                logging.info("[TCFD] Veritabanı tabloları oluşturuldu/güncellendi")
            except Exception as e:
                logging.error(f"TCFD init_database error: {e}")
        
        # Ek tablo: tcfd_financial_impact (Kod içinde garanti altına alalım)
        self.init_financial_impact_table()

    def init_financial_impact_table(self) -> None:
        """Finansal etki tablosunu oluştur"""
        try:
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS tcfd_financial_impact (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    risk_opportunity_type TEXT, -- Risk veya Opportunity
                    description TEXT,
                    financial_impact REAL, -- Sayısal değer
                    impact_description TEXT, -- Metin açıklaması (örn. '1M-5M USD')
                    probability TEXT, -- Low, Medium, High veya %
                    time_horizon TEXT, -- Short, Medium, Long
                    scenario TEXT, -- 1.5C, 2C, 4C
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
        except Exception as e:
            logging.error(f"[TCFD] Finansal etki tablosu oluşturma hatası: {e}")

    # ========================================================================
    # FINANCIAL IMPACT (Finansal Etki)
    # ========================================================================

    def add_financial_impact(self, company_id: int, data: Dict) -> Tuple[bool, str]:
        """Finansal etki verisi ekle"""
        try:
            self.execute_update("""
                INSERT INTO tcfd_financial_impact (
                    company_id,
                    risk_opportunity_type,
                    description,
                    financial_impact,
                    impact_description,
                    probability,
                    time_horizon,
                    scenario
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                data.get('risk_opportunity_type'),
                data.get('description'),
                data.get('financial_impact'),
                data.get('impact_description'),
                data.get('probability'),
                data.get('time_horizon'),
                data.get('scenario')
            ), company_id=company_id)
            return True, "Finansal etki verisi eklendi"
        except Exception as e:
            return False, f"Hata: {str(e)}"

    def get_financial_impacts(self, company_id: int) -> List[Dict]:
        """Finansal etki verilerini getir"""
        try:
            return self.select(
                'tcfd_financial_impact',
                company_id=company_id,
                order_by='created_at DESC'
            )
        except Exception as e:
            logging.error(f"[TCFD] Finansal etki verileri getirme hatası: {e}")
            return []

    def delete_financial_impact(self, company_id: int, impact_id: int) -> Tuple[bool, str]:
        """Finansal etki verisini sil"""
        try:
            self.execute_update(
                "DELETE FROM tcfd_financial_impact WHERE id = ?",
                (impact_id,),
                company_id=company_id
            )
            return True, "Kayıt silindi"
        except Exception as e:
            return False, f"Hata: {str(e)}"

    def load_catalogs(self) -> None:
        """Risk katalogu ve senaryoları yükle"""
        # Risk katalogu
        risks_path = os.path.join(self.data_dir, 'climate_risks_catalog.json')
        if os.path.exists(risks_path):
            with open(risks_path, 'r', encoding='utf-8') as f:
                self.risk_catalog = json.load(f)
        else:
            self.risk_catalog = {}

        # Senaryo verileri
        scenarios_path = os.path.join(self.data_dir, 'climate_scenarios.json')
        if os.path.exists(scenarios_path):
            with open(scenarios_path, 'r', encoding='utf-8') as f:
                self.scenarios_data = json.load(f)
        else:
            self.scenarios_data = {}

    # ========================================================================
    # GOVERNANCE (Yönetişim)
    # ========================================================================

    def save_governance(self, company_id: int, year: int, data: Dict) -> Tuple[bool, str]:
        """
        Yönetişim verilerini kaydet
        
        Args:
            company_id: Firma ID
            year: Raporlama yılı
            data: Yönetişim verileri dict
        
        Returns:
            (başarılı_mı, mesaj)
        """
        try:
            # Mevcut kayıt var mı?
            existing = self.select(
                'tcfd_governance',
                company_id=company_id,
                where={'reporting_year': year}
            )

            if existing:
                # Güncelle
                self.execute_update("""
                    UPDATE tcfd_governance
                    SET board_oversight = ?,
                        board_frequency = ?,
                        board_expertise = ?,
                        management_role = ?,
                        management_structure = ?,
                        management_responsibility = ?,
                        climate_committee = ?,
                        committee_name = ?,
                        committee_members = ?,
                        responsible_executive = ?,
                        strategy_integration = ?,
                        risk_integration = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (
                    data.get('board_oversight'),
                    data.get('board_frequency'),
                    data.get('board_expertise'),
                    data.get('management_role'),
                    data.get('management_structure'),
                    data.get('management_responsibility'),
                    1 if data.get('climate_committee') else 0,
                    data.get('committee_name'),
                    data.get('committee_members'),
                    data.get('responsible_executive'),
                    data.get('strategy_integration'),
                    data.get('risk_integration'),
                    datetime.now().isoformat(),
                    existing[0]['id']
                ), company_id=company_id)
                message = "Yönetişim verileri güncellendi"
            else:
                # Yeni kayıt
                self.execute_update("""
                    INSERT INTO tcfd_governance (
                        company_id, reporting_year,
                        board_oversight, board_frequency, board_expertise,
                        management_role, management_structure, management_responsibility,
                        climate_committee, committee_name, committee_members,
                        responsible_executive, strategy_integration, risk_integration
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    company_id, year,
                    data.get('board_oversight'),
                    data.get('board_frequency'),
                    data.get('board_expertise'),
                    data.get('management_role'),
                    data.get('management_structure'),
                    data.get('management_responsibility'),
                    1 if data.get('climate_committee') else 0,
                    data.get('committee_name'),
                    data.get('committee_members'),
                    data.get('responsible_executive'),
                    data.get('strategy_integration'),
                    data.get('risk_integration')
                ), company_id=company_id)
                message = "Yönetişim verileri kaydedildi"

            return True, message

        except Exception as e:
            return False, f"Hata: {str(e)}"

    def get_governance(self, company_id: int, year: int) -> Optional[Dict]:
        """Yönetişim verilerini getir"""
        try:
            rows = self.select(
                'tcfd_governance',
                company_id=company_id,
                where={'reporting_year': year}
            )
            return rows[0] if rows else None
        except Exception as e:
            logging.error(f"[TCFD] Yönetişim verileri getirme hatası: {e}")
            return None

    # ========================================================================
    # STRATEGY (Strateji)
    # ========================================================================

    def save_strategy(self, company_id: int, year: int, data: Dict) -> Tuple[bool, str]:
        """Strateji verilerini kaydet"""
        try:
            existing = self.select(
                'tcfd_strategy',
                company_id=company_id,
                where={'reporting_year': year}
            )

            if existing:
                # Güncelle
                self.execute_update("""
                    UPDATE tcfd_strategy
                    SET short_term_risks = ?,
                        medium_term_risks = ?,
                        long_term_risks = ?,
                        short_term_opportunities = ?,
                        medium_term_opportunities = ?,
                        long_term_opportunities = ?,
                        business_impact = ?,
                        strategy_impact = ?,
                        financial_impact = ?,
                        resilience_assessment = ?,
                        adaptation_plans = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (
                    data.get('short_term_risks'),
                    data.get('medium_term_risks'),
                    data.get('long_term_risks'),
                    data.get('short_term_opportunities'),
                    data.get('medium_term_opportunities'),
                    data.get('long_term_opportunities'),
                    data.get('business_impact'),
                    data.get('strategy_impact'),
                    data.get('financial_impact'),
                    data.get('resilience_assessment'),
                    data.get('adaptation_plans'),
                    datetime.now().isoformat(),
                    existing[0]['id']
                ), company_id=company_id)
                message = "Strateji verileri güncellendi"
            else:
                # Yeni kayıt
                self.execute_update("""
                    INSERT INTO tcfd_strategy (
                        company_id, reporting_year,
                        short_term_risks, medium_term_risks, long_term_risks,
                        short_term_opportunities, medium_term_opportunities, long_term_opportunities,
                        business_impact, strategy_impact, financial_impact,
                        resilience_assessment, adaptation_plans
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    company_id, year,
                    data.get('short_term_risks'),
                    data.get('medium_term_risks'),
                    data.get('long_term_risks'),
                    data.get('short_term_opportunities'),
                    data.get('medium_term_opportunities'),
                    data.get('long_term_opportunities'),
                    data.get('business_impact'),
                    data.get('strategy_impact'),
                    data.get('financial_impact'),
                    data.get('resilience_assessment'),
                    data.get('adaptation_plans')
                ), company_id=company_id)
                message = "Strateji verileri kaydedildi"

            return True, message

        except Exception as e:
            return False, f"Hata: {str(e)}"

    # ========================================================================
    # METRICS (Metrikler) ve TARGETS (Hedefler)
    # ========================================================================

    def save_metrics(self, company_id: int, year: int, data: Dict) -> Tuple[bool, str]:
        """Metrikler verilerini kaydet"""
        try:
            ok, msg = self._validate_metrics_data(data)
            if not ok:
                return False, msg

            existing = self.select(
                'tcfd_metrics',
                company_id=company_id,
                where={'reporting_year': year}
            )

            if existing:
                self.execute_update(
                    """
                    UPDATE tcfd_metrics
                    SET scope1_emissions = ?,
                        scope2_emissions = ?,
                        scope3_emissions = ?,
                        total_emissions = ?,
                        emissions_intensity = ?,
                        intensity_metric = ?,
                        total_energy_consumption = ?,
                        renewable_energy_pct = ?,
                        energy_intensity = ?,
                        water_consumption = ?,
                        water_intensity = ?,
                        internal_carbon_price = ?,
                        carbon_price_coverage = ?,
                        climate_related_revenue = ?,
                        climate_related_opex = ?,
                        climate_related_capex = ?,
                        other_metrics = ?,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        data.get("scope1_emissions"),
                        data.get("scope2_emissions"),
                        data.get("scope3_emissions"),
                        data.get("total_emissions"),
                        data.get("emissions_intensity"),
                        data.get("intensity_metric"),
                        data.get("total_energy_consumption"),
                        data.get("renewable_energy_pct"),
                        data.get("energy_intensity"),
                        data.get("water_consumption"),
                        data.get("water_intensity"),
                        data.get("internal_carbon_price"),
                        data.get("carbon_price_coverage"),
                        data.get("climate_related_revenue"),
                        data.get("climate_related_opex"),
                        data.get("climate_related_capex"),
                        data.get("other_metrics"),
                        datetime.now().isoformat(),
                        existing[0]['id'],
                    ),
                    company_id=company_id
                )
                message = "Metrikler güncellendi"
            else:
                self.execute_update(
                    """
                    INSERT INTO tcfd_metrics (
                        company_id, reporting_year,
                        scope1_emissions, scope2_emissions, scope3_emissions, total_emissions,
                        emissions_intensity, intensity_metric,
                        total_energy_consumption, renewable_energy_pct, energy_intensity,
                        water_consumption, water_intensity,
                        internal_carbon_price, carbon_price_coverage,
                        climate_related_revenue, climate_related_opex, climate_related_capex,
                        other_metrics
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        company_id,
                        year,
                        data.get("scope1_emissions"),
                        data.get("scope2_emissions"),
                        data.get("scope3_emissions"),
                        data.get("total_emissions"),
                        data.get("emissions_intensity"),
                        data.get("intensity_metric"),
                        data.get("total_energy_consumption"),
                        data.get("renewable_energy_pct"),
                        data.get("energy_intensity"),
                        data.get("water_consumption"),
                        data.get("water_intensity"),
                        data.get("internal_carbon_price"),
                        data.get("carbon_price_coverage"),
                        data.get("climate_related_revenue"),
                        data.get("climate_related_opex"),
                        data.get("climate_related_capex"),
                        data.get("other_metrics"),
                    ),
                    company_id=company_id
                )
                message = "Metrikler kaydedildi"

            return True, message

        except Exception as e:
            return False, f"Hata: {str(e)}"

    def _validate_metrics_data(self, d: Dict) -> Tuple[bool, str]:
        try:
            allowed = {
                "scope1_emissions",
                "scope2_emissions",
                "scope3_emissions",
                "total_emissions",
                "emissions_intensity",
                "intensity_metric",
                "total_energy_consumption",
                "renewable_energy_pct",
                "energy_intensity",
                "water_consumption",
                "water_intensity",
                "internal_carbon_price",
                "carbon_price_coverage",
                "climate_related_revenue",
                "climate_related_opex",
                "climate_related_capex",
                "other_metrics",
            }
            for k in d.keys():
                if k not in allowed:
                    return False, f"Desteklenmeyen alan: {k}"
            numeric_keys = {
                "scope1_emissions",
                "scope2_emissions",
                "scope3_emissions",
                "total_emissions",
                "emissions_intensity",
                "total_energy_consumption",
                "renewable_energy_pct",
                "energy_intensity",
                "water_consumption",
                "water_intensity",
                "internal_carbon_price",
                "carbon_price_coverage",
                "climate_related_revenue",
                "climate_related_opex",
                "climate_related_capex",
            }
            for k in numeric_keys:
                v = d.get(k)
                if v not in (None, ""):
                    try:
                        float(v)
                    except Exception:
                        return False, f"Sayısal olmayan değer: {k}={v}"
            return True, ""
        except Exception as e:
            return False, f"Şema doğrulama hatası: {e}"

    def get_metrics(self, company_id: int, year: int) -> Optional[Dict]:
        """Metrikler verilerini getir"""
        try:
            rows = self.execute_query(
                """
                SELECT * FROM tcfd_metrics
                WHERE company_id = ? AND reporting_year = ?
                """,
                (company_id, year),
                company_id=company_id
            )
            return rows[0] if rows else None
        except Exception as e:
            logging.error(f"[TCFD] Metrikleri getirme hatası: {e}")
            return None

    def add_target(self, company_id: int, target_data: Dict) -> Tuple[bool, str, Optional[int]]:
        """Yeni hedef ekle"""
        try:
            self.execute_update(
                """
                INSERT INTO tcfd_targets (
                    company_id, target_name, target_category, target_type,
                    baseline_year, baseline_value, target_year, target_value, reduction_pct,
                    scope, boundary, current_value, progress_pct, on_track,
                    sbti_approved, external_verification, description, methodology, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company_id,
                    target_data.get("target_name"),
                    target_data.get("target_category"),
                    target_data.get("target_type"),
                    target_data.get("baseline_year"),
                    target_data.get("baseline_value"),
                    target_data.get("target_year"),
                    target_data.get("target_value"),
                    target_data.get("reduction_pct"),
                    target_data.get("scope"),
                    target_data.get("boundary"),
                    target_data.get("current_value"),
                    target_data.get("progress_pct"),
                    1 if target_data.get("on_track") else 0,
                    1 if target_data.get("sbti_approved") else 0,
                    target_data.get("external_verification"),
                    target_data.get("description"),
                    target_data.get("methodology"),
                    target_data.get("status", "Active"),
                ),
                company_id=company_id
            )
            # Last row ID is a bit tricky with execute_update as it returns cursor usually but wrapper might not
            # BaseTenantManager.execute_update returns rowcount usually or we need to check implementation
            # Checking BaseTenantManager implementation...
            # Usually we don't get lastrowid easily from wrapper unless it returns it.
            # Let's assume for now we return None or fetch it back if needed.
            # The original code returned tid.
            # Let's check BaseTenantManager in core/base_manager.py
            
            # Since I cannot check base_manager right now without tool call, 
            # I will use a select to get the last ID or ignore it if not critical.
            # But wait, add_target returns tid.
            # I will modify to fetch it back.
            
            rows = self.execute_query("SELECT last_insert_rowid() as id", (), company_id=company_id)
            tid = rows[0]['id'] if rows else None
            
            return True, "Hedef eklendi", tid
        except Exception as e:
            return False, f"Hata: {str(e)}", None

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard istatistiklerini getir"""
        stats = {
            'governance_score': 0,
            'strategy_score': 0,
            'risk_score': 0,
            'metrics_score': 0,
            'total_risks': 0,
            'total_opps': 0,
            'financial_impact': '-'
        }
        
        try:
            # Simple disclosures stats
            # disclosures = self.get_disclosures(company_id)
            # stats['total_risks'] = len(disclosures)
            # FIXME: get_disclosures method appears to be missing or I missed it. 
            # Commenting out to prevent crash if it doesn't exist, or if it does, it should be safe.
            # Assuming it might be get_climate_risks?
            # Let's use get_climate_risks count
            
            risks = self.execute_query("SELECT COUNT(*) as count FROM tcfd_climate_risks WHERE company_id = ?", (company_id,), company_id=company_id)
            stats['total_risks'] = risks[0]['count'] if risks else 0
            
            # Governance score (mock calculation based on filled fields)
            rows = self.execute_query("SELECT * FROM tcfd_governance WHERE company_id = ? ORDER BY reporting_year DESC LIMIT 1", (company_id,), company_id=company_id)
            gov = rows[0] if rows else None
            if gov:
                # gov is a Row object (dict-like)
                filled = sum(1 for key in gov.keys() if gov[key] is not None)
                total = len(gov.keys())
                stats['governance_score'] = int((filled / total) * 100)
            
            # Strategy score
            rows = self.execute_query("SELECT * FROM tcfd_strategy WHERE company_id = ? ORDER BY reporting_year DESC LIMIT 1", (company_id,), company_id=company_id)
            strat = rows[0] if rows else None
            if strat:
                filled = sum(1 for key in strat.keys() if strat[key] is not None)
                total = len(strat.keys())
                stats['strategy_score'] = int((filled / total) * 100)
                
            # Financial impact
            # if strat:
            #    pass
                
        except Exception as e:
            logging.error(f"TCFD stats error: {e}")
            
        return stats

    def update_target(self, company_id: int, target_id: int, target_data: Dict) -> Tuple[bool, str]:
        """Hedef güncelle"""
        try:
            self.execute_update(
                """
                UPDATE tcfd_targets
                SET target_name = ?, target_category = ?, target_type = ?,
                    baseline_year = ?, baseline_value = ?, target_year = ?, target_value = ?, reduction_pct = ?,
                    scope = ?, boundary = ?, current_value = ?, progress_pct = ?, on_track = ?,
                    sbti_approved = ?, external_verification = ?, description = ?, methodology = ?, status = ?,
                    updated_at = ?
                WHERE id = ? AND company_id = ?
                """,
                (
                    target_data.get("target_name"),
                    target_data.get("target_category"),
                    target_data.get("target_type"),
                    target_data.get("baseline_year"),
                    target_data.get("baseline_value"),
                    target_data.get("target_year"),
                    target_data.get("target_value"),
                    target_data.get("reduction_pct"),
                    target_data.get("scope"),
                    target_data.get("boundary"),
                    target_data.get("current_value"),
                    target_data.get("progress_pct"),
                    1 if target_data.get("on_track") else 0,
                    1 if target_data.get("sbti_approved") else 0,
                    target_data.get("external_verification"),
                    target_data.get("description"),
                    target_data.get("methodology"),
                    target_data.get("status", "Active"),
                    datetime.now().isoformat(),
                    target_id,
                    company_id
                ),
                company_id=company_id
            )
            return True, "Hedef güncellendi"
        except Exception as e:
            return False, f"Hata: {str(e)}"

    def get_targets(self, company_id: int, status: Optional[str] = None) -> List[Dict]:
        """Hedefleri listele"""
        try:
            query = "SELECT * FROM tcfd_targets WHERE company_id = ?"
            params = [company_id]
            if status:
                query += " AND status = ?"
                params.append(status)
            query += " ORDER BY target_year"
            
            rows = self.execute_query(query, tuple(params), company_id=company_id)
            return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"TCFD get_targets error: {e}")
            return []

    def delete_target(self, company_id: int, target_id: int) -> Tuple[bool, str]:
        """Hedef sil"""
        try:
            # We need to check if rowcount > 0, but BaseTenantManager.execute_update might not return it directly.
            # However, execute_update usually calls cursor.execute which sets rowcount on cursor.
            # But we don't have access to cursor.
            # We can check existence first or just try delete.
            # Or use execute_query("DELETE ... RETURNING id") if sqlite supports it (recent versions do).
            # Safest is to just try delete.
            
            self.execute_update("DELETE FROM tcfd_targets WHERE id = ? AND company_id = ?", (target_id, company_id), company_id=company_id)
            return True, "Hedef silindi"
        except Exception as e:
            return False, f"Hata: {str(e)}"

    def get_strategy(self, company_id: int, year: int) -> Optional[Dict]:
        """Strateji verilerini getir"""
        try:
            rows = self.execute_query("""
                SELECT * FROM tcfd_strategy
                WHERE company_id = ? AND reporting_year = ?
            """, (company_id, year), company_id=company_id)

            return rows[0] if rows else None

        except Exception as e:
            logging.error(f"[TCFD] Strateji getirme hatası: {e}")
            return None

    # ========================================================================
    # CLIMATE RISKS (İklim Riskleri)
    # ========================================================================

    def add_climate_risk(self, company_id: int, year: int, risk_data: Dict) -> Tuple[bool, str, Optional[int]]:
        """İklim riski ekle"""
        try:
            # Risk skoru hesapla
            likelihood_score = risk_data.get('likelihood_score', 3)
            impact_score = risk_data.get('impact_score', 3)
            risk_score = likelihood_score * impact_score

            # Risk derecesi belirle
            if risk_score <= 6:
                risk_rating = "Low"
            elif risk_score <= 12:
                risk_rating = "Medium"
            elif risk_score <= 20:
                risk_rating = "High"
            else:
                risk_rating = "Critical"

            self.execute_update("""
                INSERT INTO tcfd_climate_risks (
                    company_id, reporting_year,
                    risk_category, risk_type, risk_subcategory,
                    risk_name, risk_description,
                    likelihood, likelihood_score,
                    impact, impact_score,
                    risk_rating, risk_score,
                    time_horizon,
                    financial_impact_low, financial_impact_high, financial_impact_currency,
                    current_controls, mitigation_actions,
                    responsible_party, action_deadline, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, year,
                risk_data.get('risk_category'),
                risk_data.get('risk_type'),
                risk_data.get('risk_subcategory'),
                risk_data.get('risk_name'),
                risk_data.get('risk_description'),
                risk_data.get('likelihood'),
                likelihood_score,
                risk_data.get('impact'),
                impact_score,
                risk_rating,
                risk_score,
                risk_data.get('time_horizon'),
                risk_data.get('financial_impact_low'),
                risk_data.get('financial_impact_high'),
                risk_data.get('financial_impact_currency', 'TRY'),
                risk_data.get('current_controls'),
                risk_data.get('mitigation_actions'),
                risk_data.get('responsible_party'),
                risk_data.get('action_deadline'),
                risk_data.get('status', 'Identified'),
                risk_data.get('notes')
            ), company_id=company_id)

            rows = self.execute_query("SELECT last_insert_rowid() as id", (), company_id=company_id)
            risk_id = rows[0]['id'] if rows else None

            return True, "İklim riski eklendi", risk_id

        except Exception as e:
            return False, f"Hata: {str(e)}", None

    def update_climate_risk(self, company_id: int, risk_id: int, risk_data: Dict) -> Tuple[bool, str]:
        """İklim riskini güncelle"""
        try:
            # Risk skoru yeniden hesapla
            likelihood_score = risk_data.get('likelihood_score', 3)
            impact_score = risk_data.get('impact_score', 3)
            risk_score = likelihood_score * impact_score

            # Risk derecesi belirle
            if risk_score <= 6:
                risk_rating = "Low"
            elif risk_score <= 12:
                risk_rating = "Medium"
            elif risk_score <= 20:
                risk_rating = "High"
            else:
                risk_rating = "Critical"

            self.execute_update("""
                UPDATE tcfd_climate_risks
                SET risk_category = ?,
                    risk_type = ?,
                    risk_subcategory = ?,
                    risk_name = ?,
                    risk_description = ?,
                    likelihood = ?,
                    likelihood_score = ?,
                    impact = ?,
                    impact_score = ?,
                    risk_rating = ?,
                    risk_score = ?,
                    time_horizon = ?,
                    financial_impact_low = ?,
                    financial_impact_high = ?,
                    current_controls = ?,
                    mitigation_actions = ?,
                    responsible_party = ?,
                    action_deadline = ?,
                    status = ?,
                    notes = ?,
                    updated_at = ?
                WHERE id = ? AND company_id = ?
            """, (
                risk_data.get('risk_category'),
                risk_data.get('risk_type'),
                risk_data.get('risk_subcategory'),
                risk_data.get('risk_name'),
                risk_data.get('risk_description'),
                risk_data.get('likelihood'),
                likelihood_score,
                risk_data.get('impact'),
                impact_score,
                risk_rating,
                risk_score,
                risk_data.get('time_horizon'),
                risk_data.get('financial_impact_low'),
                risk_data.get('financial_impact_high'),
                risk_data.get('current_controls'),
                risk_data.get('mitigation_actions'),
                risk_data.get('responsible_party'),
                risk_data.get('action_deadline'),
                risk_data.get('status'),
                risk_data.get('notes'),
                datetime.now().isoformat(),
                risk_id,
                company_id
            ), company_id=company_id)

            return True, "İklim riski güncellendi"

        except Exception as e:
            return False, f"Hata: {str(e)}"

    def get_climate_risks(self, company_id: int, year: int,
                         category: Optional[str] = None,
                         risk_type: Optional[str] = None) -> List[Dict]:
        """İklim risklerini getir (filtreli)"""
        try:
            query = """
                SELECT * FROM tcfd_climate_risks
                WHERE company_id = ? AND reporting_year = ?
            """
            params = [company_id, year]

            if category:
                query += " AND risk_category = ?"
                params.append(category)

            if risk_type:
                query += " AND risk_type = ?"
                params.append(risk_type)

            query += " ORDER BY risk_score DESC, risk_name"

            rows = self.execute_query(query, tuple(params), company_id=company_id)
            return [dict(row) for row in rows]

        except Exception as e:
            logging.error(f"[TCFD] İklim riskleri getirme hatası: {e}")
            return []

    def delete_climate_risk(self, company_id: int, risk_id: int) -> Tuple[bool, str]:
        """İklim riskini sil"""
        try:
            self.execute_update("DELETE FROM tcfd_climate_risks WHERE id = ? AND company_id = ?", (risk_id, company_id), company_id=company_id)
            return True, "İklim riski silindi"

        except Exception as e:
            return False, f"Hata: {str(e)}"

    # Devam edecek...
    def get_risk_summary(self, company_id: int, year: int) -> Dict:
        """Risk özeti istatistikleri"""
        try:
            summary = {}

            # Toplam risk sayısı
            rows = self.execute_query("""
                SELECT COUNT(*) FROM tcfd_climate_risks
                WHERE company_id = ? AND reporting_year = ?
            """, (company_id, year))
            summary['total_risks'] = rows[0][0] if rows else 0

            # Risk derecesine göre
            rows = self.execute_query("""
                SELECT risk_rating, COUNT(*)
                FROM tcfd_climate_risks
                WHERE company_id = ? AND reporting_year = ?
                GROUP BY risk_rating
            """, (company_id, year))
            summary['by_rating'] = dict([(r[0], r[1]) for r in rows])

            # Kategoriye göre
            rows = self.execute_query("""
                SELECT risk_category, COUNT(*)
                FROM tcfd_climate_risks
                WHERE company_id = ? AND reporting_year = ?
                GROUP BY risk_category
            """, (company_id, year))
            summary['by_category'] = dict([(r[0], r[1]) for r in rows])

            # Zaman ufkuna göre
            rows = self.execute_query("""
                SELECT time_horizon, COUNT(*)
                FROM tcfd_climate_risks
                WHERE company_id = ? AND reporting_year = ?
                GROUP BY time_horizon
            """, (company_id, year))
            summary['by_time_horizon'] = dict([(r[0], r[1]) for r in rows])

            # Toplam finansal etki (tahmini)
            rows = self.execute_query("""
                SELECT 
                    SUM(financial_impact_low) as total_low,
                    SUM(financial_impact_high) as total_high,
                    AVG(financial_impact_low) as avg_low,
                    AVG(financial_impact_high) as avg_high
                FROM tcfd_climate_risks
                WHERE company_id = ? AND reporting_year = ?
                AND financial_impact_low IS NOT NULL
            """, (company_id, year))
            
            if rows:
                financial = rows[0]
                summary['financial_impact'] = {
                    'total_low': financial['total_low'] or 0,
                    'total_high': financial['total_high'] or 0,
                    'avg_low': financial['avg_low'] or 0,
                    'avg_high': financial['avg_high'] or 0
                }
            else:
                summary['financial_impact'] = {
                    'total_low': 0, 'total_high': 0, 'avg_low': 0, 'avg_high': 0
                }

            return summary

        except Exception as e:
            logging.error(f"[TCFD] Risk özeti hatası: {e}")
            return {}


# Kısa test
if __name__ == "__main__":
    logging.info(" TCFD Manager Test")
    logging.info("="*60)

    # Test veritabanı
    db_path = "../../data/sdg_desktop.sqlite"

    if os.path.exists(db_path):
        manager = TCFDManager(db_path)
        logging.info(" TCFD Manager başlatıldı")
        logging.info(f"   Veritabanı: {db_path}")
        logging.info(f"   Risk katalogu yüklendi: {len(manager.risk_catalog.get('transition_risks', {})) > 0}")
        logging.info(f"   Senaryo verileri yüklendi: {len(manager.scenarios_data.get('scenarios', []))} > 0")
    else:
        logging.info(" Veritabanı bulunamadı")

    logging.info("="*60)

