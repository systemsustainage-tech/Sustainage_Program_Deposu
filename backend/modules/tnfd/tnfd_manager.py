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

class TNFDManager:
    """TNFD modülü iş mantığı ve veri yönetimi"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.module_dir = os.path.dirname(os.path.abspath(__file__))
        self.init_database()

    def init_database(self) -> None:
        """TNFD tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        try:
            # TNFD Governance
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tnfd_governance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_year INTEGER NOT NULL,
                    board_oversight TEXT,
                    management_role TEXT,
                    updated_at TIMESTAMP,
                    UNIQUE(company_id, reporting_year)
                )
            """)

            # TNFD Strategy
            cur.execute("""
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
            """)

            # TNFD Risk Management
            cur.execute("""
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
            """)

            # TNFD Metrics
            cur.execute("""
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
            """)
            conn.commit()
        except Exception as e:
            logging.error(f"[TNFD] Database init error: {e}")
        finally:
            conn.close()

    def get_stats(self, company_id: int, year: int) -> Dict:
        """Dashboard istatistiklerini getir"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        stats = {
            'nature_risks': 0,
            'nature_opps': 0,
            'dependencies': 0
        }
        try:
            # Strateji tablosundan risk ve fırsat sayılarını çekmeye çalış
            cur.execute("SELECT nature_risks, nature_opportunities, nature_dependencies FROM tnfd_strategy WHERE company_id = ? AND reporting_year = ?", (company_id, year))
            row = cur.fetchone()
            if row:
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

                stats['nature_risks'] = count_items(row[0])
                stats['nature_opps'] = count_items(row[1])
                stats['dependencies'] = count_items(row[2])
        except Exception as e:
            logging.error(f"[TNFD] Stats error: {e}")
        finally:
            conn.close()
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
