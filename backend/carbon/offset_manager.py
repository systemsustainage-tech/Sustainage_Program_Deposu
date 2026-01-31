#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
"""
KARBON OFFSET YÖNETİM MODÜLÜ
Karbon kredisi/offset yönetimi ve net emisyon hesaplama
Mevcut CarbonManager ile tam entegre
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from config.icons import Icons
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class OffsetManager:
    """Karbon offset/kredilendirme yönetim sınıfı"""

    # Offset proje standartları
    OFFSET_STANDARDS = {
        'VCS': 'Verified Carbon Standard',
        'GOLD_STANDARD': 'Gold Standard',
        'CDM': 'Clean Development Mechanism',
        'CAR': 'Climate Action Reserve',
        'ACR': 'American Carbon Registry',
        'PLAN_VIVO': 'Plan Vivo',
        'CUSTOM': 'Özel/Dahili Proje'
    }

    # Proje kategorileri
    PROJECT_CATEGORIES = {
        'FORESTRY': 'Ağaçlandırma ve Orman Koruma',
        'RENEWABLE': 'Yenilenebilir Enerji',
        'METHANE': 'Metan Yakalama',
        'EFFICIENCY': 'Enerji Verimliliği',
        'BLUE_CARBON': 'Mavi Karbon (Deniz/Kıyı Ekosistem)',
        'SOIL': 'Toprak Karbon Depolama',
        'BIOCHAR': 'Biochar',
        'DIRECT_CAPTURE': 'Doğrudan Hava Yakalama (DAC)',
        'CARBON_STORAGE': 'Karbon Depolama (CCS)',
        'OTHER': 'Diğer'
    }

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self.create_tables()

    def get_connection(self) -> sqlite3.Connection:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def create_tables(self) -> None:
        """Offset modülü tablolarını oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # 1. Offset Projeleri (Satın alınan offset kaynakları)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carbon_offset_projects (
                    id INTEGER PRIMARY KEY,
                    project_name TEXT NOT NULL,
                    project_type TEXT NOT NULL,              -- FORESTRY, RENEWABLE, etc.
                    standard TEXT NOT NULL,                  -- VCS, GOLD_STANDARD, etc.
                    registry_id TEXT,                        -- Kayıt/sertifika numarası
                    location_country TEXT,
                    location_region TEXT,
                    project_description TEXT,
                    vintage_year INTEGER,                    -- Offset üretim yılı
                    verification_status TEXT DEFAULT 'verified', -- verified, pending, expired
                    verification_date DATE,
                    verifier_name TEXT,
                    co_benefits TEXT,                        -- SDG, biodiversity (JSON)
                    additionality_proven BOOLEAN DEFAULT 1,  -- Ek olma kanıtı
                    permanence_years INTEGER,                -- Kalıcılık süresi
                    leakage_risk TEXT DEFAULT 'low',         -- low, medium, high
                    unit_price_usd REAL,                     -- Birim fiyat ($/tCO2e)
                    supplier_name TEXT,
                    supplier_contact TEXT,
                    contract_number TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 2. Offset İşlemleri (Satın alınan offsetler)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carbon_offset_transactions (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    project_id INTEGER NOT NULL,             -- carbon_offset_projects referansı
                    transaction_date DATE NOT NULL,
                    period TEXT NOT NULL,                    -- Hangi döneme atanacak (2024, 2024-Q1)
                    quantity_tco2e REAL NOT NULL,            -- Offset miktarı (tCO2e)
                    unit_price_usd REAL,
                    total_cost_usd REAL,
                    currency TEXT DEFAULT 'USD',
                    exchange_rate REAL DEFAULT 1.0,
                    total_cost_local REAL,                   -- Yerel para birimi
                    retirement_status TEXT DEFAULT 'active', -- active, retired, allocated
                    retirement_date DATE,
                    allocated_scope TEXT,                    -- scope1, scope2, scope3, scope1_2
                    certificate_number TEXT,
                    certificate_file TEXT,
                    invoice_number TEXT,
                    invoice_file TEXT,
                    purpose TEXT,                            -- compliance, voluntary, customer_commitment
                    sdg_contribution TEXT,                   -- İlgili SDG'ler (JSON)
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    FOREIGN KEY(project_id) REFERENCES carbon_offset_projects(id) ON DELETE RESTRICT
                )
            """)

            # 3. Net Emisyon Hesaplamaları (Cache için)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carbon_net_emissions (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    period TEXT NOT NULL,
                    scope1_gross REAL NOT NULL,              -- Brüt Scope 1
                    scope2_gross REAL NOT NULL,              -- Brüt Scope 2
                    scope3_gross REAL,                       -- Brüt Scope 3
                    total_gross REAL NOT NULL,               -- Toplam brüt emisyon
                    scope1_offset REAL DEFAULT 0,            -- Scope 1 için offset
                    scope2_offset REAL DEFAULT 0,            -- Scope 2 için offset
                    scope3_offset REAL DEFAULT 0,            -- Scope 3 için offset
                    total_offset REAL DEFAULT 0,             -- Toplam offset
                    scope1_net REAL,                         -- Net Scope 1
                    scope2_net REAL,                         -- Net Scope 2
                    scope3_net REAL,                         -- Net Scope 3
                    total_net REAL,                          -- Net toplam
                    carbon_neutral BOOLEAN DEFAULT 0,        -- Net sıfır mı?
                    offset_percentage REAL,                  -- Offset oranı %
                    calculation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    UNIQUE(company_id, period)
                )
            """)

            # 4. Offset Bütçe Planlaması
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carbon_offset_budget (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    budget_year INTEGER NOT NULL,
                    planned_emission_tco2e REAL,             -- Planlanan emisyon
                    planned_offset_tco2e REAL,               -- Planlanan offset miktarı
                    planned_budget_usd REAL,                 -- Planlanan bütçe
                    actual_offset_tco2e REAL DEFAULT 0,      -- Gerçekleşen offset
                    actual_cost_usd REAL DEFAULT 0,          -- Gerçekleşen maliyet
                    budget_utilization_pct REAL,             -- Bütçe kullanım oranı
                    status TEXT DEFAULT 'planned',           -- planned, ongoing, completed
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    UNIQUE(company_id, budget_year)
                )
            """)

            # İndeksler
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_offset_transactions_company_period
                ON carbon_offset_transactions(company_id, period)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_offset_transactions_project
                ON carbon_offset_transactions(project_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_net_emissions_company_period
                ON carbon_net_emissions(company_id, period)
            """)

            conn.commit()

        except Exception as e:
            logging.error(f"[ERROR] Offset tabloları oluşturulamadı: {e}")
            conn.rollback()
        finally:
            conn.close()

    # ==================== OFFSET PROJESİ YÖNETİMİ ====================

    def add_offset_project(self, project_data: Dict) -> Optional[int]:
        """Yeni offset projesi ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO carbon_offset_projects (
                    project_name, project_type, standard, registry_id,
                    location_country, location_region, project_description,
                    vintage_year, verification_status, verification_date,
                    verifier_name, co_benefits, additionality_proven,
                    permanence_years, leakage_risk, unit_price_usd,
                    supplier_name, supplier_contact, contract_number, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_data.get('project_name'),
                project_data.get('project_type'),
                project_data.get('standard'),
                project_data.get('registry_id'),
                project_data.get('location_country'),
                project_data.get('location_region'),
                project_data.get('project_description'),
                project_data.get('vintage_year'),
                project_data.get('verification_status', 'verified'),
                project_data.get('verification_date'),
                project_data.get('verifier_name'),
                json.dumps(project_data.get('co_benefits', [])) if isinstance(project_data.get('co_benefits'), list) else project_data.get('co_benefits'),
                project_data.get('additionality_proven', 1),
                project_data.get('permanence_years'),
                project_data.get('leakage_risk', 'low'),
                project_data.get('unit_price_usd'),
                project_data.get('supplier_name'),
                project_data.get('supplier_contact'),
                project_data.get('contract_number'),
                project_data.get('notes')
            ))

            project_id = cursor.lastrowid
            conn.commit()
            return project_id

        except Exception as e:
            logging.error(f"[ERROR] Offset projesi eklenemedi: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_offset_projects(self, project_type: Optional[str] = None,
                           standard: Optional[str] = None) -> List[Dict]:
        """Offset projelerini getir"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM carbon_offset_projects WHERE 1=1"
            params = []

            if project_type:
                query += " AND project_type = ?"
                params.append(project_type)

            if standard:
                query += " AND standard = ?"
                params.append(standard)

            query += " ORDER BY project_name"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            projects = []
            for row in rows:
                project = dict(row)
                # JSON parse
                if project.get('co_benefits'):
                    try:
                        project['co_benefits'] = json.loads(project['co_benefits'])
                    except Exception as e:
                        logging.error(f'Silent error in offset_manager.py: {str(e)}')
                projects.append(project)

            return projects

        except Exception as e:
            logging.error(f"[ERROR] Projeler getirilemedi: {e}")
            return []
        finally:
            conn.close()

    # ==================== OFFSET İŞLEM YÖNETİMİ ====================

    def purchase_offset(self, transaction_data: Dict) -> Optional[int]:
        """Offset satın al"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Otomatik hesaplamalar
            quantity = transaction_data.get('quantity_tco2e')
            unit_price = transaction_data.get('unit_price_usd')

            if quantity and unit_price:
                total_cost_usd = quantity * unit_price
            else:
                total_cost_usd = transaction_data.get('total_cost_usd', 0)

            exchange_rate = transaction_data.get('exchange_rate', 1.0)
            total_cost_local = total_cost_usd * exchange_rate

            cursor.execute("""
                INSERT INTO carbon_offset_transactions (
                    company_id, project_id, transaction_date, period,
                    quantity_tco2e, unit_price_usd, total_cost_usd,
                    currency, exchange_rate, total_cost_local,
                    retirement_status, retirement_date, allocated_scope,
                    certificate_number, certificate_file, invoice_number,
                    invoice_file, purpose, sdg_contribution, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction_data.get('company_id'),
                transaction_data.get('project_id'),
                transaction_data.get('transaction_date', datetime.now().date().isoformat()),
                transaction_data.get('period'),
                quantity,
                unit_price,
                total_cost_usd,
                transaction_data.get('currency', 'USD'),
                exchange_rate,
                total_cost_local,
                transaction_data.get('retirement_status', 'active'),
                transaction_data.get('retirement_date'),
                transaction_data.get('allocated_scope'),
                transaction_data.get('certificate_number'),
                transaction_data.get('certificate_file'),
                transaction_data.get('invoice_number'),
                transaction_data.get('invoice_file'),
                transaction_data.get('purpose', 'voluntary'),
                json.dumps(transaction_data.get('sdg_contribution', [])) if isinstance(transaction_data.get('sdg_contribution'), list) else transaction_data.get('sdg_contribution'),
                transaction_data.get('notes')
            ))

            transaction_id = cursor.lastrowid
            conn.commit()

            # Net emisyon yeniden hesapla
            self.recalculate_net_emissions(
                transaction_data.get('company_id'),
                transaction_data.get('period')
            )

            return transaction_id

        except Exception as e:
            logging.error(f"[ERROR] Offset satın alınamadı: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_offset_transactions(self, company_id: int,
                               period: Optional[str] = None) -> List[Dict]:
        """Offset işlemlerini getir"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            query = """
                SELECT 
                    t.*,
                    p.project_name,
                    p.project_type,
                    p.standard,
                    p.location_country
                FROM carbon_offset_transactions t
                LEFT JOIN carbon_offset_projects p ON t.project_id = p.id
                WHERE t.company_id = ?
            """
            params = [company_id]

            if period:
                query += " AND t.period = ?"
                params.append(period)

            query += " ORDER BY t.transaction_date DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            transactions = []
            for row in rows:
                trans = dict(row)
                # JSON parse
                if trans.get('sdg_contribution'):
                    try:
                        trans['sdg_contribution'] = json.loads(trans['sdg_contribution'])
                    except Exception as e:
                        logging.error(f'Silent error in offset_manager.py: {str(e)}')
                transactions.append(trans)

            return transactions

        except Exception as e:
            logging.error(f"[ERROR] İşlemler getirilemedi: {e}")
            return []
        finally:
            conn.close()

    def retire_offset(self, transaction_id: int) -> bool:
        """Offset'i emekliye ayır (kullan)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE carbon_offset_transactions
                SET retirement_status = 'retired',
                    retirement_date = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (datetime.now().date().isoformat(), transaction_id))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"[ERROR] Offset emekliye ayrılamadı: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    # ==================== NET EMİSYON HESAPLAMA ====================

    def recalculate_net_emissions(self, company_id: int, period: str) -> Optional[Dict]:
        """Net emisyonları yeniden hesapla (Brüt - Offset)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # 1. Brüt emisyonları al (carbon_emissions tablosundan)
            cursor.execute("""
                SELECT 
                    scope,
                    SUM(co2e_emissions) as total_co2e
                FROM carbon_emissions
                WHERE company_id = ? AND period = ?
                GROUP BY scope
            """, (company_id, period))

            emissions = cursor.fetchall()

            scope1_gross = 0
            scope2_gross = 0
            scope3_gross = 0

            for scope, total in emissions:
                if scope == 'scope1':
                    scope1_gross = total or 0
                elif scope == 'scope2':
                    scope2_gross = total or 0
                elif scope == 'scope3':
                    scope3_gross = total or 0

            total_gross = scope1_gross + scope2_gross + scope3_gross

            # 2. Offset miktarlarını al (allocated_scope'a göre)
            cursor.execute("""
                SELECT 
                    allocated_scope,
                    SUM(quantity_tco2e) as total_offset
                FROM carbon_offset_transactions
                WHERE company_id = ? 
                  AND period = ?
                  AND retirement_status = 'retired'
                GROUP BY allocated_scope
            """, (company_id, period))

            offsets = cursor.fetchall()

            scope1_offset = 0
            scope2_offset = 0
            scope3_offset = 0

            for allocated_scope, total_offset in offsets:
                if allocated_scope == 'scope1':
                    scope1_offset = total_offset or 0
                elif allocated_scope == 'scope2':
                    scope2_offset = total_offset or 0
                elif allocated_scope == 'scope3':
                    scope3_offset = total_offset or 0
                elif allocated_scope == 'scope1_2':
                    # scope1_2 için orantılı dağıt
                    if scope1_gross + scope2_gross > 0:
                        ratio1 = scope1_gross / (scope1_gross + scope2_gross)
                        ratio2 = scope2_gross / (scope1_gross + scope2_gross)
                        scope1_offset += (total_offset or 0) * ratio1
                        scope2_offset += (total_offset or 0) * ratio2

            total_offset = scope1_offset + scope2_offset + scope3_offset

            # 3. Net hesapla
            scope1_net = max(0, scope1_gross - scope1_offset)
            scope2_net = max(0, scope2_gross - scope2_offset)
            scope3_net = max(0, scope3_gross - scope3_offset)
            total_net = scope1_net + scope2_net + scope3_net

            # Karbon nötr mü?
            carbon_neutral = (total_net <= 0.01)  # Tolerans

            # Offset oranı
            offset_percentage = (total_offset / total_gross * 100) if total_gross > 0 else 0

            # 4. Veritabanına kaydet (UPSERT)
            cursor.execute("""
                INSERT INTO carbon_net_emissions (
                    company_id, period, scope1_gross, scope2_gross, scope3_gross,
                    total_gross, scope1_offset, scope2_offset, scope3_offset,
                    total_offset, scope1_net, scope2_net, scope3_net, total_net,
                    carbon_neutral, offset_percentage
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(company_id, period) DO UPDATE SET
                    scope1_gross = excluded.scope1_gross,
                    scope2_gross = excluded.scope2_gross,
                    scope3_gross = excluded.scope3_gross,
                    total_gross = excluded.total_gross,
                    scope1_offset = excluded.scope1_offset,
                    scope2_offset = excluded.scope2_offset,
                    scope3_offset = excluded.scope3_offset,
                    total_offset = excluded.total_offset,
                    scope1_net = excluded.scope1_net,
                    scope2_net = excluded.scope2_net,
                    scope3_net = excluded.scope3_net,
                    total_net = excluded.total_net,
                    carbon_neutral = excluded.carbon_neutral,
                    offset_percentage = excluded.offset_percentage,
                    calculation_date = CURRENT_TIMESTAMP
            """, (
                company_id, period, scope1_gross, scope2_gross, scope3_gross,
                total_gross, scope1_offset, scope2_offset, scope3_offset,
                total_offset, scope1_net, scope2_net, scope3_net, total_net,
                carbon_neutral, offset_percentage
            ))

            conn.commit()

            return {
                'company_id': company_id,
                'period': period,
                'gross': {
                    'scope1': scope1_gross,
                    'scope2': scope2_gross,
                    'scope3': scope3_gross,
                    'total': total_gross
                },
                'offset': {
                    'scope1': scope1_offset,
                    'scope2': scope2_offset,
                    'scope3': scope3_offset,
                    'total': total_offset
                },
                'net': {
                    'scope1': scope1_net,
                    'scope2': scope2_net,
                    'scope3': scope3_net,
                    'total': total_net
                },
                'carbon_neutral': carbon_neutral,
                'offset_percentage': offset_percentage
            }

        except Exception as e:
            logging.error(f"[ERROR] Net emisyon hesaplanamadı: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_net_emissions(self, company_id: int, period: str) -> Optional[Dict]:
        """Net emisyonları getir"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM carbon_net_emissions
                WHERE company_id = ? AND period = ?
            """, (company_id, period))

            row = cursor.fetchone()
            if row:
                return dict(row)

            # Yoksa hesapla
            return self.recalculate_net_emissions(company_id, period)

        except Exception as e:
            logging.error(f"[ERROR] Net emisyon getirilemedi: {e}")
            return None
        finally:
            conn.close()

    # ==================== BÜTÇE YÖNETİMİ ====================

    def set_offset_budget(self, company_id: int, budget_data: Dict) -> Optional[int]:
        """Offset bütçesi belirle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO carbon_offset_budget (
                    company_id, budget_year, planned_emission_tco2e,
                    planned_offset_tco2e, planned_budget_usd, notes
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(company_id, budget_year) DO UPDATE SET
                    planned_emission_tco2e = excluded.planned_emission_tco2e,
                    planned_offset_tco2e = excluded.planned_offset_tco2e,
                    planned_budget_usd = excluded.planned_budget_usd,
                    notes = excluded.notes,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                company_id,
                budget_data.get('budget_year'),
                budget_data.get('planned_emission_tco2e'),
                budget_data.get('planned_offset_tco2e'),
                budget_data.get('planned_budget_usd'),
                budget_data.get('notes')
            ))

            conn.commit()
            return cursor.lastrowid

        except Exception as e:
            logging.error(f"[ERROR] Bütçe belirlenemedi: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_offset_budget(self, company_id: int, budget_year: int) -> Optional[Dict]:
        """Offset bütçesini getir"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM carbon_offset_budget
                WHERE company_id = ? AND budget_year = ?
            """, (company_id, budget_year))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

        except Exception as e:
            logging.error(f"[ERROR] Bütçe getirilemedi: {e}")
            return None
        finally:
            conn.close()

    # ==================== İSTATİSTİKLER ====================

    def get_offset_statistics(self, company_id: int,
                             start_year: Optional[int] = None,
                             end_year: Optional[int] = None) -> Dict:
        """Offset istatistikleri"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Toplam offset miktarı ve maliyeti
            query = """
                SELECT 
                    COUNT(*) as transaction_count,
                    SUM(quantity_tco2e) as total_offset_tco2e,
                    SUM(total_cost_usd) as total_cost_usd,
                    AVG(unit_price_usd) as avg_unit_price,
                    MIN(unit_price_usd) as min_unit_price,
                    MAX(unit_price_usd) as max_unit_price
                FROM carbon_offset_transactions
                WHERE company_id = ?
            """
            params = [company_id]

            if start_year:
                query += " AND CAST(substr(period, 1, 4) AS INTEGER) >= ?"
                params.append(start_year)

            if end_year:
                query += " AND CAST(substr(period, 1, 4) AS INTEGER) <= ?"
                params.append(end_year)

            cursor.execute(query, params)
            stats = cursor.fetchone()

            # Proje tiplerine göre dağılım
            cursor.execute("""
                SELECT 
                    p.project_type,
                    COUNT(t.id) as transaction_count,
                    SUM(t.quantity_tco2e) as total_tco2e,
                    SUM(t.total_cost_usd) as total_cost
                FROM carbon_offset_transactions t
                JOIN carbon_offset_projects p ON t.project_id = p.id
                WHERE t.company_id = ?
                GROUP BY p.project_type
                ORDER BY total_tco2e DESC
            """, [company_id])

            project_breakdown = cursor.fetchall()

            return {
                'transaction_count': stats[0] or 0,
                'total_offset_tco2e': stats[1] or 0,
                'total_cost_usd': stats[2] or 0,
                'avg_unit_price': stats[3] or 0,
                'min_unit_price': stats[4] or 0,
                'max_unit_price': stats[5] or 0,
                'project_breakdown': [
                    {
                        'project_type': row[0],
                        'transaction_count': row[1],
                        'total_tco2e': row[2],
                        'total_cost': row[3]
                    }
                    for row in project_breakdown
                ]
            }

        except Exception as e:
            logging.error(f"[ERROR] İstatistikler hesaplanamadı: {e}")
            return {}
        finally:
            conn.close()


if __name__ == "__main__":
    # Test
    manager = OffsetManager()
    logging.info(f"{Icons.SUCCESS} OffsetManager tabloları oluşturuldu")

    # Test projesi
    project_id = manager.add_offset_project({
        'project_name': 'Amazon Rainforest Protection',
        'project_type': 'FORESTRY',
        'standard': 'VCS',
        'registry_id': 'VCS-1234',
        'location_country': 'Brazil',
        'vintage_year': 2023,
        'unit_price_usd': 12.50,
        'supplier_name': 'EcoOffset Ltd.'
    })

    logging.info(f"{Icons.SUCCESS} Test projesi oluşturuldu: {project_id}")
