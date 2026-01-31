#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detaylı Enerji Yöneticisi
Enerji yoğunluğu, yenilenebilir enerji oranı ve detaylı enerji analizi
"""

import logging
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict

from utils.language_manager import LanguageManager


class DetailedEnergyManager:
    """Detaylı enerji yönetimi"""

    def __init__(self, db_path: str = None) -> None:
        self.lm = LanguageManager()
        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Gerekli tabloları oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Enerji tüketim kayıtları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS energy_consumption_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    facility_id INTEGER,
                    facility_name TEXT,
                    energy_type TEXT NOT NULL, -- 'electricity', 'natural_gas', 'diesel', 'gasoline', 'coal', 'renewable'
                    energy_source TEXT, -- 'grid', 'solar', 'wind', 'hydro', 'biomass', 'geothermal'
                    consumption_amount REAL NOT NULL,
                    unit TEXT NOT NULL, -- 'kWh', 'm3', 'liter', 'ton'
                    measurement_date TEXT NOT NULL,
                    invoice_date TEXT,
                    due_date TEXT,
                    supplier TEXT,
                    billing_period_start TEXT,
                    billing_period_end TEXT,
                    cost REAL,
                    currency TEXT DEFAULT 'TRY',
                    emission_factor REAL, -- kg CO2e per unit
                    co2_emissions REAL, -- calculated
                    energy_intensity REAL, -- per unit production
                    production_volume REAL, -- for intensity calculation
                    production_unit TEXT, -- 'ton', 'piece', 'm2'
                    data_source TEXT, -- 'meter_reading', 'bill', 'estimate'
                    notes TEXT,
                    recorded_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Mevcut tabloya yeni kolonları eklemeye çalış (Migration)
            try:
                cursor.execute("ALTER TABLE energy_consumption_records ADD COLUMN invoice_date TEXT")
            except sqlite3.OperationalError:
                pass  # Kolon zaten var

            try:
                cursor.execute("ALTER TABLE energy_consumption_records ADD COLUMN due_date TEXT")
            except sqlite3.OperationalError:
                pass
                
            try:
                cursor.execute("ALTER TABLE energy_consumption_records ADD COLUMN supplier TEXT")
            except sqlite3.OperationalError:
                pass

            # Enerji kaynakları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS energy_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    source_name TEXT NOT NULL,
                    source_type TEXT NOT NULL, -- 'renewable', 'fossil', 'nuclear'
                    energy_type TEXT NOT NULL,
                    capacity REAL, -- installed capacity
                    capacity_unit TEXT, -- 'kW', 'MW'
                    efficiency REAL, -- percentage
                    emission_factor REAL, -- kg CO2e per unit
                    is_active INTEGER DEFAULT 1,
                    installation_date TEXT,
                    decommission_date TEXT,
                    location TEXT,
                    supplier TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Enerji verimliliği projeleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS energy_efficiency_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    project_type TEXT NOT NULL, -- 'lighting', 'heating', 'cooling', 'motor', 'insulation', 'renewable'
                    description TEXT,
                    facility_id INTEGER,
                    facility_name TEXT,
                    start_date TEXT,
                    completion_date TEXT,
                    investment_cost REAL,
                    currency TEXT DEFAULT 'TRY',
                    annual_savings REAL, -- energy savings
                    annual_cost_savings REAL, -- monetary savings
                    payback_period REAL, -- years
                    co2_reduction REAL, -- annual CO2 reduction
                    status TEXT DEFAULT 'planned', -- 'planned', 'in_progress', 'completed', 'cancelled'
                    responsible_person TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Enerji performans göstergeleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS energy_kpis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    kpi_name TEXT NOT NULL,
                    kpi_type TEXT NOT NULL, -- 'intensity', 'renewable_ratio', 'efficiency', 'cost'
                    calculation_method TEXT,
                    target_value REAL,
                    baseline_value REAL,
                    current_value REAL,
                    unit TEXT NOT NULL,
                    measurement_period TEXT, -- 'monthly', 'quarterly', 'annual'
                    last_updated TEXT,
                    trend TEXT, -- 'improving', 'stable', 'declining'
                    benchmark_value REAL,
                    benchmark_source TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Enerji raporları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS energy_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    report_name TEXT NOT NULL,
                    report_period TEXT NOT NULL, -- 'YYYY-MM' or 'YYYY'
                    report_type TEXT NOT NULL, -- 'monthly', 'quarterly', 'annual'
                    total_consumption REAL,
                    total_cost REAL,
                    total_emissions REAL,
                    renewable_ratio REAL, -- percentage
                    energy_intensity REAL,
                    efficiency_score REAL, -- 0-100
                    key_findings TEXT, -- JSON array
                    recommendations TEXT, -- JSON array
                    generated_by INTEGER,
                    generated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logging.info(f"[OK] {self.lm.tr('detailed_energy_tables_ready', 'Detaylı enerji tabloları hazır')}")

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('table_creation_error', 'Tablo oluşturma hatası')}: {e}")
        finally:
            conn.close()

    def record_energy_consumption(self, company_id: int, facility_id: int = None, facility_name: str = "",
                                energy_type: str = "electricity", energy_source: str = "grid",
                                consumption_amount: float = 0, unit: str = "kWh", measurement_date: str = None,
                                billing_period_start: str = None, billing_period_end: str = None,
                                cost: float = None, emission_factor: float = None, production_volume: float = None,
                                production_unit: str = "", data_source: str = "meter_reading",
                                notes: str = "", recorded_by: int = None,
                                invoice_date: str = None, due_date: str = None, supplier: str = None) -> int:
        """
        Enerji tüketim kaydı oluştur
        
        Args:
            company_id: Şirket ID
            facility_id: Tesis ID
            facility_name: Tesis adı
            energy_type: Enerji türü
            energy_source: Enerji kaynağı
            consumption_amount: Tüketim miktarı
            unit: Birim
            measurement_date: Ölçüm tarihi
            billing_period_start: Fatura dönemi başlangıç
            billing_period_end: Fatura dönemi bitiş
            cost: Maliyet
            emission_factor: Emisyon faktörü
            production_volume: Üretim hacmi (yoğunluk hesaplaması için)
            production_unit: Üretim birimi
            data_source: Veri kaynağı
            notes: Notlar
            recorded_by: Kaydeden kullanıcı ID
            invoice_date: Fatura tarihi
            due_date: Son ödeme tarihi
            supplier: Tedarikçi firma
        
        Returns:
            Oluşturulan kayıt ID'si
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if measurement_date is None:
                measurement_date = datetime.now().strftime('%Y-%m-%d')

            # CO2 emisyonlarını hesapla
            co2_emissions = consumption_amount * emission_factor if emission_factor else None

            # Enerji yoğunluğunu hesapla
            energy_intensity = consumption_amount / production_volume if production_volume and production_volume > 0 else None

            cursor.execute("""
                INSERT INTO energy_consumption_records 
                (company_id, facility_id, facility_name, energy_type, energy_source, consumption_amount,
                 unit, measurement_date, billing_period_start, billing_period_end, cost, emission_factor,
                 co2_emissions, energy_intensity, production_volume, production_unit, data_source, notes, recorded_by,
                 invoice_date, due_date, supplier)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, facility_id, facility_name, energy_type, energy_source, consumption_amount,
                unit, measurement_date, billing_period_start, billing_period_end, cost, emission_factor,
                co2_emissions, energy_intensity, production_volume, production_unit, data_source, notes, recorded_by,
                invoice_date, due_date, supplier
            ))

            record_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] {self.lm.tr('energy_consumption_record_created', 'Enerji tüketim kaydı oluşturuldu')}: {consumption_amount} {unit} (ID: {record_id})")
            return record_id

        except Exception as e:
            conn.rollback()
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('energy_record_creation_error', 'Enerji kaydı oluşturma hatası')}: {e}")
            raise
        finally:
            conn.close()

    def add_energy_source(self, company_id: int, source_name: str, source_type: str,
                         energy_type: str, capacity: float = None, capacity_unit: str = "kW",
                         efficiency: float = None, emission_factor: float = None,
                         installation_date: str = None, location: str = "", supplier: str = "",
                         notes: str = "") -> int:
        """
        Enerji kaynağı ekle
        
        Args:
            company_id: Şirket ID
            source_name: Kaynak adı
            source_type: Kaynak türü ('renewable', 'fossil', 'nuclear')
            energy_type: Enerji türü
            capacity: Kurulu güç
            capacity_unit: Güç birimi
            efficiency: Verimlilik
            emission_factor: Emisyon faktörü
            installation_date: Kurulum tarihi
            location: Konum
            supplier: Tedarikçi
            notes: Notlar
        
        Returns:
            Oluşturulan kaynak ID'si
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO energy_sources 
                (company_id, source_name, source_type, energy_type, capacity, capacity_unit,
                 efficiency, emission_factor, installation_date, location, supplier, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, source_name, source_type, energy_type, capacity, capacity_unit,
                efficiency, emission_factor, installation_date, location, supplier, notes
            ))

            source_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] {self.lm.tr('energy_source_added', 'Enerji kaynağı eklendi')}: {source_name} (ID: {source_id})")
            return source_id

        except Exception as e:
            conn.rollback()
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('energy_source_add_error', 'Enerji kaynağı ekleme hatası')}: {e}")
            raise
        finally:
            conn.close()

    def create_efficiency_project(self, company_id: int, project_name: str, project_type: str,
                                description: str = "", facility_id: int = None, facility_name: str = "",
                                start_date: str = None, completion_date: str = None, investment_cost: float = None,
                                annual_savings: float = None, annual_cost_savings: float = None,
                                payback_period: float = None, co2_reduction: float = None,
                                responsible_person: str = "", notes: str = "") -> int:
        """
        Enerji verimliliği projesi oluştur
        
        Args:
            company_id: Şirket ID
            project_name: Proje adı
            project_type: Proje türü
            description: Açıklama
            facility_id: Tesis ID
            facility_name: Tesis adı
            start_date: Başlangıç tarihi
            completion_date: Tamamlanma tarihi
            investment_cost: Yatırım maliyeti
            annual_savings: Yıllık enerji tasarrufu
            annual_cost_savings: Yıllık maliyet tasarrufu
            payback_period: Geri ödeme süresi
            co2_reduction: CO2 azalımı
            responsible_person: Sorumlu kişi
            notes: Notlar
        
        Returns:
            Oluşturulan proje ID'si
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO energy_efficiency_projects 
                (company_id, project_name, project_type, description, facility_id, facility_name,
                 start_date, completion_date, investment_cost, annual_savings, annual_cost_savings,
                 payback_period, co2_reduction, responsible_person, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, project_name, project_type, description, facility_id, facility_name,
                start_date, completion_date, investment_cost, annual_savings, annual_cost_savings,
                payback_period, co2_reduction, responsible_person, notes
            ))

            project_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] {self.lm.tr('efficiency_project_created', 'Enerji verimliliği projesi oluşturuldu')}: {project_name} (ID: {project_id})")
            return project_id

        except Exception as e:
            conn.rollback()
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('project_creation_error', 'Proje oluşturma hatası')}: {e}")
            raise
        finally:
            conn.close()

    def calculate_energy_metrics(self, company_id: int, period: str = None) -> Dict:
        """
        Enerji metriklerini hesapla
        
        Args:
            company_id: Şirket ID
            period: Dönem ('YYYY-MM' or 'YYYY')
        
        Returns:
            Hesaplanan metrikler
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Dönem filtresi
            period_filter = ""
            params = [company_id]

            if period:
                if len(period) == 7:  # YYYY-MM
                    period_filter = " AND strftime('%Y-%m', measurement_date) = ?"
                    params.append(period)
                elif len(period) == 4:  # YYYY
                    period_filter = " AND strftime('%Y', measurement_date) = ?"
                    params.append(period)

            # Toplam tüketim
            cursor.execute(f"""
                SELECT 
                    SUM(consumption_amount) as total_consumption,
                    SUM(cost) as total_cost,
                    SUM(co2_emissions) as total_emissions,
                    COUNT(*) as record_count
                FROM energy_consumption_records 
                WHERE company_id = ? {period_filter}
            """, params)

            total_result = cursor.fetchone()
            total_consumption, total_cost, total_emissions, record_count = total_result

            # Yenilenebilir enerji oranı
            cursor.execute(f"""
                SELECT SUM(consumption_amount) as renewable_consumption
                FROM energy_consumption_records 
                WHERE company_id = ? AND energy_source IN ('solar', 'wind', 'hydro', 'biomass', 'geothermal') {period_filter}
            """, params)

            renewable_result = cursor.fetchone()
            renewable_consumption = renewable_result[0] if renewable_result[0] else 0

            renewable_ratio = (renewable_consumption / total_consumption * 100) if total_consumption and total_consumption > 0 else 0

            # Enerji yoğunluğu
            cursor.execute(f"""
                SELECT AVG(energy_intensity) as avg_intensity
                FROM energy_consumption_records 
                WHERE company_id = ? AND energy_intensity IS NOT NULL {period_filter}
            """, params)

            intensity_result = cursor.fetchone()
            avg_intensity = intensity_result[0] if intensity_result[0] else 0

            # Enerji türü dağılımı
            cursor.execute(f"""
                SELECT energy_type, SUM(consumption_amount) as consumption, SUM(cost) as cost
                FROM energy_consumption_records 
                WHERE company_id = ? {period_filter}
                GROUP BY energy_type
                ORDER BY consumption DESC
            """, params)

            energy_distribution = []
            for row in cursor.fetchall():
                energy_distribution.append({
                    'energy_type': row[0],
                    'consumption': row[1],
                    'cost': row[2] or 0
                })

            # Tesis bazlı dağılım
            cursor.execute(f"""
                SELECT facility_name, SUM(consumption_amount) as consumption, SUM(cost) as cost
                FROM energy_consumption_records 
                WHERE company_id = ? AND facility_name IS NOT NULL AND facility_name != '' {period_filter}
                GROUP BY facility_name
                ORDER BY consumption DESC
            """, params)

            facility_distribution = []
            for row in cursor.fetchall():
                facility_distribution.append({
                    'facility_name': row[0],
                    'consumption': row[1],
                    'cost': row[2] or 0
                })

            return {
                'total_consumption': total_consumption or 0,
                'total_cost': total_cost or 0,
                'total_emissions': total_emissions or 0,
                'renewable_consumption': renewable_consumption,
                'renewable_ratio': round(renewable_ratio, 2),
                'avg_energy_intensity': round(avg_intensity, 2),
                'record_count': record_count,
                'energy_distribution': energy_distribution,
                'facility_distribution': facility_distribution
            }

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('metric_calculation_error', 'Metrik hesaplama hatası')}: {e}")
            return {}
        finally:
            conn.close()

    def get_energy_records(self, company_id: int, period: str = None) -> list:
        """
        Enerji kayıtlarını getir
        
        Args:
            company_id: Şirket ID
            period: Dönem ('YYYY-MM' or 'YYYY')
            
        Returns:
            Kayıt listesi
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            query = """
                SELECT *
                FROM energy_consumption_records 
                WHERE company_id = ?
            """
            params = [company_id]
            
            if period:
                if len(period) == 7:  # YYYY-MM
                    query += " AND strftime('%Y-%m', measurement_date) = ?"
                    params.append(period)
                elif len(period) == 4:  # YYYY
                    query += " AND strftime('%Y', measurement_date) = ?"
                    params.append(period)
                    
            query += " ORDER BY measurement_date DESC"
            
            cursor.execute(query, params)
            
            columns = [col[0] for col in cursor.description]
            records = []
            
            for row in cursor.fetchall():
                record = dict(zip(columns, row))
                records.append(record)
                
            return records
            
        except Exception as e:
            logging.error(f"Kayıtları getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def get_energy_trends(self, company_id: int, months: int = 12) -> Dict:
        """Enerji trendlerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            start_date = (datetime.now() - timedelta(days=months*30)).strftime('%Y-%m-%d')

            cursor.execute("""
                SELECT 
                    strftime('%Y-%m', measurement_date) as month,
                    SUM(consumption_amount) as total_consumption,
                    SUM(cost) as total_cost,
                    SUM(co2_emissions) as total_emissions,
                    AVG(energy_intensity) as avg_intensity
                FROM energy_consumption_records 
                WHERE company_id = ? AND measurement_date >= ?
                GROUP BY strftime('%Y-%m', measurement_date)
                ORDER BY month
            """, (company_id, start_date))

            results = cursor.fetchall()
            trends = {
                'months': [],
                'consumption': [],
                'cost': [],
                'emissions': [],
                'intensity': []
            }

            for row in results:
                month, consumption, cost, emissions, intensity = row
                trends['months'].append(month)
                trends['consumption'].append(consumption or 0)
                trends['cost'].append(cost or 0)
                trends['emissions'].append(emissions or 0)
                trends['intensity'].append(intensity or 0)

            return trends

        except Exception as e:
            logging.error(f"[HATA] Enerji trendleri hatası: {e}")
            return {'months': [], 'consumption': [], 'cost': [], 'emissions': [], 'intensity': []}
        finally:
            conn.close()

    def get_annual_report_data(self, company_id: int, year: int) -> Dict:
        """Yıllık rapor verilerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Toplam tüketim ve maliyet
            cursor.execute("""
                SELECT 
                    energy_type, 
                    SUM(consumption_amount) as total_consumption,
                    SUM(cost) as total_cost,
                    SUM(co2_emissions) as total_emissions
                FROM energy_consumption_records
                WHERE company_id = ? AND strftime('%Y', measurement_date) = ?
                GROUP BY energy_type
            """, (company_id, str(year)))
            
            breakdown = []
            total_co2 = 0
            total_cost = 0
            total_consumption = 0
            
            for row in cursor.fetchall():
                breakdown.append({
                    'type': row[0],
                    'consumption': row[1] or 0,
                    'cost': row[2] or 0,
                    'emissions': row[3] or 0
                })
                total_consumption += row[1] if row[1] else 0
                total_co2 += row[3] if row[3] else 0
                total_cost += row[2] if row[2] else 0
            
            return {
                'year': year,
                'breakdown': breakdown,
                'total_consumption': total_consumption,
                'total_emissions': total_co2,
                'total_cost': total_cost
            }
        except Exception as e:
            logging.error(f"Rapor verisi getirme hatası: {e}")
            return {'year': year, 'breakdown': [], 'total_consumption': 0, 'total_emissions': 0, 'total_cost': 0}
        finally:
            conn.close()

    def create_default_energy_data(self, company_id: int, created_by: int = 1) -> None:
        """Varsayılan enerji verilerini oluştur"""
        try:
            # Enerji kaynakları
            energy_sources = [
                {
                    'source_name': 'Ana Elektrik Şebekesi',
                    'source_type': 'fossil',
                    'energy_type': 'electricity',
                    'capacity': 1000,
                    'capacity_unit': 'kW',
                    'efficiency': 85,
                    'emission_factor': 0.4,  # kg CO2e/kWh
                    'location': 'Ana Tesis',
                    'supplier': 'TEDAŞ'
                },
                {
                    'source_name': 'Güneş Enerjisi Sistemi',
                    'source_type': 'renewable',
                    'energy_type': 'electricity',
                    'capacity': 500,
                    'capacity_unit': 'kW',
                    'efficiency': 20,
                    'emission_factor': 0,
                    'location': 'Çatı Kurulumu',
                    'supplier': 'SolarTech'
                },
                {
                    'source_name': 'Doğal Gaz Kazanı',
                    'source_type': 'fossil',
                    'energy_type': 'natural_gas',
                    'capacity': 200,
                    'capacity_unit': 'kW',
                    'efficiency': 90,
                    'emission_factor': 2.0,  # kg CO2e/m3
                    'location': 'Kazan Dairesi',
                    'supplier': 'BOTAŞ'
                }
            ]

            # Enerji kaynaklarını ekle
            for source in energy_sources:
                self.add_energy_source(company_id=company_id, **source)

            # Örnek enerji tüketim kayıtları
            today = datetime.now()
            for i in range(6):  # Son 6 ay
                month_date = (today - timedelta(days=i*30)).strftime('%Y-%m-%d')

                # Elektrik tüketimi
                self.record_energy_consumption(
                    company_id=company_id,
                    facility_name="Ana Tesis",
                    energy_type="electricity",
                    energy_source="grid",
                    consumption_amount=45000 + (i * 1000),
                    unit="kWh",
                    measurement_date=month_date,
                    cost=27000 + (i * 600),
                    emission_factor=0.4,
                    production_volume=1000 + (i * 50),
                    production_unit="ton",
                    recorded_by=created_by
                )

                # Güneş enerjisi
                self.record_energy_consumption(
                    company_id=company_id,
                    facility_name="Ana Tesis",
                    energy_type="electricity",
                    energy_source="solar",
                    consumption_amount=15000 + (i * 500),
                    unit="kWh",
                    measurement_date=month_date,
                    cost=0,  # Ücretsiz
                    emission_factor=0,
                    production_volume=1000 + (i * 50),
                    production_unit="ton",
                    recorded_by=created_by
                )

                # Doğal gaz
                self.record_energy_consumption(
                    company_id=company_id,
                    facility_name="Ana Tesis",
                    energy_type="natural_gas",
                    energy_source="grid",
                    consumption_amount=8000 + (i * 200),
                    unit="m3",
                    measurement_date=month_date,
                    cost=12000 + (i * 300),
                    emission_factor=2.0,
                    production_volume=1000 + (i * 50),
                    production_unit="ton",
                    recorded_by=created_by
                )

            # Enerji verimliliği projeleri
            projects = [
                {
                    'project_name': 'LED Aydınlatma Projesi',
                    'project_type': 'lighting',
                    'description': 'Tüm tesis LED aydınlatmaya dönüştürüldü',
                    'facility_name': 'Ana Tesis',
                    'start_date': '2024-01-01',
                    'completion_date': '2024-03-01',
                    'investment_cost': 50000,
                    'annual_savings': 25000,
                    'annual_cost_savings': 15000,
                    'payback_period': 3.3,
                    'co2_reduction': 12.5,
                    'responsible_person': 'Enerji Müdürü'
                },
                {
                    'project_name': 'Motor Verimliliği Artırma',
                    'project_type': 'motor',
                    'description': 'Eski motorlar verimli motorlarla değiştirildi',
                    'facility_name': 'Üretim Tesisi',
                    'start_date': '2024-02-01',
                    'completion_date': '2024-05-01',
                    'investment_cost': 120000,
                    'annual_savings': 40000,
                    'annual_cost_savings': 24000,
                    'payback_period': 5.0,
                    'co2_reduction': 20.0,
                    'responsible_person': 'Üretim Müdürü'
                }
            ]

            # Projeleri ekle
            for project in projects:
                self.create_efficiency_project(company_id=company_id, **project)

            logging.info("[OK] Varsayılan enerji verileri oluşturuldu")

        except Exception as e:
            logging.error(f"[HATA] Varsayılan enerji verileri oluşturma hatası: {e}")


if __name__ == "__main__":
    # Test
    manager = DetailedEnergyManager()
    manager.create_default_energy_data(company_id=1, created_by=1)

    # Metrikleri hesapla
    metrics = manager.calculate_energy_metrics(company_id=1)
    logging.info("Enerji Metrikleri:")
    logging.info(f"- Toplam Tüketim: {metrics.get('total_consumption', 0):,.0f} kWh")
    logging.info(f"- Toplam Maliyet: {metrics.get('total_cost', 0):,.0f} TL")
    logging.info(f"- CO2 Emisyonları: {metrics.get('total_emissions', 0):,.0f} kg")
    logging.info(f"- Yenilenebilir Oranı: {metrics.get('renewable_ratio', 0):.1f}%")
    logging.info(f"- Ortalama Enerji Yoğunluğu: {metrics.get('avg_energy_intensity', 0):.2f} kWh/ton")

    # Trendleri getir
    trends = manager.get_energy_trends(company_id=1)
    logging.info("\nEnerji Trendleri:")
    logging.info(f"- {len(trends['months'])} aylık veri bulundu")
    logging.info(f"- Son ay tüketimi: {trends['consumption'][-1] if trends['consumption'] else 0:,.0f} kWh")
