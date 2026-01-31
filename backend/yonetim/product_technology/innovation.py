#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
İNOVASYON VE AR-GE MODÜLÜ
- R&D yatırımları ve metrikleri
- Patent ve faydalı model takibi
- Eko-tasarım uygulamaları
- Ürün yaşam döngüsü değerlendirmesi
"""

import sqlite3
from typing import Dict, List


class InnovationModule:
    """İnovasyon ve AR-GE yönetimi sınıfı"""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def create_innovation_tables(self) -> None:
        """İnovasyon tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # AR-GE metrikleri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS innovation_metrics (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                period TEXT NOT NULL,
                rd_investment_ratio REAL, -- Toplam ciro içindeki AR-GE oranı (%)
                rd_investment_amount REAL, -- AR-GE yatırım miktarı (TL)
                patent_applications INTEGER DEFAULT 0, -- Patent başvuru sayısı
                utility_models INTEGER DEFAULT 0, -- Faydalı model sayısı
                patents_granted INTEGER DEFAULT 0, -- Verilen patent sayısı
                ecodesign_integration BOOLEAN DEFAULT 0, -- Eko-tasarım entegrasyonu
                lca_implementation BOOLEAN DEFAULT 0, -- LCA uygulaması
                innovation_budget REAL, -- İnovasyon bütçesi (TL)
                innovation_projects INTEGER DEFAULT 0, -- Aktif inovasyon proje sayısı
                sustainability_innovation_ratio REAL, -- Sürdürülebilir inovasyon oranı (%)
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """)

        # İnovasyon projeleri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS innovation_projects (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                project_name TEXT NOT NULL,
                project_type TEXT, -- R&D, P&D, Sustainability, Digital
                description TEXT,
                start_date TEXT,
                end_date TEXT,
                budget REAL,
                status TEXT DEFAULT 'active', -- active, completed, cancelled
                sdg_mapping TEXT, -- İlgili SDG hedefleri
                sustainability_focus BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """)

        # Patent ve fikri mülkiyet tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS intellectual_property (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                ip_type TEXT NOT NULL, -- patent, utility_model, trademark, copyright
                title TEXT NOT NULL,
                application_number TEXT,
                application_date TEXT,
                grant_date TEXT,
                status TEXT, -- applied, granted, rejected, expired
                description TEXT,
                sdg_mapping TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()

    def add_innovation_metrics(self, company_id: int, period: str,
                              rd_investment_ratio: float = None,
                              rd_investment_amount: float = None,
                              patent_applications: int = 0,
                              utility_models: int = 0,
                              patents_granted: int = 0,
                              ecodesign_integration: bool = False,
                              lca_implementation: bool = False,
                              innovation_budget: float = None,
                              innovation_projects: int = 0,
                              sustainability_innovation_ratio: float = None) -> int:
        """İnovasyon metrikleri ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO innovation_metrics 
            (company_id, period, rd_investment_ratio, rd_investment_amount,
             patent_applications, utility_models, patents_granted,
             ecodesign_integration, lca_implementation, innovation_budget,
             innovation_projects, sustainability_innovation_ratio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, period, rd_investment_ratio, rd_investment_amount,
              patent_applications, utility_models, patents_granted,
              ecodesign_integration, lca_implementation, innovation_budget,
              innovation_projects, sustainability_innovation_ratio))

        metric_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return metric_id

    def add_innovation_project(self, company_id: int, project_name: str,
                              project_type: str, description: str = None,
                              start_date: str = None, end_date: str = None,
                              budget: float = None, sdg_mapping: str = None,
                              sustainability_focus: bool = False) -> int:
        """İnovasyon projesi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO innovation_projects 
            (company_id, project_name, project_type, description,
             start_date, end_date, budget, sdg_mapping, sustainability_focus)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, project_name, project_type, description,
              start_date, end_date, budget, sdg_mapping, sustainability_focus))

        project_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return project_id

    def add_intellectual_property(self, company_id: int, ip_type: str,
                                 title: str, application_number: str = None,
                                 application_date: str = None, grant_date: str = None,
                                 status: str = None, description: str = None,
                                 sdg_mapping: str = None) -> int:
        """Fikri mülkiyet kaydı ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO intellectual_property 
            (company_id, ip_type, title, application_number, application_date,
             grant_date, status, description, sdg_mapping)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, ip_type, title, application_number, application_date,
              grant_date, status, description, sdg_mapping))

        ip_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return ip_id

    def get_innovation_dashboard(self, company_id: int, period: str = None) -> Dict:
        """İnovasyon dashboard verilerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Son dönem metrikleri
        if period:
            cursor.execute("""
                SELECT * FROM innovation_metrics 
                WHERE company_id = ? AND period = ?
                ORDER BY created_at DESC LIMIT 1
            """, (company_id, period))
        else:
            cursor.execute("""
                SELECT * FROM innovation_metrics 
                WHERE company_id = ?
                ORDER BY created_at DESC LIMIT 1
            """, (company_id,))

        metrics = cursor.fetchone()

        # Aktif projeler
        cursor.execute("""
            SELECT COUNT(*) FROM innovation_projects 
            WHERE company_id = ? AND status = 'active'
        """, (company_id,))
        active_projects = cursor.fetchone()[0]

        # Toplam patent sayısı
        cursor.execute("""
            SELECT COUNT(*) FROM intellectual_property 
            WHERE company_id = ? AND ip_type = 'patent' AND status = 'granted'
        """, (company_id,))
        total_patents = cursor.fetchone()[0]

        # Sürdürülebilir inovasyon projeleri
        cursor.execute("""
            SELECT COUNT(*) FROM innovation_projects 
            WHERE company_id = ? AND sustainability_focus = 1
        """, (company_id,))
        sustainability_projects = cursor.fetchone()[0]

        conn.close()

        if metrics:
            return {
                'rd_investment_ratio': metrics[3],
                'rd_investment_amount': metrics[4],
                'patent_applications': metrics[5],
                'utility_models': metrics[6],
                'patents_granted': metrics[7],
                'ecodesign_integration': bool(metrics[8]),
                'lca_implementation': bool(metrics[9]),
                'innovation_budget': metrics[10],
                'innovation_projects': metrics[11],
                'sustainability_innovation_ratio': metrics[12],
                'active_projects': active_projects,
                'total_patents': total_patents,
                'sustainability_projects': sustainability_projects
            }
        else:
            return {
                'rd_investment_ratio': 0,
                'rd_investment_amount': 0,
                'patent_applications': 0,
                'utility_models': 0,
                'patents_granted': 0,
                'ecodesign_integration': False,
                'lca_implementation': False,
                'innovation_budget': 0,
                'innovation_projects': 0,
                'sustainability_innovation_ratio': 0,
                'active_projects': active_projects,
                'total_patents': total_patents,
                'sustainability_projects': sustainability_projects
            }

    def get_innovation_trends(self, company_id: int, years: int = 3) -> List[Dict]:
        """İnovasyon trendlerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT period, rd_investment_ratio, patent_applications, 
                   patents_granted, innovation_projects
            FROM innovation_metrics 
            WHERE company_id = ?
            ORDER BY period DESC
            LIMIT ?
        """, (company_id, years))

        trends = []
        for row in cursor.fetchall():
            trends.append({
                'period': row[0],
                'rd_investment_ratio': row[1],
                'patent_applications': row[2],
                'patents_granted': row[3],
                'innovation_projects': row[4]
            })

        conn.close()
        return trends
