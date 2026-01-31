import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Görselleştirme Merkezi GUI
Tüm gelişmiş görselleştirme özellikleri
"""

import tkinter as tk
from tkinter import messagebox, ttk

from .advanced_charts import AdvancedCharts


class VisualizationCenterGUI:
    """Görselleştirme merkezi GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.charts = AdvancedCharts()

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()

    def setup_ui(self) -> None:
        """Görselleştirme arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#E65100', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=" Gelişmiş Görselleştirme Merkezi",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#E65100')
        title_label.pack(expand=True)

        # Ana içerik alanı
        content_frame = tk.Frame(main_frame, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Notebook oluştur
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Sekmeleri oluştur
        self.create_widgets_tab()
        self.create_drilldown_tab()
        self.create_sankey_tab()
        self.create_network_tab()
        self.create_maps_tab()

    def create_widgets_tab(self) -> None:
        """Dashboard widget'ları sekmesi"""
        widgets_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(widgets_frame, text=" Dashboard Widget'ları")

        # Başlık
        tk.Label(widgets_frame, text="İnteraktif Dashboard Widget'ları",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Widget alanı
        widgets_container = tk.Frame(widgets_frame, bg='white')
        widgets_container.pack(fill='both', expand=True, padx=20, pady=10)

        # Örnek KPI kartları
        kpi_frame = tk.Frame(widgets_container, bg='white')
        kpi_frame.pack(fill='x', pady=10)

        kpi_examples = [
            {'title': 'Karbon Emisyonu', 'value': 125.5, 'unit': 'tCO2e',
             'change': -8.3, 'target': 100, 'color': '#2E7D32'},
            {'title': 'Enerji Tüketimi', 'value': 450, 'unit': 'MWh',
             'change': -5.1, 'target': 400, 'color': '#1976D2'},
            {'title': 'Su Kullanımı', 'value': 320, 'unit': 'm³',
             'change': -12.5, 'target': 280, 'color': '#0288D1'},
        ]

        for i, kpi in enumerate(kpi_examples):
            card = self.charts.create_kpi_card(kpi_frame, kpi)
            card.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            kpi_frame.grid_columnconfigure(i, weight=1)

        # Gauge örneği
        gauge_frame = tk.Frame(widgets_container, bg='white')
        gauge_frame.pack(fill='both', expand=True, pady=20)

        tk.Button(widgets_frame, text=" Widget'ları Yenile",
                 bg='#F57C00', fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=10).pack(pady=10)

    def create_drilldown_tab(self) -> None:
        """Drill-down grafikler sekmesi"""
        drilldown_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(drilldown_frame, text=" Drill-Down Grafikler")

        # Başlık
        tk.Label(drilldown_frame, text="Drill-Down Grafikler - Tıklayarak Detay",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Grafik alanı
        chart_frame = tk.Frame(drilldown_frame, bg='white')
        chart_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Örnek drill-down data
        data = {
            'categories': ['2020', '2021', '2022', '2023', '2024'],
            'values': [120, 115, 105, 98, 90],
            'details': {
                '2024': {'Scope 1': 50, 'Scope 2': 30, 'Scope 3': 10}
            }
        }

        def on_click(year):
            messagebox.showinfo("Detay", f"{year} yılı detayları:\n\nScope 1: 50\nScope 2: 30\nScope 3: 10")

        self.charts.create_drilldown_chart(chart_frame, data, on_click)

    def create_sankey_tab(self) -> None:
        """Sankey diyagram sekmesi"""
        sankey_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(sankey_frame, text=" Sankey (Akış)")

        # Başlık
        tk.Label(sankey_frame, text="Sankey Akış Diyagramları",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Grafik alanı
        chart_frame = tk.Frame(sankey_frame, bg='white')
        chart_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Örnek akış verisi
        flow_data = {
            'nodes': ['Enerji Girişi', 'Üretim', 'Ürün', 'Atık', 'Geri Dönüşüm'],
            'links': [
                {'source': 0, 'target': 1, 'value': 100},
                {'source': 1, 'target': 2, 'value': 80},
                {'source': 1, 'target': 3, 'value': 20},
                {'source': 3, 'target': 4, 'value': 15}
            ]
        }

        self.charts.create_sankey_diagram(chart_frame, flow_data)

    def create_network_tab(self) -> None:
        """Network graph sekmesi"""
        network_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(network_frame, text=" Network (Bağlantı)")

        # Başlık
        tk.Label(network_frame, text="Network Bağlantı Haritası",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Grafik alanı
        chart_frame = tk.Frame(network_frame, bg='white')
        chart_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Örnek network verisi (6 Sermaye)
        network_data = {
            'nodes': [
                {'id': 'Mali', 'label': 'Mali Sermaye', 'size': 20},
                {'id': 'Imalat', 'label': 'İmalat Sermayesi', 'size': 18},
                {'id': 'Entel', 'label': 'Entelektüel', 'size': 15},
                {'id': 'Insani', 'label': 'İnsan', 'size': 22},
                {'id': 'Sosyal', 'label': 'Sosyal', 'size': 16},
                {'id': 'Dogal', 'label': 'Doğal', 'size': 14}
            ],
            'edges': [
                {'source': 'Mali', 'target': 'Imalat', 'weight': 8},
                {'source': 'Imalat', 'target': 'Mali', 'weight': 6},
                {'source': 'Insani', 'target': 'Entel', 'weight': 5},
                {'source': 'Entel', 'target': 'Mali', 'weight': 4},
                {'source': 'Sosyal', 'target': 'Mali', 'weight': 3},
                {'source': 'Dogal', 'target': 'Mali', 'weight': 2}
            ]
        }

        self.charts.create_network_graph(chart_frame, network_data)

    def create_maps_tab(self) -> None:
        """Harita görselleştirmeleri sekmesi"""
        maps_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(maps_frame, text="️ Haritalar")

        # Başlık
        tk.Label(maps_frame, text="Harita Görselleştirmeleri",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Grafik alanı
        chart_frame = tk.Frame(maps_frame, bg='white')
        chart_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Örnek bölgesel veri
        map_data = {
            'regions': ['İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya'],
            'values': [150, 120, 100, 80, 60],
            'metric': 'Karbon Emisyonu (tCO2e)'
        }

        self.charts.create_choropleth_map(chart_frame, map_data)
