#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Manager - OpenAI entegrasyonu ve rapor olusturma
"""

import logging
import json
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from backend.core.language_manager import LanguageManager
except ImportError:
    try:
        from core.language_manager import LanguageManager
    except ImportError:
        class LanguageManager:
            def __init__(self, base_dir): pass
            def get_text(self, key, lang=None, default=None): return default or key

from modules.reporting.advanced_report_manager import AdvancedReportManager
from modules.ai.prompts import get_prompt
from config.database import DB_PATH
from modules.ai.report_validator import ReportValidator


class AIManager:
    """AI islemlerini yoneten sinif"""

    def __init__(self, db_path: str = DB_PATH):
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)

        self.db_path = db_path
        self.base_dir = os.path.dirname(os.path.dirname(db_path))
        
        # Initialize LanguageManager
        try:
            root_dir = os.path.dirname(self.base_dir)
            self.lm = LanguageManager(root_dir)
        except Exception as e:
            logging.error(f"LanguageManager initialization failed: {e}")
            # Fallback mock
            self.lm = type('MockLM', (), {'get_text': lambda s, k, l=None, d=None: d or k})()

        # Konfigurasyonu yukle
        self.config = self._load_config()
        self.api_key = self.config.get("api_key")
        self.model = self.config.get("model", "gpt-3.5-turbo")
        self.temperature = float(self.config.get("temperature", 0.7))
        self.max_tokens = int(self.config.get("max_tokens", 1000))
        
        self.client = None

        if self.api_key:
            self._init_openai()
            
        # Initialize Validator
        self.validator = ReportValidator()

    def _get_text_safe(self, key: str, lang: str = "tr", default: str = None) -> str:
        """LanguageManager uzerinden guvenli ceviri al"""
        try:
            return self.lm.get_text(key, lang, default)
        except Exception as e:
            logging.error(f"Translation error for key {key}: {e}")
            return default or key

    def _load_config(self) -> Dict[str, Any]:
        """Konfigurasyonu .env dosyasindan yukle"""
        config = {
            "api_key": None,
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        candidates = []
        try:
            candidates.append(os.path.join(self.base_dir, ".env"))
        except Exception:
            pass
        try:
            root_dir = os.path.dirname(self.base_dir)
            candidates.append(os.path.join(root_dir, ".env"))
        except Exception:
            pass
        try:
            candidates.append(os.path.join(os.getcwd(), ".env"))
        except Exception:
            pass
            
        seen = set()
        for env_file in candidates:
            if not env_file or env_file in seen:
                continue
            seen.add(env_file)
            if not os.path.exists(env_file):
                continue
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip()
                            
                            if key == "OPENAI_API_KEY":
                                config["api_key"] = value
                            elif key == "AI_MODEL":
                                config["model"] = value
                            elif key == "AI_TEMPERATURE":
                                try:
                                    config["temperature"] = float(value)
                                except ValueError:
                                    pass
                            elif key == "AI_MAX_TOKENS":
                                try:
                                    config["max_tokens"] = int(value)
                                except ValueError:
                                    pass
            except Exception as e:
                logging.error(f"[HATA] Config okunamadi ({env_file}): {e}")
        
        return config

    def _init_openai(self):
        """OpenAI client baslatma"""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            logging.info("[OK] OpenAI client baslatildi")
        except ImportError:
            logging.info("[UYARI] openai paketi yuklu degil. pip install openai")
            self.client = None
        except Exception as e:
            logging.error(f"[HATA] OpenAI client baslatilamadi: {e}")
            self.client = None

    def is_available(self) -> bool:
        """AI ozellikleri kullanilabilir mi?"""
        return self.client is not None

    def build_unified_kpi_snapshot(
        self,
        company_id: int,
        reporting_period: str,
        selected_modules: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        snapshot: Dict[str, Any] = {
            "company": {},
            "period": {},
            "kpis": [],
            "alignments": {}
        }
        try:
            year = int(str(reporting_period)[:4])
        except Exception:
            year = datetime.now().year
        snapshot["period"] = {"year": year, "label": str(reporting_period)}
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            company_info: Dict[str, Any] = {}
            try:
                cursor.execute("PRAGMA table_info(companies)")
                cols = [row[1] for row in cursor.fetchall()]
                if cols:
                    base_cols: List[str] = []
                    for name in ["id", "name", "sector", "industry", "country"]:
                        if name in cols:
                            base_cols.append(name)
                    if base_cols:
                        query = "SELECT " + ",".join(base_cols) + " FROM companies WHERE id = ?"
                        cursor.execute(query, (company_id,))
                        row = cursor.fetchone()
                        if row:
                            for idx, name in enumerate(base_cols):
                                company_info[name] = row[idx]
            except Exception as e:
                logging.error(f"Unified KPI snapshot company read error: {e}")
            snapshot["company"] = company_info
            conn.close()
        except Exception as e:
            logging.error(f"Unified KPI snapshot connection error: {e}")
        modules = selected_modules or []
        try:
            sdg_kpis = self._export_sdg_kpis(company_id)
            if sdg_kpis:
                snapshot["kpis"].extend(sdg_kpis)
        except Exception as e:
            logging.error(f"Unified KPI snapshot SDG export error: {e}")
        try:
            gri_kpis = self._export_gri_kpis(company_id)
            if gri_kpis:
                snapshot["kpis"].extend(gri_kpis)
        except Exception as e:
            logging.error(f"Unified KPI snapshot GRI export error: {e}")
        try:
            tsrs_kpis = self._export_tsrs_kpis(company_id, reporting_period)
            if tsrs_kpis:
                snapshot["kpis"].extend(tsrs_kpis)
        except Exception as e:
            logging.error(f"Unified KPI snapshot TSRS export error: {e}")
        try:
            issb_kpis = self._export_issb_kpis(company_id, year)
            if issb_kpis:
                snapshot["kpis"].extend(issb_kpis)
        except Exception as e:
            logging.error(f"Unified KPI snapshot ISSB export error: {e}")
        try:
            csrd_kpis = self._export_csrd_kpis(company_id, year)
            if csrd_kpis:
                snapshot["kpis"].extend(csrd_kpis)
        except Exception as e:
            logging.error(f"Unified KPI snapshot CSRD export error: {e}")
        try:
            carbon_kpis = self._export_carbon_kpis(company_id, year)
            if carbon_kpis:
                snapshot["kpis"].extend(carbon_kpis)
        except Exception as e:
            logging.error(f"Unified KPI snapshot carbon export error: {e}")
        try:
            energy_kpis = self._export_energy_kpis(company_id)
            if energy_kpis:
                snapshot["kpis"].extend(energy_kpis)
        except Exception as e:
            logging.error(f"Unified KPI snapshot energy export error: {e}")
        try:
            water_kpis = self._export_water_kpis(company_id, year)
            if water_kpis:
                snapshot["kpis"].extend(water_kpis)
        except Exception as e:
            logging.error(f"Unified KPI snapshot water export error: {e}")
        try:
            waste_kpis = self._export_waste_kpis(company_id, year)
            if waste_kpis:
                snapshot["kpis"].extend(waste_kpis)
        except Exception as e:
            logging.error(f"Unified KPI snapshot waste export error: {e}")
        try:
            sc_kpis = self._export_supply_chain_kpis(company_id)
            if sc_kpis:
                snapshot["kpis"].extend(sc_kpis)
        except Exception as e:
            logging.error(f"Unified KPI snapshot supply-chain export error: {e}")
        try:
            social_kpis = self._export_social_kpis(company_id, year)
            if social_kpis:
                snapshot["kpis"].extend(social_kpis)
        except Exception as e:
            logging.error(f"Unified KPI snapshot social export error: {e}")
        try:
            from modules.mapping.mapping_manager import MappingManager
            mapping_manager = MappingManager(self.db_path)
            mappings = mapping_manager.get_all_mappings({"verified_only": True})
            snapshot["alignments"]["standard_mappings"] = mappings
        except Exception as e:
            logging.error(f"Unified KPI snapshot alignment load error: {e}")
        try:
            snapshots_dir = os.path.join(self.base_dir, "ai_snapshots")
            os.makedirs(snapshots_dir, exist_ok=True)
            safe_period = str(reporting_period).replace("/", "-").replace("\\", "-").replace(" ", "_")
            filename = f"company_{company_id}_{year}_{safe_period}.json"
            file_path = os.path.join(snapshots_dir, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, ensure_ascii=False, indent=2)
            snapshot["snapshot_file"] = file_path
        except Exception as e:
            logging.error(f"Unified KPI snapshot file write error: {e}")
        return snapshot

    def _export_sdg_kpis(self, company_id: int) -> List[Dict[str, Any]]:
        try:
            from modules.sdg.sdg_data_validation import SDGDataValidation
        except ImportError:
            return []
        validator = SDGDataValidation(self.db_path)
        scores_by_sdg = validator.calculate_quality_scores_by_sdg(company_id)
        if not scores_by_sdg:
            return []
        kpis: List[Dict[str, Any]] = []
        goal_titles: Dict[int, Dict[str, Any]] = {}
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT id, code, title_tr FROM sdg_goals")
                for row in cursor.fetchall():
                    try:
                        num = int(str(row[1]))
                        goal_titles[num] = {"code": row[1], "title": row[2]}
                    except Exception:
                        continue
            except Exception:
                pass
            conn.close()
        except Exception as e:
            logging.error(f"Unified KPI snapshot SDG goal titles error: {e}")
        for sdg_no, scores in scores_by_sdg.items():
            info = goal_titles.get(sdg_no, {})
            code_str = info.get("code") or f"SDG{sdg_no}"
            title_str = info.get("title") or ""
            for key, value in scores.items():
                kpi_code = f"{code_str}_{key.upper()}"
                name_parts: List[str] = [f"SDG {sdg_no}"]
                if title_str:
                    name_parts.append(title_str)
                name_parts.append(key)
                kpis.append(
                    {
                        "module": "sdg",
                        "module_subtype": "quality",
                        "code": kpi_code,
                        "name": " - ".join(name_parts),
                        "value": value,
                        "unit": "%",
                        "year": None,
                        "direction": "higher_is_better",
                        "mappings": {
                            "sdg_goal": str(sdg_no)
                        },
                        "meta": {
                            "dimension": key
                        }
                    }
                )
        return kpis

    def _export_gri_kpis(self, company_id: int) -> List[Dict[str, Any]]:
        try:
            from modules.gri.gri_kpi_reports import GRIKPIReports
        except ImportError:
            return []
        reports = GRIKPIReports(self.db_path)
        dashboard = reports.generate_kpi_dashboard(company_id)
        if not dashboard:
            return []
        kpis: List[Dict[str, Any]] = []
        for category_key in ["universal", "economic", "environmental", "social", "sector"]:
            items = dashboard.get(category_key) or []
            for kpi in items:
                period = kpi.get("period")
                year_val: Optional[int] = None
                if period:
                    try:
                        year_val = int(str(period)[:4])
                    except Exception:
                        year_val = None
                kpis.append(
                    {
                        "module": "gri",
                        "module_subtype": category_key,
                        "code": kpi.get("disclosure_code") or "",
                        "name": kpi.get("kpi_name") or "",
                        "value": kpi.get("numerical_value"),
                        "unit": kpi.get("unit"),
                        "year": year_val,
                        "direction": None,
                        "mappings": {
                            "gri_disclosure": kpi.get("disclosure_code"),
                            "gri_standard": kpi.get("standard_code")
                        },
                        "meta": {
                            "category": kpi.get("category"),
                            "response_value": kpi.get("response_value"),
                            "reporting_status": kpi.get("reporting_status"),
                            "period": period,
                            "has_response": kpi.get("has_response")
                        }
                    }
                )
        return kpis

    def _export_tsrs_kpis(self, company_id: int, reporting_period: str) -> List[Dict[str, Any]]:
        try:
            from modules.tsrs.tsrs_manager import TSRSManager
        except ImportError:
            return []
        manager = TSRSManager(self.db_path)
        responses = manager.get_tsrs_responses(company_id, reporting_period)
        if not responses:
            return []
        kpis: List[Dict[str, Any]] = []
        for row in responses:
            period = row.get("reporting_period")
            year_val: Optional[int] = None
            if period:
                try:
                    year_val = int(str(period)[:4])
                except Exception:
                    year_val = None
            kpis.append(
                {
                    "module": "tsrs",
                    "module_subtype": row.get("category"),
                    "code": row.get("indicator_code") or "",
                    "name": row.get("indicator_title") or "",
                    "value": row.get("numerical_value"),
                    "unit": row.get("unit"),
                    "year": year_val,
                    "direction": None,
                    "mappings": {
                        "tsrs_standard": row.get("standard_code"),
                        "tsrs_indicator": row.get("indicator_code")
                    },
                    "meta": {
                        "response_value": row.get("response_value"),
                        "reporting_status": row.get("reporting_status"),
                        "period": period,
                        "data_source": row.get("data_source"),
                        "methodology_used": row.get("methodology_used")
                    }
                }
            )
        return kpis

    def _export_csrd_kpis(self, company_id: int, year: int) -> List[Dict[str, Any]]:
        try:
            from modules.csrd.csrd_compliance_manager import CSRDComplianceManager
        except ImportError:
            return []
        manager = CSRDComplianceManager(self.db_path)
        summary = manager.get_csrd_compliance_summary(company_id)
        stats = manager.get_dashboard_stats(company_id)
        taxonomy_stats = manager.get_taxonomy_stats(company_id)
        kpis: List[Dict[str, Any]] = []
        total_req = summary.get("total_requirements") or 0
        completed_req = summary.get("completed") or 0
        compliance_pct = summary.get("compliance_percentage")
        if total_req > 0 and compliance_pct is not None:
            kpis.append(
                {
                    "module": "csrd",
                    "module_subtype": "compliance",
                    "code": "CSRD_COMPLIANCE_PCT",
                    "name": "CSRD uyum oranı",
                    "value": compliance_pct,
                    "unit": "%",
                    "year": year,
                    "direction": "higher_is_better",
                    "mappings": {
                        "framework": "CSRD/ESRS"
                    },
                    "meta": {
                        "company_id": company_id,
                        "total_requirements": total_req,
                        "completed_requirements": completed_req,
                        "in_progress_requirements": summary.get("in_progress") or 0,
                        "not_started_requirements": summary.get("not_started") or 0,
                    },
                }
            )
        material_topics = stats.get("material_topics")
        if material_topics is not None:
            kpis.append(
                {
                    "module": "csrd",
                    "module_subtype": "double_materiality",
                    "code": "CSRD_MATERIAL_TOPICS_COUNT",
                    "name": "Önemli konu sayısı (çift önemlilik)",
                    "value": material_topics,
                    "unit": "adet",
                    "year": year,
                    "direction": None,
                    "mappings": {},
                    "meta": {
                        "company_id": company_id,
                    },
                }
            )
        completed_disclosures = stats.get("completed_disclosures")
        if completed_disclosures is not None:
            kpis.append(
                {
                    "module": "csrd",
                    "module_subtype": "disclosures",
                    "code": "CSRD_COMPLETED_DISCLOSURES",
                    "name": "Tamamlanan ESRS açıklama sayısı",
                    "value": completed_disclosures,
                    "unit": "adet",
                    "year": year,
                    "direction": "higher_is_better",
                    "mappings": {},
                    "meta": {
                        "company_id": company_id,
                    },
                }
            )
        taxonomy_alignment = stats.get("taxonomy_alignment")
        if taxonomy_alignment is not None:
            kpis.append(
                {
                    "module": "csrd",
                    "module_subtype": "taxonomy",
                    "code": "CSRD_TAXONOMY_ALIGNMENT_PCT",
                    "name": "AB Taksonomisi uyum oranı (ortalama)",
                    "value": taxonomy_alignment,
                    "unit": "%",
                    "year": year,
                    "direction": "higher_is_better",
                    "mappings": {},
                    "meta": {
                        "company_id": company_id,
                    },
                }
            )
        turnover_pct = taxonomy_stats.get("turnover_pct")
        if turnover_pct is not None and turnover_pct > 0:
            kpis.append(
                {
                    "module": "csrd",
                    "module_subtype": "taxonomy",
                    "code": "CSRD_TAXONOMY_TURNOVER_PCT",
                    "name": "Taxonomy uyumlu ciro oranı",
                    "value": turnover_pct,
                    "unit": "%",
                    "year": year,
                    "direction": "higher_is_better",
                    "mappings": {},
                    "meta": {
                        "company_id": company_id,
                    },
                }
            )
        capex_pct = taxonomy_stats.get("capex_pct")
        if capex_pct is not None and capex_pct > 0:
            kpis.append(
                {
                    "module": "csrd",
                    "module_subtype": "taxonomy",
                    "code": "CSRD_TAXONOMY_CAPEX_PCT",
                    "name": "Taxonomy uyumlu CapEx oranı",
                    "value": capex_pct,
                    "unit": "%",
                    "year": year,
                    "direction": "higher_is_better",
                    "mappings": {},
                    "meta": {
                        "company_id": company_id,
                    },
                }
            )
        opex_pct = taxonomy_stats.get("opex_pct")
        if opex_pct is not None and opex_pct > 0:
            kpis.append(
                {
                    "module": "csrd",
                    "module_subtype": "taxonomy",
                    "code": "CSRD_TAXONOMY_OPEX_PCT",
                    "name": "Taxonomy uyumlu OpEx oranı",
                    "value": opex_pct,
                    "unit": "%",
                    "year": year,
                    "direction": "higher_is_better",
                    "mappings": {},
                    "meta": {
                        "company_id": company_id,
                    },
                }
            )
        return kpis

    def _export_issb_kpis(self, company_id: int, year: int) -> List[Dict[str, Any]]:
        try:
            from modules.issb.issb_manager import ISSBManager
        except ImportError:
            return []
        manager = ISSBManager(self.db_path)
        records = manager.get_recent_records(company_id, limit=1000)
        if not records:
            return []
        kpis: List[Dict[str, Any]] = []
        for rec in records:
            rec_year = rec.get("year")
            kpis.append(
                {
                    "module": "issb",
                    "module_subtype": rec.get("standard"),
                    "code": rec.get("disclosure") or "",
                    "name": rec.get("disclosure") or "",
                    "value": rec.get("metric"),
                    "unit": None,
                    "year": rec_year,
                    "direction": None,
                    "mappings": {
                        "issb_standard": rec.get("standard"),
                        "ifrs_reference": rec.get("standard")
                    },
                    "meta": {
                        "created_at": rec.get("created_at")
                    }
                }
            )
        return kpis

    def _export_carbon_kpis(self, company_id: int, year: int) -> List[Dict[str, Any]]:
        try:
            from modules.environmental.carbon_manager import CarbonManager
        except ImportError:
            return []
        manager = CarbonManager(self.db_path)
        footprint = manager.get_total_carbon_footprint(company_id, year)
        if not footprint:
            return []
        kpis: List[Dict[str, Any]] = []
        total = footprint.get("total_footprint")
        if total is not None:
            kpis.append(
                {
                    "module": "environmental",
                    "module_subtype": "carbon",
                    "code": "CARBON_TOTAL_FOOTPRINT",
                    "name": "Toplam karbon ayak izi",
                    "value": total,
                    "unit": "tCO2e",
                    "year": year,
                    "direction": "lower_is_better",
                    "mappings": {},
                    "meta": {
                        "scope1_total": footprint.get("scope1_total"),
                        "scope2_total": footprint.get("scope2_total"),
                        "scope3_total": footprint.get("scope3_total"),
                        "company_id": company_id,
                    },
                }
            )
        for key, scope_code, scope_name in [
            ("scope1_total", "SCOPE1", "Scope 1 emisyonları"),
            ("scope2_total", "SCOPE2", "Scope 2 emisyonları"),
            ("scope3_total", "SCOPE3", "Scope 3 emisyonları"),
        ]:
            value = footprint.get(key)
            if value is None:
                continue
            kpis.append(
                {
                    "module": "environmental",
                    "module_subtype": "carbon",
                    "code": f"CARBON_{scope_code}",
                    "name": scope_name,
                    "value": value,
                    "unit": "tCO2e",
                    "year": year,
                    "direction": "lower_is_better",
                    "mappings": {},
                    "meta": {
                        "company_id": company_id,
                    },
                }
            )
        return kpis

    def _export_energy_kpis(self, company_id: int) -> List[Dict[str, Any]]:
        try:
            from modules.environmental.energy_manager import EnergyManager
        except ImportError:
            return []
        manager = EnergyManager(self.db_path)
        stats = manager.get_dashboard_stats(company_id)
        if not stats:
            return []
        kpis: List[Dict[str, Any]] = []
        total_consumption = stats.get("total_consumption")
        if total_consumption is not None:
            kpis.append(
                {
                    "module": "environmental",
                    "module_subtype": "energy",
                    "code": "ENERGY_TOTAL_CONSUMPTION",
                    "name": "Toplam enerji tüketimi",
                    "value": total_consumption,
                    "unit": None,
                    "year": None,
                    "direction": "lower_is_better",
                    "mappings": {},
                    "meta": {
                        "total_cost": stats.get("total_cost"),
                        "company_id": company_id,
                    },
                }
            )
        renewable_ratio = stats.get("renewable_ratio")
        if renewable_ratio is not None:
            kpis.append(
                {
                    "module": "environmental",
                    "module_subtype": "energy",
                    "code": "ENERGY_RENEWABLE_RATIO",
                    "name": "Yenilenebilir enerji oranı",
                    "value": renewable_ratio,
                    "unit": "%",
                    "year": None,
                    "direction": "higher_is_better",
                    "mappings": {},
                    "meta": {
                        "company_id": company_id,
                    },
                }
            )
        return kpis

    def _export_water_kpis(self, company_id: int, year: int) -> List[Dict[str, Any]]:
        try:
            from modules.environmental.water_manager import WaterManager
        except ImportError:
            return []
        manager = WaterManager(self.db_path)
        data = manager.calculate_water_kpis(company_id, year)
        if not data:
            return []
        kpis: List[Dict[str, Any]] = []
        kpis.append(
            {
                "module": "environmental",
                "module_subtype": "water",
                "code": "WATER_TOTAL_CONSUMPTION",
                "name": "Toplam su tüketimi",
                "value": data.get("total_water_consumption"),
                "unit": "m3",
                "year": year,
                "direction": "lower_is_better",
                "mappings": {},
                "meta": {
                    "company_id": company_id,
                },
            }
        )
        kpis.append(
            {
                "module": "environmental",
                "module_subtype": "water",
                "code": "WATER_RECYCLING_RATIO",
                "name": "Su geri kazanım oranı",
                "value": data.get("water_recycling_ratio"),
                "unit": "%",
                "year": year,
                "direction": "higher_is_better",
                "mappings": {},
                "meta": {
                    "company_id": company_id,
                },
            }
        )
        kpis.append(
            {
                "module": "environmental",
                "module_subtype": "water",
                "code": "WATER_QUALITY_COMPLIANCE",
                "name": "Su kalite uyum oranı",
                "value": data.get("quality_compliance_rate"),
                "unit": "%",
                "year": year,
                "direction": "higher_is_better",
                "mappings": {},
                "meta": {
                    "company_id": company_id,
                },
            }
        )
        return kpis

    def _export_waste_kpis(self, company_id: int, year: Optional[int]) -> List[Dict[str, Any]]:
        try:
            from modules.environmental.waste_manager import WasteManager
        except ImportError:
            return []
        manager = WasteManager(self.db_path)
        data = manager.calculate_waste_metrics(company_id, year)
        if not data:
            return []
        kpis: List[Dict[str, Any]] = []
        kpis.append(
            {
                "module": "environmental",
                "module_subtype": "waste",
                "code": "WASTE_TOTAL_AMOUNT",
                "name": "Toplam atık miktarı",
                "value": data.get("total_waste"),
                "unit": None,
                "year": year,
                "direction": "lower_is_better",
                "mappings": {},
                "meta": {
                    "total_recycled": data.get("total_recycled"),
                    "company_id": company_id,
                },
            }
        )
        kpis.append(
            {
                "module": "environmental",
                "module_subtype": "waste",
                "code": "WASTE_RECYCLING_RATIO",
                "name": "Atık geri dönüşüm oranı",
                "value": data.get("recycling_ratio"),
                "unit": "%",
                "year": year,
                "direction": "higher_is_better",
                "mappings": {},
                "meta": {
                    "company_id": company_id,
                },
            }
        )
        return kpis

    def _export_supply_chain_kpis(self, company_id: int) -> List[Dict[str, Any]]:
        try:
            from modules.supply_chain.supply_chain_manager import SupplyChainManager
        except ImportError:
            return []
        manager = SupplyChainManager(self.db_path)
        stats = manager.get_dashboard_stats(company_id)
        if not stats:
            return []
        kpis: List[Dict[str, Any]] = []
        for key, code, name, unit, direction in [
            ("total_suppliers", "SC_TOTAL_SUPPLIERS", "Toplam tedarikçi sayısı", "adet", "higher_is_better"),
            ("active_suppliers", "SC_ACTIVE_SUPPLIERS", "Aktif tedarikçi sayısı", "adet", "higher_is_better"),
            ("local_supplier_pct", "SC_LOCAL_SUPPLIER_RATIO", "Yerel tedarikçi oranı", "%", "higher_is_better"),
            ("sustainable_pct", "SC_SUSTAINABLE_RATIO", "Sürdürülebilir tedarikçi oranı", "%", "higher_is_better"),
            ("avg_score", "SC_AVG_SCORE", "Ortalama tedarikçi skoru", "puan", "higher_is_better"),
            ("high_risk_count", "SC_HIGH_RISK_SUPPLIERS", "Yüksek riskli tedarikçi sayısı", "adet", "lower_is_better"),
            ("total_spend", "SC_TOTAL_SPEND", "Toplam tedarik harcaması", None, "lower_is_better"),
        ]:
            value = stats.get(key)
            if value is None:
                continue
            kpis.append(
                {
                    "module": "supply_chain",
                    "module_subtype": "dashboard",
                    "code": code,
                    "name": name,
                    "value": value,
                    "unit": unit,
                    "year": None,
                    "direction": direction,
                    "mappings": {},
                    "meta": {
                        "company_id": company_id,
                    },
                }
            )
        return kpis

    def _export_social_kpis(self, company_id: int, year: int) -> List[Dict[str, Any]]:
        try:
            from modules.social.social_manager import SocialManager
        except ImportError:
            return []
        manager = SocialManager(self.db_path)
        stats = manager.get_dashboard_kpis(company_id, year)
        if not stats:
            return []
        kpis: List[Dict[str, Any]] = []
        kpis.append(
            {
                "module": "social",
                "module_subtype": "workforce",
                "code": "SOC_TOTAL_EMPLOYEES",
                "name": "Toplam çalışan sayısı",
                "value": stats.get("total_employees"),
                "unit": "kişi",
                "year": year,
                "direction": "higher_is_better",
                "mappings": {},
                "meta": {
                    "company_id": company_id,
                },
            }
        )
        kpis.append(
            {
                "module": "social",
                "module_subtype": "ohs",
                "code": "SOC_LTIFR",
                "name": "Kayıp zamanlı kaza sıklık oranı (LTIFR)",
                "value": stats.get("ltifr"),
                "unit": None,
                "year": year,
                "direction": "lower_is_better",
                "mappings": {},
                "meta": {
                    "company_id": company_id,
                },
            }
        )
        kpis.append(
            {
                "module": "social",
                "module_subtype": "training",
                "code": "SOC_TRAINING_HOURS_PER_EMPLOYEE",
                "name": "Çalışan başına eğitim saati",
                "value": stats.get("training_hours_per_employee"),
                "unit": "saat/kişi",
                "year": year,
                "direction": "higher_is_better",
                "mappings": {},
                "meta": {
                    "company_id": company_id,
                },
            }
        )
        return kpis

    def prepare_context(self, data: Dict[str, Any]) -> str:
        """Veriyi AI icin JSON formatinda hazirla"""
        try:
            # Gereksiz veya buyuk alanlari temizle (opsiyonel)
            # Ornegin binary veriler, cok uzun loglar vs.
            
            # JSON stringe cevir
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Context hazirlama hatasi: {e}")
            return str(data)

    def generate_summary(self, data: Dict, report_type: str = "genel", language: str = "tr") -> Optional[str]:
        """Veri ozetleme"""
        if not self.is_available():
            return self._get_text_safe("AI_SERVICE_UNAVAILABLE", language, "AI servisi kullanılamıyor. Lutfen API key ekleyin.")

        try:
            # Context hazirla
            context = self.prepare_context(data)
            
            # Prompt olustur
            prompt = get_prompt(report_type, context, language)
            
            # System role localization
            system_role = self._get_text_safe("AI_SYSTEM_ROLE_REPORTING_EXPERT", language, "Sen surdurulebilirlik raporlama uzmanisin.")

            # OpenAI API cagir
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            content = response.choices[0].message.content
            
            # Validasyon
            if self.validator:
                warnings = self.validator.validate_report_content(content, data)
                if warnings:
                    warning_header = self._get_text_safe("AI_VALIDATION_WARNING_HEADER", language, "\n\n**Doğrulama Uyarıları (Olası Halüsinasyonlar):**\n")
                    content += warning_header
                    for w in warnings:
                        content += f"- {w}\n"

            return content

        except Exception as e:
            error_prefix = self._get_text_safe("AI_ERROR_PREFIX", language, "AI hatasi: ")
            return f"{error_prefix}{str(e)}"

    def analyze_performance(self, metrics: List[Dict], language: str = "tr") -> Optional[str]:
        """Performans analizi"""
        if not self.is_available():
            return self._get_text_safe("AI_SERVICE_UNAVAILABLE_SHORT", language, "AI servisi kullanılamıyor.")

        try:
            # Prompt localized intro
            intro = self._get_text_safe("AI_PERFORMANCE_ANALYSIS_INTRO", language, "Asagidaki performans metriklerini analiz et:")
            instructions = self._get_text_safe("AI_PERFORMANCE_ANALYSIS_INSTRUCTIONS", language, "Lutfen:\n1. Guclu yonleri belirt\n2. Iyilestirme alanlari onerilerde bulun\n3. Onem siralamasi yap")
            
            prompt = f"""
{intro}
{json.dumps(metrics, indent=2, ensure_ascii=False)}

