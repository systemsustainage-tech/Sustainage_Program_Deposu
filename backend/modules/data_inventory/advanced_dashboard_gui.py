#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GELİŞMİŞ DASHBOARD GUI
======================

Gelişmiş veri envanteri için kullanıcı arayüzü
"""

import logging
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Dict, List

from utils.language_manager import LanguageManager

from .advanced_dashboard import AdvancedDashboard
from config.icons import Icons
from modules.environmental.detailed_energy_manager import DetailedEnergyManager
from modules.environmental.waste_manager import WasteManager
from modules.environmental.water_manager import WaterManager
from modules.environmental.carbon_manager import CarbonManager
from datetime import datetime


class AdvancedDashboardGUI:
    """Gelişmiş dashboard GUI sınıfı"""

    def __init__(self, parent, company_id: int = None, db_path: str = None):
        self.parent = parent
        self.company_id = company_id or 1
        self.db_path = db_path or 'data/sdg_desktop.db'
        self.lm = LanguageManager()

        # Dashboard
        self.dashboard = AdvancedDashboard(db_path)

        # Theme
        self.theme = {
            'bg': '#f5f5f5',
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'text': '#2c3e50',
            'light': '#ecf0f1'
        }

        self.setup_ui()

    def setup_ui(self):
        """UI oluştur"""
        # Main container
        main_frame = tk.Frame(self.parent, bg=self.theme['bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Header
        self._create_header(main_frame)

        # Content with notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, pady=20)

        # Tabs
        self._create_dashboard_tab(notebook)
        self._create_widgets_tab(notebook)
        self._create_data_sources_tab(notebook)
        self._create_kpis_tab(notebook)

    def _create_header(self, parent):
        """Header oluştur"""
        header_frame = tk.Frame(parent, bg=self.theme['primary'], height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(
            header_frame,
            text=f" {self.lm.tr('adv_dashboard_title', 'GELİŞMİŞ VERİ ENVANTERİ')}",
            font=('Segoe UI', 18, 'bold'),
            bg=self.theme['primary'],
            fg='white'
        )
        title_label.pack(side='left', padx=20, pady=20)

        # Refresh button
        refresh_btn = tk.Button(
            header_frame,
            text=f" {self.lm.tr('btn_refresh', 'Yenile')}",
            font=('Segoe UI', 12, 'bold'),
            bg=self.theme['success'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10,
            command=self._refresh_dashboard
        )
        refresh_btn.pack(side='right', padx=20, pady=20)

    def _create_dashboard_tab(self, notebook):
        """Dashboard sekmesi"""
        dashboard_frame = tk.Frame(notebook, bg=self.theme['bg'])
        notebook.add(dashboard_frame, text=f" {self.lm.tr('menu_dashboard', 'Dashboard')}")

        # Header
        header_frame = tk.Frame(dashboard_frame, bg=self.theme['bg'])
        header_frame.pack(fill='x', pady=10)

        tk.Label(
            header_frame,
            text=self.lm.tr('dashboard_main_title', "Ana Dashboard"),
            font=('Segoe UI', 14, 'bold'),
            bg=self.theme['bg'],
            fg=self.theme['text']
        ).pack(side='left')

        # Dashboard content
        self.dashboard_content = tk.Frame(dashboard_frame, bg=self.theme['bg'])
        self.dashboard_content.pack(fill='both', expand=True, pady=10)

        # Load initial data
        self._load_dashboard()

    def _create_widgets_tab(self, notebook):
        """Widget'lar sekmesi"""
        widgets_frame = tk.Frame(notebook, bg=self.theme['bg'])
        widget_tab_text = self.lm.tr('tab_widgets', 'Widget\'lar')
        notebook.add(widgets_frame, text=f" {widget_tab_text}")

        # Header
        header_frame = tk.Frame(widgets_frame, bg=self.theme['bg'])
        header_frame.pack(fill='x', pady=10)

        tk.Label(
            header_frame,
            text=self.lm.tr('dashboard_widgets_title', "Dashboard Widget'ları"),
            font=('Segoe UI', 14, 'bold'),
            bg=self.theme['bg'],
            fg=self.theme['text']
        ).pack(side='left')

        # Add widget button
        tk.Button(
            header_frame,
            text=f" {self.lm.tr('btn_new_widget', 'Yeni Widget')}",
            font=('Segoe UI', 10),
            bg=self.theme['success'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=10,
            pady=5,
            command=self._add_widget
        ).pack(side='right')

        # Widgets list
        self.widgets_frame = tk.Frame(widgets_frame, bg=self.theme['bg'])
        self.widgets_frame.pack(fill='both', expand=True, pady=10)

        # Load initial data
        self._load_widgets()

    def _create_data_sources_tab(self, notebook):
        """Veri kaynakları sekmesi"""
        sources_frame = tk.Frame(notebook, bg=self.theme['bg'])
        notebook.add(sources_frame, text=f" {self.lm.tr('tab_data_sources', 'Veri Kaynakları')}")

        # Header
        header_frame = tk.Frame(sources_frame, bg=self.theme['bg'])
        header_frame.pack(fill='x', pady=10)

        tk.Label(
            header_frame,
            text=self.lm.tr('data_sources_title', "Veri Kaynakları"),
            font=('Segoe UI', 14, 'bold'),
            bg=self.theme['bg'],
            fg=self.theme['text']
        ).pack(side='left')

        # Add source button
        tk.Button(
            header_frame,
            text=f" {self.lm.tr('btn_new_source', 'Yeni Kaynak')}",
            font=('Segoe UI', 10),
            bg=self.theme['success'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=10,
            pady=5,
            command=self._add_data_source
        ).pack(side='right')

        # Sources list
        self.sources_frame = tk.Frame(sources_frame, bg=self.theme['bg'])
        self.sources_frame.pack(fill='both', expand=True, pady=10)

        # Load initial data
        self._load_data_sources()

    def _create_kpis_tab(self, notebook):
        """KPI'lar sekmesi"""
        kpis_frame = tk.Frame(notebook, bg=self.theme['bg'])
        kpi_tab_text = self.lm.tr('tab_kpis', 'KPI\'lar')
        notebook.add(kpis_frame, text=f" {kpi_tab_text}")

        # Header
        header_frame = tk.Frame(kpis_frame, bg=self.theme['bg'])
        header_frame.pack(fill='x', pady=10)

        tk.Label(
            header_frame,
            text=self.lm.tr('kpi_management_title', "KPI Yönetimi"),
            font=('Segoe UI', 14, 'bold'),
            bg=self.theme['bg'],
            fg=self.theme['text']
        ).pack(side='left')

        # Add KPI button
        tk.Button(
            header_frame,
            text=f" {self.lm.tr('btn_new_kpi', 'Yeni KPI')}",
            font=('Segoe UI', 10),
            bg=self.theme['success'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=10,
            pady=5,
            command=self._add_kpi
        ).pack(side='right')

        # KPIs list
        self.kpis_frame = tk.Frame(kpis_frame, bg=self.theme['bg'])
        self.kpis_frame.pack(fill='both', expand=True, pady=10)

        # Load initial data
        self._load_kpis()

    def _load_dashboard(self):
        """Dashboard'u yükle"""
        try:
            # Clear existing widgets
            for widget in self.dashboard_content.winfo_children():
                widget.destroy()

            # Gerçek veri yöneticilerini başlat
            energy_manager = DetailedEnergyManager(self.db_path)
            water_manager = WaterManager(self.db_path)
            waste_manager = WasteManager(self.db_path)
            carbon_manager = CarbonManager(self.db_path)

            current_year = datetime.now().year
            
            # Enerji Verileri
            energy_data = energy_manager.get_annual_report_data(self.company_id, current_year)
            total_energy = energy_data.get('total_consumption', 0)
            energy_cost = energy_data.get('total_cost', 0)
            
            # Su Verileri
            water_data = water_manager.get_water_summary(self.company_id, current_year)
            total_water = water_data.get('total_consumption', 0)
            water_recycling_ratio = water_data.get('recycling_ratio', 0)
            
            # Atık Verileri
            waste_data = waste_manager.get_waste_summary(self.company_id, current_year)
            total_waste = waste_data.get('total_generation', 0)
            waste_recycling_ratio = waste_data.get('recycling_ratio', 0)

            # Karbon Verileri
            carbon_data = carbon_manager.get_total_carbon_footprint(self.company_id, current_year)
            total_carbon = carbon_data.get('total_footprint', 0)
            
            # Widget verilerini hazırla
            dashboard_data = {
                'summary': {
                    'total_widgets': 5,
                    'total_data_sources': 4,  # Enerji, Su, Atık, Karbon
                    'total_kpis': 8
                },
                'widgets': [
                    {
                        'id': 'widget_energy',
                        'title': self.lm.tr('widget_energy_consumption', 'Enerji Tüketimi'),
                        'type': 'metric',
                        'data': {
                            'value': f"{total_energy:,.2f}", 
                            'unit': 'kWh', 
                            'trend': '0%' 
                        }
                    },
                    {
                        'id': 'widget_water',
                        'title': self.lm.tr('widget_water_consumption', 'Su Tüketimi'),
                        'type': 'metric',
                        'data': {
                            'value': f"{total_water:,.2f}", 
                            'unit': 'm³', 
                            'trend': '0%'
                        }
                    },
                    {
                        'id': 'widget_waste',
                        'title': self.lm.tr('widget_waste_generation', 'Atık Üretimi'),
                        'type': 'metric',
                        'data': {
                            'value': f"{total_waste:,.2f}", 
                            'unit': 'ton', 
                            'trend': '0%'
                        }
                    },
                    {
                        'id': 'widget_carbon',
                        'title': self.lm.tr('widget_carbon_footprint', 'Karbon Ayak İzi'),
                        'type': 'metric',
                        'data': {
                            'value': f"{total_carbon:,.2f}", 
                            'unit': 'tCO2e', 
                            'trend': '0%'
                        }
                    },
                    {
                        'id': 'widget_recycling',
                        'title': self.lm.tr('widget_recycling_rate', 'Geri Dönüşüm Oranı'),
                        'type': 'metric',
                        'data': {
                            'value': f"{waste_recycling_ratio:.1f}", 
                            'unit': '%', 
                            'trend': '0%'
                        }
                    }
                ]
            }

            # Summary cards
            self._create_summary_cards(dashboard_data['summary'])

            # Widgets grid
            self._create_widgets_grid(dashboard_data['widgets'])

        except Exception as e:
            logging.error(f"[HATA] Dashboard yüklenemedi: {e}")

    def _create_summary_cards(self, summary: Dict[str, Any]):
        """Özet kartları oluştur"""
        summary_frame = tk.Frame(self.dashboard_content, bg=self.theme['bg'])
        summary_frame.pack(fill='x', pady=10)

        # Widgets count
        widgets_card = tk.Frame(summary_frame, bg='white', relief='solid', bd=1)
        widgets_card.pack(side='left', fill='x', expand=True, padx=5)

        widget_label = self.lm.tr('tab_widgets', 'Widget\'lar')
        tk.Label(
            widgets_card,
            text=f" {widget_label}",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg=self.theme['text']
        ).pack(pady=5)

        tk.Label(
            widgets_card,
            text=f"{summary['total_widgets']}",
            font=('Segoe UI', 24, 'bold'),
            bg='white',
            fg=self.theme['secondary']
        ).pack(pady=5)

        # Data sources count
        sources_card = tk.Frame(summary_frame, bg='white', relief='solid', bd=1)
        sources_card.pack(side='left', fill='x', expand=True, padx=5)

        tk.Label(
            sources_card,
            text=f" {self.lm.tr('tab_data_sources', 'Veri Kaynakları')}",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg=self.theme['text']
        ).pack(pady=5)

        tk.Label(
            sources_card,
            text=f"{summary['total_data_sources']}",
            font=('Segoe UI', 24, 'bold'),
            bg='white',
            fg=self.theme['success']
        ).pack(pady=5)

        # KPIs count
        kpis_card = tk.Frame(summary_frame, bg='white', relief='solid', bd=1)
        kpis_card.pack(side='left', fill='x', expand=True, padx=5)

        kpi_label = self.lm.tr('tab_kpis', 'KPI\'lar')
        tk.Label(
            kpis_card,
            text=f" {kpi_label}",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg=self.theme['text']
        ).pack(pady=5)

        tk.Label(
            kpis_card,
            text=f"{summary['total_kpis']}",
            font=('Segoe UI', 24, 'bold'),
            bg='white',
            fg=self.theme['warning']
        ).pack(pady=5)

    def _create_widgets_grid(self, widgets: List[Dict[str, Any]]):
        """Widget'lar grid'i oluştur"""
        grid_frame = tk.Frame(self.dashboard_content, bg=self.theme['bg'])
        grid_frame.pack(fill='both', expand=True, pady=10)

        # 2x2 grid
        for i, widget in enumerate(widgets):
            row = i // 2
            col = i % 2

            widget_frame = tk.Frame(grid_frame, bg='white', relief='solid', bd=1)
            widget_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')

            # Configure grid weights
            grid_frame.grid_rowconfigure(row, weight=1)
            grid_frame.grid_columnconfigure(col, weight=1)

            # Widget content
            self._create_widget_content(widget_frame, widget)

    def _create_widget_content(self, parent, widget: Dict[str, Any]):
        """Widget içeriği oluştur"""
        # Header
        header_frame = tk.Frame(parent, bg='white')
        header_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(
            header_frame,
            text=widget['title'],
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg=self.theme['text']
        ).pack(side='left')

        # Content based on type
        if widget['type'] == 'chart':
            self._create_chart_widget(parent, widget)
        elif widget['type'] == 'metric':
            self._create_metric_widget(parent, widget)
        elif widget['type'] == 'table':
            self._create_table_widget(parent, widget)

    def _create_chart_widget(self, parent, widget: Dict[str, Any]):
        """Grafik widget oluştur"""
        content_frame = tk.Frame(parent, bg='white')
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Chart placeholder
        chart_frame = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        chart_frame.pack(fill='both', expand=True, padx=5, pady=5)

        tk.Label(
            chart_frame,
            text=self.lm.tr("chart_label", " Grafik"),
            font=('Segoe UI', 16),
            bg='#f8f9fa',
            fg=self.theme['secondary']
        ).pack(expand=True)

        # Data
        data = widget['data']
        tk.Label(
            content_frame,
            text=f"{self.lm.tr('progress_label', 'İlerleme:')} %{data['progress']:.1f}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(anchor='w')

        tk.Label(
            content_frame,
            text=f"{self.lm.tr('target_label', 'Hedef:')} %{data['target']:.1f}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['secondary']
        ).pack(anchor='w')

    def _create_metric_widget(self, parent, widget: Dict[str, Any]):
        """Metrik widget oluştur"""
        content_frame = tk.Frame(parent, bg='white')
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Value
        data = widget['data']
        value_label = tk.Label(
            content_frame,
            text=f"{data['value']} {data['unit']}",
            font=('Segoe UI', 20, 'bold'),
            bg='white',
            fg=self.theme['success']
        )
        value_label.pack(pady=10)

        # Trend
        trend_color = self.theme['success'] if data['trend'].startswith('-') else self.theme['danger']
        tk.Label(
            content_frame,
            text=f"{self.lm.tr('trend_label', 'Trend:')} {data['trend']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=trend_color
        ).pack(anchor='w')

    def _create_table_widget(self, parent, widget: Dict[str, Any]):
        """Tablo widget oluştur"""
        content_frame = tk.Frame(parent, bg='white')
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Table placeholder
        table_frame = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        table_frame.pack(fill='both', expand=True, padx=5, pady=5)

        tk.Label(
            table_frame,
            text=f" {self.lm.tr('table_placeholder', 'Tablo Alanı')}",
            font=('Segoe UI', 16),
            bg='#f8f9fa',
            fg=self.theme['secondary']
        ).pack(expand=True)

    def _load_widgets(self):
        """Widget'ları yükle"""
        try:
            # Clear existing widgets
            for widget in self.widgets_frame.winfo_children():
                widget.destroy()

            # Test verisi
            test_widgets = [
                {
                    'id': 'widget_1',
                    'title': 'SDG İlerleme Grafiği',
                    'type': 'chart',
                    'data_source': 'SDG Verileri',
                    'position': (0, 0),
                    'size': (4, 3),
                    'is_active': True
                },
                {
                    'id': 'widget_2',
                    'title': 'Toplam Emisyon',
                    'type': 'metric',
                    'data_source': 'KPI',
                    'position': (4, 0),
                    'size': (2, 2),
                    'is_active': True
                },
                {
                    'id': 'widget_3',
                    'title': 'Enerji Tüketimi',
                    'type': 'metric',
                    'data_source': 'KPI',
                    'position': (6, 0),
                    'size': (2, 2),
                    'is_active': True
                },
                {
                    'id': 'widget_4',
                    'title': 'Atık Azaltımı',
                    'type': 'metric',
                    'data_source': 'KPI',
                    'position': (0, 3),
                    'size': (2, 2),
                    'is_active': False
                }
            ]

            for widget in test_widgets:
                self._create_widget_card(self.widgets_frame, widget)

        except Exception as e:
            logging.error(f"[HATA] Widget'lar yüklenemedi: {e}")

    def _create_widget_card(self, parent, widget: Dict[str, Any]):
        """Widget kartı oluştur"""
        # Card frame
        card_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        card_frame.pack(fill='x', pady=5, padx=10)

        # Header
        header_frame = tk.Frame(card_frame, bg='white')
        header_frame.pack(fill='x', padx=15, pady=10)

        # Title
        title_label = tk.Label(
            header_frame,
            text=f" {widget['title']}",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg=self.theme['text']
        )
        title_label.pack(side='left')

        # Type badge
        type_badge = tk.Label(
            header_frame,
            text=widget['type'].upper(),
            font=('Segoe UI', 9),
            bg=self.theme['secondary'],
            fg='white',
            padx=8,
            pady=2
        )
        type_badge.pack(side='right')

        # Content
        content_frame = tk.Frame(card_frame, bg='white')
        content_frame.pack(fill='x', padx=15, pady=(0, 10))

        # Data source
        tk.Label(
            content_frame,
            text=f"{self.lm.tr('data_source_label', ' Veri Kaynağı:')} {widget['data_source']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(anchor='w')

        # Position
        tk.Label(
            content_frame,
            text=f"{self.lm.tr('position_label', ' Konum:')} ({widget['position'][0]}, {widget['position'][1]})",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(anchor='w')

        # Size
        tk.Label(
            content_frame,
            text=f"{self.lm.tr('size_label', ' Boyut:')} {widget['size'][0]}x{widget['size'][1]}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(anchor='w')

        # Status
        status_color = self.theme['success'] if widget['is_active'] else self.theme['danger']
        status_text = self.lm.tr('status_active', 'Aktif') if widget['is_active'] else self.lm.tr('status_passive', 'Pasif')
        tk.Label(
            content_frame,
            text=f"{self.lm.tr('status_label', ' Durum:')} {status_text}",
            font=('Segoe UI', 10),
            bg='white',
            fg=status_color
        ).pack(anchor='w')

        # Actions
        actions_frame = tk.Frame(card_frame, bg='white')
        actions_frame.pack(fill='x', padx=15, pady=(0, 10))

        # Edit button
        tk.Button(
            actions_frame,
            text=self.lm.tr('btn_edit', " Düzenle"),
            font=('Segoe UI', 9),
            bg=self.theme['secondary'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=3,
            command=lambda: self._edit_widget(widget['id'])
        ).pack(side='left', padx=(0, 5))

        # Delete button
        tk.Button(
            actions_frame,
            text=self.lm.tr('btn_delete', " Sil"),
            font=('Segoe UI', 9),
            bg=self.theme['danger'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=3,
            command=lambda: self._delete_widget(widget['id'])
        ).pack(side='left', padx=(0, 5))

        # Toggle button
        toggle_text = self.lm.tr('btn_deactivate', 'Pasifleştir') if widget['is_active'] else self.lm.tr('btn_activate', 'Aktifleştir')
        toggle_color = self.theme['warning'] if widget['is_active'] else self.theme['success']
        tk.Button(
            actions_frame,
            text=toggle_text,
            font=('Segoe UI', 9),
            bg=toggle_color,
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=3,
            command=lambda: self._toggle_widget(widget['id'])
        ).pack(side='left')

    def _load_data_sources(self):
        """Veri kaynaklarını yükle"""
        try:
            # Clear existing widgets
            for widget in self.sources_frame.winfo_children():
                widget.destroy()

            # Test verisi
            test_sources = [
                {
                    'id': 'source_1',
                    'name': 'SDG Verileri',
                    'type': 'database',
                    'connection': 'data/sdg_desktop.db',
                    'query': 'SELECT * FROM responses',
                    'refresh_interval': 60,
                    'last_updated': '2025-10-21 10:30',
                    'is_active': True
                },
                {
                    'id': 'source_2',
                    'name': 'ERP Verileri',
                    'type': 'api',
                    'connection': 'https://erp.company.com/api',
                    'query': 'GET /financial-data',
                    'refresh_interval': 120,
                    'last_updated': '2025-10-21 09:15',
                    'is_active': True
                },
                {
                    'id': 'source_3',
                    'name': 'Excel Dosyası',
                    'type': 'file',
                    'connection': 'data/imports/data.xlsx',
                    'query': 'Sheet1',
                    'refresh_interval': 240,
                    'last_updated': '2025-10-20 16:45',
                    'is_active': False
                }
            ]

            for source in test_sources:
                self._create_source_card(self.sources_frame, source)

        except Exception as e:
            logging.error(f"[HATA] Veri kaynakları yüklenemedi: {e}")

    def _create_source_card(self, parent, source: Dict[str, Any]):
        """Veri kaynağı kartı oluştur"""
        # Card frame
        card_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        card_frame.pack(fill='x', pady=5, padx=10)

        # Header
        header_frame = tk.Frame(card_frame, bg='white')
        header_frame.pack(fill='x', padx=15, pady=10)

        # Name
        name_label = tk.Label(
            header_frame,
            text=f" {source['name']}",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg=self.theme['text']
        )
        name_label.pack(side='left')

        # Type badge
        type_badge = tk.Label(
            header_frame,
            text=source['type'].upper(),
            font=('Segoe UI', 9),
            bg=self.theme['secondary'],
            fg='white',
            padx=8,
            pady=2
        )
        type_badge.pack(side='right')

        # Content
        content_frame = tk.Frame(card_frame, bg='white')
        content_frame.pack(fill='x', padx=15, pady=(0, 10))

        # Connection
        tk.Label(
            content_frame,
            text=f" Bağlantı: {source['connection']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(anchor='w')

        # Query
        tk.Label(
            content_frame,
            text=f" Sorgu: {source['query']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(anchor='w')

        # Refresh interval
        tk.Label(
            content_frame,
            text=f"{Icons.TIME} Yenileme: {source['refresh_interval']} dakika",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(anchor='w')

        # Last updated
        tk.Label(
            content_frame,
            text=f" Son Güncelleme: {source['last_updated']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['secondary']
        ).pack(anchor='w')

        # Status
        status_color = self.theme['success'] if source['is_active'] else self.theme['danger']
        status_text = 'Aktif' if source['is_active'] else 'Pasif'
        tk.Label(
            content_frame,
            text=f" Durum: {status_text}",
            font=('Segoe UI', 10),
            bg='white',
            fg=status_color
        ).pack(anchor='w')

        # Actions
        actions_frame = tk.Frame(card_frame, bg='white')
        actions_frame.pack(fill='x', padx=15, pady=(0, 10))

        # Test button
        tk.Button(
            actions_frame,
            text=" Test",
            font=('Segoe UI', 9),
            bg=self.theme['warning'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=3,
            command=lambda: self._test_source(source['id'])
        ).pack(side='left', padx=(0, 5))

        # Edit button
        tk.Button(
            actions_frame,
            text=" Düzenle",
            font=('Segoe UI', 9),
            bg=self.theme['secondary'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=3,
            command=lambda: self._edit_source(source['id'])
        ).pack(side='left', padx=(0, 5))

        # Delete button
        tk.Button(
            actions_frame,
            text=" Sil",
            font=('Segoe UI', 9),
            bg=self.theme['danger'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=3,
            command=lambda: self._delete_source(source['id'])
        ).pack(side='left')

    def _load_kpis(self):
        """KPI'ları yükle"""
        try:
            # Clear existing widgets
            for widget in self.kpis_frame.winfo_children():
                widget.destroy()

            # Test verisi
            test_kpis = [
                {
                    'id': 'kpi_1',
                    'name': 'Toplam Emisyon',
                    'description': 'Yıllık toplam emisyon miktarı',
                    'value': 150.5,
                    'target': 100.0,
                    'unit': 'tCO2e',
                    'category': 'Çevre',
                    'trend': '+5.2%',
                    'status': 'Hedefin üzerinde'
                },
                {
                    'id': 'kpi_2',
                    'name': 'Enerji Tüketimi',
                    'description': 'Aylık enerji tüketimi',
                    'value': 2500.0,
                    'target': 2000.0,
                    'unit': 'kWh',
                    'category': 'Enerji',
                    'trend': '-2.1%',
                    'status': 'Hedefin üzerinde'
                },
                {
                    'id': 'kpi_3',
                    'name': 'Atık Azaltımı',
                    'description': 'Atık azaltım oranı',
                    'value': 25.0,
                    'target': 30.0,
                    'unit': '%',
                    'category': 'Atık',
                    'trend': '+3.5%',
                    'status': 'Hedefin altında'
                }
            ]

            for kpi in test_kpis:
                self._create_kpi_card(self.kpis_frame, kpi)

        except Exception as e:
            logging.error(f"[HATA] KPI'lar yüklenemedi: {e}")

    def _create_kpi_card(self, parent, kpi: Dict[str, Any]):
        """KPI kartı oluştur"""
        # Card frame
        card_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        card_frame.pack(fill='x', pady=5, padx=10)

        # Header
        header_frame = tk.Frame(card_frame, bg='white')
        header_frame.pack(fill='x', padx=15, pady=10)

        # Name
        name_label = tk.Label(
            header_frame,
            text=f" {kpi['name']}",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg=self.theme['text']
        )
        name_label.pack(side='left')

        # Category badge
        category_badge = tk.Label(
            header_frame,
            text=kpi['category'],
            font=('Segoe UI', 9),
            bg=self.theme['secondary'],
            fg='white',
            padx=8,
            pady=2
        )
        category_badge.pack(side='right')

        # Content
        content_frame = tk.Frame(card_frame, bg='white')
        content_frame.pack(fill='x', padx=15, pady=(0, 10))

        # Description
        tk.Label(
            content_frame,
            text=kpi['description'],
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(anchor='w')

        # Value and target
        value_frame = tk.Frame(content_frame, bg='white')
        value_frame.pack(fill='x', pady=5)

        # Current value
        tk.Label(
            value_frame,
            text=f" Mevcut: {kpi['value']} {kpi['unit']}",
            font=('Segoe UI', 11, 'bold'),
            bg='white',
            fg=self.theme['success']
        ).pack(side='left')

        # Target
        tk.Label(
            value_frame,
            text=f" Hedef: {kpi['target']} {kpi['unit']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['secondary']
        ).pack(side='right')

        # Trend
        trend_color = self.theme['success'] if kpi['trend'].startswith('-') else self.theme['danger']
        tk.Label(
            content_frame,
            text=f" Trend: {kpi['trend']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=trend_color
        ).pack(anchor='w')

        # Status
        status_color = self.theme['success'] if 'altında' in kpi['status'] else self.theme['warning']
        tk.Label(
            content_frame,
            text=f" Durum: {kpi['status']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=status_color
        ).pack(anchor='w')

        # Actions
        actions_frame = tk.Frame(card_frame, bg='white')
        actions_frame.pack(fill='x', padx=15, pady=(0, 10))

        # Calculate button
        tk.Button(
            actions_frame,
            text=" Hesapla",
            font=('Segoe UI', 9),
            bg=self.theme['warning'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=3,
            command=lambda: self._calculate_kpi(kpi['id'])
        ).pack(side='left', padx=(0, 5))

        # Edit button
        tk.Button(
            actions_frame,
            text=" Düzenle",
            font=('Segoe UI', 9),
            bg=self.theme['secondary'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=3,
            command=lambda: self._edit_kpi(kpi['id'])
        ).pack(side='left', padx=(0, 5))

        # Delete button
        tk.Button(
            actions_frame,
            text=" Sil",
            font=('Segoe UI', 9),
            bg=self.theme['danger'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=3,
            command=lambda: self._delete_kpi(kpi['id'])
        ).pack(side='left')

    def _refresh_dashboard(self):
        """Dashboard'u yenile"""
        self._load_dashboard()
        messagebox.showinfo("Başarılı", "Dashboard yenilendi!")

    def _add_widget(self):
        """Yeni widget ekle"""
        messagebox.showinfo("Bilgi", "Yeni widget ekleme özelliği yakında!")

    def _add_data_source(self):
        """Yeni veri kaynağı ekle"""
        messagebox.showinfo("Bilgi", "Yeni veri kaynağı ekleme özelliği yakında!")

    def _add_kpi(self):
        """Yeni KPI ekle"""
        messagebox.showinfo("Bilgi", "Yeni KPI ekleme özelliği yakında!")

    def _edit_widget(self, widget_id: str):
        """Widget düzenle"""
        messagebox.showinfo("Bilgi", f"Widget düzenleme: {widget_id}")

    def _delete_widget(self, widget_id: str):
        """Widget sil"""
        if messagebox.askyesno("Onay", "Bu widget'ı silmek istediğinizden emin misiniz?"):
            messagebox.showinfo("Başarılı", "Widget silindi!")
            self._load_widgets()

    def _toggle_widget(self, widget_id: str):
        """Widget aktif/pasif yap"""
        messagebox.showinfo("Başarılı", "Widget durumu değiştirildi!")
        self._load_widgets()

    def _test_source(self, source_id: str):
        """Veri kaynağını test et"""
        messagebox.showinfo("Test", f"Veri kaynağı test edildi: {source_id}")

    def _edit_source(self, source_id: str):
        """Veri kaynağını düzenle"""
        messagebox.showinfo("Bilgi", f"Veri kaynağı düzenleme: {source_id}")

    def _delete_source(self, source_id: str):
        """Veri kaynağını sil"""
        if messagebox.askyesno("Onay", "Bu veri kaynağını silmek istediğinizden emin misiniz?"):
            messagebox.showinfo("Başarılı", "Veri kaynağı silindi!")
            self._load_data_sources()

    def _calculate_kpi(self, kpi_id: str):
        """KPI hesapla"""
        messagebox.showinfo("Hesaplama", f"KPI hesaplandı: {kpi_id}")
        self._load_kpis()

    def _edit_kpi(self, kpi_id: str):
        """KPI düzenle"""
        messagebox.showinfo("Bilgi", f"KPI düzenleme: {kpi_id}")

    def _delete_kpi(self, kpi_id: str):
        """KPI sil"""
        if messagebox.askyesno("Onay", "Bu KPI'yı silmek istediğinizden emin misiniz?"):
            messagebox.showinfo("Başarılı", "KPI silindi!")
            self._load_kpis()


if __name__ == "__main__":
    # Test
    root = tk.Tk()
    root.title("Gelişmiş Dashboard")
    root.geometry("1200x800")

    gui = AdvancedDashboardGUI(root)
    root.mainloop()
