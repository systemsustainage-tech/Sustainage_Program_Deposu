import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATIK YÖNETİMİ GUI
Atık yönetimi modülü kullanıcı arayüzü
"""

import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk, filedialog

from utils.language_manager import LanguageManager
from utils.ui_theme import apply_theme

from .waste_calculator import WasteCalculator
from .waste_factors import WasteFactors
from .waste_manager import WasteManager
from .waste_reporting import WasteReporting


class WasteGUI:
    """Atık Yönetimi Modülü GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.waste_manager = WasteManager()
        self.waste_manager.company_id = company_id
        self.waste_calculator = WasteCalculator()
        self.waste_factors = WasteFactors()
        self.waste_reporting = WasteReporting(self.waste_manager)
        self.lm = LanguageManager()

        # Atık türlerini doldur
        self.waste_manager.populate_waste_types()

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Atık yönetimi arayüzünü oluştur"""
        apply_theme(self.parent)
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık ve çıkış butonu
        header_frame = tk.Frame(main_frame, bg='#f0f2f5')
        header_frame.pack(fill='x', pady=(0, 20))

        # Başlık ve çıkış butonu yan yana
        title_frame = tk.Frame(header_frame, bg='#f0f2f5')
        title_frame.pack(side='left', fill='both', expand=True)

        title_label = tk.Label(title_frame, text=self.lm.tr('waste_title', "Atık Yönetimi"),
                              font=('Segoe UI', 20, 'bold'), fg='#1e293b', bg='#f0f2f5')
        title_label.pack(side='left')

        toolbar = ttk.Frame(header_frame)
        toolbar.pack(side='right', padx=12, pady=10)
        ttk.Button(toolbar, text=self.lm.tr('btn_report_center', ' Rapor Merkezi'), style='Primary.TButton', command=self.open_report_center_waste).pack(side='right', padx=6)
        ttk.Button(toolbar, text=self.lm.tr('btn_close', ' Kapat'), style='Primary.TButton', command=self.parent.destroy).pack(side='right', padx=6)

        # Sol panel - Menü
        left_panel = tk.Frame(main_frame, bg='#ecf0f1', width=250)
        left_panel.pack(side='left', fill='y', padx=(0, 15))
        left_panel.pack_propagate(False)

        # Menü başlığı
        menu_title = tk.Label(left_panel, text=self.lm.tr('waste_menu_title', "Atık Yönetimi Menüsü"),
                             font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#ecf0f1')
        menu_title.pack(pady=15)

        # Menü butonları
        menu_buttons = [
            ("", self.lm.tr('menu_dashboard', "Dashboard"), self.show_dashboard),
            ("", self.lm.tr('menu_waste_records', "Atık Kayıtları"), self.show_waste_records),
            ("", self.lm.tr('menu_reduction_targets', "Azaltma Hedefleri"), self.show_reduction_targets),
            ("", self.lm.tr('menu_recycling_projects', "Geri Dönüşüm Projeleri"), self.show_recycling_projects),
            ("", self.lm.tr('menu_metrics_analysis', "Metrikler & Analiz"), self.show_metrics),
            ("", self.lm.tr('menu_reports', "Raporlar"), self.show_reports),
            ("️", self.lm.tr('menu_settings', "Ayarlar"), self.show_settings)
        ]

        self.menu_buttons = {}
        for icon, text, command in menu_buttons:
            btn = ttk.Button(left_panel, text=f"{icon} {text}", style='Primary.TButton', command=command)
            btn.pack(fill='x', padx=10, pady=5)
            self.menu_buttons[text] = btn

        # Sağ panel - İçerik (scrollable)
        content_outer = tk.Frame(main_frame, bg='white')
        content_outer.pack(side='right', fill='both', expand=True)
        content_canvas = tk.Canvas(content_outer, bg='white', highlightthickness=0)
        content_scroll = ttk.Scrollbar(content_outer, orient='vertical', command=content_canvas.yview)
        self.content_frame = tk.Frame(content_canvas, bg='white')
        self.content_frame.bind('<Configure>', lambda e: content_canvas.configure(scrollregion=content_canvas.bbox('all')))
        content_canvas.create_window((0, 0), window=self.content_frame, anchor='nw')
        content_canvas.configure(yscrollcommand=content_scroll.set)
        content_canvas.pack(side='left', fill='both', expand=True)
        content_scroll.pack(side='right', fill='y')

        # İçerik başlığı
        self.content_title = tk.Label(self.content_frame, text=self.lm.tr('waste_dashboard_title', "Atık Yönetimi Dashboard"),
                                     font=('Segoe UI', 15, 'bold'), fg='#2c3e50', bg='white')
        self.content_title.pack(pady=12)

        # İçerik alanı
        self.content_area = tk.Frame(self.content_frame, bg='white')
        self.content_area.pack(fill='both', expand=True, padx=12, pady=10)

        # Başlangıç içeriği
        self.show_dashboard()

    def open_report_center_waste(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('atik')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for atik: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_report_center', 'Rapor Merkezi açılamadı')}:\n{e}")
            logging.error(f"Error opening report center: {e}")

    def show_dashboard(self) -> None:
        """Dashboard göster"""
        self.clear_content()
        self.update_menu_buttons(self.lm.tr('menu_dashboard', "Dashboard"))

        # Dashboard içeriği
        dashboard_frame = tk.Frame(self.content_area, bg='white')
        dashboard_frame.pack(fill='both', expand=True)

        # Metrik kartları
        metrics_frame = tk.Frame(dashboard_frame, bg='white')
        metrics_frame.pack(fill='x', pady=(0, 20))

        # İstatistikleri al
        statistics = self.waste_manager.get_waste_statistics(self.company_id)

        # Metrik kartları oluştur
        metrics_data = [
            ("", self.lm.tr('metric_total_records', "Toplam Kayıt"), statistics.get('total_records', 0), "#3498db"),
            ("️", self.lm.tr('metric_waste_type', "Atık Türü"), statistics.get('total_waste_types', 0), "#e74c3c"),
            ("", self.lm.tr('metric_active_targets', "Aktif Hedef"), statistics.get('active_targets', 0), "#f39c12"),
            ("", self.lm.tr('metric_active_projects', "Aktif Proje"), statistics.get('active_projects', 0), "#27ae60")
        ]

        for i, (icon, title, value, color) in enumerate(metrics_data):
            metric_card = tk.Frame(metrics_frame, bg=color, relief='solid', bd=1)
            metric_card.pack(side='left', fill='x', expand=True, padx=(0, 10) if i < 3 else (0, 0))

            # Metrik içeriği
            icon_label = tk.Label(metric_card, text=icon, font=('Segoe UI', 24),
                                 fg='white', bg=color)
            icon_label.pack(pady=(15, 5))

            value_label = tk.Label(metric_card, text=str(value), font=('Segoe UI', 20, 'bold'),
                                  fg='white', bg=color)
            value_label.pack()

            title_label = tk.Label(metric_card, text=title, font=('Segoe UI', 10),
                                  fg='white', bg=color)
            title_label.pack(pady=(5, 15))

        # Son atık kayıtları
        recent_frame = tk.LabelFrame(dashboard_frame, text=self.lm.tr('recent_waste_records', "Son Atık Kayıtları"),
                                    font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        recent_frame.pack(fill='both', expand=True, pady=(0, 20))

        # Treeview oluştur
        columns = (self.lm.tr('col_waste_code', 'Atık Kodu'), self.lm.tr('col_waste_name', 'Atık Adı'), self.lm.tr('col_amount', 'Miktar'), self.lm.tr('col_category', 'Kategori'), self.lm.tr('col_recycling_rate', 'Geri Dönüşüm Oranı'))
        self.recent_tree = ttk.Treeview(recent_frame, columns=columns, show='headings', height=8)

        for col in columns:
            self.recent_tree.heading(col, text=col)
            self.recent_tree.column(col, width=120)

        # Scrollbar
        scrollbar = ttk.Scrollbar(recent_frame, orient='vertical', command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=scrollbar.set)

        self.recent_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

        # Son kayıtları yükle
        recent_records = self.waste_manager.get_waste_records(self.company_id, '2024')[:10]
        for record in recent_records:
            self.recent_tree.insert('', 'end', values=(
                record.get('waste_code', ''),
                record.get('waste_name', ''),
                f"{record.get('quantity', 0):.2f} {record.get('unit', 'kg')}",
                record.get('waste_category', ''),
                f"%{record.get('recycling_rate', 0):.1f}"
            ))

        # Hızlı işlemler
        quick_actions_frame = tk.LabelFrame(dashboard_frame, text=self.lm.tr('quick_actions', "Hızlı İşlemler"),
                                           font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        quick_actions_frame.pack(fill='x')

        actions_frame = tk.Frame(quick_actions_frame, bg='white')
        actions_frame.pack(pady=15)

        quick_buttons = [
            (" " + self.lm.tr('btn_new_waste_record', "Yeni Atık Kaydı"), self.add_waste_record),
            (" " + self.lm.tr('btn_add_target', "Hedef Ekle"), self.add_reduction_target),
            (" " + self.lm.tr('btn_add_project', "Proje Ekle"), self.add_recycling_project),
            (" " + self.lm.tr('btn_calc_metrics', "Metrik Hesapla"), self.calculate_metrics)
        ]

        for i, (text, command) in enumerate(quick_buttons):
            btn = ttk.Button(actions_frame, text=text, style='Primary.TButton', command=command)
            btn.pack(side='left', padx=(0, 10) if i < 3 else (0, 0))

    def show_waste_records(self) -> None:
        """Atık kayıtları göster"""
        self.clear_content()
        self.update_menu_buttons(self.lm.tr('menu_waste_records', "Atık Kayıtları"))

        # Atık kayıtları içeriği
        records_frame = tk.Frame(self.content_area, bg='white')
        records_frame.pack(fill='both', expand=True)

        # Üst panel - Filtreler ve butonlar
        top_frame = tk.Frame(records_frame, bg='white')
        top_frame.pack(fill='x', pady=(0, 15))

        # Filtreler
        filters_frame = tk.Frame(top_frame, bg='white')
        filters_frame.pack(side='left', fill='x', expand=True)

        tk.Label(filters_frame, text=self.lm.tr('lbl_period', "Dönem:"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='white').pack(side='left', padx=(0, 5))

        self.period_var = tk.StringVar(value='2024')
        period_combo = ttk.Combobox(filters_frame, textvariable=self.period_var,
                                   values=['2023', '2024', '2025'], width=10)
        period_combo.pack(side='left', padx=(0, 15))

        tk.Label(filters_frame, text=self.lm.tr('lbl_category', "Kategori:"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='white').pack(side='left', padx=(0, 5))

        self.category_var = tk.StringVar(value=self.lm.tr('all', 'Tümü'))
        category_combo = ttk.Combobox(filters_frame, textvariable=self.category_var,
                                     values=[self.lm.tr('all', 'Tümü'), self.lm.tr('cat_organic', 'Organik'), self.lm.tr('cat_recycle', 'Geri Dönüşüm'), self.lm.tr('cat_hazardous', 'Tehlikeli'),
                                            self.lm.tr('cat_construction', 'İnşaat'), self.lm.tr('cat_textile', 'Tekstil'), self.lm.tr('cat_medical', 'Tıbbi'), self.lm.tr('cat_general', 'Genel')], width=12)
        category_combo.pack(side='left', padx=(0, 15))

        # Butonlar
        buttons_frame = tk.Frame(top_frame, bg='white')
        buttons_frame.pack(side='right')

        refresh_btn = ttk.Button(buttons_frame, text=" " + self.lm.tr('btn_refresh', "Yenile"), style='Primary.TButton', command=self.refresh_waste_records)
        refresh_btn.pack(side='left', padx=(0, 5))

        add_btn = ttk.Button(buttons_frame, text=" " + self.lm.tr('btn_new_record', "Yeni Kayıt"), style='Primary.TButton', command=self.add_waste_record)
        add_btn.pack(side='left')

        # Atık kayıtları tablosu
        table_frame = tk.Frame(records_frame, bg='white')
        table_frame.pack(fill='both', expand=True)

        columns = ('ID', self.lm.tr('col_waste_code', 'Atık Kodu'), self.lm.tr('col_waste_name', 'Atık Adı'), self.lm.tr('col_amount', 'Miktar'), self.lm.tr('col_unit', 'Birim'), self.lm.tr('col_category', 'Kategori'),
                  self.lm.tr('col_recycling_rate', 'Geri Dönüşüm Oranı'), self.lm.tr('col_disposal_method', 'Bertaraf Yöntemi'), self.lm.tr('col_cost', 'Maliyet'), self.lm.tr('col_carbon', 'Karbon'))
        self.records_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.records_tree.heading(col, text=col)
            self.records_tree.column(col, width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.records_tree.yview)
        self.records_tree.configure(yscrollcommand=scrollbar.set)

        self.records_tree.pack(side='left', fill='both', expand=True, padx=(0, 5))
        scrollbar.pack(side='right', fill='y')

        # Kayıtları yükle
        self.refresh_waste_records()

    def show_reduction_targets(self) -> None:
        """Azaltma hedefleri göster"""
        self.clear_content()
        self.update_menu_buttons(self.lm.tr('menu_reduction_targets', "Azaltma Hedefleri"))

        # Hedefler içeriği
        targets_frame = tk.Frame(self.content_area, bg='white')
        targets_frame.pack(fill='both', expand=True)

        # Üst panel
        top_frame = tk.Frame(targets_frame, bg='white')
        top_frame.pack(fill='x', pady=(0, 15))

        add_target_btn = ttk.Button(top_frame, text=" " + self.lm.tr('btn_new_target', "Yeni Hedef"), style='Primary.TButton', command=self.add_reduction_target)
        add_target_btn.pack(side='right')

        # Hedefler tablosu
        table_frame = tk.Frame(targets_frame, bg='white')
        table_frame.pack(fill='both', expand=True)

        columns = (self.lm.tr('col_target_name', 'Hedef Adı'), self.lm.tr('col_type', 'Türü'), self.lm.tr('col_category', 'Kategori'), self.lm.tr('col_start_year', 'Başlangıç Yılı'), self.lm.tr('col_target_year', 'Hedef Yılı'),
                  self.lm.tr('col_base_amount', 'Başlangıç Miktarı'), self.lm.tr('col_target_amount', 'Hedef Miktarı'), self.lm.tr('col_reduction_percent', 'Azaltma %'), self.lm.tr('col_status', 'Durum'))
        self.targets_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)

        for col in columns:
            self.targets_tree.heading(col, text=col)
            self.targets_tree.column(col, width=120)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.targets_tree.yview)
        self.targets_tree.configure(yscrollcommand=scrollbar.set)

        self.targets_tree.pack(side='left', fill='both', expand=True, padx=(0, 5))
        scrollbar.pack(side='right', fill='y')

        # Hedefleri yükle
        targets = self.waste_manager.get_waste_targets(self.company_id)
        for target in targets:
            self.targets_tree.insert('', 'end', values=(
                target.get('target_name', ''),
                target.get('target_type', ''),
                target.get('waste_category', ''),
                target.get('base_year', ''),
                target.get('target_year', ''),
                f"{target.get('base_quantity', 0):.2f}",
                f"{target.get('target_quantity', 0):.2f}",
                f"%{target.get('reduction_percentage', 0):.1f}",
                target.get('status', '')
            ))

    def show_recycling_projects(self) -> None:
        """Geri dönüşüm projeleri göster"""
        self.clear_content()
        self.update_menu_buttons(self.lm.tr('menu_recycling_projects', "Geri Dönüşüm Projeleri"))

        # Projeler içeriği
        projects_frame = tk.Frame(self.content_area, bg='white')
        projects_frame.pack(fill='both', expand=True)

        # Üst panel
        top_frame = tk.Frame(projects_frame, bg='white')
        top_frame.pack(fill='x', pady=(0, 15))

        add_project_btn = ttk.Button(top_frame, text=" " + self.lm.tr('btn_new_project', "Yeni Proje"), style='Primary.TButton',
                                     command=self.add_recycling_project)
        add_project_btn.pack(side='right')

        # Projeler tablosu
        table_frame = tk.Frame(projects_frame, bg='white')
        table_frame.pack(fill='both', expand=True)

        columns = (self.lm.tr('col_project_name', 'Proje Adı'), self.lm.tr('col_type', 'Türü'), self.lm.tr('col_waste_types', 'Atık Türleri'), self.lm.tr('col_start', 'Başlangıç'), self.lm.tr('col_end', 'Bitiş'),
                  self.lm.tr('col_status', 'Durum'), self.lm.tr('col_investment', 'Yatırım'), self.lm.tr('col_expected_savings', 'Beklenen Tasarruf'), self.lm.tr('col_current_rate', 'Mevcut Oran'), self.lm.tr('col_target_rate', 'Hedef Oran'))
        self.projects_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)

        for col in columns:
            self.projects_tree.heading(col, text=col)
            self.projects_tree.column(col, width=120)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.projects_tree.yview)
        self.projects_tree.configure(yscrollcommand=scrollbar.set)

        self.projects_tree.pack(side='left', fill='both', expand=True, padx=(0, 5))
        scrollbar.pack(side='right', fill='y')

        # Projeleri yükle
        projects = self.waste_manager.get_recycling_projects(self.company_id)
        for project in projects:
            self.projects_tree.insert('', 'end', values=(
                project.get('project_name', ''),
                project.get('project_type', ''),
                project.get('waste_types', ''),
                project.get('start_date', ''),
                project.get('end_date', ''),
                project.get('status', ''),
                f"{project.get('investment_amount', 0):.2f} TL",
                f"{project.get('expected_savings', 0):.2f} TL",
                f"%{project.get('current_recycling_rate', 0):.1f}",
                f"%{project.get('recycling_rate_target', 0):.1f}"
            ))

    def show_metrics(self) -> None:
        """Metrikler ve analiz göster"""
        self.clear_content()
        self.update_menu_buttons(self.lm.tr('menu_metrics_analysis', "Metrikler & Analiz"))

        # Metrikler içeriği
        metrics_frame = tk.Frame(self.content_area, bg='white')
        metrics_frame.pack(fill='both', expand=True)

        # Metrikleri hesapla
        metrics = self.waste_manager.calculate_waste_metrics(self.company_id, '2024')

        if metrics:
            # Metrik kartları
            metrics_cards_frame = tk.Frame(metrics_frame, bg='white')
            metrics_cards_frame.pack(fill='x', pady=(0, 20))

            metrics_data = [
                ("️", self.lm.tr('metric_total_waste', "Toplam Atık"), f"{metrics.get('total_waste_generated', 0):.2f} kg", "#e74c3c"),
                ("", self.lm.tr('metric_recycling_rate', "Geri Dönüşüm"), f"%{metrics.get('recycling_rate', 0):.1f}", "#27ae60"),
                ("", self.lm.tr('metric_reduction_rate', "Azaltma Oranı"), f"%{metrics.get('waste_reduction_rate', 0):.1f}", "#f39c12"),
                ("️", self.lm.tr('metric_circular_economy', "Döngüsel Ekonomi"), f"{metrics.get('circular_economy_index', 0):.1f}", "#3498db"),
                ("", self.lm.tr('metric_total_cost', "Toplam Maliyet"), f"{metrics.get('waste_cost', 0):.2f} TL", "#9b59b6"),
                ("", self.lm.tr('metric_carbon_footprint', "Karbon Ayak İzi"), f"{metrics.get('carbon_footprint', 0):.2f} kg CO2e", "#34495e")
            ]

            for i, (icon, title, value, color) in enumerate(metrics_data):
                metric_card = tk.Frame(metrics_cards_frame, bg=color, relief='solid', bd=1)
                metric_card.pack(side='left', fill='x', expand=True,
                               padx=(0, 10) if i < 5 else (0, 0))

                # Metrik içeriği
                icon_label = tk.Label(metric_card, text=icon, font=('Segoe UI', 20),
                                     fg='white', bg=color)
                icon_label.pack(pady=(10, 5))

                value_label = tk.Label(metric_card, text=value, font=('Segoe UI', 14, 'bold'),
                                      fg='white', bg=color)
                value_label.pack()

                title_label = tk.Label(metric_card, text=title, font=('Segoe UI', 9),
                                      fg='white', bg=color)
                title_label.pack(pady=(5, 10))

        # Analiz butonları
        analysis_frame = tk.LabelFrame(metrics_frame, text=self.lm.tr('analysis_tools', "Analiz Araçları"),
                                      font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        analysis_frame.pack(fill='x', pady=(0, 20))

        analysis_buttons_frame = tk.Frame(analysis_frame, bg='white')
        analysis_buttons_frame.pack(pady=15)

        analysis_buttons = [
            (" " + self.lm.tr('btn_carbon_analysis', "Karbon Analizi"), self.show_carbon_analysis),
            (" " + self.lm.tr('btn_economic_analysis', "Ekonomik Analiz"), self.show_economic_analysis),
            ("️ " + self.lm.tr('btn_circular_economy', "Döngüsel Ekonomi"), self.show_circular_economy_analysis),
            (" " + self.lm.tr('btn_sdg12_analysis', "SDG 12 Katkısı"), self.show_sdg12_analysis)
        ]

        for i, (text, command) in enumerate(analysis_buttons):
            btn = ttk.Button(analysis_buttons_frame, text=text, style='Primary.TButton',
                             command=command)
            btn.pack(side='left', padx=(0, 10) if i < 3 else (0, 0))

    def show_reports(self) -> None:
        """Raporlar göster"""
        self.clear_content()
        self.update_menu_buttons(self.lm.tr('menu_reports', "Raporlar"))

        # Raporlar içeriği
        reports_frame = tk.Frame(self.content_area, bg='white')
        reports_frame.pack(fill='both', expand=True)

        # Rapor oluşturma butonları
        create_frame = tk.LabelFrame(reports_frame, text=self.lm.tr('create_report', "Rapor Oluştur"),
                                    font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        create_frame.pack(fill='x', pady=(0, 20))

        create_buttons_frame = tk.Frame(create_frame, bg='white')
        create_buttons_frame.pack(pady=15)

        create_buttons = [
            (" " + self.lm.tr('btn_docx_report', "DOCX Raporu"), lambda: self.generate_report('DOCX')),
            (" " + self.lm.tr('btn_excel_report', "Excel Raporu"), lambda: self.generate_report('Excel')),
            (" " + self.lm.tr('btn_csv_report', "CSV Raporu"), lambda: self.generate_report('CSV'))
        ]

        for i, (text, command) in enumerate(create_buttons):
            btn = ttk.Button(create_buttons_frame, text=text, style='Primary.TButton',
                             command=command)
            btn.pack(side='left', padx=(0, 15) if i < 2 else (0, 0))

        preview_buttons_frame = tk.Frame(create_frame, bg='white')
        preview_buttons_frame.pack(pady=(0, 10))
        ttk.Button(preview_buttons_frame, text=" " + self.lm.tr('btn_preview_exit', 'Önizleme ve Çıkışlar'), style='Primary.TButton', command=self._open_preview_window).pack(side='left', padx=5)
        ttk.Button(preview_buttons_frame, text=" " + self.lm.tr('btn_open_report', 'Raporu Aç'), style='Primary.TButton', command=self._open_last_report).pack(side='left', padx=5)

        # Mevcut raporlar
        existing_frame = tk.LabelFrame(reports_frame, text=self.lm.tr('lbl_existing_reports', "Mevcut Raporlar"),
                                      font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        existing_frame.pack(fill='both', expand=True)

        # Raporlar tablosu
        table_frame = tk.Frame(existing_frame, bg='white')
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = (self.lm.tr('col_report_name', 'Rapor Adı'), self.lm.tr('col_type', 'Türü'), self.lm.tr('col_period', 'Dönem'), self.lm.tr('col_created_at', 'Oluşturulma Tarihi'), self.lm.tr('col_file_path', 'Dosya Yolu'))
        self.reports_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)

        for col in columns:
            self.reports_tree.heading(col, text=col)
            self.reports_tree.column(col, width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.reports_tree.yview)
        self.reports_tree.configure(yscrollcommand=scrollbar.set)

        self.reports_tree.pack(side='left', fill='both', expand=True, padx=(0, 5))
        scrollbar.pack(side='right', fill='y')

        # Raporları yükle
        self.refresh_reports()

    def show_settings(self) -> None:
        """Ayarlar göster"""
        self.clear_content()
        self.update_menu_buttons(self.lm.tr('menu_settings', "Ayarlar"))

        # Ayarlar içeriği
        settings_frame = tk.Frame(self.content_area, bg='white')
        settings_frame.pack(fill='both', expand=True)

        # Genel ayarlar
        general_frame = tk.LabelFrame(settings_frame, text=self.lm.tr('lbl_general_settings', "Genel Ayarlar"),
                                     font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        general_frame.pack(fill='x', pady=(0, 20))

        general_content = tk.Frame(general_frame, bg='white')
        general_content.pack(pady=15)

        # Varsayılan dönem
        tk.Label(general_content, text=self.lm.tr('lbl_default_period', "Varsayılan Dönem:"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='white').pack(side='left', padx=(0, 10))

        self.default_period_var = tk.StringVar(value='2024')
        period_combo = ttk.Combobox(general_content, textvariable=self.default_period_var,
                                   values=['2023', '2024', '2025'], width=10)
        period_combo.pack(side='left', padx=(0, 20))

        # Varsayılan birim
        tk.Label(general_content, text=self.lm.tr('lbl_default_unit', "Varsayılan Birim:"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='white').pack(side='left', padx=(0, 10))

        self.default_unit_var = tk.StringVar(value='kg')
        unit_combo = ttk.Combobox(general_content, textvariable=self.default_unit_var,
                                 values=['kg', 'ton', 'g', 'm3', 'l'], width=10)
        unit_combo.pack(side='left', padx=(0, 20))

        # Kaydet butonu
        save_btn = ttk.Button(general_content, text=" " + self.lm.tr('btn_save', "Kaydet"), style='Primary.TButton',
                              command=self.save_settings)
        save_btn.pack(side='left')

        # Atık türleri yönetimi
        types_frame = tk.LabelFrame(settings_frame, text=self.lm.tr('lbl_waste_types_management', "Atık Türleri Yönetimi"),
                                   font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        types_frame.pack(fill='both', expand=True)

        types_content = tk.Frame(types_frame, bg='white')
        types_content.pack(pady=15)

        # Atık türleri tablosu
        types_table_frame = tk.Frame(types_content, bg='white')
        types_table_frame.pack(fill='both', expand=True)

        columns = (self.lm.tr('col_waste_code', 'Atık Kodu'), self.lm.tr('col_waste_name', 'Atık Adı'), self.lm.tr('col_category', 'Kategori'), self.lm.tr('col_hazard_level', 'Tehlikeli Seviye'), self.lm.tr('col_recycling_potential', 'Geri Dönüşüm Potansiyeli'))
        self.types_tree = ttk.Treeview(types_table_frame, columns=columns, show='headings', height=8)

        for col in columns:
            self.types_tree.heading(col, text=col)
            self.types_tree.column(col, width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(types_table_frame, orient='vertical', command=self.types_tree.yview)
        self.types_tree.configure(yscrollcommand=scrollbar.set)

        self.types_tree.pack(side='left', fill='both', expand=True, padx=(0, 5))
        scrollbar.pack(side='right', fill='y')

        # Atık türlerini yükle
        self.load_waste_types()

    def clear_content(self) -> None:
        """İçeriği temizle"""
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def update_menu_buttons(self, active_button) -> None:
        """Menü butonlarını güncelle"""
        for text, btn in self.menu_buttons.items():
            if text == active_button:
                try:
                    btn.config(style='Primary.TButton')
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
            else:
                try:
                    btn.config(style='TButton')
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")

    def load_data(self) -> None:
        """Verileri yükle"""
        pass

    def refresh_waste_records(self) -> None:
        """Atık kayıtlarını yenile"""
        # Tabloyu temizle
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)

        # Filtreleri al
        period = self.period_var.get()
        category = self.category_var.get()

        # Kayıtları al
        records = self.waste_manager.get_waste_records(self.company_id, period)

        # Filtrele
        if category != 'Tümü':
            records = [r for r in records if r.get('waste_category') == category]

        # Tabloya ekle
        for record in records:
            self.records_tree.insert('', 'end', values=(
                record.get('id', ''),
                record.get('waste_code', ''),
                record.get('waste_name', ''),
                f"{record.get('quantity', 0):.2f}",
                record.get('unit', ''),
                record.get('waste_category', ''),
                f"%{record.get('recycling_rate', 0):.1f}",
                record.get('disposal_method', ''),
                f"{record.get('disposal_cost', 0):.2f} TL",
                f"{record.get('carbon_footprint', 0):.2f} kg CO2e"
            ))

    def add_waste_record(self) -> None:
        """Yeni atık kaydı ekle"""
        self.show_waste_record_form()

    def add_reduction_target(self) -> None:
        """Yeni azaltma hedefi ekle"""
        self.show_reduction_target_form()

    def add_recycling_project(self) -> None:
        """Yeni geri dönüşüm projesi ekle"""
        self.show_recycling_project_form()

    def calculate_metrics(self) -> None:
        """Metrikleri hesapla"""
        metrics = self.waste_manager.calculate_waste_metrics(self.company_id, '2024')
        if metrics:
            self.waste_manager.save_waste_metrics(self.company_id, '2024', metrics)
            messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('metrics_calculated_saved', "Metrikler hesaplandı ve kaydedildi!"))
        else:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('metrics_calc_error', "Metrikler hesaplanamadı!"))

    def generate_report(self, report_type) -> None:
        """Rapor oluştur"""
        period = '2024'

        try:
            # Rapor oluşturma progress dialog
            progress_window = tk.Toplevel(self.parent)
            progress_window.title(" " + self.lm.tr('title_creating_report', "Rapor Oluşturuluyor"))
            progress_window.geometry("400x150")
            progress_window.configure(bg='#f8f9fa')
            progress_window.grab_set()

            # Progress frame
            progress_frame = tk.Frame(progress_window, bg='#f8f9fa')
            progress_frame.pack(expand=True)

            # Progress label
            progress_label = tk.Label(progress_frame, text=f"{report_type} {self.lm.tr('msg_creating_report', 'raporu oluşturuluyor...')}",
                                    font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#f8f9fa')
            progress_label.pack(pady=20)

            # Progress bar
            progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
            progress_bar.pack(pady=10, padx=20, fill='x')
            progress_bar.start()

            # Update window
            progress_window.update()

            filepath = None

            if report_type == 'DOCX':
                filepath = self.waste_reporting.generate_waste_management_report(
                    self.company_id, period, include_details=True)
            elif report_type == 'Excel':
                filepath = self.waste_reporting.generate_excel_report(self.company_id, period)
            elif report_type == 'CSV':
                filepath = self.waste_reporting.generate_csv_report(self.company_id, period)

            # Close progress window
            progress_window.destroy()

            if filepath:
                # Rapor bilgilerini veritabanına kaydet
                self.save_report_to_db(report_type, period, filepath)
                self.last_waste_report_path = filepath

                messagebox.showinfo(self.lm.tr('success', "Başarılı"),
                    f"{report_type} {self.lm.tr('report_created_success', 'raporu başarıyla oluşturuldu!')}\n\n"
                    f"{self.lm.tr('file', 'Dosya')}: {filepath}\n\n"
                    f"{self.lm.tr('report_view_hint', "Rapor 'Mevcut Raporlar' bölümünde görüntülenebilir.")}")

                # Raporlar tablosunu yenile
                if hasattr(self, 'reports_tree'):
                    self.refresh_reports()
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), f"{report_type} {self.lm.tr('report_create_error', 'raporu oluşturulamadı!')}")

        except Exception as e:
            if 'progress_window' in locals():
                progress_window.destroy()
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('report_create_exception', 'Rapor oluşturma sırasında hata')}: {str(e)}")

    def _open_preview_window(self) -> None:
        try:
            win = tk.Toplevel(self.parent)
            win.title(self.lm.tr('title_preview', "Atık Raporu Önizleme"))
            win.geometry("900x600")
            top = tk.Frame(win, bg='white')
            top.pack(fill='x', padx=10, pady=6)
            ttk.Button(top, text=self.lm.tr('btn_close', 'Kapat'), style='Primary.TButton', command=win.destroy).pack(side='left')
            controls = tk.Frame(win, bg='white')
            controls.pack(fill='x', padx=10, pady=6)
            tk.Label(controls, text=self.lm.tr('lbl_period', 'Dönem:'), bg='white').pack(side='left')
            self.preview_period_var = tk.StringVar(value='2024')
            entry = tk.Entry(controls, textvariable=self.preview_period_var, width=12)
            entry.pack(side='left', padx=8)
            self.waste_report_text = tk.Text(win, height=20, wrap='word')
            r_scroll = ttk.Scrollbar(win, orient='vertical', command=self.waste_report_text.yview)
            self.waste_report_text.configure(yscrollcommand=r_scroll.set)
            self.waste_report_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
            r_scroll.pack(side='right', fill='y', pady=10)
            tools = tk.Frame(win, bg='white')
            tools.pack(fill='x', padx=10, pady=(0,10))
            ttk.Button(tools, text=self.lm.tr('btn_fill_preview', 'Önizlemeyi Doldur'), style='Primary.TButton', command=self._fill_preview_text).pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('btn_open', 'Aç'), style='Primary.TButton', command=self._open_last_report).pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('btn_save_txt', 'Kaydet (.txt)'), style='Primary.TButton', command=self._save_preview_text).pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('btn_print', 'Yazdır'), style='Primary.TButton', command=self._print_preview_text).pack(side='left', padx=4)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('msg_preview_error', 'Önizleme penceresi hatası')}: {e}")

    def _fill_preview_text(self) -> None:
        try:
            period = self.preview_period_var.get().strip() or '2024'
            metrics = self.waste_manager.calculate_waste_metrics(self.company_id, period)
            if not metrics:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('msg_metrics_not_found', "Metrikler bulunamadı"))
                return
            self.waste_report_text.delete('1.0', tk.END)
            self.waste_report_text.insert(tk.END, f"{self.lm.tr('report_title', 'ATIK YÖNETİMİ RAPORU')}\n")
            self.waste_report_text.insert(tk.END, f"{self.lm.tr('report_period', 'Dönem:')} {period}\n")
            self.waste_report_text.insert(tk.END, f"{self.lm.tr('report_total_waste', 'Toplam Atık:')} {metrics.get('total_waste',0):.2f} kg\n")
            self.waste_report_text.insert(tk.END, f"{self.lm.tr('report_recycling_rate', 'Geri Dönüşüm Oranı:')} %{metrics.get('recycling_rate',0)*100:.1f}\n")
            self.waste_report_text.insert(tk.END, f"{self.lm.tr('report_carbon_footprint', 'Karbon Ayak İzi:')} {metrics.get('carbon_footprint',0):.2f} kg CO2e\n")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('msg_preview_error', 'Önizleme hatası')}: {e}")

    def _save_preview_text(self) -> None:
        try:
            content = self.waste_report_text.get('1.0', tk.END)
            if not content.strip():
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('msg_preview_empty', "Önizleme içeriği boş"))
                return
            out = filedialog.asksaveasfilename(
                title=self.lm.tr('save_report', "Raporu Kaydet"),
                defaultextension='.txt',
                filetypes=[(self.lm.tr('file_text', 'Metin'),'*.txt')]
            )
            if not out:
                return
            with open(out, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo(self.lm.tr('info', "Bilgi"), f"{self.lm.tr('msg_preview_saved', 'Önizleme kaydedildi')}: {out}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('msg_save_error', 'Kaydetme hatası')}: {e}")

    def _print_preview_text(self) -> None:
        try:
            import tempfile
            content = self.waste_report_text.get('1.0', tk.END)
            if not content.strip():
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('msg_preview_empty', "Önizleme içeriği boş"))
                return
            tmp = os.path.join(tempfile.gettempdir(), 'waste_preview.txt')
            with open(tmp, 'w', encoding='utf-8') as f:
                f.write(content)
            try:
                os.startfile(tmp, 'print')
                messagebox.showinfo(self.lm.tr('info', "Bilgi"), self.lm.tr('msg_printing_started', "Yazdırma başlatıldı"))
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('msg_printing_error', 'Yazdırma hatası')}: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('msg_print_prep_error', 'Yazdırmaya hazırlık hatası')}: {e}")

    def _open_last_report(self) -> None:
        try:
            path = getattr(self, 'last_waste_report_path', None)
            if path and os.path.exists(path):
                os.startfile(path)
            else:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('msg_report_not_found', "Açılacak rapor bulunamadı"))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('msg_open_error', 'Açma hatası')}: {e}")

    def save_report_to_db(self, report_type, period, filepath) -> None:
        """Rapor bilgilerini veritabanına kaydet"""
        try:
            conn = self.waste_manager.get_connection()
            cursor = conn.cursor()

            # Rapor adı oluştur
            report_name = f"{self.lm.tr('waste_report_title_prefix', 'Atık Yönetimi')} {report_type} {self.lm.tr('report_suffix', 'Raporu')} - {period}"

            cursor.execute("""
                INSERT INTO waste_reports 
                (company_id, report_name, report_type, period, file_path, generated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (self.company_id, report_name, report_type, period, filepath))

            conn.commit()
            conn.close()
            logging.info(f"[OK] Rapor veritabanına kaydedildi: {report_name}")

        except Exception as e:
            logging.error(f"[HATA] Rapor veritabanına kaydedilemedi: {e}")

    def refresh_reports(self) -> None:
        """Raporlar tablosunu yenile"""
        if hasattr(self, 'reports_tree'):
            # Tabloyu temizle
            for item in self.reports_tree.get_children():
                self.reports_tree.delete(item)

            # Raporları al ve tabloya ekle
            reports = self.get_waste_reports()
            for report in reports:
                self.reports_tree.insert('', 'end', values=(
                    report.get('report_name', ''),
                    report.get('report_type', ''),
                    report.get('period', ''),
                    report.get('generated_at', '')[:10] if report.get('generated_at') else '',
                    report.get('file_path', '')
                ))

    def get_waste_reports(self) -> None:
        """Atık yönetimi raporlarını getir"""
        try:
            conn = self.waste_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM waste_reports 
                WHERE company_id = ?
                ORDER BY generated_at DESC
            """, (self.company_id,))

            columns = [description[0] for description in cursor.description]
            results = []

            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            conn.close()
            return results

        except Exception as e:
            logging.error(f"[HATA] Raporlar getirilirken hata: {e}")
            return []

    def save_settings(self) -> None:
        """Ayarları kaydet"""
        messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('msg_settings_saved', "Ayarlar kaydedildi!"))

    def load_waste_types(self) -> None:
        """Atık türlerini yükle"""
        # Atık türleri tablosunu temizle
        for item in self.types_tree.get_children():
            self.types_tree.delete(item)

        # Basit atık türleri listesi
        waste_types = [
            ('ORGANIC-001', self.lm.tr('waste_organic_kitchen', 'Organik Mutfak Atığı'), self.lm.tr('cat_organic', 'Organik'), self.lm.tr('level_non_hazardous', 'Non-hazardous'), self.lm.tr('level_high', 'High')),
            ('RECYCLE-001', self.lm.tr('waste_paper_cardboard', 'Kağıt ve Karton'), self.lm.tr('cat_recycle', 'Geri Dönüşüm'), self.lm.tr('level_non_hazardous', 'Non-hazardous'), self.lm.tr('level_high', 'High')),
            ('RECYCLE-002', self.lm.tr('waste_plastic', 'Plastik'), self.lm.tr('cat_recycle', 'Geri Dönüşüm'), self.lm.tr('level_non_hazardous', 'Non-hazardous'), self.lm.tr('level_medium', 'Medium')),
            ('HAZARD-001', self.lm.tr('waste_chemical', 'Kimyasal Atık'), self.lm.tr('cat_hazardous', 'Tehlikeli'), self.lm.tr('level_hazardous', 'Hazardous'), self.lm.tr('level_low', 'Low')),
            ('CONSTRUCTION-001', self.lm.tr('waste_concrete', 'Beton Atığı'), self.lm.tr('cat_construction', 'İnşaat'), self.lm.tr('level_non_hazardous', 'Non-hazardous'), self.lm.tr('level_high', 'High'))
        ]

        for waste_type in waste_types:
            self.types_tree.insert('', 'end', values=waste_type)

    def show_carbon_analysis(self) -> None:
        """Karbon analizi göster"""
        self.show_analysis_window(self.lm.tr('title_carbon_analysis', "Karbon Analizi"), self.get_carbon_analysis_data())

    def show_economic_analysis(self) -> None:
        """Ekonomik analiz göster"""
        self.show_analysis_window(self.lm.tr('title_economic_analysis', "Ekonomik Analiz"), self.get_economic_analysis_data())

    def show_circular_economy_analysis(self) -> None:
        """Döngüsel ekonomi analizi göster"""
        self.show_analysis_window(self.lm.tr('title_circular_economy', "Döngüsel Ekonomi Analizi"), self.get_circular_economy_analysis_data())

    def show_sdg12_analysis(self) -> None:
        """SDG 12 analizi göster"""
        self.show_analysis_window(self.lm.tr('title_sdg12_contribution', "SDG 12 Katkısı"), self.get_sdg12_analysis_data())

    def show_analysis_window(self, title, data) -> None:
        """Analiz penceresi göster"""
        # Analiz penceresi oluştur
        analysis_window = tk.Toplevel(self.parent)
        analysis_window.title(f" {title}")
        analysis_window.geometry("800x600")
        analysis_window.configure(bg='#f8f9fa')
        analysis_window.grab_set()

        # Pencereyi merkeze al
        analysis_window.transient(self.parent)
        analysis_window.focus_force()

        # Başlık
        header_frame = tk.Frame(analysis_window, bg='#3498db', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text=f" {title}",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#3498db')
        title_label.pack(expand=True)

        # Ana içerik
        main_frame = tk.Frame(analysis_window, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Metrik kartları
        metrics_frame = tk.Frame(main_frame, bg='#f8f9fa')
        metrics_frame.pack(fill='x', pady=(0, 20))

        for i, (icon, title_text, value, color) in enumerate(data.get('metrics', [])):
            metric_card = tk.Frame(metrics_frame, bg=color, relief='solid', bd=1)
            metric_card.pack(side='left', fill='x', expand=True,
                           padx=(0, 10) if i < len(data.get('metrics', [])) - 1 else (0, 0))

            # Metrik içeriği
            icon_label = tk.Label(metric_card, text=icon, font=('Segoe UI', 20),
                                 fg='white', bg=color)
            icon_label.pack(pady=(10, 5))

            value_label = tk.Label(metric_card, text=value, font=('Segoe UI', 14, 'bold'),
                                  fg='white', bg=color)
            value_label.pack()

            title_label = tk.Label(metric_card, text=title_text, font=('Segoe UI', 9),
                                  fg='white', bg=color)
            title_label.pack(pady=(5, 10))

        # Detaylı analiz
        if data.get('details'):
            details_frame = tk.LabelFrame(main_frame, text=self.lm.tr('lbl_detailed_analysis', "Detaylı Analiz"),
                                        font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
            details_frame.pack(fill='both', expand=True)

            # Text widget for detailed analysis
            text_widget = tk.Text(details_frame, font=('Segoe UI', 11), wrap='word',
                                 bg='white', fg='#2c3e50', relief='flat')
            scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)

            text_widget.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            scrollbar.pack(side="right", fill="y", pady=10)

            # Analiz detaylarını ekle
            for detail in data['details']:
                text_widget.insert('end', f"• {detail}\n")

            text_widget.config(state='disabled')

        # Kapat butonu
        close_btn = ttk.Button(main_frame, text=" " + self.lm.tr('btn_close', "Kapat"), style='Primary.TButton',
                               command=analysis_window.destroy)
        close_btn.pack(pady=(20, 0))

    def get_carbon_analysis_data(self) -> None:
        """Karbon analizi verilerini al"""
        metrics = self.waste_manager.calculate_waste_metrics(self.company_id, '2024')

        return {
            'metrics': [
                ("", self.lm.tr('title_total_carbon_footprint', "Toplam Karbon Ayak İzi"), f"{metrics.get('carbon_footprint', 0):.2f} kg CO2e", "#e74c3c"),
                ("️", self.lm.tr('title_recycling_rate', "Geri Dönüşüm Oranı"), f"%{metrics.get('recycling_rate', 0):.1f}", "#27ae60"),
                ("", self.lm.tr('title_carbon_reduction', "Karbon Azaltma"), f"%{metrics.get('waste_reduction_rate', 0):.1f}", "#f39c12"),
                ("", self.lm.tr('title_sustainability_index', "Sürdürülebilirlik İndeksi"), f"{metrics.get('circular_economy_index', 0):.1f}/100", "#3498db")
            ],
            'details': [
                f"{self.lm.tr('detail_total_waste', 'Toplam atık üretimi:')} {metrics.get('total_waste_generated', 0):.2f} kg",
                f"{self.lm.tr('detail_recycled_waste', 'Geri dönüştürülen atık:')} {metrics.get('total_waste_recycled', 0):.2f} kg",
                f"{self.lm.tr('detail_carbon_reduction_potential', 'Karbon ayak izi azaltma potansiyeli:')} %{(100 - metrics.get('recycling_rate', 0)):.1f}",
                f"{self.lm.tr('detail_recommendations', 'Öneriler:')} {self.lm.tr('rec_compost_recycle', 'Organik atık kompostlaştırma, plastik geri dönüşüm artırma')}",
                f"{self.lm.tr('detail_goal', 'Hedef:')} {self.lm.tr('goal_carbon_reduction', '2025 yılına kadar karbon ayak izini %25 azaltma')}"
            ]
        }

    def get_economic_analysis_data(self) -> None:
        """Ekonomik analiz verilerini al"""
        metrics = self.waste_manager.calculate_waste_metrics(self.company_id, '2024')

        return {
            'metrics': [
                ("", self.lm.tr('title_total_cost', "Toplam Maliyet"), f"{metrics.get('waste_cost', 0):.2f} TL", "#f39c12"),
                ("", self.lm.tr('title_savings_potential', "Tasarruf Potansiyeli"), f"%{metrics.get('recycling_rate', 0) * 2:.1f}", "#27ae60"),
                ("", self.lm.tr('title_roi_potential', "ROI Potansiyeli"), f"%{(metrics.get('recycling_rate', 0) * 3):.1f}", "#3498db"),
                ("", self.lm.tr('title_economic_impact', "Ekonomik Etki"), f"{metrics.get('circular_economy_index', 0):.1f}/100", "#9b59b6")
            ],
            'details': [
                f"{self.lm.tr('detail_total_cost', 'Atık yönetimi toplam maliyeti:')} {metrics.get('waste_cost', 0):.2f} TL",
                f"{self.lm.tr('detail_savings_potential', 'Geri dönüşüm oranı artırılarak tasarruf potansiyeli:')} %{metrics.get('recycling_rate', 0) * 2:.1f}",
                f"{self.lm.tr('detail_recommendations', 'Öneriler:')} {self.lm.tr('rec_projects_strategies', 'Geri dönüşüm projeleri, atık azaltma stratejileri')}",
                f"{self.lm.tr('detail_investment_recommendations', 'Yatırım önerileri:')} {self.lm.tr('rec_facilities_equipment', 'Kompost tesisleri, geri dönüşüm ekipmanları')}",
                f"{self.lm.tr('detail_goal', 'Hedef:')} {self.lm.tr('goal_roi_increase', '3 yıl içinde ROI %150 artırma')}"
            ]
        }

    def get_circular_economy_analysis_data(self) -> None:
        """Döngüsel ekonomi analizi verilerini al"""
        metrics = self.waste_manager.calculate_waste_metrics(self.company_id, '2024')

        return {
            'metrics': [
                ("️", self.lm.tr('title_circular_economy_index', "Döngüsel Ekonomi İndeksi"), f"{metrics.get('circular_economy_index', 0):.1f}/100", "#27ae60"),
                ("", self.lm.tr('title_resource_efficiency', "Kaynak Verimliliği"), f"%{metrics.get('recycling_rate', 0):.1f}", "#3498db"),
                ("️", self.lm.tr('title_recycling_rate', "Geri Dönüşüm Oranı"), f"%{metrics.get('recycling_rate', 0):.1f}", "#2ecc71"),
                ("", self.lm.tr('title_sustainability', "Sürdürülebilirlik"), f"{metrics.get('circular_economy_index', 0):.1f}/100", "#16a085")
            ],
            'details': [
                f"{self.lm.tr('detail_circular_economy_index', 'Döngüsel ekonomi indeksi:')} {metrics.get('circular_economy_index', 0):.1f}/100",
                f"{self.lm.tr('detail_recycling_rate', 'Geri dönüşüm oranı:')} %{metrics.get('recycling_rate', 0):.1f}",
                f"{self.lm.tr('detail_waste_reduction_rate', 'Atık azaltma oranı:')} %{metrics.get('waste_reduction_rate', 0):.1f}",
                f"{self.lm.tr('detail_circular_principles', 'Döngüsel ekonomi prensipleri:')} Reduce, Reuse, Recycle",
                f"{self.lm.tr('detail_goal', 'Hedef:')} {self.lm.tr('goal_circular_index', '2030 yılına kadar %80 döngüsel ekonomi indeksi')}"
            ]
        }

    def get_sdg12_analysis_data(self) -> None:
        """SDG 12 analizi verilerini al"""
        metrics = self.waste_manager.calculate_waste_metrics(self.company_id, '2024')

        return {
            'metrics': [
                ("", self.lm.tr('title_sdg12_progress', "SDG 12 İlerleme"), f"{metrics.get('circular_economy_index', 0):.1f}/100", "#27ae60"),
                ("️", self.lm.tr('title_sustainable_production', "Sürdürülebilir Üretim"), f"%{metrics.get('recycling_rate', 0):.1f}", "#3498db"),
                ("", self.lm.tr('title_responsible_consumption', "Sorumlu Tüketim"), f"%{metrics.get('waste_reduction_rate', 0):.1f}", "#e74c3c"),
                ("", self.lm.tr('title_goal_alignment', "Hedef Uyumu"), f"{metrics.get('circular_economy_index', 0):.1f}/100", "#f39c12")
            ],
            'details': [
                f"SDG 12: {self.lm.tr('sdg12_title', 'Sorumlu Üretim ve Tüketim')}",
                f"{self.lm.tr('detail_waste_reduction_progress', 'Atık azaltma hedefi ilerlemesi:')} %{metrics.get('waste_reduction_rate', 0):.1f}",
                f"{self.lm.tr('detail_recycling_progress', 'Geri dönüşüm hedefi ilerlemesi:')} %{metrics.get('recycling_rate', 0):.1f}",
                f"{self.lm.tr('detail_sdg12_subgoals', 'SDG 12 alt hedefleri:')} 12.3, 12.4, 12.5",
                f"{self.lm.tr('detail_goal', 'Hedef:')} {self.lm.tr('goal_zero_waste', '2030 yılına kadar sıfır atık hedefine ulaşma')}"
            ]
        }

    def show_waste_record_form(self) -> None:
        """Atık kaydı ekleme formunu göster"""
        # Form penceresi oluştur
        form_window = tk.Toplevel(self.parent)
        form_window.title(" " + self.lm.tr('title_new_waste_record', "Yeni Atık Kaydı"))
        form_window.geometry("600x700")
        form_window.configure(bg='#f8f9fa')
        form_window.grab_set()

        # Pencereyi merkeze al
        form_window.transient(self.parent)
        form_window.focus_force()

        # Başlık
        header_frame = tk.Frame(form_window, bg='#27ae60', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text=" " + self.lm.tr('title_add_waste_record', "Yeni Atık Kaydı Ekle"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#27ae60')
        title_label.pack(expand=True)

        # Ana form alanı
        main_frame = tk.Frame(form_window, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Scrollable frame
        canvas = tk.Canvas(main_frame, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f8f9fa')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Form değişkenleri
        self.form_vars = {}

        # Form alanları
        form_fields = [
            (self.lm.tr('col_waste_code', "Atık Kodu"), "waste_code", "text", True, self.lm.tr('placeholder_waste_code', "Örn: ORGANIC-001")),
            (self.lm.tr('col_waste_name', "Atık Adı"), "waste_name", "text", True, self.lm.tr('placeholder_waste_name', "Örn: Organik Mutfak Atığı")),
            (self.lm.tr('col_category', "Kategori"), "waste_category", "combo", True, [
                self.lm.tr('cat_organic', "Organik"), 
                self.lm.tr('cat_recycle', "Geri Dönüşüm"), 
                self.lm.tr('cat_hazardous', "Tehlikeli"), 
                self.lm.tr('cat_construction', "İnşaat"), 
                self.lm.tr('cat_textile', "Tekstil"), 
                self.lm.tr('cat_medical', "Tıbbi"), 
                self.lm.tr('cat_general', "Genel")
            ]),
            (self.lm.tr('col_amount', "Miktar"), "quantity", "number", True, "0.00"),
            (self.lm.tr('col_unit', "Birim"), "unit", "combo", True, ["kg", "ton", "g", "m3", "l"]),
            (self.lm.tr('lbl_hazard_level', "Tehlikeli Seviye"), "hazard_level", "combo", True, [
                self.lm.tr('level_non_hazardous', "Non-hazardous"), 
                self.lm.tr('level_hazardous', "Hazardous"), 
                self.lm.tr('level_special', "Special")
            ]),
            (self.lm.tr('col_recycling_rate', "Geri Dönüşüm Oranı") + " (%)", "recycling_rate", "number", False, "0"),
            (self.lm.tr('col_disposal_method', "Bertaraf Yöntemi"), "disposal_method", "combo", False, [
                self.lm.tr('method_recycling', "Geri Dönüşüm"), 
                self.lm.tr('method_incineration', "Yakma"), 
                self.lm.tr('method_landfill', "Depolama"), 
                self.lm.tr('method_compost', "Kompost"), 
                self.lm.tr('method_other', "Diğer")
            ]),
            (self.lm.tr('col_cost', "Maliyet") + " (TL)", "disposal_cost", "number", False, "0.00"),
            (self.lm.tr('lbl_carbon_footprint', "Karbon Ayak İzi (kg CO2e)"), "carbon_footprint", "number", False, "0.00"),
            (self.lm.tr('lbl_invoice_date', "Fatura Tarihi"), "invoice_date", "date", False, ""),
            (self.lm.tr('lbl_due_date', "Son Ödeme Tarihi"), "due_date", "date", False, ""),
            (self.lm.tr('lbl_supplier', "Tedarikçi Firma"), "supplier", "text", False, ""),
            (self.lm.tr('lbl_record_date', "Kayıt Tarihi"), "record_date", "date", True, datetime.now().strftime("%Y-%m-%d")),
            (self.lm.tr('lbl_responsible_person', "Sorumlu Kişi"), "responsible_person", "text", False, ""),
            (self.lm.tr('lbl_notes', "Notlar"), "notes", "textarea", False, "")
        ]

        # Form alanlarını oluştur
        for i, (label_text, field_name, field_type, required, default_value) in enumerate(form_fields):
            # Alan container
            field_frame = tk.Frame(scrollable_frame, bg='white', relief='solid', bd=1)
            field_frame.pack(fill='x', pady=5)

            # Label
            label = tk.Label(field_frame, text=label_text + (" *" if required else ""),
                           font=('Segoe UI', 10, 'bold'), fg='#2c3e50', bg='white')
            label.pack(anchor='w', padx=10, pady=(10, 5))

            # Input field
            if field_type == "text":
                var = tk.StringVar(value=default_value)
                entry = tk.Entry(field_frame, textvariable=var, font=('Segoe UI', 11),
                               relief='solid', bd=1, width=50)
                entry.pack(padx=10, pady=(0, 10), fill='x')

            elif field_type == "number":
                var = tk.StringVar(value=default_value)
                entry = tk.Entry(field_frame, textvariable=var, font=('Segoe UI', 11),
                               relief='solid', bd=1, width=50)
                entry.pack(padx=10, pady=(0, 10), fill='x')

            elif field_type == "date":
                var = tk.StringVar(value=default_value)
                entry = tk.Entry(field_frame, textvariable=var, font=('Segoe UI', 11),
                               relief='solid', bd=1, width=50)
                entry.pack(padx=10, pady=(0, 10), fill='x')

            elif field_type == "combo":
                var = tk.StringVar(value=default_value[0] if isinstance(default_value, list) else "")
                combo = ttk.Combobox(field_frame, textvariable=var, values=default_value,
                                   font=('Segoe UI', 11), width=47)
                combo.pack(padx=10, pady=(0, 10), fill='x')

            elif field_type == "textarea":
                var = tk.StringVar(value=default_value)
                text_area = tk.Text(field_frame, font=('Segoe UI', 11), height=3,
                                  relief='solid', bd=1, wrap='word')
                text_area.pack(padx=10, pady=(0, 10), fill='x')
                text_area.insert('1.0', default_value)

            self.form_vars[field_name] = var if field_type != "textarea" else text_area

        # Canvas ve scrollbar'ı pack et
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Butonlar
        button_frame = tk.Frame(form_window, bg='#f8f9fa', height=60)
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        button_frame.pack_propagate(False)

        # Kaydet butonu
        save_btn = ttk.Button(button_frame, text=" " + self.lm.tr('btn_save', "Kaydet"), style='Primary.TButton',
                              command=lambda: self.save_waste_record(form_window))
        save_btn.pack(side='left')

        # İptal butonu
        cancel_btn = ttk.Button(button_frame, text=" " + self.lm.tr('btn_cancel', "İptal"), style='Primary.TButton',
                                command=form_window.destroy)
        cancel_btn.pack(side='right')

        # Temizle butonu
        clear_btn = ttk.Button(button_frame, text="️ " + self.lm.tr('btn_clear', "Temizle"), style='Primary.TButton',
                                command=lambda: self.clear_waste_form())
        clear_btn.pack(side='left', padx=(20, 0))

    def save_waste_record(self, form_window) -> None:
        """Atık kaydını kaydet"""
        try:
            # Form verilerini al
            form_data = {}
            required_fields = ["waste_code", "waste_name", "waste_category", "quantity", "unit", "record_date"]

            # Gerekli alanları kontrol et
            for field in required_fields:
                if field in self.form_vars:
                    value = self.form_vars[field].get().strip()
                    if not value:
                        messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr(field, field)} {self.lm.tr('msg_field_required', 'alanı zorunludur!')}")
                        return
                    form_data[field] = value

            # Diğer alanları al
            for field_name, var in self.form_vars.items():
                if field_name not in form_data:
                    if field_name == "notes":
                        form_data[field_name] = var.get('1.0', 'end-1c').strip()
                    else:
                        form_data[field_name] = var.get().strip()

            # Sayısal alanları dönüştür
            try:
                form_data['quantity'] = float(form_data['quantity'])
                form_data['recycling_rate'] = float(form_data.get('recycling_rate', 0))
                form_data['disposal_cost'] = float(form_data.get('disposal_cost', 0))
                form_data['carbon_footprint'] = float(form_data.get('carbon_footprint', 0))
            except ValueError:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('msg_invalid_number', "Sayısal alanlarda geçersiz değer!"))
                return

            # Tarih formatını kontrol et
            try:
                datetime.strptime(form_data['record_date'], "%Y-%m-%d")
            except ValueError:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('msg_invalid_date', "Tarih formatı hatalı! (YYYY-MM-DD)"))
                return
            # Opsiyonel tarihleri kontrol et (varsa)
            for opt_date_field in ("invoice_date", "due_date"):
                val = form_data.get(opt_date_field)
                if val:
                    try:
                        datetime.strptime(val, "%Y-%m-%d")
                    except ValueError:
                        messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('msg_invalid_date', "Tarih formatı hatalı! (YYYY-MM-DD)"))
                        return

            # Veritabanına kaydet
            success = self.waste_manager.add_waste_record(self.company_id, form_data)

            if success:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('msg_waste_record_added', "Atık kaydı başarıyla eklendi!"))
                form_window.destroy()

                # Kayıtlar tablosunu yenile
                if hasattr(self, 'records_tree'):
                    self.refresh_waste_records()
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('msg_waste_record_failed', "Atık kaydı eklenemedi!"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('msg_save_error', 'Kayıt sırasında hata oluştu')}: {str(e)}")

    def clear_waste_form(self) -> None:
        """Formu temizle"""
        for field_name, var in self.form_vars.items():
            if field_name == "notes":
                var.delete('1.0', 'end')
                var.insert('1.0', "")
            else:
                var.set("")

        # Varsayılan değerleri geri yükle
        if "record_date" in self.form_vars:
            self.form_vars["record_date"].set(datetime.now().strftime("%Y-%m-%d"))
        if "unit" in self.form_vars:
            self.form_vars["unit"].set("kg")
        if "hazard_level" in self.form_vars:
            self.form_vars["hazard_level"].set(self.lm.tr('level_non_hazardous', "Tehlikesiz"))

    def show_reduction_target_form(self) -> None:
        """Atık azaltma hedefi ekleme formunu göster"""
        # Form penceresi oluştur
        form_window = tk.Toplevel(self.parent)
        form_window.title(" " + self.lm.tr('title_new_target', "Yeni Azaltma Hedefi"))
        form_window.geometry("600x650")
        form_window.configure(bg='#f8f9fa')
        form_window.grab_set()

        # Pencereyi merkeze al
        form_window.transient(self.parent)
        form_window.focus_force()

        # Başlık
        header_frame = tk.Frame(form_window, bg='#f39c12', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text=" " + self.lm.tr('title_add_reduction_target', "Yeni Azaltma Hedefi Ekle"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#f39c12')
        title_label.pack(expand=True)

        # Ana form alanı
        main_frame = tk.Frame(form_window, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Scrollable frame
        canvas = tk.Canvas(main_frame, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f8f9fa')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Form değişkenleri
        self.target_form_vars = {}

        # Form alanları
        form_fields = [
            (self.lm.tr('col_target_name', "Hedef Adı"), "target_name", "text", True, self.lm.tr('placeholder_target_name', "Örn: Organik Atık Azaltma")),
            (self.lm.tr('col_type', "Hedef Türü"), "target_type", "combo", True, [
                self.lm.tr('type_reduction', "Azaltma"), 
                self.lm.tr('type_recycle_increase', "Geri Dönüşüm Artırma"), 
                self.lm.tr('type_zero_waste', "Sıfır Atık"), 
                self.lm.tr('type_carbon_reduction', "Karbon Azaltma")
            ]),
            (self.lm.tr('col_category', "Atık Kategorisi"), "waste_category", "combo", False, [
                self.lm.tr('cat_organic', "Organik"), 
                self.lm.tr('cat_recycle', "Geri Dönüşüm"), 
                self.lm.tr('cat_hazardous', "Tehlikeli"), 
                self.lm.tr('cat_construction', "İnşaat"), 
                self.lm.tr('cat_textile', "Tekstil"), 
                self.lm.tr('cat_medical', "Tıbbi"), 
                self.lm.tr('cat_general', "Genel"), 
                self.lm.tr('all', "Tümü")
            ]),
            (self.lm.tr('col_base_year', "Başlangıç Yılı"), "base_year", "combo", True, ["2020", "2021", "2022", "2023", "2024"]),
            (self.lm.tr('col_target_year', "Hedef Yılı"), "target_year", "combo", True, ["2024", "2025", "2026", "2027", "2028", "2030"]),
            (self.lm.tr('col_base_amount', "Başlangıç Miktarı"), "base_quantity", "number", True, "0.00"),
            (self.lm.tr('col_target_amount', "Hedef Miktarı"), "target_quantity", "number", True, "0.00"),
            (self.lm.tr('col_unit', "Birim"), "target_unit", "combo", True, ["kg", "ton", "g", "m3", "l"]),
            (self.lm.tr('col_reduction_percent', "Azaltma Yüzdesi (%)"), "reduction_percentage", "number", False, "0"),
            (self.lm.tr('col_description', "Hedef Açıklaması"), "description", "textarea", False, ""),
            (self.lm.tr('col_start_date', "Başlangıç Tarihi"), "start_date", "date", False, datetime.now().strftime("%Y-%m-%d")),
            (self.lm.tr('col_end_date', "Bitiş Tarihi"), "end_date", "date", False, ""),
            (self.lm.tr('lbl_responsible_person', "Sorumlu Kişi"), "responsible_person", "text", False, ""),
            (self.lm.tr('lbl_notes', "Notlar"), "notes", "textarea", False, "")
        ]

        # Form alanlarını oluştur
        for i, (label_text, field_name, field_type, required, default_value) in enumerate(form_fields):
            # Alan container
            field_frame = tk.Frame(scrollable_frame, bg='white', relief='solid', bd=1)
            field_frame.pack(fill='x', pady=5)

            # Label
            label = tk.Label(field_frame, text=label_text + (" *" if required else ""),
                           font=('Segoe UI', 10, 'bold'), fg='#2c3e50', bg='white')
            label.pack(anchor='w', padx=10, pady=(10, 5))

            # Input field
            if field_type == "text":
                var = tk.StringVar(value=default_value)
                entry = tk.Entry(field_frame, textvariable=var, font=('Segoe UI', 11),
                               relief='solid', bd=1, width=50)
                entry.pack(padx=10, pady=(0, 10), fill='x')

            elif field_type == "number":
                var = tk.StringVar(value=default_value)
                entry = tk.Entry(field_frame, textvariable=var, font=('Segoe UI', 11),
                               relief='solid', bd=1, width=50)
                entry.pack(padx=10, pady=(0, 10), fill='x')

            elif field_type == "date":
                var = tk.StringVar(value=default_value)
                entry = tk.Entry(field_frame, textvariable=var, font=('Segoe UI', 11),
                               relief='solid', bd=1, width=50)
                entry.pack(padx=10, pady=(0, 10), fill='x')

            elif field_type == "combo":
                var = tk.StringVar(value=default_value[0] if isinstance(default_value, list) else "")
                combo = ttk.Combobox(field_frame, textvariable=var, values=default_value,
                                   font=('Segoe UI', 11), width=47)
                combo.pack(padx=10, pady=(0, 10), fill='x')

            elif field_type == "textarea":
                var = tk.StringVar(value=default_value)
                text_area = tk.Text(field_frame, font=('Segoe UI', 11), height=3,
                                  relief='solid', bd=1, wrap='word')
                text_area.pack(padx=10, pady=(0, 10), fill='x')
                text_area.insert('1.0', default_value)

            self.target_form_vars[field_name] = var if field_type != "textarea" else text_area

        # Canvas ve scrollbar'ı pack et
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Butonlar
        button_frame = tk.Frame(form_window, bg='#f8f9fa', height=60)
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        button_frame.pack_propagate(False)

        # Kaydet butonu
        save_btn = ttk.Button(button_frame, text=" " + self.lm.tr('btn_save', "Kaydet"), style='Primary.TButton',
                              command=lambda: self.save_reduction_target(form_window))
        save_btn.pack(side='left')

        # İptal butonu
        cancel_btn = ttk.Button(button_frame, text=" " + self.lm.tr('btn_cancel', "İptal"), style='Primary.TButton',
                                command=form_window.destroy)
        cancel_btn.pack(side='right')

        # Temizle butonu
        clear_btn = ttk.Button(button_frame, text="️ " + self.lm.tr('btn_clear', "Temizle"), style='Primary.TButton',
                               command=lambda: self.clear_target_form())
        clear_btn.pack(side='left', padx=(20, 0))

    def save_reduction_target(self, form_window) -> None:
        """Azaltma hedefini kaydet"""
        try:
            # Form verilerini al
            form_data = {}
            required_fields = ["target_name", "target_type", "base_year", "target_year", "base_quantity", "target_quantity", "target_unit"]

            # Gerekli alanları kontrol et
            for field in required_fields:
                if field in self.target_form_vars:
                    value = self.target_form_vars[field].get().strip()
                    if not value:
                        messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr(field, field)} {self.lm.tr('msg_field_required', 'alanı zorunludur!')}")
                        return
                    form_data[field] = value

            # Diğer alanları al
            for field_name, var in self.target_form_vars.items():
                if field_name not in form_data:
                    if field_name in ["description", "notes"]:
                        form_data[field_name] = var.get('1.0', 'end-1c').strip()
                    else:
                        form_data[field_name] = var.get().strip()

            # Sayısal alanları dönüştür
            try:
                form_data['base_quantity'] = float(form_data['base_quantity'])
                form_data['target_quantity'] = float(form_data['target_quantity'])
                form_data['reduction_percentage'] = float(form_data.get('reduction_percentage', 0))
                form_data['base_year'] = int(form_data['base_year'])
                form_data['target_year'] = int(form_data['target_year'])
            except ValueError:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('msg_invalid_number', "Sayısal alanlarda geçersiz değer!"))
                return

            # Tarih formatını kontrol et
            if form_data.get('start_date'):
                try:
                    datetime.strptime(form_data['start_date'], "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('msg_invalid_start_date', "Başlangıç tarihi formatı hatalı! (YYYY-MM-DD)"))
                    return

            if form_data.get('end_date'):
                try:
                    datetime.strptime(form_data['end_date'], "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('msg_invalid_end_date', "Bitiş tarihi formatı hatalı! (YYYY-MM-DD)"))
                    return

            # Azaltma yüzdesini hesapla
            if form_data['base_quantity'] > 0 and form_data['reduction_percentage'] == 0:
                form_data['reduction_percentage'] = ((form_data['base_quantity'] - form_data['target_quantity']) / form_data['base_quantity']) * 100

            # Veritabanına kaydet
            success = self.waste_manager.add_waste_target(
                company_id=self.company_id,
                target_name=form_data['target_name'],
                target_type=form_data['target_type'],
                waste_category=form_data.get('waste_category'),
                base_year=form_data['base_year'],
                target_year=form_data['target_year'],
                base_quantity=form_data['base_quantity'],
                target_quantity=form_data['target_quantity'],
                reduction_percentage=form_data['reduction_percentage'],
                target_unit=form_data['target_unit'],
                description=form_data.get('description')
            )

            if success:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('msg_target_added', "Azaltma hedefi başarıyla eklendi!"))
                form_window.destroy()

                # Hedefler tablosunu yenile
                if hasattr(self, 'targets_tree'):
                    self.refresh_targets()
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('msg_target_failed', "Azaltma hedefi eklenemedi!"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('msg_save_error', 'Hedef kayıt sırasında hata oluştu')}: {str(e)}")

    def clear_target_form(self) -> None:
        """Hedef formunu temizle"""
        for field_name, var in self.target_form_vars.items():
            if field_name in ["description", "notes"]:
                var.delete('1.0', 'end')
                var.insert('1.0', "")
            else:
                var.set("")

        # Varsayılan değerleri geri yükle
        if "base_year" in self.target_form_vars:
            self.target_form_vars["base_year"].set("2023")
        if "target_year" in self.target_form_vars:
            self.target_form_vars["target_year"].set("2025")
        if "target_unit" in self.target_form_vars:
            self.target_form_vars["target_unit"].set("kg")
        if "start_date" in self.target_form_vars:
            self.target_form_vars["start_date"].set(datetime.now().strftime("%Y-%m-%d"))

    def refresh_targets(self) -> None:
        """Hedefler tablosunu yenile"""
        if hasattr(self, 'targets_tree'):
            # Tabloyu temizle
            for item in self.targets_tree.get_children():
                self.targets_tree.delete(item)

            # Hedefleri al ve tabloya ekle
            targets = self.waste_manager.get_waste_targets(self.company_id)
            for target in targets:
                self.targets_tree.insert('', 'end', values=(
                    target.get('target_name', ''),
                    target.get('target_type', ''),
                    target.get('waste_category', ''),
                    target.get('base_year', ''),
                    target.get('target_year', ''),
                    f"{target.get('base_quantity', 0):.2f}",
                    f"{target.get('target_quantity', 0):.2f}",
                    f"%{target.get('reduction_percentage', 0):.1f}",
                    target.get('status', '')
                ))

    def show_recycling_project_form(self) -> None:
        """Geri dönüşüm projesi ekleme formunu göster"""
        # Form penceresi oluştur
        form_window = tk.Toplevel(self.parent)
        form_window.title(" " + self.lm.tr('title_new_project', "Yeni Geri Dönüşüm Projesi"))
        form_window.geometry("600x700")
        form_window.configure(bg='#f8f9fa')
        form_window.grab_set()

        # Pencereyi merkeze al
        form_window.transient(self.parent)
        form_window.focus_force()

        # Başlık
        header_frame = tk.Frame(form_window, bg='#27ae60', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text=" " + self.lm.tr('title_add_project', "Yeni Geri Dönüşüm Projesi Ekle"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#27ae60')
        title_label.pack(expand=True)

        # Ana form alanı
        main_frame = tk.Frame(form_window, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Scrollable frame
        canvas = tk.Canvas(main_frame, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f8f9fa')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Form değişkenleri
        self.project_form_vars = {}

        # Form alanları
        form_fields = [
            (self.lm.tr('col_project_name', "Proje Adı"), "project_name", "text", True, self.lm.tr('placeholder_project_name', "Örn: Plastik Geri Dönüşüm Projesi")),
            (self.lm.tr('col_project_type', "Proje Türü"), "project_type", "combo", True, [
                self.lm.tr('type_recycling', "Geri Dönüşüm"), 
                self.lm.tr('type_compost', "Kompost"), 
                self.lm.tr('type_biogas', "Biyogaz"), 
                self.lm.tr('type_energy_generation', "Enerji Üretimi"), 
                self.lm.tr('type_material_recovery', "Malzeme Geri Kazanımı")
            ]),
            (self.lm.tr('col_waste_types', "Atık Türleri"), "waste_types", "text", True, self.lm.tr('placeholder_waste_types', "Örn: Plastik, Kağıt, Organik")),
            (self.lm.tr('col_start_date', "Başlangıç Tarihi"), "start_date", "date", True, datetime.now().strftime("%Y-%m-%d")),
            (self.lm.tr('col_end_date', "Bitiş Tarihi"), "end_date", "date", False, ""),
            (self.lm.tr('col_status', "Durum"), "status", "combo", True, [
                self.lm.tr('status_planning', "Planlama"), 
                self.lm.tr('status_active', "Aktif"), 
                self.lm.tr('status_completed', "Tamamlandı"), 
                self.lm.tr('status_stopped', "Durduruldu")
            ]),
            (self.lm.tr('col_investment_amount', "Yatırım Tutarı (TL)"), "investment_amount", "number", False, "0.00"),
            (self.lm.tr('col_expected_savings', "Beklenen Tasarruf (TL)"), "expected_savings", "number", False, "0.00"),
            (self.lm.tr('col_recycling_rate_before', "Mevcut Geri Dönüşüm Oranı (%)"), "recycling_rate_before", "number", False, "0"),
            (self.lm.tr('col_recycling_rate_target', "Hedef Geri Dönüşüm Oranı (%)"), "recycling_rate_target", "number", False, "0"),
            (self.lm.tr('col_environmental_impact', "Çevresel Etki"), "environmental_impact", "textarea", False, ""),
            (self.lm.tr('col_economic_benefits', "Ekonomik Faydalar"), "economic_benefits", "textarea", False, ""),
            (self.lm.tr('col_challenges', "Karşılaşılan Zorluklar"), "challenges", "textarea", False, ""),
            (self.lm.tr('col_lessons_learned', "Öğrenilen Dersler"), "lessons_learned", "textarea", False, ""),
            (self.lm.tr('col_next_steps', "Sonraki Adımlar"), "next_steps", "textarea", False, ""),
            (self.lm.tr('lbl_responsible_person', "Sorumlu Kişi"), "responsible_person", "text", False, ""),
            (self.lm.tr('lbl_notes', "Notlar"), "notes", "textarea", False, "")
        ]

        # Form alanlarını oluştur
        for i, (label_text, field_name, field_type, required, default_value) in enumerate(form_fields):
            # Alan container
            field_frame = tk.Frame(scrollable_frame, bg='white', relief='solid', bd=1)
            field_frame.pack(fill='x', pady=5)

            # Label
            label = tk.Label(field_frame, text=label_text + (" *" if required else ""),
                           font=('Segoe UI', 10, 'bold'), fg='#2c3e50', bg='white')
            label.pack(anchor='w', padx=10, pady=(10, 5))

            # Input field
            if field_type == "text":
                var = tk.StringVar(value=default_value)
                entry = tk.Entry(field_frame, textvariable=var, font=('Segoe UI', 11),
                               relief='solid', bd=1, width=50)
                entry.pack(padx=10, pady=(0, 10), fill='x')

            elif field_type == "number":
                var = tk.StringVar(value=default_value)
                entry = tk.Entry(field_frame, textvariable=var, font=('Segoe UI', 11),
                               relief='solid', bd=1, width=50)
                entry.pack(padx=10, pady=(0, 10), fill='x')

            elif field_type == "date":
                var = tk.StringVar(value=default_value)
                entry = tk.Entry(field_frame, textvariable=var, font=('Segoe UI', 11),
                               relief='solid', bd=1, width=50)
                entry.pack(padx=10, pady=(0, 10), fill='x')

            elif field_type == "combo":
                var = tk.StringVar(value=default_value[0] if isinstance(default_value, list) else "")
                combo = ttk.Combobox(field_frame, textvariable=var, values=default_value,
                                   font=('Segoe UI', 11), width=47)
                combo.pack(padx=10, pady=(0, 10), fill='x')

            elif field_type == "textarea":
                var = tk.StringVar(value=default_value)
                text_area = tk.Text(field_frame, font=('Segoe UI', 11), height=3,
                                  relief='solid', bd=1, wrap='word')
                text_area.pack(padx=10, pady=(0, 10), fill='x')
                text_area.insert('1.0', default_value)

            self.project_form_vars[field_name] = var if field_type != "textarea" else text_area

        # Canvas ve scrollbar'ı pack et
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Butonlar
        button_frame = tk.Frame(form_window, bg='#f8f9fa', height=60)
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        button_frame.pack_propagate(False)

        # Kaydet butonu
        save_btn = ttk.Button(button_frame, text=" " + self.lm.tr('btn_save', "Kaydet"), style='Primary.TButton',
                              command=lambda: self.save_recycling_project(form_window))
        save_btn.pack(side='left')

        # İptal butonu
        cancel_btn = ttk.Button(button_frame, text=" " + self.lm.tr('btn_cancel', "İptal"), style='Primary.TButton',
                                command=form_window.destroy)
        cancel_btn.pack(side='right')

        # Temizle butonu
        clear_btn = ttk.Button(button_frame, text="️ " + self.lm.tr('btn_clear', "Temizle"), style='Primary.TButton',
                               command=lambda: self.clear_project_form())
        clear_btn.pack(side='left', padx=(20, 0))

    def save_recycling_project(self, form_window) -> None:
        """Geri dönüşüm projesini kaydet"""
        try:
            # Form verilerini al
            form_data = {}
            required_fields = ["project_name", "project_type", "waste_types", "start_date", "status"]

            # Gerekli alanları kontrol et
            for field in required_fields:
                if field in self.project_form_vars:
                    value = self.project_form_vars[field].get().strip()
                    if not value:
                        messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr(field, field)} {self.lm.tr('msg_field_required', 'alanı zorunludur!')}")
                        return
                    form_data[field] = value

            # Diğer alanları al
            for field_name, var in self.project_form_vars.items():
                if field_name not in form_data:
                    if field_name in ["environmental_impact", "economic_benefits", "challenges", "lessons_learned", "next_steps", "notes"]:
                        form_data[field_name] = var.get('1.0', 'end-1c').strip()
                    else:
                        form_data[field_name] = var.get().strip()

            # Sayısal alanları dönüştür
            try:
                form_data['investment_amount'] = float(form_data.get('investment_amount', 0))
                form_data['expected_savings'] = float(form_data.get('expected_savings', 0))
                form_data['recycling_rate_before'] = float(form_data.get('recycling_rate_before', 0))
                form_data['recycling_rate_target'] = float(form_data.get('recycling_rate_target', 0))
            except ValueError:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('msg_invalid_number', "Sayısal alanlarda geçersiz değer!"))
                return

            # Tarih formatını kontrol et
            try:
                datetime.strptime(form_data['start_date'], "%Y-%m-%d")
            except ValueError:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('msg_invalid_start_date', "Başlangıç tarihi formatı hatalı! (YYYY-MM-DD)"))
                return

            if form_data.get('end_date'):
                try:
                    datetime.strptime(form_data['end_date'], "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('msg_invalid_end_date', "Bitiş tarihi formatı hatalı! (YYYY-MM-DD)"))
                    return

            # Veritabanına kaydet
            success = self.waste_manager.add_recycling_project(
                company_id=self.company_id,
                project_name=form_data['project_name'],
                project_type=form_data['project_type'],
                waste_types=form_data['waste_types'],
                start_date=form_data['start_date'],
                end_date=form_data.get('end_date'),
                investment_amount=form_data['investment_amount'],
                expected_savings=form_data['expected_savings'],
                recycling_rate_before=form_data['recycling_rate_before'],
                recycling_rate_target=form_data['recycling_rate_target'],
                environmental_impact=form_data.get('environmental_impact'),
                economic_benefits=form_data.get('economic_benefits'),
                challenges=form_data.get('challenges'),
                lessons_learned=form_data.get('lessons_learned'),
                next_steps=form_data.get('next_steps')
            )

            if success:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('msg_project_added', "Geri dönüşüm projesi başarıyla eklendi!"))
                form_window.destroy()

                # Projeler tablosunu yenile
                if hasattr(self, 'projects_tree'):
                    self.refresh_projects()
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('msg_project_failed', "Geri dönüşüm projesi eklenemedi!"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('msg_save_error', 'Proje kayıt sırasında hata oluştu')}: {str(e)}")

    def clear_project_form(self) -> None:
        """Proje formunu temizle"""
        for field_name, var in self.project_form_vars.items():
            if field_name in ["environmental_impact", "economic_benefits", "challenges", "lessons_learned", "next_steps", "notes"]:
                var.delete('1.0', 'end')
                var.insert('1.0', "")
            else:
                var.set("")

        # Varsayılan değerleri geri yükle
        if "start_date" in self.project_form_vars:
            self.project_form_vars["start_date"].set(datetime.now().strftime("%Y-%m-%d"))
        if "status" in self.project_form_vars:
            self.project_form_vars["status"].set(self.lm.tr('status_planning', "Planlama"))

    def refresh_projects(self) -> None:
        """Projeler tablosunu yenile"""
        if hasattr(self, 'projects_tree'):
            # Tabloyu temizle
            for item in self.projects_tree.get_children():
                self.projects_tree.delete(item)

            # Projeleri al ve tabloya ekle
            projects = self.waste_manager.get_recycling_projects(self.company_id)
            for project in projects:
                self.projects_tree.insert('', 'end', values=(
                    project.get('project_name', ''),
                    project.get('project_type', ''),
                    project.get('waste_types', ''),
                    project.get('start_date', ''),
                    project.get('end_date', ''),
                    project.get('status', ''),
                    f"{project.get('investment_amount', 0):.2f} TL",
                    f"{project.get('expected_savings', 0):.2f} TL",
                    f"%{project.get('recycling_rate_before', 0):.1f}",
                    f"%{project.get('recycling_rate_target', 0):.1f}"
                ))
