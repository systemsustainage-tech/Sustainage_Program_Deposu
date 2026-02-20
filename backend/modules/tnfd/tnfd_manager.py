#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TNFD MANAGER - İş Mantığı ve Veri Yönetimi
Taskforce on Nature-related Financial Disclosures
"""

import logging
import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
try:
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    from core.base_manager import BaseTenantManager

class TNFDManager(BaseTenantManager):
    """TNFD modülü iş mantığı ve veri yönetimi"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        super().__init__(db_path, company_id)
        self.module_dir = os.path.dirname(os.path.abspath(__file__))
        self.init_database()

    def init_database(self) -> None:
        """TNFD tablolarını oluştur"""
        try:
            # TNFD Governance
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS tnfd_governance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_year INTEGER NOT NULL,
                    board_oversight TEXT,
                    management_role TEXT,
                    updated_at TIMESTAMP,
                    UNIQUE(company_id, reporting_year)
                )
            """, skip_tenant_filter=True)

            # TNFD Strategy
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS tnfd_strategy (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_year INTEGER NOT NULL,
                    nature_dependencies TEXT,
                    nature_impacts TEXT,
                    nature_risks TEXT,
                    nature_opportunities TEXT,
                    updated_at TIMESTAMP,
                    UNIQUE(company_id, reporting_year)
                )
            """, skip_tenant_filter=True)

            # TNFD Risk Management
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS tnfd_risk_management (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_year INTEGER NOT NULL,
                    risk_identification_process TEXT,
                    risk_assessment_process TEXT,
                    risk_management_process TEXT,
                    updated_at TIMESTAMP,
                    UNIQUE(company_id, reporting_year)
                )
            """, skip_tenant_filter=True)

            # TNFD Metrics
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS tnfd_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_year INTEGER NOT NULL,
                    core_metrics TEXT,
                    sector_metrics TEXT,
                    targets TEXT,
                    updated_at TIMESTAMP,
                    UNIQUE(company_id, reporting_year)
                )
            """, skip_tenant_filter=True)
            
        except Exception as e:
            logging.error(f"[TNFD] Database init error: {e}")

    def get_stats(self, company_id: int, year: int) -> Dict:
        """Dashboard istatistiklerini getir"""
        stats = {
            'nature_risks': 0,
            'nature_opps': 0,
            'dependencies': 0
        }
        try:
            # Strateji tablosundan risk ve fırsat sayılarını çekmeye çalış
            # BaseTenantManager ile sorgu
            # Not: execute_query zaten company_id filtresi ekler eğer tablo tenant-specific ise.
            # Ancak burada company_id parametresi de var.
            # execute_query metodunu kullanarak yapalım.
            
            query = "SELECT nature_risks, nature_opportunities, nature_dependencies FROM tnfd_strategy WHERE reporting_year = ?"
            params = [year]
            
            # Eğer company_id parametresi verilmişse ve self.company_id'den farklıysa veya self.company_id None ise
            # BaseTenantManager genellikle self.company_id kullanır.
            # Metod imzasındaki company_id'yi kullanmak için, geçici olarak self.company_id'yi set edebiliriz 
            # veya execute_query'nin tenant filtresini kullanıp company_id'yi parametre olarak geçmeyiz (otomatik eklenir).
            
            # En güvenli yol: Eğer company_id parametresi varsa, onu kullan.
            # BaseTenantManager.execute_query otomatik olarak company_id ekler.
            # Eğer metod parametresi company_id ile self.company_id farklıysa dikkatli olunmalı.
            # Genellikle bu manager'lar request context'inde oluşturulur ve company_id inject edilir.
            
            # Mevcut yapı: get_stats(self, company_id, year)
            # Bizim yapımız: self.execute_query(sql, params) -> otomatik company_id ekler.
            
            # Manuel company_id kontrolü için:
            rows = self.execute_query(query, params)

            if rows:
                row = rows[0]
                # Verilerin JSON formatında liste olup olmadığını kontrol et
                def count_items(data):
                    if not data:
                        return 0
                    try:
                        parsed = json.loads(data)
                        if isinstance(parsed, list):
                            return len(parsed)
                        return 1 # JSON ama liste değilse 1 say
                    except json.JSONDecodeError:
                        return 1 if data.strip() else 0 # Düz metinse ve doluysa 1 say

                # BaseTenantManager ile satırlar dictionary benzeri döner (keys ile erişilebilir)
                stats['nature_risks'] = count_items(row['nature_risks'])
                stats['nature_opps'] = count_items(row['nature_opportunities'])
                stats['dependencies'] = count_items(row['nature_dependencies'])
        except Exception as e:
            logging.error(f"[TNFD] Stats error: {e}")
        return stats

    def get_recommendations(self, company_id: int, year: int) -> List[Dict]:
        """Önerileri getir"""
        recommendations = []
        stats = self.get_stats(company_id, year)
        
        if stats['nature_risks'] == 0:
            recommendations.append({
                'category': 'Risk Yönetimi',
                'text': 'Doğa ile ilgili risklerinizi belirleyin ve değerlendirin.',
                'priority': 'Yüksek'
            })
            
        if stats['nature_opps'] == 0:
            recommendations.append({
                'category': 'Strateji',
                'text': 'Doğa ile ilgili fırsatları değerlendirin.',
                'priority': 'Orta'
            })
            
        if stats['dependencies'] == 0:
            recommendations.append({
                'category': 'Analiz',
                'text': 'Doğa bağımlılıklarınızı analiz edin (LEAP yaklaşımı).',
                'priority': 'Yüksek'
            })
            
        return recommendations
