#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GELİŞMİŞ VERİ ENVANTERİ
======================

Dashboard iyileştirmeleri ve gelişmiş veri yönetimi
"""

import logging
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class DashboardWidget:
    """Dashboard widget veri yapısı"""
    widget_id: str
    widget_type: str  # chart, table, metric, alert
    title: str
    data_source: str
    config: Dict[str, Any]
    position: Tuple[int, int]
    size: Tuple[int, int]
    is_active: bool

@dataclass
class DataSource:
    """Veri kaynağı yapısı"""
    source_id: str
    source_name: str
    source_type: str  # database, api, file, erp
    connection_string: str
    query: str
    refresh_interval: int  # minutes
    last_updated: str
    is_active: bool

class AdvancedDashboard:
    """Gelişmiş dashboard yöneticisi"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or 'data/sdg_desktop.db'
        self.widgets = {}
        self.data_sources = {}
        self._create_tables()

    def _create_tables(self):
        """Dashboard tablolarını oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Dashboard widget'ları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_widgets (
                    id TEXT PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    widget_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    data_source TEXT NOT NULL,
                    config TEXT NOT NULL,
                    position_x INTEGER DEFAULT 0,
                    position_y INTEGER DEFAULT 0,
                    width INTEGER DEFAULT 4,
                    height INTEGER DEFAULT 3,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id)
                )
            """)

            # Veri kaynakları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_sources (
                    id TEXT PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    source_name TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    connection_string TEXT NOT NULL,
                    query TEXT NOT NULL,
                    refresh_interval INTEGER DEFAULT 60,
                    last_updated TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id)
                )
            """)

            # Dashboard layout'ları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_layouts (
                    id TEXT PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    layout_name TEXT NOT NULL,
                    layout_config TEXT NOT NULL,
                    is_default INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id)
                )
            """)

            # KPI tanımları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kpi_definitions (
                    id TEXT PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    kpi_name TEXT NOT NULL,
                    kpi_description TEXT,
                    calculation_formula TEXT NOT NULL,
                    target_value REAL,
                    unit TEXT,
                    category TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id)
                )
            """)

            # KPI değerleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kpi_values (
                    id TEXT PRIMARY KEY,
                    kpi_id TEXT NOT NULL,
                    company_id INTEGER NOT NULL,
                    period TEXT NOT NULL,
                    value REAL NOT NULL,
                    calculated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(kpi_id) REFERENCES kpi_definitions(id),
                    FOREIGN KEY(company_id) REFERENCES companies(id)
                )
            """)

            conn.commit()
            conn.close()

        except Exception as e:
            logging.error(f"[HATA] Dashboard tabloları oluşturulamadı: {e}")

    def add_data_source(self, company_id: int, source_name: str, source_type: str,
                       connection_string: str, query: str, refresh_interval: int = 60) -> str:
        """Veri kaynağı ekle"""
        try:
            source_id = f"source_{company_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO data_sources
                (id, company_id, source_name, source_type, connection_string, query, refresh_interval)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (source_id, company_id, source_name, source_type, connection_string, query, refresh_interval))

            conn.commit()
            conn.close()

            logging.info(f"[OK] Veri kaynağı eklendi: {source_id}")
            return source_id

        except Exception as e:
            logging.error(f"[HATA] Veri kaynağı eklenemedi: {e}")
            return ""

    def add_dashboard_widget(self, company_id: int, widget_type: str, title: str,
                           data_source: str, config: Dict[str, Any],
                           position: Tuple[int, int] = (0, 0),
                           size: Tuple[int, int] = (4, 3)) -> str:
        """Dashboard widget ekle"""
        try:
            widget_id = f"widget_{company_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO dashboard_widgets
                (id, company_id, widget_type, title, data_source, config, position_x, position_y, width, height)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                widget_id, company_id, widget_type, title, data_source,
                json.dumps(config), position[0], position[1], size[0], size[1]
            ))

            conn.commit()
            conn.close()

            logging.info(f"[OK] Dashboard widget eklendi: {widget_id}")
            return widget_id

        except Exception as e:
            logging.error(f"[HATA] Dashboard widget eklenemedi: {e}")
            return ""

    def get_dashboard_data(self, company_id: int) -> Dict[str, Any]:
        """Dashboard verilerini getir"""
        try:
            # Widget'ları al
            widgets = self._get_widgets(company_id)

            # Veri kaynaklarını al
            data_sources = self._get_data_sources(company_id)

            # KPI'ları al
            kpis = self._get_kpis(company_id)

            # Dashboard verilerini oluştur
            dashboard_data = {
                'widgets': widgets,
                'data_sources': data_sources,
                'kpis': kpis,
                'last_updated': datetime.now().isoformat()
            }

            return dashboard_data

        except Exception as e:
            logging.error(f"[HATA] Dashboard verileri alınamadı: {e}")
            return {}

    def _get_widgets(self, company_id: int) -> List[Dict[str, Any]]:
        """Widget'ları getir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM dashboard_widgets WHERE company_id = ? AND is_active = 1
                ORDER BY position_y, position_x
            """, (company_id,))

            widgets = []
            for row in cursor.fetchall():
                widgets.append({
                    'id': row[0],
                    'widget_type': row[2],
                    'title': row[3],
                    'data_source': row[4],
                    'config': json.loads(row[5]),
                    'position': (row[6], row[7]),
                    'size': (row[8], row[9])
                })

            conn.close()
            return widgets

        except Exception as e:
            logging.error(f"[HATA] Widget'lar alınamadı: {e}")
            return []

    def _get_data_sources(self, company_id: int) -> List[Dict[str, Any]]:
        """Veri kaynaklarını getir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM data_sources WHERE company_id = ? AND is_active = 1
            """, (company_id,))

            sources = []
            for row in cursor.fetchall():
                sources.append({
                    'id': row[0],
                    'source_name': row[2],
                    'source_type': row[3],
                    'connection_string': row[4],
                    'query': row[5],
                    'refresh_interval': row[6],
                    'last_updated': row[7]
                })

            conn.close()
            return sources

        except Exception as e:
            logging.error(f"[HATA] Veri kaynakları alınamadı: {e}")
            return []

    def _get_kpis(self, company_id: int) -> List[Dict[str, Any]]:
        """KPI'ları getir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT kd.*, kv.value, kv.period, kv.calculated_at
                FROM kpi_definitions kd
                LEFT JOIN kpi_values kv ON kd.id = kv.kpi_id
                WHERE kd.company_id = ? AND kd.is_active = 1
                ORDER BY kd.category, kd.kpi_name
            """, (company_id,))

            kpis = []
            for row in cursor.fetchall():
                kpis.append({
                    'id': row[0],
                    'kpi_name': row[2],
                    'kpi_description': row[3],
                    'calculation_formula': row[4],
                    'target_value': row[5],
                    'unit': row[6],
                    'category': row[7],
                    'current_value': row[9],
                    'period': row[10],
                    'calculated_at': row[11]
                })

            conn.close()
            return kpis

        except Exception as e:
            logging.error(f"[HATA] KPI'lar alınamadı: {e}")
            return []

    def create_chart_widget(self, company_id: int, title: str, chart_type: str,
                          data_source: str, x_column: str, y_column: str) -> str:
        """Grafik widget oluştur"""
        try:
            config = {
                'chart_type': chart_type,
                'x_column': x_column,
                'y_column': y_column,
                'colors': ['#3498db', '#e74c3c', '#2ecc71', '#f39c12'],
                'show_legend': True,
                'show_grid': True
            }

            widget_id = self.add_dashboard_widget(
                company_id=company_id,
                widget_type='chart',
                title=title,
                data_source=data_source,
                config=config
            )

            return widget_id

        except Exception as e:
            logging.error(f"[HATA] Grafik widget oluşturulamadı: {e}")
            return ""

    def create_metric_widget(self, company_id: int, title: str, metric_name: str,
                           target_value: float = None, unit: str = "") -> str:
        """Metrik widget oluştur"""
        try:
            config = {
                'metric_name': metric_name,
                'target_value': target_value,
                'unit': unit,
                'show_trend': True,
                'show_target': target_value is not None
            }

            widget_id = self.add_dashboard_widget(
                company_id=company_id,
                widget_type='metric',
                title=title,
                data_source='kpi',
                config=config
            )

            return widget_id

        except Exception as e:
            logging.error(f"[HATA] Metrik widget oluşturulamadı: {e}")
            return ""

    def create_table_widget(self, company_id: int, title: str, data_source: str,
                           columns: List[str], page_size: int = 10) -> str:
        """Tablo widget oluştur"""
        try:
            config = {
                'columns': columns,
                'page_size': page_size,
                'sortable': True,
                'filterable': True,
                'exportable': True
            }

            widget_id = self.add_dashboard_widget(
                company_id=company_id,
                widget_type='table',
                title=title,
                data_source=data_source,
                config=config
            )

            return widget_id

        except Exception as e:
            logging.error(f"[HATA] Tablo widget oluşturulamadı: {e}")
            return ""

    def add_kpi_definition(self, company_id: int, kpi_name: str, description: str,
                          calculation_formula: str, target_value: float = None,
                          unit: str = "", category: str = "") -> str:
        """KPI tanımı ekle"""
        try:
            kpi_id = f"kpi_{company_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO kpi_definitions
                (id, company_id, kpi_name, kpi_description, calculation_formula, target_value, unit, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (kpi_id, company_id, kpi_name, description, calculation_formula, target_value, unit, category))

            conn.commit()
            conn.close()

            logging.info(f"[OK] KPI tanımı eklendi: {kpi_id}")
            return kpi_id

        except Exception as e:
            logging.error(f"[HATA] KPI tanımı eklenemedi: {e}")
            return ""

    def calculate_kpi_value(self, kpi_id: str, company_id: int, period: str) -> float:
        """KPI değerini hesapla"""
        try:
            # KPI tanımını al
            kpi_definition = self._get_kpi_definition(kpi_id)
            if not kpi_definition:
                return 0.0

            # Formülü hesapla (gerçek uygulamada daha karmaşık hesaplamalar olacak)
            formula = kpi_definition['calculation_formula']

            # Test hesaplama (gerçek uygulamada veritabanından veri çekilecek)
            if 'total_emissions' in formula:
                value = 150.5  # Test değeri
            elif 'energy_consumption' in formula:
                value = 2500.0  # Test değeri
            elif 'waste_reduction' in formula:
                value = 25.0  # Test değeri
            else:
                value = 100.0  # Varsayılan değer

            # KPI değerini kaydet
            self._save_kpi_value(kpi_id, company_id, period, value)

            return value

        except Exception as e:
            logging.error(f"[HATA] KPI değeri hesaplanamadı: {e}")
            return 0.0

    def _get_kpi_definition(self, kpi_id: str) -> Optional[Dict[str, Any]]:
        """KPI tanımını al"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM kpi_definitions WHERE id = ?
            """, (kpi_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    'id': row[0],
                    'kpi_name': row[2],
                    'calculation_formula': row[4],
                    'target_value': row[5],
                    'unit': row[6]
                }
            return None

        except Exception as e:
            logging.error(f"[HATA] KPI tanımı alınamadı: {e}")
            return None

    def _save_kpi_value(self, kpi_id: str, company_id: int, period: str, value: float):
        """KPI değerini kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            value_id = f"value_{kpi_id}_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            cursor.execute("""
                INSERT OR REPLACE INTO kpi_values
                (id, kpi_id, company_id, period, value)
                VALUES (?, ?, ?, ?, ?)
            """, (value_id, kpi_id, company_id, period, value))

            conn.commit()
            conn.close()

        except Exception as e:
            logging.error(f"[HATA] KPI değeri kaydedilemedi: {e}")

    def generate_dashboard_report(self, company_id: int) -> Dict[str, Any]:
        """Dashboard raporu oluştur"""
        try:
            # Dashboard verilerini al
            dashboard_data = self.get_dashboard_data(company_id)

            # Rapor oluştur
            report = {
                'company_id': company_id,
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_widgets': len(dashboard_data.get('widgets', [])),
                    'total_data_sources': len(dashboard_data.get('data_sources', [])),
                    'total_kpis': len(dashboard_data.get('kpis', []))
                },
                'widgets': dashboard_data.get('widgets', []),
                'kpis': dashboard_data.get('kpis', []),
                'data_sources': dashboard_data.get('data_sources', [])
            }

            return report

        except Exception as e:
            logging.error(f"[HATA] Dashboard raporu oluşturulamadı: {e}")
            return {}


if __name__ == "__main__":
    # Test
    logging.info("[TEST] Gelişmiş Dashboard...")

    dashboard = AdvancedDashboard()

    # Test veri kaynağı ekle
    source_id = dashboard.add_data_source(
        company_id=1,
        source_name="SDG Verileri",
        source_type="database",
        connection_string="data/sdg_desktop.db",
        query="SELECT * FROM responses WHERE company_id = 1"
    )

    logging.info(f"Veri kaynağı eklendi: {source_id}")

    # Test widget ekle
    widget_id = dashboard.create_chart_widget(
        company_id=1,
        title="SDG İlerleme Grafiği",
        chart_type="line",
        data_source=source_id,
        x_column="period",
        y_column="progress_pct"
    )

    logging.info(f"Widget eklendi: {widget_id}")

    # Test KPI ekle
    kpi_id = dashboard.add_kpi_definition(
        company_id=1,
        kpi_name="Toplam Emisyon",
        description="Yıllık toplam emisyon miktarı",
        calculation_formula="SUM(emissions)",
        target_value=100.0,
        unit="tCO2e",
        category="Çevre"
    )

    logging.info(f"KPI tanımı eklendi: {kpi_id}")

    # KPI değerini hesapla
    value = dashboard.calculate_kpi_value(kpi_id, 1, "2024")
    logging.info(f"KPI değeri hesaplandı: {value}")

    logging.info("[OK] Test tamamlandı")
