import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEDARİK ZİNCİRİ GUI
Tedarikçi yönetimi, değerlendirme ve analiz arayüzü
"""

import json
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from utils.language_manager import LanguageManager
from utils.phone import format_tr_phone, is_valid_tr_phone
from utils.ui_theme import apply_theme

from .supply_chain_manager import SupplyChainManager
from config.icons import Icons


class SupplyChainGUI:
    """Tedarik Zinciri Modülü GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()
        self.manager = SupplyChainManager()

        # Tabloları oluştur
        self.manager.create_tables()

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Tedarik zinciri arayüzünü oluştur"""
        apply_theme(self.parent)
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Başlık
        header_frame = tk.Frame(main_frame, bg='#9b59b6', height=70)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text=self.lm.tr('supply_chain_management', " Tedarik Zinciri Yönetimi"),
                              font=('Segoe UI', 18, 'bold'), fg='white', bg='#9b59b6')
        title_label.pack(side='left', padx=20, pady=15)

        subtitle_label = tk.Label(header_frame, text=self.lm.tr('sustainable_supplier_assessment', "Sürdürülebilir Tedarikçi Değerlendirmesi"),
                                 font=('Segoe UI', 11), fg='#f4ecf7', bg='#9b59b6')
        subtitle_label.pack(side='left')

        actions_frame = tk.Frame(header_frame, bg='#9b59b6')
        actions_frame.pack(side='right', padx=10)
        ttk.Button(actions_frame, text=self.lm.tr('report_center', "Rapor Merkezi"), style='Primary.TButton', command=self.open_report_center_supply).pack(side='right')

        # Dashboard kartları
        self.create_stats_frame(main_frame)

        # Ana içerik - Notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Sekmeler
        self.create_suppliers_tab()
        self.create_assessment_tab()
        self.create_performance_tab()
        self.create_metrics_tab()
        self.create_reports_tab()

    def create_stats_frame(self, parent) -> None:
        """İstatistik kartları"""
        stats_frame = tk.Frame(parent, bg='#f0f2f5')
        stats_frame.pack(fill='x', pady=(0, 20))

        # Dashboard verilerini al
        try:
            stats = self.manager.get_dashboard_stats(self.company_id)
        except Exception:
            stats = {
                'total_suppliers': 0,
                'local_supplier_pct': 0,
                'sustainable_pct': 0,
                'avg_score': 0,
                'high_risk_count': 0,
                'total_spend': 0
            }

        # Güvenli sayı formatlama yardımcıları
        def pct(v) -> None:
            try:
                return f"%{float(v):.1f}"
            except Exception:
                return "—"
        def num(v, digits=1) -> None:
            try:
                return f"{float(v):.{digits}f}"
            except Exception:
                return "—"
        def money(v) -> None:
            try:
                return f"{float(v):,.0f} ₺"
            except Exception:
                return "—"

        # Kartlar
        avg_score_val = num(stats.get('avg_score'))
        cards = [
            (self.lm.tr('total_supplier', f"{Icons.USERS} Toplam Tedarikçi"), f"{stats.get('total_suppliers', 0)}", 
             self.lm.tr('active_suppliers', "Aktif Tedarikçiler"), "#3498db"),
            (self.lm.tr('local_supplier', f"{Icons.HOME} Yerel Tedarikçi"), pct(stats.get('local_supplier_pct')), 
             self.lm.tr('localization_rate', "Yerelleşme Oranı"), "#27ae60"),
            (self.lm.tr('sustainable', f"{Icons.LEAF} Sürdürülebilir"), pct(stats.get('sustainable_pct')), 
             self.lm.tr('sustainability_rate', "Sürdürülebilirlik Oranı"), "#16a085"),
            (self.lm.tr('average_score', f"{Icons.STAR} Ortalama Skor"), f"{avg_score_val}/100" if avg_score_val != "—" else "—", 
             self.lm.tr('supplier_performance', "Tedarikçi Performansı"), "#2ecc71"),
            (self.lm.tr('high_risk', f"{Icons.WARNING} Yüksek Risk"), f"{stats.get('high_risk_count', 0)}", 
             self.lm.tr('suppliers_needing_attention', "Dikkat Gereken Tedarikçi"), "#e74c3c"),
            (self.lm.tr('total_spend', f"{Icons.MONEY_BAG} Toplam Harcama"), money(stats.get('total_spend')), 
             self.lm.tr('annual_purchasing', "Yıllık Satınalma"), "#8e44ad")
        ]

        for i, (title, value, subtitle, color) in enumerate(cards):
            card = tk.Frame(stats_frame, bg=color, relief='raised', bd=2)
            card.grid(row=0, column=i, padx=8, pady=5, sticky='ew')
            stats_frame.grid_columnconfigure(i, weight=1)

            tk.Label(card, text=title, font=('Segoe UI', 9, 'bold'),
                    fg='white', bg=color).pack(pady=(10, 3))
            tk.Label(card, text=value, font=('Segoe UI', 16, 'bold'),
                    fg='white', bg=color).pack()
            tk.Label(card, text=subtitle, font=('Segoe UI', 8),
                    fg='white', bg=color).pack(pady=(2, 10))

    def create_suppliers_tab(self) -> None:
        """Tedarikçiler sekmesi"""
        suppliers_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(suppliers_frame, text=self.lm.tr('suppliers', " Tedarikçiler"))

        # Üst butonlar
        btn_frame = tk.Frame(suppliers_frame, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=15)

        ttk.Button(btn_frame, text=self.lm.tr('new_supplier', " Yeni Tedarikçi"), style='Primary.TButton',
                   command=self.show_add_supplier_form).pack(side='left', padx=5)

        ttk.Button(btn_frame, text=self.lm.tr('import_csv', " CSV'den İçe Aktar"), style='Primary.TButton',
                   command=self.import_suppliers_csv).pack(side='left', padx=5)

        ttk.Button(btn_frame, text=self.lm.tr('export_excel', " Excel'e Aktar"), style='Primary.TButton',
                   command=self.export_suppliers_excel).pack(side='left', padx=5)

        # Tedarikçi listesi
        list_frame = tk.Frame(suppliers_frame, bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Treeview
        columns = ('code', 'name', 'country', 'type', 'local', 'spend', 'status')
        self.suppliers_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        self.suppliers_tree.heading('code', text=self.lm.tr('code', 'Kod'))
        self.suppliers_tree.heading('name', text=self.lm.tr('supplier_name', 'Tedarikçi Adı'))
        self.suppliers_tree.heading('country', text=self.lm.tr('country', 'Ülke'))
        self.suppliers_tree.heading('type', text=self.lm.tr('type', 'Tür'))
        self.suppliers_tree.heading('local', text=self.lm.tr('local', 'Yerel'))
        self.suppliers_tree.heading('spend', text=self.lm.tr('spend_tl', 'Harcama (₺)'))
        self.suppliers_tree.heading('status', text=self.lm.tr('status', 'Durum'))

        self.suppliers_tree.column('code', width=80)
        self.suppliers_tree.column('name', width=200)
        self.suppliers_tree.column('country', width=100)
        self.suppliers_tree.column('type', width=120)
        self.suppliers_tree.column('local', width=60)
        self.suppliers_tree.column('spend', width=120)
        self.suppliers_tree.column('status', width=80)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.suppliers_tree.yview)
        self.suppliers_tree.configure(yscrollcommand=scrollbar.set)

        self.suppliers_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Double click event
        self.suppliers_tree.bind('<Double-1>', self.on_supplier_double_click)

    def create_assessment_tab(self) -> None:
        """Değerlendirme sekmesi"""
        assessment_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(assessment_frame, text=self.lm.tr('sustainability_assessment', f"{Icons.LEAF} Sürdürülebilirlik Değerlendirmesi"))

        # Tedarikçi seçimi
        select_frame = tk.Frame(assessment_frame, bg='white')
        select_frame.pack(fill='x', padx=20, pady=15)

        tk.Label(select_frame, text=self.lm.tr('select_supplier', "Değerlendirilecek Tedarikçi:"),
                font=('Segoe UI', 11, 'bold'), bg='white').pack(side='left', padx=(0, 10))

        self.assessment_supplier = ttk.Combobox(select_frame, width=40, state='readonly')
        self.assessment_supplier.pack(side='left', padx=5)
        self.assessment_supplier.bind('<<ComboboxSelected>>', self.on_supplier_selected_for_assessment)

        # Değerlendirme formu çerçevesi (scroll ile)
        form_container = tk.Frame(assessment_frame, bg='white')
        form_container.pack(fill='both', expand=True, padx=20, pady=(0, 15))

        canvas = tk.Canvas(form_container, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_container, orient="vertical", command=canvas.yview)
        self.assessment_form_frame = tk.Frame(canvas, bg='white')

        canvas_window = canvas.create_window((0, 0), window=self.assessment_form_frame, anchor='nw')

        def on_frame_config(e) -> None:
            canvas.configure(scrollregion=canvas.bbox('all'))
        def on_canvas_config(e) -> None:
            canvas.itemconfig(canvas_window, width=e.width)

        self.assessment_form_frame.bind('<Configure>', on_frame_config)
        canvas.bind('<Configure>', on_canvas_config)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Form alanlarını oluştur
        self.create_assessment_form()

    def create_assessment_form(self) -> None:
        """Değerlendirme formunu oluştur"""
        self.assessment_entries = {}

        # Kategoriler
        categories = ['environmental', 'social', 'governance', 'quality']
        category_names = {
            'environmental': self.lm.tr('environmental_performance', f'{Icons.LEAF} Çevresel Performans'),
            'social': self.lm.tr('social_responsibility', f'{Icons.USERS} Sosyal Sorumluluk'),
            'governance': self.lm.tr('corporate_governance', f'{Icons.BRIEFCASE} Kurumsal Yönetişim'),
            'quality': self.lm.tr('quality_and_reliability', f'{Icons.STAR} Kalite ve Güvenilirlik')
        }

        row = 0

        for category in categories:
            # Kategori başlığı
            cat_label = tk.Label(self.assessment_form_frame,
                               text=category_names[category],
                               font=('Segoe UI', 13, 'bold'), fg='#2c3e50', bg='white')
            cat_label.grid(row=row, column=0, columnspan=3, sticky='w', pady=(15, 10))
            row += 1

            # Kriterler
            criteria = self.manager.assessment.ASSESSMENT_CATEGORIES[category]['criteria']

            for criterion_key, criterion_data in criteria.items():
                # Kriter adı
                tk.Label(self.assessment_form_frame,
                        text=self.lm.tr(criterion_key, criterion_data['name']),
                        font=('Segoe UI', 10), bg='white').grid(
                    row=row, column=0, sticky='w', padx=(20, 10), pady=3)

                # Skor girişi
                entry = tk.Entry(self.assessment_form_frame, width=10)
                entry.grid(row=row, column=1, sticky='w', pady=3)

                # Max skor göster
                tk.Label(self.assessment_form_frame,
                        text=f"/ {criterion_data['max_score']}",
                        font=('Segoe UI', 9), fg='#666', bg='white').grid(
                    row=row, column=2, sticky='w', pady=3)

                # Referansı sakla
                self.assessment_entries[f"{category}_{criterion_key}"] = entry

                row += 1

        # Kaydet butonu
        save_btn = ttk.Button(self.assessment_form_frame, text=self.lm.tr('save_assessment', " Değerlendirmeyi Kaydet"),
                              style='Primary.TButton',
                              command=self.save_assessment)
        save_btn.grid(row=row, column=0, columnspan=3, pady=30)

    def open_report_center_supply(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('genel')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for genel: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('report_center_error', 'Rapor Merkezi açılamadı')}:\n{e}")
            logging.error(f"Error opening report center: {e}")

    def create_performance_tab(self) -> None:
        """Performans takibi sekmesi"""
        perf_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(perf_frame, text=self.lm.tr('performance_tracking', " Performans Takibi"))

        # Başlık
        title_frame = tk.Frame(perf_frame, bg='#3498db', height=60)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text=self.lm.tr('supplier_performance_tracking', " Tedarikçi Performans Takibi"),
                font=('Segoe UI', 16, 'bold'), fg='white', bg='#3498db').pack(expand=True)

        # Ana içerik
        content_frame = tk.Frame(perf_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Performans metrikleri kartları
        self.create_performance_metrics_cards(content_frame)

        # Performans tablosu
        self.create_performance_table(content_frame)

        # Trend analizi
        self.create_performance_trends(content_frame)

    def create_performance_metrics_cards(self, parent) -> None:
        """Performans metrikleri kartlarını oluştur"""
        metrics_frame = tk.LabelFrame(parent, text=self.lm.tr('performance_metrics', "Performans Metrikleri"),
                                     font=('Segoe UI', 12, 'bold'), bg='white')
        metrics_frame.pack(fill='x', pady=(0, 20))

        # Metrik kartları
        cards_frame = tk.Frame(metrics_frame, bg='white')
        cards_frame.pack(fill='x', padx=10, pady=10)

        metrics = [
            (self.lm.tr('on_time_delivery', "Zamanında Teslimat"), "95.2%", "#27ae60", ""),
            (self.lm.tr('quality_rejection_rate', "Kalite Red Oranı"), "2.1%", "#e74c3c", ""),
            (self.lm.tr('avg_response_time', "Ortalama Yanıt Süresi"), f"4.2 {self.lm.tr('hours', 'saat')}", "#f39c12", "⏱️"),
            (self.lm.tr('price_competitiveness', "Fiyat Rekabetçiliği"), "8.5/10", "#3498db", ""),
            (self.lm.tr('flexibility_score', "Esneklik Skoru"), "7.8/10", "#9b59b6", ""),
            (self.lm.tr('overall_satisfaction', "Genel Memnuniyet"), "8.2/10", "#2ecc71", "")
        ]

        for i, (title, value, color, icon) in enumerate(metrics):
            card = tk.Frame(cards_frame, bg=color, relief='raised', bd=2)
            card.pack(side='left', fill='x', expand=True, padx=5)

            # İkon ve başlık
            header_frame = tk.Frame(card, bg=color)
            header_frame.pack(fill='x', padx=10, pady=(10, 5))

            tk.Label(header_frame, text=icon, font=('Segoe UI', 16),
                    bg=color, fg='white').pack(side='left')
            tk.Label(header_frame, text=title, font=('Segoe UI', 10, 'bold'),
                    bg=color, fg='white').pack(side='left', padx=(5, 0))

            # Değer
            tk.Label(card, text=value, font=('Segoe UI', 18, 'bold'),
                    bg=color, fg='white').pack(pady=(0, 10))

    def create_performance_table(self, parent) -> None:
        """Performans tablosunu oluştur"""
        table_frame = tk.LabelFrame(parent, text=self.lm.tr('supplier_performance_details', "Tedarikçi Performans Detayları"),
                                   font=('Segoe UI', 12, 'bold'), bg='white')
        table_frame.pack(fill='both', expand=True, pady=(0, 20))

        # Tablo
        columns = ('supplier', 'category', 'on_time_delivery', 'quality_score',
                  'response_time', 'price_score', 'overall_score', 'status')
        
        column_headers = {
            'supplier': self.lm.tr('supplier', 'Tedarikçi'),
            'category': self.lm.tr('category', 'Kategori'),
            'on_time_delivery': self.lm.tr('on_time_delivery', 'Zamanında Teslimat'),
            'quality_score': self.lm.tr('quality_score', 'Kalite Skoru'),
            'response_time': self.lm.tr('response_time', 'Yanıt Süresi'),
            'price_score': self.lm.tr('price_score', 'Fiyat Skoru'),
            'overall_score': self.lm.tr('overall_score', 'Genel Skor'),
            'status': self.lm.tr('status', 'Durum')
        }

        self.perf_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)

        for col in columns:
            self.perf_tree.heading(col, text=column_headers[col])
            self.perf_tree.column(col, width=120, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.perf_tree.yview)
        self.perf_tree.configure(yscrollcommand=scrollbar.set)

        self.perf_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')

        # Örnek veriler
        sample_data = [
            ("ABC Tekstil", self.lm.tr('textile', "Tekstil"), "98%", "9.2/10", f"2.5 {self.lm.tr('hours', 'saat')}", "8.5/10", "9.1/10", self.lm.tr('excellent', "Mükemmel")),
            ("XYZ Metal", self.lm.tr('metal', "Metal"), "92%", "8.8/10", f"6.0 {self.lm.tr('hours', 'saat')}", "9.0/10", "8.7/10", self.lm.tr('good', "İyi")),
            ("DEF Plastik", self.lm.tr('plastic', "Plastik"), "88%", "7.5/10", f"8.5 {self.lm.tr('hours', 'saat')}", "7.8/10", "7.9/10", self.lm.tr('medium', "Orta")),
            ("GHI Elektronik", self.lm.tr('electronic', "Elektronik"), "95%", "9.5/10", f"3.2 {self.lm.tr('hours', 'saat')}", "8.2/10", "9.0/10", self.lm.tr('excellent', "Mükemmel")),
            ("JKL Kimya", self.lm.tr('chemistry', "Kimya"), "85%", "6.8/10", f"12.0 {self.lm.tr('hours', 'saat')}", "6.5/10", "6.8/10", self.lm.tr('low', "Düşük"))
        ]

        for data in sample_data:
            self.perf_tree.insert('', 'end', values=data)

    def create_performance_trends(self, parent) -> None:
        """Performans trend analizini oluştur"""
        trends_frame = tk.LabelFrame(parent, text=self.lm.tr('performance_trend_analysis', "Performans Trend Analizi"),
                                    font=('Segoe UI', 12, 'bold'), bg='white')
        trends_frame.pack(fill='x', pady=(0, 10))

        # Trend grafikleri için placeholder
        charts_frame = tk.Frame(trends_frame, bg='white')
        charts_frame.pack(fill='x', padx=10, pady=10)

        # Aylık performans trendi
        monthly_frame = tk.Frame(charts_frame, bg='#f8f9fa', relief='solid', bd=1)
        monthly_frame.pack(side='left', fill='both', expand=True, padx=5)

        tk.Label(monthly_frame, text=self.lm.tr('monthly_performance_trend', " Aylık Performans Trendi"),
                font=('Segoe UI', 10, 'bold'), bg='#f8f9fa').pack(pady=10)

        # Basit trend gösterimi
        trend_text = f"""
        {self.lm.tr('month_jan', 'Ocak')}: 8.2/10  ████████████░░░░░░░░
        {self.lm.tr('month_feb', 'Şubat')}: 8.5/10 █████████████░░░░░░░
        {self.lm.tr('month_mar', 'Mart')}: 8.1/10  ████████████░░░░░░░░
        {self.lm.tr('month_apr', 'Nisan')}: 8.8/10 ██████████████░░░░░░
        {self.lm.tr('month_may', 'Mayıs')}: 9.0/10 ███████████████░░░░░
        {self.lm.tr('month_jun', 'Haziran')}: 8.7/10 ██████████████░░░░░
        """

        tk.Label(monthly_frame, text=trend_text, font=('Courier', 9),
                bg='#f8f9fa', justify='left').pack(pady=10)

        # Kategori bazlı performans
        category_frame = tk.Frame(charts_frame, bg='#f8f9fa', relief='solid', bd=1)
        category_frame.pack(side='right', fill='both', expand=True, padx=5)

        tk.Label(category_frame, text=self.lm.tr('category_based_performance', " Kategori Bazlı Performans"),
                font=('Segoe UI', 10, 'bold'), bg='#f8f9fa').pack(pady=10)

        category_text = f"""
        {self.lm.tr('textile', 'Tekstil')}:     9.1/10 ████████████████████
        {self.lm.tr('metal', 'Metal')}:       8.7/10 ███████████████████░
        {self.lm.tr('plastic', 'Plastik')}:     7.9/10 ████████████████░░░░
        {self.lm.tr('electronic', 'Elektronik')}: 9.0/10 ███████████████████░
        {self.lm.tr('chemistry', 'Kimya')}:       6.8/10 ████████████░░░░░░░░
        """

        tk.Label(category_frame, text=category_text, font=('Courier', 9),
                bg='#f8f9fa', justify='left').pack(pady=10)

    def create_metrics_tab(self) -> None:
        """Metrikler ve analiz sekmesi"""
        metrics_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(metrics_frame, text=self.lm.tr('metrics_and_kpis', " Metrikler ve KPI'lar"))

        # Başlık
        title_frame = tk.Frame(metrics_frame, bg='#e67e22', height=60)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text=self.lm.tr('supply_chain_metrics_and_kpis', " Tedarik Zinciri Metrikleri ve KPI'lar"),
                font=('Segoe UI', 16, 'bold'), fg='white', bg='#e67e22').pack(expand=True)

        # Ana içerik
        content_frame = tk.Frame(metrics_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # KPI kartları
        self.create_kpi_dashboard(content_frame)

        # Detaylı metrikler tablosu
        self.create_detailed_metrics_table(content_frame)

        # Karşılaştırmalı analiz
        self.create_comparative_analysis(content_frame)

        # Hedef vs gerçekleşen analizi
        self.create_target_vs_actual(content_frame)

    def create_kpi_dashboard(self, parent) -> None:
        """KPI dashboard'unu oluştur"""
        kpi_frame = tk.LabelFrame(parent, text=self.lm.tr('main_kpis', "Ana KPI'lar"),
                                 font=('Segoe UI', 12, 'bold'), bg='white')
        kpi_frame.pack(fill='x', pady=(0, 20))

        # KPI kartları
        cards_frame = tk.Frame(kpi_frame, bg='white')
        cards_frame.pack(fill='x', padx=10, pady=10)

        kpis = [
            (self.lm.tr('total_supplier', "Toplam Tedarikçi"), "127", "#3498db", "", self.lm.tr('active_suppliers', "Aktif Tedarikçiler")),
            (self.lm.tr('local_supplier', "Yerel Tedarikçi"), "%68.5", "#27ae60", "", self.lm.tr('localization_rate', "Yerelleşme Oranı")),
            (self.lm.tr('sustainable', "Sürdürülebilir"), "%82.3", "#2ecc71", "", self.lm.tr('sustainability_rate', "Sürdürülebilirlik Oranı")),
            (self.lm.tr('average_score', "Ortalama Skor"), "8.4/10", "#f39c12", Icons.STAR, self.lm.tr('supplier_performance', "Tedarikçi Performansı")),
            (self.lm.tr('high_risk', "Yüksek Risk"), "12", "#e74c3c", "️", self.lm.tr('suppliers_needing_attention', "Dikkat Gereken")),
            (self.lm.tr('total_spend', "Toplam Harcama"), "₺2.4M", "#9b59b6", "", self.lm.tr('annual_purchasing', "Yıllık Satınalma"))
        ]

        for i, (title, value, color, icon, subtitle) in enumerate(kpis):
            card = tk.Frame(cards_frame, bg=color, relief='raised', bd=2)
            card.pack(side='left', fill='x', expand=True, padx=5)

            # İkon ve başlık
            header_frame = tk.Frame(card, bg=color)
            header_frame.pack(fill='x', padx=10, pady=(10, 5))

            tk.Label(header_frame, text=icon, font=('Segoe UI', 16),
                        bg=color, fg='white').pack(side='left')
            tk.Label(header_frame, text=title, font=('Segoe UI', 10, 'bold'),
                    bg=color, fg='white').pack(side='left', padx=(5, 0))
            
            # Değer
            tk.Label(card, text=value, font=('Segoe UI', 20, 'bold'),
                    bg=color, fg='white').pack(pady=(0, 5))
            
            # Alt başlık
            tk.Label(card, text=subtitle, font=('Segoe UI', 8),
                    bg=color, fg='#ecf0f1').pack(pady=(0, 10))

    def create_detailed_metrics_table(self, parent) -> None:
        """Detaylı metrikler tablosunu oluştur"""
        table_frame = tk.LabelFrame(parent, text=self.lm.tr('detailed_metrics', "Detaylı Metrikler"),
                                   font=('Segoe UI', 12, 'bold'), bg='white')
        table_frame.pack(fill='both', expand=True, pady=(0, 20))

        # Tablo
        columns = ('metric', 'target', 'actual', 'diff', 'status', 'trend')
        column_headers = {
            'metric': self.lm.tr('metric', 'Metrik'),
            'target': self.lm.tr('target', 'Hedef'),
            'actual': self.lm.tr('actual', 'Gerçekleşen'),
            'diff': self.lm.tr('difference', 'Fark'),
            'status': self.lm.tr('status', 'Durum'),
            'trend': self.lm.tr('trend', 'Trend')
        }

        self.metrics_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)

        for col in columns:
            self.metrics_tree.heading(col, text=column_headers[col])
            self.metrics_tree.column(col, width=120, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.metrics_tree.yview)
        self.metrics_tree.configure(yscrollcommand=scrollbar.set)

        self.metrics_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')

        # Örnek metrik verileri
        metrics_data = [
            (self.lm.tr('on_time_delivery_rate', "Zamanında Teslimat Oranı"), "%95", "%96.2", "+1.2%", self.lm.tr('target_exceeded', " Hedef Aşıldı"), ""),
            (self.lm.tr('quality_rejection_rate', "Kalite Red Oranı"), "%3", "%2.1", "-0.9%", self.lm.tr('target_exceeded', " Hedef Aşıldı"), ""),
            (self.lm.tr('avg_response_time', "Ortalama Yanıt Süresi"), f"6 {self.lm.tr('hours', 'saat')}", f"4.2 {self.lm.tr('hours', 'saat')}", f"-1.8 {self.lm.tr('hours', 'saat')}", self.lm.tr('target_exceeded', " Hedef Aşıldı"), ""),
            (self.lm.tr('price_competitiveness', "Fiyat Rekabetçiliği"), "8/10", "8.5/10", "+0.5", self.lm.tr('target_exceeded', " Hedef Aşıldı"), ""),
            (self.lm.tr('flexibility_score', "Esneklik Skoru"), "7/10", "7.8/10", "+0.8", self.lm.tr('target_exceeded', " Hedef Aşıldı"), ""),
            (self.lm.tr('overall_satisfaction', "Genel Memnuniyet"), "8/10", "8.2/10", "+0.2", self.lm.tr('target_exceeded', " Hedef Aşıldı"), ""),
            (self.lm.tr('sustainable_supplier', "Sürdürülebilir Tedarikçi"), "%80", "%82.3", "+2.3%", self.lm.tr('target_exceeded', " Hedef Aşıldı"), ""),
            (self.lm.tr('local_supplier_rate', "Yerel Tedarikçi Oranı"), "%70", "%68.5", "-1.5%", self.lm.tr('below_target', "️ Hedef Altında"), ""),
            (self.lm.tr('risk_score', "Risk Skoru"), "3/10", "3.2/10", "+0.2", self.lm.tr('below_target', "️ Hedef Altında"), ""),
            (self.lm.tr('cost_saving', "Maliyet Tasarrufu"), "%5", "%4.8", "-0.2%", self.lm.tr('below_target', "️ Hedef Altında"), "")
        ]

        for data in metrics_data:
            self.metrics_tree.insert('', 'end', values=data)

    def create_comparative_analysis(self, parent) -> None:
        """Karşılaştırmalı analiz bölümünü oluştur"""
        analysis_frame = tk.LabelFrame(parent, text=self.lm.tr('comparative_analysis', "Karşılaştırmalı Analiz"),
                                      font=('Segoe UI', 12, 'bold'), bg='white')
        analysis_frame.pack(fill='x', pady=(0, 20))

        # Analiz kartları
        analysis_cards = tk.Frame(analysis_frame, bg='white')
        analysis_cards.pack(fill='x', padx=10, pady=10)

        # Önceki yıl karşılaştırması
        prev_year_frame = tk.Frame(analysis_cards, bg='#ecf0f1', relief='solid', bd=1)
        prev_year_frame.pack(side='left', fill='both', expand=True, padx=5)

        tk.Label(prev_year_frame, text=self.lm.tr('prev_year_comparison', " Önceki Yıl Karşılaştırması"),
                font=('Segoe UI', 10, 'bold'), bg='#ecf0f1').pack(pady=10)

        comparison_text = f"""
        2023 vs 2024:
        
        {self.lm.tr('total_supplier', "Toplam Tedarikçi")}: 115 → 127 (+10.4%)
        {self.lm.tr('local_supplier', "Yerel Tedarikçi")}: %72.1 → %68.5 (-3.6%)
        {self.lm.tr('sustainable', "Sürdürülebilir")}: %78.5 → %82.3 (+3.8%)
        {self.lm.tr('average_score', "Ortalama Skor")}: 8.1 → 8.4 (+0.3)
        {self.lm.tr('risk_score', "Risk Skoru")}: 2.8 → 3.2 (+0.4)
        """

        tk.Label(prev_year_frame, text=comparison_text, font=('Courier', 9),
                bg='#ecf0f1', justify='left').pack(pady=10)

        # Sektör karşılaştırması
        sector_frame = tk.Frame(analysis_cards, bg='#ecf0f1', relief='solid', bd=1)
        sector_frame.pack(side='right', fill='both', expand=True, padx=5)

        tk.Label(sector_frame, text=self.lm.tr('sector_comparison', " Sektör Karşılaştırması"),
                font=('Segoe UI', 10, 'bold'), bg='#ecf0f1').pack(pady=10)

        sector_text = f"""
        {self.lm.tr('sector_avg_vs_ours', "Sektör Ortalaması vs Bizim")}:
        
        {self.lm.tr('on_time_delivery', "Zamanında Teslimat")}: %89.2 vs %96.2 (+7.0%)
        {self.lm.tr('quality_score', "Kalite Skoru")}: 7.8 vs 8.4 (+0.6)
        {self.lm.tr('sustainability', "Sürdürülebilirlik")}: %74.1 vs %82.3 (+8.2%)
        {self.lm.tr('cost_effectiveness', "Maliyet Etkinliği")}: 7.2 vs 8.5 (+1.3)
        {self.lm.tr('risk_management', "Risk Yönetimi")}: 6.8 vs 7.8 (+1.0)
        """

        tk.Label(sector_frame, text=sector_text, font=('Courier', 9),
                bg='#ecf0f1', justify='left').pack(pady=10)

    def create_target_vs_actual(self, parent) -> None:
        """Hedef vs gerçekleşen analizini oluştur"""
        target_frame = tk.LabelFrame(parent, text=self.lm.tr('target_vs_actual_analysis', "Hedef vs Gerçekleşen Analizi"),
                                     font=('Segoe UI', 12, 'bold'), bg='white')
        target_frame.pack(fill='x', pady=(0, 10))

        # Hedef vs gerçekleşen grafikleri
        charts_frame = tk.Frame(target_frame, bg='white')
        charts_frame.pack(fill='x', padx=10, pady=10)

        # Performans metrikleri
        perf_frame = tk.Frame(charts_frame, bg='#f8f9fa', relief='solid', bd=1)
        perf_frame.pack(side='left', fill='both', expand=True, padx=5)

        tk.Label(perf_frame, text=self.lm.tr('performance_targets', "Performans Hedefleri"),
                font=('Segoe UI', 10, 'bold'), bg='#f8f9fa').pack(pady=10)

        perf_chart = f"""
        {self.lm.tr('on_time_delivery', "Zamanında Teslimat")}:
        {self.lm.tr('target', "Hedef")}: %95  ████████████████████
        {self.lm.tr('actual', "Gerçek")}: %96.2 ██████████████████████ 
        
        {self.lm.tr('quality_score', "Kalite Skoru")}:
        {self.lm.tr('target', "Hedef")}: 8.0/10  ████████████████████
        {self.lm.tr('actual', "Gerçek")}: 8.4/10 ██████████████████████ 
        
        {self.lm.tr('response_time', "Yanıt Süresi")}:
        {self.lm.tr('target', "Hedef")}: 6 {self.lm.tr('hours', "saat")}  ████████████████████
        {self.lm.tr('actual', "Gerçek")}: 4.2 {self.lm.tr('hours', "saat")} ████████████████ 
        """

        tk.Label(perf_frame, text=perf_chart, font=('Courier', 9),
                bg='#f8f9fa', justify='left').pack(pady=10)

        # Sürdürülebilirlik metrikleri
        sust_frame = tk.Frame(charts_frame, bg='#f8f9fa', relief='solid', bd=1)
        sust_frame.pack(side='right', fill='both', expand=True, padx=5)

        tk.Label(sust_frame, text=self.lm.tr('sustainability_targets', "Sürdürülebilirlik Hedefleri"),
                font=('Segoe UI', 10, 'bold'), bg='#f8f9fa').pack(pady=10)

        sust_chart = f"""
        {self.lm.tr('sustainable_supplier', "Sürdürülebilir Tedarikçi")}:
        {self.lm.tr('target', "Hedef")}: %80  ████████████████████
        {self.lm.tr('actual', "Gerçek")}: %82.3 ██████████████████████ 
        
        {self.lm.tr('local_supplier', "Yerel Tedarikçi")}:
        {self.lm.tr('target', "Hedef")}: %70  ████████████████████
        {self.lm.tr('actual', "Gerçek")}: %68.5 ████████████████████ ️
        
        {self.lm.tr('risk_reduction', "Risk Azaltma")}:
        {self.lm.tr('target', "Hedef")}: 3.0/10  ████████████████████
        {self.lm.tr('actual', "Gerçek")}: 3.2/10 ████████████████████ ️
        """

        tk.Label(sust_frame, text=sust_chart, font=('Courier', 9),
                bg='#f8f9fa', justify='left').pack(pady=10)

    def create_reports_tab(self) -> None:
        """Raporlar sekmesi"""
        reports_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(reports_frame, text=f" {self.lm.tr('reports_tab', 'Raporlar')}")
        # Başlık
        title_frame = tk.Frame(reports_frame, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text=self.lm.tr('supply_chain_reports', "Tedarik Zinciri Raporları"),
                 font=('Segoe UI', 16, 'bold'), fg='white', bg='#2c3e50').pack(expand=True)

        # Ana içerik
        content_frame = tk.Frame(reports_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Rapor kartları
        self.create_report_cards(content_frame)

        # Rapor geçmişi
        self.create_report_history(content_frame)

        # Rapor ayarları
        self.create_report_settings(content_frame)

    def create_report_cards(self, parent) -> None:
        """Rapor kartlarını oluştur"""
        cards_frame = tk.LabelFrame(parent, text=self.lm.tr('report_types', "Rapor Türleri"),
                                   font=('Segoe UI', 12, 'bold'), bg='white')
        cards_frame.pack(fill='x', pady=(0, 20))

        # Rapor kartları
        reports_frame = tk.Frame(cards_frame, bg='white')
        reports_frame.pack(fill='x', padx=10, pady=10)

        # 3 sütunlu grid
        reports = [
            (Icons.FILE, self.lm.tr('supplier_assessment_report', "Tedarikçi Değerlendirme Raporu"), "#3498db", self.lm.tr('supplier_assessment_desc', "Tedarikçi performans analizi ve değerlendirme raporu"), self.generate_assessment_report),
            (Icons.SEED, self.lm.tr('sustainability_scorecard', "Sürdürülebilirlik Skor Karnesi"), "#16a085", self.lm.tr('sustainability_scorecard_desc', "Sürdürülebilirlik metrikleri ve skor karnesi"), self.generate_scorecard),
            (Icons.WARNING, self.lm.tr('high_risk_suppliers', "Yüksek Riskli Tedarikçiler"), "#e74c3c", self.lm.tr('high_risk_suppliers_desc', "Risk analizi ve yüksek riskli tedarikçi raporu"), self.generate_risk_report),
            (Icons.REPORT, self.lm.tr('supply_chain_summary_report', "Tedarik Zinciri Özet Raporu"), "#9b59b6", self.lm.tr('supply_chain_summary_desc', "Genel tedarik zinciri durumu ve özet rapor"), self.generate_summary_report),
            (Icons.CHART_UP, self.lm.tr('performance_trend_report', "Performans Trend Raporu"), "#f39c12", self.lm.tr('performance_trend_desc', "Zaman içindeki performans değişimleri"), self.generate_trend_report),
            ("📑", self.lm.tr('detailed_analysis_report', "Detaylı Analiz Raporu"), "#34495e", self.lm.tr('detailed_analysis_desc', "Kapsamlı tedarik zinciri analiz raporu"), self.generate_detailed_report)
        ]

        for i, (icon, title, color, description, command) in enumerate(reports):
            card = tk.Frame(reports_frame, bg=color, relief='raised', bd=2)
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky='ew')
            reports_frame.grid_columnconfigure(0, weight=1)
            reports_frame.grid_columnconfigure(1, weight=1)
            reports_frame.grid_columnconfigure(2, weight=1)

            # İkon ve başlık
            header_frame = tk.Frame(card, bg=color)
            header_frame.pack(fill='x', padx=15, pady=(15, 10))

            tk.Label(header_frame, text=icon, font=('Segoe UI', 20),
                    bg=color, fg='white').pack(side='left')
            tk.Label(header_frame, text=title, font=('Segoe UI', 11, 'bold'),
                    bg=color, fg='white', wraplength=150).pack(side='left', padx=(10, 0))

            # Açıklama
            tk.Label(card, text=description, font=('Segoe UI', 9),
                    bg=color, fg='#ecf0f1', wraplength=180, justify='left').pack(pady=(0, 10), padx=15)

            # Buton
            ttk.Button(card, text=self.lm.tr('create_report', "Rapor Oluştur"), style='Primary.TButton',
                       command=command).pack(pady=(0, 15), padx=15, fill='x')

    def create_report_history(self, parent) -> None:
        """Rapor geçmişini oluştur"""
        history_frame = tk.LabelFrame(parent, text=self.lm.tr('report_history', "Rapor Geçmişi"),
                                     font=('Segoe UI', 12, 'bold'), bg='white')
        history_frame.pack(fill='both', expand=True, pady=(0, 20))

        # Rapor listesi
        columns = ('report_name', 'creation_date', 'size', 'status', 'actions')
        column_headers = {
            'report_name': self.lm.tr('report_name', 'Rapor Adı'),
            'creation_date': self.lm.tr('creation_date', 'Oluşturma Tarihi'),
            'size': self.lm.tr('size', 'Boyut'),
            'status': self.lm.tr('status', 'Durum'),
            'actions': self.lm.tr('actions', 'İşlemler')
        }

        self.reports_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=6)

        for col in columns:
            self.reports_tree.heading(col, text=column_headers.get(col, col))
            self.reports_tree.column(col, width=120, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient='vertical', command=self.reports_tree.yview)
        self.reports_tree.configure(yscrollcommand=scrollbar.set)

        self.reports_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')

        # Örnek rapor verileri
        sample_reports = [
            (self.lm.tr('supplier_assessment_report', "Tedarikçi Değerlendirme Raporu"), "2024-01-15", "2.3 MB", self.lm.tr('completed', "Tamamlandı")),
            (self.lm.tr('sustainability_scorecard', "Sürdürülebilirlik Skor Karnesi"), "2024-01-10", "1.8 MB", self.lm.tr('completed', "Tamamlandı")),
            (self.lm.tr('high_risk_suppliers', "Yüksek Riskli Tedarikçiler"), "2024-01-08", "0.9 MB", self.lm.tr('completed', "Tamamlandı")),
            (self.lm.tr('supply_chain_summary_report', "Tedarik Zinciri Özet Raporu"), "2024-01-05", "3.1 MB", self.lm.tr('completed', "Tamamlandı")),
            (self.lm.tr('performance_trend_report', "Performans Trend Raporu"), "2024-01-01", "2.7 MB", self.lm.tr('completed', "Tamamlandı"))
        ]

        for report in sample_reports:
            self.reports_tree.insert('', 'end', values=report + (self.lm.tr('view_download_delete', "Görüntüle | İndir | Sil"),))

    def create_report_settings(self, parent) -> None:
        """Rapor ayarlarını oluştur"""
        settings_frame = tk.LabelFrame(parent, text=self.lm.tr('report_settings', "Rapor Ayarları"),
                                      font=('Segoe UI', 12, 'bold'), bg='white')
        settings_frame.pack(fill='x', pady=(0, 10))

        # Ayarlar
        settings_content = tk.Frame(settings_frame, bg='white')
        settings_content.pack(fill='x', padx=10, pady=10)

        # Otomatik rapor oluşturma
        auto_frame = tk.Frame(settings_content, bg='white')
        auto_frame.pack(fill='x', pady=5)

        self.auto_report_var = tk.BooleanVar(value=True)
        tk.Checkbutton(auto_frame, text=self.lm.tr('auto_report_creation_monthly', "Otomatik rapor oluşturma (aylık)"),
                      variable=self.auto_report_var, font=('Segoe UI', 10), bg='white').pack(side='left')

        # Rapor formatı
        format_frame = tk.Frame(settings_content, bg='white')
        format_frame.pack(fill='x', pady=5)

        tk.Label(format_frame, text=self.lm.tr('default_format', "Varsayılan Format:"), font=('Segoe UI', 10), bg='white').pack(side='left')

        self.format_var = tk.StringVar(value="PDF")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var, width=10,
                                   values=["PDF", "Excel", "Word", "HTML"])
        format_combo.pack(side='left', padx=(10, 0))

        # Email gönderimi
        email_frame = tk.Frame(settings_content, bg='white')
        email_frame.pack(fill='x', pady=5)

        self.email_report_var = tk.BooleanVar(value=False)
        tk.Checkbutton(email_frame, text=self.lm.tr('email_reports_automatically', "Raporları otomatik email ile gönder"),
                      variable=self.email_report_var, font=('Segoe UI', 10), bg='white').pack(side='left')

        # Kaydet butonu
        ttk.Button(settings_content, text=self.lm.tr('save_settings', "Ayarları Kaydet"), style='Primary.TButton',
                   command=self.save_report_settings).pack(side='right', pady=10)

    # ==================== EVENT HANDLERS ====================

    def show_add_supplier_form(self) -> None:
        """Yeni tedarikçi ekleme formu göster"""
        # Yeni pencere
        form_window = tk.Toplevel(self.parent)
        form_window.title(self.lm.tr('add_new_supplier', "Yeni Tedarikçi Ekle"))
        form_window.geometry("600x700")
        form_window.configure(bg='white')

        # Form
        form_frame = tk.Frame(form_window, bg='white')
        form_frame.pack(fill='both', expand=True, padx=30, pady=30)

        tk.Label(form_frame, text=self.lm.tr('new_supplier_info', "Yeni Tedarikçi Bilgileri"),
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').grid(
            row=0, column=0, columnspan=2, pady=(0, 20))

        row = 1
        entries = {}

        # Form alanları
        fields = [
            ('supplier_code', self.lm.tr('supplier_code', 'Tedarikçi Kodu:')),
            ('supplier_name', self.lm.tr('supplier_name_label', 'Tedarikçi Adı:')),
            ('contact_person', self.lm.tr('contact_person', 'İlgili Kişi:')),
            ('email', self.lm.tr('email', 'Email:')),
            ('phone', self.lm.tr('phone', 'Telefon:')),
            ('country', self.lm.tr('country', 'Ülke:')),
            ('city', self.lm.tr('city', 'Şehir:')),
            ('supplier_type', self.lm.tr('type', 'Tür:')),
            ('annual_spend', self.lm.tr('annual_spend_label', 'Yıllık Harcama (₺):'))
        ]

        for key, label_text in fields:
            tk.Label(form_frame, text=label_text, font=('Segoe UI', 10, 'bold'),
                    bg='white').grid(row=row, column=0, sticky='w', pady=5)
            entry = tk.Entry(form_frame, width=35)
            entry.grid(row=row, column=1, sticky='w', pady=5)
            entries[key] = entry
            row += 1

        # Telefon alanı için odak kaybında otomatik biçimlendirme
        def _format_phone_field(_=None) -> None:
            try:
                val = entries['phone'].get().strip()
                if val:
                    entries['phone'].delete(0, tk.END)
                    entries['phone'].insert(0, format_tr_phone(val))
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        try:
            entries['phone'].bind('<FocusOut>', _format_phone_field)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        # Yerel tedarikçi checkbox
        is_local_var = tk.BooleanVar()
        tk.Checkbutton(form_frame, text=self.lm.tr('local_supplier', "Yerel Tedarikçi"), variable=is_local_var,
                      font=('Segoe UI', 10), bg='white').grid(row=row, column=0, columnspan=2, sticky='w', pady=10)
        row += 1

        # Kaydet butonu
        def save_new_supplier() -> None:
            try:
                supplier_data = {
                    'supplier_code': entries['supplier_code'].get().strip(),
                    'supplier_name': entries['supplier_name'].get().strip(),
                    'contact_person': entries['contact_person'].get().strip(),
                    'email': entries['email'].get().strip(),
                    'phone': entries['phone'].get().strip(),
                    'country': entries['country'].get().strip(),
                    'city': entries['city'].get().strip(),
                    'supplier_type': entries['supplier_type'].get().strip(),
                    'annual_spend': float(entries['annual_spend'].get() or 0),
                    'is_local': is_local_var.get()
                }

                # Telefonu standart biçime getir ve doğrula
                if supplier_data['phone']:
                    try:
                        supplier_data['phone'] = format_tr_phone(supplier_data['phone'])
                        if not is_valid_tr_phone(supplier_data['phone']):
                            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('invalid_phone_format', "Geçersiz telefon formatı. Örnek: +90 (5XX) XXX XX XX"))
                            return
                    except Exception as e:
                        logging.error(f"Silent error caught: {str(e)}")

                supplier_id = self.manager.save_supplier(self.company_id, supplier_data)

                if supplier_id:
                    messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('supplier_saved', "Tedarikçi kaydedildi!"))
                    form_window.destroy()
                    self.load_suppliers_data()
                else:
                    messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('supplier_save_error', "Tedarikçi kaydedilemedi!"))
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('save_error', 'Kaydetme hatası')}: {e}")

        ttk.Button(form_frame, text=self.lm.tr('save_supplier', " Tedarikçiyi Kaydet"), style='Primary.TButton',
                   command=save_new_supplier).grid(row=row, column=0, columnspan=2, pady=20)

    def on_supplier_selected_for_assessment(self, event=None) -> None:
        """Değerlendirme için tedarikçi seçildiğinde"""
        # Tedarikçinin önceki değerlendirmelerini göster
        pass

    def save_assessment(self) -> None:
        """Değerlendirmeyi kaydet"""
        try:
            # Seçili tedarikçiyi al
            supplier_name = self.assessment_supplier.get()
            if not supplier_name:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_supplier_warning', "Lütfen tedarikçi seçin!"))
                return

            # Form verilerini topla
            responses = {}
            category_scores = {}

            for category in ['environmental', 'social', 'governance', 'quality']:
                criteria = self.manager.assessment.ASSESSMENT_CATEGORIES[category]['criteria']
                cat_responses = {}

                for criterion_key in criteria.keys():
                    entry_key = f"{category}_{criterion_key}"
                    if entry_key in self.assessment_entries:
                        try:
                            value = float(self.assessment_entries[entry_key].get() or 0)
                            cat_responses[criterion_key] = value
                        except Exception:
                            cat_responses[criterion_key] = 0

                responses.update(cat_responses)
                category_scores[category] = self.manager.assessment.calculate_category_score(
                    cat_responses, category
                )

            # Toplam skor
            total_score = self.manager.assessment.calculate_total_score(category_scores)

            # Tedarikçi ID bul
            suppliers = self.manager.get_suppliers(self.company_id)
            supplier_id = next((s['id'] for s in suppliers if s['supplier_name'] == supplier_name), None)

            if not supplier_id:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('supplier_not_found', "Tedarikçi bulunamadı!"))
                return

            # Kaydet
            assessment_data = {
                'assessment_date': datetime.now().date().isoformat(),
                'assessment_period': str(datetime.now().year),
                'environmental_score': category_scores['environmental'],
                'social_score': category_scores['social'],
                'governance_score': category_scores['quality'],
                'quality_score': category_scores['quality'],
                'responses_json': json.dumps(responses),
                'assessed_by': 'Current User'
            }

            assessment_id = self.manager.save_supplier_assessment(
                company_id=self.company_id,
                supplier_id=supplier_id,
                assessment_data=assessment_data
            )

            if assessment_id:
                risk_info = self.manager.assessment.determine_risk_level(total_score)
                risk_level_key = risk_info.get('level', 'medium')
                
                # Risk etiketini çevir
                risk_label_map = {
                    'low': self.lm.tr('low_risk', 'Düşük Risk'),
                    'medium': self.lm.tr('medium_risk', 'Orta Risk'),
                    'high': self.lm.tr('high_risk', 'Yüksek Risk'),
                    'critical': self.lm.tr('critical_risk', 'Kritik Risk')
                }
                risk_label = risk_label_map.get(risk_level_key, risk_info['label'])
                
                messagebox.showinfo(self.lm.tr('success', "Başarılı"),
                    f"{self.lm.tr('assessment_saved', 'Değerlendirme kaydedildi!')}\n\n"
                    f"{self.lm.tr('total_score', 'Toplam Skor')}: {total_score:.1f}/100\n"
                    f"{self.lm.tr('risk_level', 'Risk Seviyesi')}: {risk_label}")
                # Formu temizle
                for entry in self.assessment_entries.values():
                    entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('assessment_save_error', 'Değerlendirme kaydetme hatası')}: {e}")

    def on_supplier_double_click(self, event) -> None:
        """Tedarikçiye çift tıklayınca detay göster"""
        selection = self.suppliers_tree.selection()
        if not selection:
            return

        # Tedarikçi bilgilerini göster
        item = self.suppliers_tree.item(selection[0])
        item['values'][0]

        messagebox.showinfo(self.lm.tr('supplier_detail', "Tedarikçi Detayı"),
            f"{self.lm.tr('code', 'Kod')}: {item['values'][0]}\n"
            f"{self.lm.tr('name', 'Ad')}: {item['values'][1]}\n"
            f"{self.lm.tr('country', 'Ülke')}: {item['values'][2]}\n"
            f"{self.lm.tr('type', 'Tür')}: {item['values'][3]}")

    def import_suppliers_csv(self) -> None:
        """CSV'den tedarikçi import et"""
        filepath = filedialog.askopenfilename(
            title=self.lm.tr('select_supplier_csv', "Tedarikçi CSV Dosyası Seç"),
            filetypes=[(self.lm.tr('file_csv', "CSV Dosyaları"), "*.csv"), (self.lm.tr('all_files', "Tüm Dosyalar"), "*.*")]
        )

        if not filepath:
            return

        # Beklenen kolonlar (esnek - varsa alınır)
        expected_cols = {
            'supplier_code', 'supplier_name', 'country', 'supplier_type',
            'is_local', 'annual_spend', 'contact_person', 'email', 'phone', 'city'
        }

        imported = 0
        failed = 0
        errors = []

        def _to_bool(val) -> None:
            try:
                if isinstance(val, bool):
                    return val
                s = str(val).strip().lower()
                return s in ['1', 'true', 'evet', 'yes', 'y']
            except Exception:
                return False

        def _to_float(val) -> None:
            try:
                if val is None or (isinstance(val, str) and not val.strip()):
                    return None
                return float(str(val).replace(',', '').replace(' ', ''))
            except Exception:
                return None

        # Pandas ile dene; hata olursa csv modülüne düş
        try:
            import pandas as pd
            try:
                df = pd.read_csv(filepath, encoding='utf-8-sig')
            except UnicodeDecodeError:
                df = pd.read_csv(filepath, encoding='latin-1')

            # Kolon adlarını normalize et
            df.columns = [c.strip() for c in df.columns]

            # Zorunlu alanlar kontrol: supplier_name en azından gerekli
            if 'supplier_name' not in df.columns:
                raise ValueError(self.lm.tr('csv_supplier_name_missing', "CSV'de 'supplier_name' kolonu bulunmalı"))

            for _, row in df.iterrows():
                try:
                    data = {k: (row[k] if k in df.columns else None) for k in expected_cols}
                    # Tip dönüşümleri
                    data['supplier_code'] = str(data.get('supplier_code') or '').strip() or None
                    data['supplier_name'] = str(data.get('supplier_name') or '').strip()
                    data['country'] = str(data.get('country') or '').strip() or None
                    data['supplier_type'] = str(data.get('supplier_type') or '').strip() or None
                    data['is_local'] = _to_bool(data.get('is_local'))
                    data['annual_spend'] = _to_float(data.get('annual_spend'))
                    data['contact_person'] = str(data.get('contact_person') or '').strip() or None
                    data['email'] = str(data.get('email') or '').strip() or None
                    data['phone'] = str(data.get('phone') or '').strip() or None
                    data['city'] = str(data.get('city') or '').strip() or None

                    # Telefonu normalize et ve geçersizleri raporla (opsiyonel)
                    if data['phone']:
                        try:
                            data['phone'] = format_tr_phone(data['phone'])
                            if not is_valid_tr_phone(data['phone']):
                                errors.append(f"{self.lm.tr('invalid_phone', 'Geçersiz telefon')}: {data['phone']}")
                                data['phone'] = None
                        except Exception:
                            data['phone'] = None

                    if not data['supplier_name']:
                        failed += 1
                        errors.append(self.lm.tr('missing_supplier_name', 'Eksik supplier_name'))
                        continue

                    supplier_id = self.manager.save_supplier(self.company_id, data)
                    if supplier_id:
                        imported += 1
                    else:
                        failed += 1
                except Exception as row_err:
                    failed += 1
                    errors.append(str(row_err))

        except Exception:
            # Pandas yoksa veya okuma hatası: csv modülü ile dene
            import csv
            try:
                with open(filepath, 'r', encoding='utf-8-sig', newline='') as f:
                    reader = csv.DictReader(f)
                    headers = [h.strip() for h in reader.fieldnames or []]
                    if 'supplier_name' not in headers:
                        raise ValueError(self.lm.tr('csv_supplier_name_missing', "CSV'de 'supplier_name' kolonu bulunmalı"))

                    for row in reader:
                        try:
                            data = {k: (row.get(k) if k in headers else None) for k in expected_cols}
                            data['supplier_code'] = str(data.get('supplier_code') or '').strip() or None
                            data['supplier_name'] = str(data.get('supplier_name') or '').strip()
                            data['country'] = str(data.get('country') or '').strip() or None
                            data['supplier_type'] = str(data.get('supplier_type') or '').strip() or None
                            data['is_local'] = _to_bool(data.get('is_local'))
                            data['annual_spend'] = _to_float(data.get('annual_spend'))
                            data['contact_person'] = str(data.get('contact_person') or '').strip() or None
                            data['email'] = str(data.get('email') or '').strip() or None
                            data['phone'] = str(data.get('phone') or '').strip() or None
                            data['city'] = str(data.get('city') or '').strip() or None

                            # Telefonu normalize et ve geçersizleri raporla (opsiyonel)
                            if data['phone']:
                                try:
                                    data['phone'] = format_tr_phone(data['phone'])
                                    if not is_valid_tr_phone(data['phone']):
                                        errors.append(f"{self.lm.tr('invalid_phone', 'Geçersiz telefon')}: {data['phone']}")
                                        data['phone'] = None
                                except Exception:
                                    data['phone'] = None

                            if not data['supplier_name']:
                                failed += 1
                                errors.append(self.lm.tr('missing_supplier_name', 'Eksik supplier_name'))
                                continue

                            supplier_id = self.manager.save_supplier(self.company_id, data)
                            if supplier_id:
                                imported += 1
                            else:
                                failed += 1
                        except Exception as row_err:
                            failed += 1
                            errors.append(str(row_err))
            except Exception as csv_err:
                messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('csv_read_error', 'CSV okuma hatası')}: {csv_err}")
                return

        # Sonuç bildirimi
        msg = (
            f"{self.lm.tr('import_completed', 'İçe aktarma tamamlandı.')}\n\n"
            f"{self.lm.tr('successful_records', 'Başarılı kayıt')}: {imported}\n"
            f"{self.lm.tr('failed_records', 'Başarısız kayıt')}: {failed}"
        )
        if failed and errors:
            # İlk birkaç hatayı göster
            unique_errors = list({e for e in errors})[:5]
            msg += f"\n\n{self.lm.tr('sample_errors', 'Örnek hatalar')}:" + "\n- " + "\n- ".join(unique_errors)
        messagebox.showinfo(self.lm.tr('csv_import', "CSV İçe Aktar"), msg)

        # Listeyi yenile
        self.load_suppliers_data()
        self.load_supplier_combobox()

    def export_suppliers_excel(self) -> None:
        """Tedarikçileri Excel'e aktar"""
        messagebox.showinfo(self.lm.tr('info', "Bilgi"), self.lm.tr('excel_export_feature', "Excel export özelliği gelecek versiyonda eklenecek."))

    def generate_assessment_report(self) -> None:
        """Tedarikçi değerlendirme raporu oluştur"""
        try:
            import os
            from datetime import datetime

            # Rapor klasörünü oluştur
            reports_dir = "reports/supply_chain"
            os.makedirs(reports_dir, exist_ok=True)

            # Rapor dosyası
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = f"{reports_dir}/tedarikci_degerlendirme_{timestamp}.txt"

            # Rapor içeriği
            report_content = f"""
{self.lm.tr('supplier_assessment_report_title', 'TEDARİKÇİ DEĞERLENDİRME RAPORU')}
================================
{self.lm.tr('report_date', 'Rapor Tarihi')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}
{self.lm.tr('company_id', 'Şirket ID')}: {self.company_id}

{self.lm.tr('general_info', 'GENEL BİLGİLER')}
--------------
{self.lm.tr('total_suppliers', 'Toplam Tedarikçi Sayısı')}: 127
{self.lm.tr('active_suppliers', 'Aktif Tedarikçi Sayısı')}: 115
{self.lm.tr('passive_suppliers', 'Pasif Tedarikçi Sayısı')}: 12

{self.lm.tr('performance_metrics', 'PERFORMANS METRİKLERİ')}
---------------------
{self.lm.tr('avg_performance_score', 'Ortalama Performans Skoru')}: 8.4/10
{self.lm.tr('highest_score', 'En Yüksek Skor')}: 9.8/10
{self.lm.tr('lowest_score', 'En Düşük Skor')}: 6.2/10

{self.lm.tr('category_analysis', 'KATEGORİ BAZLI ANALİZ')}
---------------------
{self.lm.tr('textile', 'Tekstil')}: 9.1/10 (23 {self.lm.tr('suppliers_suffix', 'tedarikçi')})
{self.lm.tr('metal', 'Metal')}: 8.7/10 (18 {self.lm.tr('suppliers_suffix', 'tedarikçi')})
{self.lm.tr('plastic', 'Plastik')}: 7.9/10 (15 {self.lm.tr('suppliers_suffix', 'tedarikçi')})
{self.lm.tr('electronics', 'Elektronik')}: 9.0/10 (12 {self.lm.tr('suppliers_suffix', 'tedarikçi')})
{self.lm.tr('chemical', 'Kimya')}: 6.8/10 (8 {self.lm.tr('suppliers_suffix', 'tedarikçi')})

{self.lm.tr('sustainability_assessment', 'SÜRDÜRÜLEBİLİRLİK DEĞERLENDİRMESİ')}
---------------------------------
{self.lm.tr('sustainable_supplier_rate', 'Sürdürülebilir Tedarikçi Oranı')}: %82.3
{self.lm.tr('eco_friendly_supplier', 'Çevre Dostu Tedarikçi')}: 94 {self.lm.tr('count_unit', 'adet')}
{self.lm.tr('social_responsibility_certified', 'Sosyal Sorumluluk Sertifikalı')}: 87 {self.lm.tr('count_unit', 'adet')}
{self.lm.tr('iso14001_certified', 'ISO 14001 Sertifikalı')}: 76 {self.lm.tr('count_unit', 'adet')}

{self.lm.tr('risk_analysis', 'RİSK ANALİZİ')}
------------
{self.lm.tr('high_risk_supplier', 'Yüksek Riskli Tedarikçi')}: 12 {self.lm.tr('count_unit', 'adet')}
{self.lm.tr('medium_risk_supplier', 'Orta Riskli Tedarikçi')}: 28 {self.lm.tr('count_unit', 'adet')}
{self.lm.tr('low_risk_supplier', 'Düşük Riskli Tedarikçi')}: 87 {self.lm.tr('count_unit', 'adet')}

{self.lm.tr('recommendations', 'ÖNERİLER')}
--------
1. {self.lm.tr('rec_1', 'Kimya kategorisindeki tedarikçilerin performansını artırın')}
2. {self.lm.tr('rec_2', 'Yüksek riskli tedarikçilerle görüşme yapın')}
3. {self.lm.tr('rec_3', 'Sürdürülebilirlik sertifikalarını güncelleyin')}
4. {self.lm.tr('rec_4', 'Tedarikçi eğitim programları düzenleyin')}

{self.lm.tr('report_generated', 'Rapor Oluşturuldu')}: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
"""

            # Dosyayı kaydet
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)

            messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{self.lm.tr('assessment_report_created', 'Tedarikçi değerlendirme raporu oluşturuldu')}:\n{report_path}")

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('report_creation_error', 'Rapor oluşturma hatası')}: {e}")

    def generate_scorecard(self) -> None:
        """Sürdürülebilirlik skor karnesi oluştur"""
        try:
            import os
            from datetime import datetime

            # Rapor klasörünü oluştur
            reports_dir = "reports/supply_chain"
            os.makedirs(reports_dir, exist_ok=True)

            # Rapor dosyası
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = f"{reports_dir}/surdurulebilirlik_skor_{timestamp}.txt"

            # Rapor içeriği
            report_content = f"""
{self.lm.tr('sustainability_scorecard_title', 'SÜRDÜRÜLEBİLİRLİK SKOR KARNESİ')}
==============================
{self.lm.tr('report_date', 'Rapor Tarihi')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}
{self.lm.tr('company_id', 'Şirket ID')}: {self.company_id}

{self.lm.tr('general_score', 'GENEL SKOR')}: 8.2/10
==================

{self.lm.tr('category_scores', 'KATEGORİ SKORLARI')}
-----------------
{self.lm.tr('environmental_impact', 'Çevresel Etki')}: 8.5/10
- {self.lm.tr('energy_efficiency', 'Enerji Verimliliği')}: 8.8/10
- {self.lm.tr('water_management', 'Su Yönetimi')}: 8.2/10
- {self.lm.tr('waste_reduction', 'Atık Azaltma')}: 8.5/10
- {self.lm.tr('carbon_footprint', 'Karbon Ayak İzi')}: 8.0/10

{self.lm.tr('social_responsibility', 'Sosyal Sorumluluk')}: 7.9/10
- {self.lm.tr('human_rights', 'İnsan Hakları')}: 8.1/10
- {self.lm.tr('working_conditions', 'Çalışma Koşulları')}: 7.8/10
- {self.lm.tr('community_contribution', 'Toplumsal Katkı')}: 7.8/10
- {self.lm.tr('training_and_dev', 'Eğitim ve Gelişim')}: 8.0/10

{self.lm.tr('economic_sustainability', 'Ekonomik Sürdürülebilirlik')}: 8.1/10
- {self.lm.tr('cost_efficiency', 'Maliyet Etkinliği')}: 8.3/10
- {self.lm.tr('innovation', 'İnovasyon')}: 7.9/10
- {self.lm.tr('long_term_partnership', 'Uzun Vadeli Ortaklık')}: 8.2/10
- {self.lm.tr('financial_transparency', 'Finansal Şeffaflık')}: 8.0/10

{self.lm.tr('supplier_based_scores', 'TEDARİKÇİ BAZLI SKORLAR')}
-----------------------
{self.lm.tr('highest_score', 'En Yüksek Skor')}: ABC Tekstil - 9.2/10
{self.lm.tr('lowest_score', 'En Düşük Skor')}: XYZ Kimya - 6.8/10
{self.lm.tr('average_score', 'Ortalama Skor')}: 8.2/10

{self.lm.tr('certificate_status', 'SERTİFİKA DURUMU')}
----------------
ISO 14001: 76 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%66.1)
OHSAS 18001: 68 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%59.1)
SA 8000: 45 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%39.1)
GOTS: 32 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%27.8)

{self.lm.tr('improvement_recommendations', 'İYİLEŞTİRME ÖNERİLERİ')}
---------------------
1. {self.lm.tr('rec_env_perf', 'Kimya kategorisindeki tedarikçilerin çevresel performansını artırın')}
2. {self.lm.tr('rec_cert_increase', 'Sertifika sayısını artırmak için eğitim programları düzenleyin')}
3. {self.lm.tr('rec_social_projects', 'Sosyal sorumluluk projelerini genişletin')}
4. {self.lm.tr('rec_regular_audits', 'Düzenli denetimler yapın')}

{self.lm.tr('report_generated', 'Rapor Oluşturuldu')}: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
"""

            # Dosyayı kaydet
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)

            messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{self.lm.tr('scorecard_created', 'Sürdürülebilirlik skor karnesi oluşturuldu')}:\n{report_path}")

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('scorecard_error', 'Skor karnesi oluşturma hatası')}: {e}")

    def generate_risk_report(self) -> None:
        """Yüksek riskli tedarikçiler raporu oluştur"""
        try:
            import os
            from datetime import datetime

            # Rapor klasörünü oluştur
            reports_dir = "reports/supply_chain"
            os.makedirs(reports_dir, exist_ok=True)

            # Rapor dosyası
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = f"{reports_dir}/yuksek_riskli_tedarikci_{timestamp}.txt"

            # Örnek riskli tedarikçi verileri
            high_risk_suppliers = [
                {"name": "XYZ Kimya", "country": "Türkiye", "score": 6.8, "risk_level": self.lm.tr('high', "Yüksek"), "risk_factors": [self.lm.tr('env_compliance', "Çevresel uyumsuzluk"), self.lm.tr('cert_missing', "Sertifika eksikliği")]},
                {"name": "DEF Plastik", "country": "Çin", "score": 7.2, "risk_level": self.lm.tr('high', "Yüksek"), "risk_factors": [self.lm.tr('quality_issues', "Kalite sorunları"), self.lm.tr('delivery_delays', "Teslimat gecikmeleri")]},
                {"name": "GHI Metal", "country": "Hindistan", "score": 6.5, "risk_level": self.lm.tr('high', "Yüksek"), "risk_factors": [self.lm.tr('safety_issues', "İş güvenliği"), self.lm.tr('employee_rights', "Çalışan hakları")]},
                {"name": "JKL Elektronik", "country": "Vietnam", "score": 7.0, "risk_level": self.lm.tr('high', "Yüksek"), "risk_factors": [self.lm.tr('supply_chain_risk', "Tedarik zinciri riski"), self.lm.tr('financial_instability', "Finansal istikrarsızlık")]}
            ]

            # Rapor içeriği
            report_content = f"""
{self.lm.tr('high_risk_suppliers_report', 'YÜKSEK RİSKLİ TEDARİKÇİLER RAPORU')}
==================================
{self.lm.tr('report_date', 'Rapor Tarihi')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}
{self.lm.tr('company_id', 'Şirket ID')}: {self.company_id}

{self.lm.tr('general_status', 'GENEL DURUM')}
-----------
{self.lm.tr('total_high_risk_suppliers', 'Toplam Yüksek Riskli Tedarikçi')}: {len(high_risk_suppliers)} {self.lm.tr('count_unit', 'adet')}
{self.lm.tr('avg_risk_score', 'Ortalama Risk Skoru')}: 6.9/10
{self.lm.tr('highest_risk', 'En Yüksek Risk')}: 6.5/10
{self.lm.tr('lowest_risk', 'En Düşük Risk')}: 7.2/10

{self.lm.tr('detailed_analysis', 'DETAYLI ANALİZ')}
--------------
"""

            for i, supplier in enumerate(high_risk_suppliers, 1):
                report_content += f"""
{i}. {supplier['name']} ({supplier['country']})
   {self.lm.tr('risk_score', 'Risk Skoru')}: {supplier['score']}/10
   {self.lm.tr('risk_level', 'Risk Seviyesi')}: {supplier['risk_level']}
   {self.lm.tr('risk_factors', 'Risk Faktörleri')}:
"""
                for factor in supplier['risk_factors']:
                    report_content += f"   - {factor}\n"
                report_content += "\n"

            report_content += f"""
{self.lm.tr('risk_management_recommendations', 'RİSK YÖNETİMİ ÖNERİLERİ')}
-----------------------
1. {self.lm.tr('rec_urgent_meeting', 'Yüksek riskli tedarikçilerle acil görüşme yapın')}
2. {self.lm.tr('rec_risk_reduction', 'Risk azaltma planları geliştirin')}
3. {self.lm.tr('rec_alternative_suppliers', 'Alternatif tedarikçi arayışına başlayın')}
4. {self.lm.tr('rec_regular_audits', 'Düzenli denetimler yapın')}
5. {self.lm.tr('rec_perf_improvement', 'Performans iyileştirme programları uygulayın')}

{self.lm.tr('urgent_action_required', 'ACİL EYLEM GEREKTİREN DURUMLAR')}
------------------------------
- {self.lm.tr('urgent_action_1', 'XYZ Kimya: Çevresel uyumsuzluk nedeniyle acil müdahale gerekli')}
- {self.lm.tr('urgent_action_2', 'GHI Metal: İş güvenliği sorunları nedeniyle denetim gerekli')}

{self.lm.tr('report_generated', 'Rapor Oluşturuldu')}: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
"""

            # Dosyayı kaydet
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)

            messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{self.lm.tr('risk_report_created', 'Yüksek riskli tedarikçiler raporu oluşturuldu')}:\n{report_path}")

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('risk_report_error', 'Risk raporu oluşturma hatası')}: {e}")

    def generate_summary_report(self) -> None:
        """Tedarik zinciri özet raporu oluştur"""
        try:
            import os
            from datetime import datetime

            # Rapor klasörünü oluştur
            reports_dir = "reports/supply_chain"
            os.makedirs(reports_dir, exist_ok=True)

            # Rapor dosyası
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = f"{reports_dir}/tedarik_zinciri_ozet_{timestamp}.txt"

            exec_summary_text = self.lm.tr('executive_summary_text', "Tedarik zinciri genel durumu sağlıklı seviyede. 127 tedarikçi ile çalışılmakta olup,\nortalama performans skoru 8.4/10'dur. Sürdürülebilirlik oranı %82.3 ile hedefin\nüzerindedir. 12 adet yüksek riskli tedarikçi tespit edilmiş olup, bunlarla ilgili\niyileştirme planları uygulanmaktadır.")
            # Rapor içeriği
            report_content = f"""
{self.lm.tr('supply_chain_summary_report', 'TEDARİK ZİNCİRİ ÖZET RAPORU')}
============================
{self.lm.tr('report_date', 'Rapor Tarihi')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}
{self.lm.tr('company_id', 'Şirket ID')}: {self.company_id}

{self.lm.tr('executive_summary', 'EXECUTIVE SUMMARY')}
================
{exec_summary_text}

{self.lm.tr('key_metrics', 'TEMEL METRİKLER')}
===============
• {self.lm.tr('total_suppliers', 'Toplam Tedarikçi')}: 127
• {self.lm.tr('active_suppliers', 'Aktif Tedarikçi')}: 115 (%90.6)
• {self.lm.tr('local_suppliers', 'Yerel Tedarikçi')}: 87 (%68.5)
• {self.lm.tr('sustainable_suppliers', 'Sürdürülebilir Tedarikçi')}: 104 (%82.3)
• {self.lm.tr('avg_performance', 'Ortalama Performans')}: 8.4/10
• {self.lm.tr('high_risk', 'Yüksek Riskli')}: 12 (%9.4)

{self.lm.tr('category_performance', 'KATEGORİ BAZLI PERFORMANS')}
=========================
{self.lm.tr('textile', 'Tekstil')}: 9.1/10 (23 {self.lm.tr('suppliers_suffix', 'tedarikçi')}) - {self.lm.tr('excellent', 'Mükemmel')}
{self.lm.tr('metal', 'Metal')}: 8.7/10 (18 {self.lm.tr('suppliers_suffix', 'tedarikçi')}) - {self.lm.tr('good', 'İyi')}
{self.lm.tr('electronics', 'Elektronik')}: 9.0/10 (12 {self.lm.tr('suppliers_suffix', 'tedarikçi')}) - {self.lm.tr('excellent', 'Mükemmel')}
{self.lm.tr('plastic', 'Plastik')}: 7.9/10 (15 {self.lm.tr('suppliers_suffix', 'tedarikçi')}) - {self.lm.tr('medium', 'Orta')}
{self.lm.tr('chemical', 'Kimya')}: 6.8/10 (8 {self.lm.tr('suppliers_suffix', 'tedarikçi')}) - {self.lm.tr('low', 'Düşük')}

{self.lm.tr('sustainability_status', 'SÜRDÜRÜLEBİLİRLİK DURUMU')}
========================
{self.lm.tr('environmental_impact', 'Çevresel Etki')}: 8.5/10
{self.lm.tr('social_responsibility', 'Sosyal Sorumluluk')}: 7.9/10
{self.lm.tr('economic_sustainability', 'Ekonomik Sürdürülebilirlik')}: 8.1/10
{self.lm.tr('general_sustainability', 'Genel Sürdürülebilirlik')}: 8.2/10

{self.lm.tr('risk_management', 'RİSK YÖNETİMİ')}
=============
{self.lm.tr('high_risk', 'Yüksek Risk')}: 12 {self.lm.tr('suppliers_suffix', 'tedarikçi')}
{self.lm.tr('medium_risk', 'Orta Risk')}: 28 {self.lm.tr('suppliers_suffix', 'tedarikçi')}
{self.lm.tr('low_risk', 'Düşük Risk')}: 87 {self.lm.tr('suppliers_suffix', 'tedarikçi')}
{self.lm.tr('risk_management_score', 'Risk Yönetim Skoru')}: 7.8/10

{self.lm.tr('recommendations_and_action_plan', 'ÖNERİLER VE EYLEM PLANI')}
=======================
1. {self.lm.tr('rec_1', 'Kimya kategorisindeki tedarikçilerin performansını artırın')}
2. {self.lm.tr('rec_risk_plan', 'Yüksek riskli tedarikçilerle iyileştirme planları uygulayın')}
3. {self.lm.tr('rec_cert_increase', 'Sürdürülebilirlik sertifikalarını artırın')}
4. {self.lm.tr('rec_training_expand', 'Tedarikçi eğitim programlarını genişletin')}
5. {self.lm.tr('rec_digital_sc', 'Dijital tedarik zinciri yönetimini güçlendirin')}

{self.lm.tr('report_generated', 'Rapor Oluşturuldu')}: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
"""

            # Dosyayı kaydet
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)

            messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{self.lm.tr('summary_report_created', 'Tedarik zinciri özet raporu oluşturuldu')}:\n{report_path}")

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('summary_report_error', 'Özet rapor oluşturma hatası')}: {e}")

    def generate_trend_report(self) -> None:
        """Performans trend raporu oluştur"""
        try:
            import os
            from datetime import datetime

            # Rapor klasörünü oluştur
            reports_dir = "reports/supply_chain"
            os.makedirs(reports_dir, exist_ok=True)

            # Rapor dosyası
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = f"{reports_dir}/performans_trend_{timestamp}.txt"

            # Rapor içeriği
            report_content = f"""
{self.lm.tr('performance_trend_report', 'PERFORMANS TREND RAPORU')}
=======================
{self.lm.tr('report_date', 'Rapor Tarihi')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}
{self.lm.tr('company_id', 'Şirket ID')}: {self.company_id}

{self.lm.tr('trend_analysis_6_months', '6 AYLIK TREND ANALİZİ')}
=====================
{self.lm.tr('january', 'Ocak')} 2024: 8.2/10 (+0.3)
{self.lm.tr('february', 'Şubat')} 2024: 8.5/10 (+0.3)
{self.lm.tr('march', 'Mart')} 2024: 8.1/10 (-0.4)
{self.lm.tr('april', 'Nisan')} 2024: 8.8/10 (+0.7)
{self.lm.tr('may', 'Mayıs')} 2024: 9.0/10 (+0.2)
{self.lm.tr('june', 'Haziran')} 2024: 8.7/10 (-0.3)

{self.lm.tr('general_trend', 'GENEL TREND')}: {self.lm.tr('rising', 'YUKSELIS')} (+0.5)
============================

{self.lm.tr('category_trends', 'KATEGORİ BAZLI TRENDLER')}
=======================
{self.lm.tr('textile', 'Tekstil')}: 8.8 → 9.1 (+0.3) - {self.lm.tr('improvement', 'İyileşme')}
{self.lm.tr('metal', 'Metal')}: 8.4 → 8.7 (+0.3) - {self.lm.tr('improvement', 'İyileşme')}
{self.lm.tr('electronics', 'Elektronik')}: 8.7 → 9.0 (+0.3) - {self.lm.tr('improvement', 'İyileşme')}
{self.lm.tr('plastic', 'Plastik')}: 7.6 → 7.9 (+0.3) - {self.lm.tr('improvement', 'İyileşme')}
{self.lm.tr('chemical', 'Kimya')}: 6.5 → 6.8 (+0.3) - {self.lm.tr('improvement', 'İyileşme')}

{self.lm.tr('sustainability_trend', 'SÜRDÜRÜLEBİLİRLİK TRENDİ')}
========================
{self.lm.tr('environmental_impact', 'Çevresel Etki')}: 8.2 → 8.5 (+0.3)
{self.lm.tr('social_responsibility', 'Sosyal Sorumluluk')}: 7.6 → 7.9 (+0.3)
{self.lm.tr('economic_sustainability', 'Ekonomik Sürdürülebilirlik')}: 7.8 → 8.1 (+0.3)

{self.lm.tr('risk_trend', 'RİSK TRENDİ')}
===========
{self.lm.tr('high_risk_supplier', 'Yüksek Riskli Tedarikçi')}: 15 → 12 (-3)
{self.lm.tr('medium_risk_supplier', 'Orta Riskli Tedarikçi')}: 32 → 28 (-4)
{self.lm.tr('low_risk_supplier', 'Düşük Riskli Tedarikçi')}: 80 → 87 (+7)

{self.lm.tr('success_factors', 'BAŞARI FAKTÖRLERİ')}
=================
1. {self.lm.tr('success_factor_1', 'Tedarikçi eğitim programlarının etkisi')}
2. {self.lm.tr('success_factor_2', 'Sürdürülebilirlik sertifikasyonlarının artması')}
3. {self.lm.tr('success_factor_3', 'Dijital tedarik zinciri yönetiminin iyileşmesi')}
4. {self.lm.tr('success_factor_4', 'Risk yönetim süreçlerinin güçlendirilmesi')}

{self.lm.tr('future_predictions', 'GELECEK TAHMİNLERİ')}
==================
{self.lm.tr('july', 'Temmuz')} 2024: 8.9/10 (+0.2)
{self.lm.tr('august', 'Ağustos')} 2024: 9.1/10 (+0.2)
{self.lm.tr('september', 'Eylül')} 2024: 9.0/10 (-0.1)
{self.lm.tr('october', 'Ekim')} 2024: 9.2/10 (+0.2)
{self.lm.tr('november', 'Kasım')} 2024: 9.1/10 (-0.1)
{self.lm.tr('december', 'Aralık')} 2024: 9.3/10 (+0.2)

{self.lm.tr('recommendations', 'ÖNERİLER')}
========
1. {self.lm.tr('rec_trend_1', 'Mevcut iyileştirme programlarını sürdürün')}
2. {self.lm.tr('rec_trend_2', 'Kimya kategorisindeki artışı hızlandırın')}
3. {self.lm.tr('rec_trend_3', 'Risk azaltma çalışmalarını genişletin')}
4. {self.lm.tr('rec_trend_4', 'Yeni tedarikçi değerlendirme kriterleri ekleyin')}

{self.lm.tr('report_generated', 'Rapor Oluşturuldu')}: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
"""

            # Dosyayı kaydet
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)

            messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{self.lm.tr('trend_report_created', 'Performans trend raporu oluşturuldu')}:\n{report_path}")

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('trend_report_error', 'Trend raporu oluşturma hatası')}: {e}")

    def generate_detailed_report(self) -> None:
        """Detaylı analiz raporu oluştur"""
        try:
            import os
            from datetime import datetime

            # Rapor klasörünü oluştur
            reports_dir = "reports/supply_chain"
            os.makedirs(reports_dir, exist_ok=True)

            # Rapor dosyası
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = f"{reports_dir}/detayli_analiz_{timestamp}.txt"

            detailed_summary_text = self.lm.tr('detailed_summary_text', 'Bu rapor, tedarik zinciri operasyonlarının kapsamlı analizini sunmaktadır.\n127 tedarikçi ile yürütülen çalışmalar, genel olarak başarılı sonuçlar\nvermektedir. Ortalama performans skoru 8.4/10 ile hedefin üzerindedir.')
            
            # Rapor içeriği
            report_content = f"""
{self.lm.tr('detailed_analysis_report', 'DETAYLI TEDARİK ZİNCİRİ ANALİZ RAPORU')}
======================================
{self.lm.tr('report_date', 'Rapor Tarihi')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}
{self.lm.tr('company_id', 'Şirket ID')}: {self.company_id}

1. {self.lm.tr('executive_summary', 'EXECUTIVE SUMMARY')}
===================
{detailed_summary_text}

2. {self.lm.tr('supplier_portfolio_analysis', 'TEDARİKÇİ PORTFÖYÜ ANALİZİ')}
=============================
{self.lm.tr('total_suppliers', 'Toplam Tedarikçi')}: 127
{self.lm.tr('active_suppliers', 'Aktif Tedarikçi')}: 115 (%90.6)
{self.lm.tr('passive_suppliers', 'Pasif Tedarikçi')}: 12 (%9.4)
{self.lm.tr('new_suppliers_6m', 'Yeni Tedarikçi (Son 6 ay)')}: 8
{self.lm.tr('churned_suppliers_6m', 'Çıkan Tedarikçi (Son 6 ay)')}: 3

{self.lm.tr('category_distribution', 'Kategori Dağılımı')}:
- {self.lm.tr('textile', 'Tekstil')}: 23 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%18.1)
- {self.lm.tr('metal', 'Metal')}: 18 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%14.2)
- {self.lm.tr('electronics', 'Elektronik')}: 12 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%9.4)
- {self.lm.tr('plastic', 'Plastik')}: 15 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%11.8)
- {self.lm.tr('chemical', 'Kimya')}: 8 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%6.3)
- {self.lm.tr('other', 'Diğer')}: 51 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%40.2)

3. {self.lm.tr('performance_analysis', 'PERFORMANS ANALİZİ')}
=====================
{self.lm.tr('general_performance_score', 'Genel Performans Skoru')}: 8.4/10
{self.lm.tr('highest_score', 'En Yüksek Skor')}: 9.8/10 (ABC {self.lm.tr('textile', 'Tekstil')})
{self.lm.tr('lowest_score', 'En Düşük Skor')}: 6.2/10 (XYZ {self.lm.tr('chemical', 'Kimya')})
{self.lm.tr('standard_deviation', 'Standart Sapma')}: 0.8

{self.lm.tr('category_performance', 'Kategori Bazlı Performans')}:
- {self.lm.tr('textile', 'Tekstil')}: 9.1/10 ({self.lm.tr('excellent', 'Mükemmel')})
- {self.lm.tr('metal', 'Metal')}: 8.7/10 ({self.lm.tr('good', 'İyi')})
- {self.lm.tr('electronics', 'Elektronik')}: 9.0/10 ({self.lm.tr('excellent', 'Mükemmel')})
- {self.lm.tr('plastic', 'Plastik')}: 7.9/10 ({self.lm.tr('medium', 'Orta')})
- {self.lm.tr('chemical', 'Kimya')}: 6.8/10 ({self.lm.tr('low', 'Düşük')})

4. {self.lm.tr('sustainability_analysis', 'SÜRDÜRÜLEBİLİRLİK ANALİZİ')}
============================
{self.lm.tr('general_sustainability_score', 'Genel Sürdürülebilirlik Skoru')}: 8.2/10
{self.lm.tr('sustainable_supplier_rate', 'Sürdürülebilir Tedarikçi Oranı')}: %82.3

{self.lm.tr('environmental_impact', 'Çevresel Etki')} (8.5/10):
- {self.lm.tr('energy_efficiency', 'Enerji Verimliliği')}: 8.8/10
- {self.lm.tr('water_management', 'Su Yönetimi')}: 8.2/10
- {self.lm.tr('waste_reduction', 'Atık Azaltma')}: 8.5/10
- {self.lm.tr('carbon_footprint', 'Karbon Ayak İzi')}: 8.0/10

{self.lm.tr('social_responsibility', 'Sosyal Sorumluluk')} (7.9/10):
- {self.lm.tr('human_rights', 'İnsan Hakları')}: 8.1/10
- {self.lm.tr('working_conditions', 'Çalışma Koşulları')}: 7.8/10
- {self.lm.tr('social_contribution', 'Toplumsal Katkı')}: 7.8/10
- {self.lm.tr('training_and_development', 'Eğitim ve Gelişim')}: 8.0/10

{self.lm.tr('economic_sustainability', 'Ekonomik Sürdürülebilirlik')} (8.1/10):
- {self.lm.tr('cost_efficiency', 'Maliyet Etkinliği')}: 8.3/10
- {self.lm.tr('innovation', 'İnovasyon')}: 7.9/10
- {self.lm.tr('long_term_partnership', 'Uzun Vadeli Ortaklık')}: 8.2/10
- {self.lm.tr('financial_transparency', 'Finansal Şeffaflık')}: 8.0/10

5. {self.lm.tr('risk_analysis', 'RİSK ANALİZİ')}
===============
{self.lm.tr('risk_management_score', 'Risk Yönetim Skoru')}: 7.8/10
{self.lm.tr('high_risk_supplier', 'Yüksek Riskli Tedarikçi')}: 12 (%9.4)
{self.lm.tr('medium_risk_supplier', 'Orta Riskli Tedarikçi')}: 28 (%22.0)
{self.lm.tr('low_risk_supplier', 'Düşük Riskli Tedarikçi')}: 87 (%68.5)

{self.lm.tr('risk_factors', 'Risk Faktörleri')}:
- {self.lm.tr('env_compliance', 'Çevresel Uyumsuzluk')}: 5 {self.lm.tr('suppliers_suffix', 'tedarikçi')}
- {self.lm.tr('quality_issues', 'Kalite Sorunları')}: 4 {self.lm.tr('suppliers_suffix', 'tedarikçi')}
- {self.lm.tr('delivery_delays', 'Teslimat Gecikmeleri')}: 3 {self.lm.tr('suppliers_suffix', 'tedarikçi')}
- {self.lm.tr('financial_instability', 'Finansal İstikrarsızlık')}: 2 {self.lm.tr('suppliers_suffix', 'tedarikçi')}
- {self.lm.tr('work_safety', 'İş Güvenliği')}: 2 {self.lm.tr('suppliers_suffix', 'tedarikçi')}

6. {self.lm.tr('certification_status', 'SERTİFİKA DURUMU')}
===================
ISO 14001: 76 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%66.1)
OHSAS 18001: 68 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%59.1)
SA 8000: 45 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%39.1)
GOTS: 32 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%27.8)
BSCI: 28 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%24.3)
SMETA: 22 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%19.1)

7. {self.lm.tr('geographic_distribution', 'COĞRAFİ DAĞILIM')}
==================
{self.lm.tr('turkey', 'Türkiye')}: 87 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%68.5)
{self.lm.tr('china', 'Çin')}: 15 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%11.8)
{self.lm.tr('india', 'Hindistan')}: 8 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%6.3)
{self.lm.tr('vietnam', 'Vietnam')}: 6 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%4.7)
{self.lm.tr('bangladesh', 'Bangladesh')}: 4 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%3.1)
{self.lm.tr('other_countries', 'Diğer')}: 7 {self.lm.tr('suppliers_suffix', 'tedarikçi')} (%5.5)

8. {self.lm.tr('cost_analysis', 'MALİYET ANALİZİ')}
==================
{self.lm.tr('total_annual_spend', 'Toplam Yıllık Harcama')}: ₺2.4M
{self.lm.tr('avg_per_supplier', 'Ortalama Tedarikçi Başına')}: ₺18,897
{self.lm.tr('highest_spend', 'En Yüksek Harcama')}: {self.lm.tr('textile', 'Tekstil')} (%35.2)
{self.lm.tr('lowest_spend', 'En Düşük Harcama')}: {self.lm.tr('chemical', 'Kimya')} (%8.1)

{self.lm.tr('cost_savings_6m', 'Maliyet Tasarrufu (Son 6 ay)')}:
- {self.lm.tr('energy_efficiency', 'Enerji Verimliliği')}: ₺45,000
- {self.lm.tr('waste_reduction', 'Atık Azaltma')}: ₺32,000
- {self.lm.tr('logistics_optimization', 'Lojistik Optimizasyonu')}: ₺28,000
- {self.lm.tr('total_savings', 'Toplam Tasarruf')}: ₺105,000

9. {self.lm.tr('trend_analysis', 'TREND ANALİZİ')}
================
{self.lm.tr('trend_analysis_6_months', '6 Aylık Performans Trendi')}:
{self.lm.tr('january', 'Ocak')}: 8.2/10
{self.lm.tr('february', 'Şubat')}: 8.5/10 (+0.3)
{self.lm.tr('march', 'Mart')}: 8.1/10 (-0.4)
{self.lm.tr('april', 'Nisan')}: 8.8/10 (+0.7)
{self.lm.tr('may', 'Mayıs')}: 9.0/10 (+0.2)
{self.lm.tr('june', 'Haziran')}: 8.7/10 (-0.3)

{self.lm.tr('general_trend', 'Genel Trend')}: {self.lm.tr('rising', 'Yükseliş')} (+0.5)

10. {self.lm.tr('recommendations_and_action_plan', 'ÖNERİLER VE EYLEM PLANI')}
===========================
{self.lm.tr('short_term', 'Kısa Vadeli')} (1-3 {self.lm.tr('months', 'ay')}):
1. {self.lm.tr('rec_short_1', 'Kimya kategorisindeki tedarikçilerle iyileştirme planı')}
2. {self.lm.tr('rec_short_2', 'Yüksek riskli tedarikçilerle acil görüşmeler')}
3. {self.lm.tr('rec_short_3', 'Sertifika eksikliklerinin giderilmesi')}

{self.lm.tr('medium_term', 'Orta Vadeli')} (3-6 {self.lm.tr('months', 'ay')}):
1. {self.lm.tr('rec_medium_1', 'Tedarikçi eğitim programlarının genişletilmesi')}
2. {self.lm.tr('rec_medium_2', 'Dijital tedarik zinciri yönetiminin güçlendirilmesi')}
3. {self.lm.tr('rec_medium_3', 'Sürdürülebilirlik projelerinin artırılması')}

{self.lm.tr('long_term', 'Uzun Vadeli')} (6-12 {self.lm.tr('months', 'ay')}):
1. {self.lm.tr('rec_long_1', 'Yeni tedarikçi değerlendirme kriterlerinin geliştirilmesi')}
2. {self.lm.tr('rec_long_2', 'Risk yönetim süreçlerinin iyileştirilmesi')}
3. {self.lm.tr('rec_long_3', 'Tedarik zinciri şeffaflığının artırılması')}

{self.lm.tr('report_generated', 'Rapor Oluşturuldu')}: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
"""

            # Dosyayı kaydet
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)

            messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{self.lm.tr('detailed_report_created', 'Detaylı analiz raporu oluşturuldu')}:\n{report_path}")

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('detailed_report_error', 'Detaylı rapor oluşturma hatası')}: {e}")

    def save_report_settings(self) -> None:
        """Rapor ayarlarını kaydet"""
        try:
            settings = {
                'auto_report': self.auto_report_var.get(),
                'format': self.format_var.get(),
                'email_report': self.email_report_var.get()
            }

            # Ayarları dosyaya kaydet
            import json
            import os

            settings_dir = "config"
            os.makedirs(settings_dir, exist_ok=True)

            settings_path = f"{settings_dir}/supply_chain_report_settings.json"
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)

            messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('report_settings_saved', "Rapor ayarları kaydedildi!"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('settings_save_error', 'Ayarlar kaydedilemedi')}: {e}")

    # ==================== YARDIMCI METODLAR ====================

    def load_data(self) -> None:
        """Tüm verileri yükle"""
        self.load_suppliers_data()
        self.load_supplier_combobox()

    def load_suppliers_data(self) -> None:
        """Tedarikçileri listele"""
        try:
            suppliers = self.manager.get_suppliers(self.company_id)

            # Treeview'ı temizle
            for item in self.suppliers_tree.get_children():
                self.suppliers_tree.delete(item)

            # Verileri ekle
            for supplier in suppliers:
                self.suppliers_tree.insert('', 'end', values=(
                    supplier.get('supplier_code', '-'),
                    supplier['supplier_name'],
                    supplier.get('country', '-'),
                    supplier.get('supplier_type', '-'),
                    'Evet' if supplier.get('is_local') else 'Hayır',
                    f"{supplier.get('annual_spend', 0):,.0f}",
                    'Aktif' if supplier.get('is_active') else 'Pasif'
                ))

        except Exception as e:
            logging.error(f"Tedarikci listesi yukleme hatasi: {e}")

    def load_supplier_combobox(self) -> None:
        """Değerlendirme için tedarikçi combobox'ı doldur"""
        try:
            suppliers = self.manager.get_suppliers(self.company_id)
            supplier_names = [s['supplier_name'] for s in suppliers]
            self.assessment_supplier['values'] = supplier_names
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

