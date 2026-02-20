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

from backend.core.base_manager import BaseTenantManager

class AdvancedDashboard(BaseTenantManager):
    """Gelişmiş dashboard yöneticisi"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None):
        super().__init__(db_path, company_id)
        self._create_tables()

    def _create_tables(self):
        """Dashboard tablolarını oluştur"""
        try:
            # Tabloları oluştur (DatabaseManager zaten bağlantıyı yönetir)
            queries = [
                """
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
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    -- FOREIGN KEY constraint is handled by logical checks in SQLite usually, 
                    -- or enforced if PRAGMA foreign_keys=ON. 
                    -- We rely on BaseTenantManager for isolation.
                )
                """,
                """
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
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS dashboard_layouts (
                    id TEXT PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    layout_name TEXT NOT NULL,
                    layout_config TEXT NOT NULL,
                    is_default INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """,
                """
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
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS kpi_values (
                    id TEXT PRIMARY KEY,
                    kpi_id TEXT NOT NULL,
                    company_id INTEGER NOT NULL,
                    period TEXT NOT NULL,
                    value REAL NOT NULL,
                    calculated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(kpi_id) REFERENCES kpi_definitions(id)
                )
                """
            ]
            
            for query in queries:
                self.db.execute_update(query)
                
        except Exception as e:
            logging.error(f"[HATA] Dashboard tabloları oluşturulamadı: {e}")

    def add_data_source(self, company_id: Optional[int], source_name: str, source_type: str,
                       connection_string: str, query: str, refresh_interval: int = 60) -> str:
        """Veri kaynağı ekle"""
        try:
            cid = self._ensure_context(company_id)
            source_id = f"source_{cid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            data = {
                'id': source_id,
                'source_name': source_name,
                'source_type': source_type,
                'connection_string': connection_string,
                'query': query,
                'refresh_interval': refresh_interval
            }
            
            self.insert('data_sources', data, company_id=cid)
            logging.info(f"[OK] Veri kaynağı eklendi: {source_id}")
            return source_id

        except Exception as e:
            logging.error(f"[HATA] Veri kaynağı eklenemedi: {e}")
            return ""

    def add_dashboard_widget(self, company_id: Optional[int], widget_type: str, title: str,
                           data_source: str, config: Dict[str, Any],
                           position: Tuple[int, int] = (0, 0),
                           size: Tuple[int, int] = (4, 3)) -> str:
        """Dashboard widget ekle"""
        try:
            cid = self._ensure_context(company_id)
            widget_id = f"widget_{cid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            data = {
                'id': widget_id,
                'widget_type': widget_type,
                'title': title,
                'data_source': data_source,
                'config': json.dumps(config),
                'position_x': position[0],
                'position_y': position[1],
                'width': size[0],
                'height': size[1]
            }
            
            self.insert('dashboard_widgets', data, company_id=cid)
            logging.info(f"[OK] Dashboard widget eklendi: {widget_id}")
            return widget_id

        except Exception as e:
            logging.error(f"[HATA] Dashboard widget eklenemedi: {e}")
            return ""

    def get_dashboard_data(self, company_id: Optional[int] = None) -> Dict[str, Any]:
        """Dashboard verilerini getir"""
        try:
            cid = self._ensure_context(company_id)
            
            # Widget'ları al
            widgets = self._get_widgets(cid)

            # Veri kaynaklarını al
            data_sources = self._get_data_sources(cid)

            # KPI'ları al
            kpis = self._get_kpis(cid)
            
            # İstatistikler (Şablon uyumluluğu için)
            stats = {
                'total_widgets': len(widgets),
                'active_sources': len(data_sources),
                'kpi_count': len(kpis),
                'system_status': 'Active'
            }

            # Kayıtlar (Şablon uyumluluğu için - KPI listesi)
            records = []
            for kpi in kpis:
                records.append({
                    'KPI Adı': kpi.get('kpi_name'),
                    'Değer': f"{kpi.get('value', 0)} {kpi.get('unit', '')}",
                    'Hedef': kpi.get('target_value'),
                    'Durum': 'İyi' if (kpi.get('value', 0) or 0) >= (kpi.get('target_value', 0) or 0) else 'Riskli'
                })

            # Dashboard verilerini oluştur
            dashboard_data = {
                'widgets': widgets,
                'data_sources': data_sources,
                'kpis': kpis,
                'stats': stats,
                'records': records,
                'columns': ['KPI Adı', 'Değer', 'Hedef', 'Durum'],
                'last_updated': datetime.now().isoformat()
            }

            return dashboard_data

        except Exception as e:
            logging.error(f"[HATA] Dashboard verileri alınamadı: {e}")
            return {}

    def _get_widgets(self, company_id: int) -> List[Dict[str, Any]]:
        """Widget'ları getir"""
        try:
            rows = self.select('dashboard_widgets', company_id=company_id, where="is_active = 1", order_by="position_y, position_x")
            
            widgets = []
            for row in rows:
                widgets.append({
                    'id': row['id'],
                    'widget_type': row['widget_type'],
                    'title': row['title'],
                    'data_source': row['data_source'],
                    'config': json.loads(row['config']),
                    'position': (row['position_x'], row['position_y']),
                    'size': (row['width'], row['height'])
                })
            return widgets

        except Exception as e:
            logging.error(f"[HATA] Widget'lar alınamadı: {e}")
            return []

    def _get_data_sources(self, company_id: int) -> List[Dict[str, Any]]:
        """Veri kaynaklarını getir"""
        try:
            rows = self.select('data_sources', company_id=company_id, where="is_active = 1")
            
            sources = []
            for row in rows:
                sources.append({
                    'id': row['id'],
                    'source_name': row['source_name'],
                    'source_type': row['source_type'],
                    'connection_string': row['connection_string'],
                    'query': row['query'],
                    'refresh_interval': row['refresh_interval'],
                    'last_updated': row['last_updated']
                })
            return sources

        except Exception as e:
            logging.error(f"[HATA] Veri kaynakları alınamadı: {e}")
            return []

    def _get_kpis(self, company_id: int) -> List[Dict[str, Any]]:
        """KPI'ları getir"""
        try:
            # JOIN işlemi BaseTenantManager'da doğrudan desteklenmez, bu yüzden raw query kullanacağız ama company_id'yi inject edeceğiz
            query = """
                SELECT kd.*, kv.value, kv.period, kv.calculated_at
                FROM kpi_definitions kd
                LEFT JOIN kpi_values kv ON kd.id = kv.kpi_id
                WHERE kd.company_id = ? AND kd.is_active = 1
                ORDER BY kd.category, kd.kpi_name
            """
            
            # BaseTenantManager.db.execute_query doğrudan kullanılabilir
            rows = self.db.execute_query(query, (company_id,))
            
            kpis = []
            for row in rows:
                kpis.append({
                    'id': row[0],
                    'company_id': row[1],
                    'kpi_name': row[2],
                    'kpi_description': row[3],
                    'calculation_formula': row[4],
                    'target_value': row[5],
                    'unit': row[6],
                    'category': row[7],
                    'value': row[8],
                    'period': row[9],
                    'calculated_at': row[10]
                })
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
            cid = self._ensure_context(company_id)
            kpi_id = f"kpi_{cid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            data = {
                'id': kpi_id,
                'kpi_name': kpi_name,
                'kpi_description': description,
                'calculation_formula': calculation_formula,
                'target_value': target_value,
                'unit': unit,
                'category': category
            }
            
            self.insert('kpi_definitions', data, company_id=cid)
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
            # Not: BaseTenantManager.select genellikle company_id filtreler, ancak ID ile doğrudan seçimde gerek olmayabilir
            # Yine de güvenli tarafta kalmak için raw query kullanabiliriz veya select
            # Burada company_id bağlamı olmadığı için raw query daha güvenli
            
            rows = self.db.execute_query("SELECT * FROM kpi_definitions WHERE id = ?", (kpi_id,))
            if rows:
                row = rows[0]
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
            cid = self._ensure_context(company_id)
            value_id = f"value_{kpi_id}_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Upsert mantığı
            self.db.execute_update("""
                INSERT OR REPLACE INTO kpi_values
                (id, kpi_id, company_id, period, value)
                VALUES (?, ?, ?, ?, ?)
            """, (value_id, kpi_id, cid, period, value))

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
