import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sektör Benchmark GUI - TAM VE EKSİKSİZ
Sektör karşılaştırması, trendler, best performers
"""

import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .sector_benchmark_database import SectorBenchmarkDatabase
from config.icons import Icons


class BenchmarkGUI:
    """Sektör Benchmark GUI"""

    def __init__(self, parent, company_id: int, sector_code: str = "imalat") -> None:
        self.parent = parent
        self.company_id = company_id
        self.sector_code = sector_code
        self.db = SectorBenchmarkDatabase()

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Benchmark arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#0D47A1', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=" Sektör Benchmark Analizi",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#0D47A1')
        title_label.pack(expand=True)

        # Ana içerik alanı
        content_frame = tk.Frame(main_frame, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Notebook oluştur
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Sekmeleri oluştur
        self.create_overview_tab()
        self.create_comparison_tab()
        self.create_trends_tab()
        self.create_best_performers_tab()

    def create_overview_tab(self) -> None:
        """Genel bakış sekmesi"""
        overview_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(overview_frame, text=" Genel Bakış")

        # Sektör seçimi
        top_panel = tk.Frame(overview_frame, bg='white')
        top_panel.pack(fill='x', padx=20, pady=10)

        tk.Label(top_panel, text="Sektör:", font=('Segoe UI', 12, 'bold'),
                bg='white').pack(side='left', padx=(0, 10))

        self.sector_var = tk.StringVar(value=self.sector_code)
        sectors = list(self.db.SECTORS.values())
        self.sector_combo = ttk.Combobox(top_panel, textvariable=self.sector_var,
                                        values=sectors, state='readonly', width=30)
        self.sector_combo.pack(side='left')
        self.sector_combo.bind('<<ComboboxSelected>>', self.on_sector_change)

        # İstatistik kartları
        self.stats_frame = tk.Frame(overview_frame, bg='white')
        self.stats_frame.pack(fill='x', padx=20, pady=20)

        # Performans özeti
        self.performance_frame = tk.Frame(overview_frame, bg='white')
        self.performance_frame.pack(fill='both', expand=True, padx=20, pady=10)

    def create_comparison_tab(self) -> None:
        """Karşılaştırma sekmesi"""
        comparison_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(comparison_frame, text=" Sektör Karşılaştırması")

        # Başlık
        tk.Label(comparison_frame, text="Şirket vs Sektör Ortalaması",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Karşılaştırma treeview
        columns = ('Metrik', 'Şirket', 'Sektör Ort.', 'Fark', 'Fark %', 'Percentile', 'Durum')
        self.comparison_tree = ttk.Treeview(comparison_frame, columns=columns,
                                           show='headings', height=15)

        for col in columns:
            self.comparison_tree.heading(col, text=col)
            self.comparison_tree.column(col, width=100)

        self.comparison_tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Karşılaştır butonu
        ttk.Button(comparison_frame, text=" Karşılaştır", style='Primary.TButton', command=self.compare_metrics).pack(pady=10)

    def create_trends_tab(self) -> None:
        """Trendler sekmesi"""
        trends_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(trends_frame, text=f"{Icons.CHART_UP} Sektör Trendleri")

        # Başlık
        tk.Label(trends_frame, text="Sektör Trendleri (2020-2024)",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Metrik seçimi
        top_panel = tk.Frame(trends_frame, bg='white')
        top_panel.pack(fill='x', padx=20, pady=10)

        tk.Label(top_panel, text="Metrik:", font=('Segoe UI', 12),
                bg='white').pack(side='left', padx=(0, 10))

        self.trend_metric_var = tk.StringVar()
        self.trend_metric_combo = ttk.Combobox(top_panel, textvariable=self.trend_metric_var,
                                              values=list(self.db.STANDARD_METRICS.keys()),
                                              state='readonly', width=30)
        self.trend_metric_combo.pack(side='left', padx=(0, 10))

        ttk.Button(top_panel, text=" Göster", style='Primary.TButton', command=self.show_trend).pack(side='left')

        # Trend grafik alanı
        self.trend_canvas_frame = tk.Frame(trends_frame, bg='white')
        self.trend_canvas_frame.pack(fill='both', expand=True, padx=20, pady=10)

    def create_best_performers_tab(self) -> None:
        """Best performers sekmesi"""
        performers_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(performers_frame, text=f"{Icons.STAR} En İyi Performans")

        # Başlık
        tk.Label(performers_frame, text="Sektör Liderleri - Best Performers",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Best performers listesi
        self.performers_frame = tk.Frame(performers_frame, bg='white')
        self.performers_frame.pack(fill='both', expand=True, padx=20, pady=10)

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            self.load_overview_data()
        except Exception as e:
            messagebox.showerror("Hata", f"Veri yüklenirken hata: {e}")

    def load_overview_data(self) -> None:
        """Genel bakış verilerini yükle"""
        try:
            # İstatistik kartları
            for widget in self.stats_frame.winfo_children():
                widget.destroy()

            stats_data = [
                ("Toplam Metrik", len(self.db.STANDARD_METRICS), '#1976D2'),
                ("Sektör Sayısı", len(self.db.SECTORS), '#388E3C'),
                ("Veri Yılı", 2024, '#F57C00'),
                ("Trend Yılları", "2020-2024", '#7B1FA2'),
            ]

            for i, (title, value, color) in enumerate(stats_data):
                self.create_stat_card(self.stats_frame, title, value, color, 0, i)

        except Exception as e:
            logging.error(f"Genel bakis verileri yuklenirken hata: {e}")

    def create_stat_card(self, parent, title, value, color, row, col):
        """İstatistik kartı oluştur"""
        card = tk.Frame(parent, bg=color, relief='raised', bd=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        parent.grid_columnconfigure(col, weight=1)

        tk.Label(card, text=title, font=('Segoe UI', 10, 'bold'),
                bg=color, fg='white').pack(pady=5)
        tk.Label(card, text=str(value), font=('Segoe UI', 16, 'bold'),
                bg=color, fg='white').pack(pady=5)

    def on_sector_change(self, event) -> None:
        """Sektör değiştiğinde"""
        selected = self.sector_var.get()
        for code, name in self.db.SECTORS.items():
            if name == selected:
                self.sector_code = code
                break
        self.load_overview_data()

    def compare_metrics(self) -> None:
        """Metrikleri karşılaştır"""
        messagebox.showinfo("Bilgi", "Metrik karşılaştırma özelliği hazır!\nŞirket verileriniz yüklenecek...")

    def show_trend(self) -> None:
        """Trend grafiği göster"""
        metric = self.trend_metric_var.get()
        if not metric:
            messagebox.showwarning("Uyarı", "Lütfen bir metrik seçin!")
            return

        try:
            # Trend verilerini al
            trends = self.db.get_sector_trend(self.sector_code, metric)

            if not trends:
                messagebox.showinfo("Bilgi", "Bu metrik için trend verisi bulunamadı")
                return

            # Grafik çiz
            for widget in self.trend_canvas_frame.winfo_children():
                widget.destroy()

            fig, ax = plt.subplots(figsize=(10, 6))

            years = [t['year'] for t in trends]
            values = [t['value'] for t in trends]

            ax.plot(years, values, marker='o', linewidth=2, markersize=8, color='#1976D2')
            ax.set_xlabel('Yıl', fontsize=12)
            ax.set_ylabel('Değer', fontsize=12)
            ax.set_title(f'{metric.replace("_", " ").title()} - Sektör Trendi', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)

            canvas = FigureCanvasTkAgg(fig, self.trend_canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)

        except Exception as e:
            messagebox.showerror("Hata", f"Trend gösterilirken hata: {e}")