{instructions}
"""

            system_role = self._get_text_safe("AI_SYSTEM_ROLE_ANALYSIS_EXPERT", language, "Sen surdurulebilirlik analiz uzmanisin.")

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            error_prefix = self._get_text_safe("AI_ERROR_PREFIX", language, "AI hatasi: ")
            return f"{error_prefix}{str(e)}"

    def get_recommendations(self, context: str, language: str = "tr") -> Optional[str]:
        """Akilli oneriler"""
        if not self.is_available():
            return self._get_text_safe("AI_SERVICE_UNAVAILABLE_SHORT", language, "AI servisi kullanılamıyor.")

        try:
            intro = self._get_text_safe("AI_RECOMMENDATIONS_INTRO", language, "Asagidaki surdurulebilirlik durumu icin oneriler sun:")
            instruction = self._get_text_safe("AI_RECOMMENDATIONS_INSTRUCTION", language, "Lutfen somut ve uygulanabilir oneriler ver.")
            
            prompt = f"""
{intro}
{context}

{instruction}
"""
            system_role = self._get_text_safe("AI_SYSTEM_ROLE_CONSULTANT", language, "Sen surdurulebilirlik danismanisin.")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            return response.choices[0].message.content

        except Exception as e:
            error_prefix = self._get_text_safe("AI_ERROR_PREFIX", language, "AI hatasi: ")
            return f"{error_prefix}{str(e)}"

    def save_report(self, report_content: str, report_name: str) -> bool:
        """AI raporunu kaydet"""
        try:
            reports_dir = os.path.join(self.base_dir, "reports", "ai")
            os.makedirs(reports_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_name}_{timestamp}.txt"
            filepath = os.path.join(reports_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            mgr = AdvancedReportManager(self.db_path)
            reg_id = mgr.register_existing_file(
                company_id=1,
                module_code="ai",
                report_name=report_name,
                report_type="txt",
                file_path=filepath,
                reporting_period=str(datetime.now().year),
                tags=["ai"],
                description="AI tarafından üretilmiş özet"
            )
            if reg_id:
                logging.info(f"[OK] AI raporu kaydedildi: {filepath}")
                return True
            return False
        except Exception as e:
            logging.error(f"[HATA] AI raporu kaydedilemedi: {e}")
            return False

