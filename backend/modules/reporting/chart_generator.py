#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grafik Oluşturma Modülü
Veri görselleştirme ve grafik üretimi
"""

import logging
import json
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, Optional
from config.database import DB_PATH


class ChartGenerator:
    """Grafik oluşturma ve veri görselleştirme"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """Grafik modülü tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chart_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    chart_name TEXT NOT NULL,
                    chart_type TEXT NOT NULL,
                    chart_config TEXT NOT NULL,
                    data_source TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            conn.commit()
            logging.info("[OK] Grafik olusturma modulu tablolari basariyla olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] Grafik olusturma modulu tablo olusturma: {e}")
            conn.rollback()
        finally:
            conn.close()

    def create_chart_config(self, chart_type: str, data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Grafik konfigürasyonu oluştur"""
        config = {
            'type': chart_type,
            'data': data,
            'options': options or {}
        }

        # Grafik tipine göre özel ayarlar
        opts: Dict[str, Any] = config['options'] if isinstance(config['options'], dict) else {}
        config['options'] = opts
        if chart_type == 'line':
            opts['responsive'] = True
            opts['scales'] = {
                'y': {'beginAtZero': True}
            }
        elif chart_type == 'bar':
            opts['responsive'] = True
            opts['scales'] = {
                'y': {'beginAtZero': True}
            }
        elif chart_type == 'pie':
            opts['responsive'] = True
            opts['plugins'] = {
                'legend': {'position': 'bottom'}
            }

        return config

    def generate_carbon_footprint_chart(self, company_id: int, year: int) -> Dict[str, Any]:
        """Karbon ayak izi grafiği oluştur"""
        # Bu fonksiyon gerçek veri çekerek grafik oluşturur
        # Şimdilik örnek veri döndürüyor

        data = {
            'labels': ['Scope 1', 'Scope 2', 'Scope 3'],
            'datasets': [{
                'label': 'Karbon Emisyonları (tCO2e)',
                'data': [150, 300, 200],
                'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56']
            }]
        }

        options = {
            'title': {
                'display': True,
                'text': f'{year} Yılı Karbon Ayak İzi'
            }
        }

        return self.create_chart_config('pie', data, options)

    def generate_energy_consumption_chart(self, company_id: int, year: int) -> Dict[str, Any]:
        """Enerji tüketimi grafiği oluştur"""
        data = {
            'labels': ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
                      'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'],
            'datasets': [{
                'label': 'Elektrik Tüketimi (kWh)',
                'data': [1200, 1350, 1100, 980, 1050, 1300, 1400, 1450, 1200, 1100, 1000, 1150],
                'borderColor': '#36A2EB',
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'fill': True
            }]
        }

        options = {
            'title': {
                'display': True,
                'text': f'{year} Yılı Aylık Enerji Tüketimi'
            }
        }

        return self.create_chart_config('line', data, options)

    def generate_employee_satisfaction_chart(self, company_id: int, year: int) -> Dict[str, Any]:
        """Çalışan memnuniyeti grafiği oluştur"""
        data = {
            'labels': ['Çok Memnun', 'Memnun', 'Orta', 'Memnun Değil', 'Hiç Memnun Değil'],
            'datasets': [{
                'label': 'Çalışan Sayısı',
                'data': [45, 120, 80, 25, 10],
                'backgroundColor': [
                    '#4CAF50',  # Çok Memnun - Yeşil
                    '#8BC34A',  # Memnun - Açık Yeşil
                    '#FFC107',  # Orta - Sarı
                    '#FF9800',  # Memnun Değil - Turuncu
                    '#F44336'   # Hiç Memnun Değil - Kırmızı
                ]
            }]
        }

        options = {
            'title': {
                'display': True,
                'text': f'{year} Yılı Çalışan Memnuniyeti'
            }
        }

        return self.create_chart_config('doughnut', data, options)

    def generate_sustainability_kpi_chart(self, company_id: int, year: int) -> Dict[str, Any]:
        """Sürdürülebilirlik KPI grafiği oluştur"""
        data = {
            'labels': ['Çevresel', 'Sosyal', 'Ekonomik', 'Yönetişim'],
            'datasets': [{
                'label': 'KPI Skoru',
                'data': [85, 78, 92, 88],
                'backgroundColor': ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0']
            }]
        }

        options = {
            'title': {
                'display': True,
                'text': f'{year} Yılı Sürdürülebilirlik KPI Skorları'
            },
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'max': 100
                }
            }
        }

        return self.create_chart_config('bar', data, options)

    def export_chart_to_html(self, chart_config: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Grafiği HTML olarak dışa aktar"""
        if not filename:
            filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Grafik - {chart_config.get('options', {}).get('title', {}).get('text', 'Veri Grafiği')}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div style="width: 800px; height: 600px; margin: 50px auto;">
        <canvas id="myChart"></canvas>
    </div>
    
    <script>
        const ctx = document.getElementById('myChart').getContext('2d');
        const chart = new Chart(ctx, {json.dumps(chart_config, ensure_ascii=False, indent=2)});
    </script>
</body>
</html>
"""

        return html_content
