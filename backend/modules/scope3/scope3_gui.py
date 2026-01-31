import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scope 3 Kategorileri GUI
GHG Protocol Scope 3 kategorileri için kullanıcı arayüzü
"""

import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from utils.language_manager import LanguageManager
from utils.tooltip import add_rich_tooltip, add_tooltip
from utils.ui_theme import apply_theme

from .scope3_manager import Scope3Manager
from config.icons import Icons


class Scope3GUI:
    """Scope 3 kategorileri GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.manager = Scope3Manager()
        self.lm = LanguageManager()
        self.last_scope3_report_path = None

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Scope 3 modülü arayüzünü oluştur"""
        apply_theme(self.parent)
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#27ae60', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=self.lm.tr('scope3_title', " Scope 3 Kategorileri - GHG Protocol"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#27ae60')
        title_label.pack(expand=True)

        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill='x', pady=(0, 10))
        ttk.Button(toolbar, text=self.lm.tr('btn_report_center', " Rapor Merkezi"), style='Primary.TButton', command=self.open_report_center_scope3).pack(side='left', padx=6)
        ttk.Button(toolbar, text=self.lm.tr('btn_refresh', " Yenile"), style='Primary.TButton', command=self.load_data).pack(side='left', padx=6)

        # Ana içerik alanı
        content_frame = tk.Frame(main_frame, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Notebook oluştur
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True)

        # Sekmeler
        self.create_overview_tab()
        self.create_categories_tab()
        self.create_emissions_tab()
        self.create_targets_tab()
        self.create_reports_tab()

    def create_overview_tab(self) -> None:
        """Genel bakış sekmesi"""
        overview_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(overview_frame, text=self.lm.tr('tab_overview', " Genel Bakış"))

        # Sol panel - İstatistikler
        left_frame = tk.Frame(overview_frame, bg='white', relief='raised', bd=1)
        left_frame.pack(side='left', fill='both', expand=True, padx=(10, 5), pady=10)

        stats_title = tk.Label(left_frame, text=self.lm.tr('scope3_stats_title', "Scope 3 İstatistikleri"),
                              font=('Segoe UI', 12, 'bold'), bg='white', fg='#27ae60')
        stats_title.pack(pady=10)

        self.stats_frame = tk.Frame(left_frame, bg='white')
        self.stats_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Sağ panel - Kategori dağılımı
        right_frame = tk.Frame(overview_frame, bg='white', relief='raised', bd=1)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 10), pady=10)

        chart_title = tk.Label(right_frame, text=self.lm.tr('chart_category_dist', "Kategori Dağılımı"),
                              font=('Segoe UI', 12, 'bold'), bg='white', fg='#27ae60')
        chart_title.pack(pady=10)

        self.chart_frame = tk.Frame(right_frame, bg='white')
        self.chart_frame.pack(fill='both', expand=True, padx=10, pady=10)

    def create_categories_tab(self) -> None:
        """Kategoriler sekmesi"""
        categories_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(categories_frame, text=self.lm.tr('tab_categories', " Kategoriler"))

        # Üst butonlar
        btn_frame = tk.Frame(categories_frame, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=15)

        ttk.Button(btn_frame, text=self.lm.tr('btn_refresh', " Yenile"), style='Primary.TButton', command=self.refresh_categories).pack(side='left', padx=5)

        # Kategoriler listesi
        list_frame = tk.Frame(categories_frame, bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Treeview oluştur
        columns = (
            self.lm.tr('col_category', 'Kategori'),
            self.lm.tr('col_description', 'Açıklama'),
            self.lm.tr('col_type', 'Tip'),
            self.lm.tr('col_upstream', 'Upstream'),
            self.lm.tr('col_downstream', 'Downstream')
        )
        self.categories_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        # Sütun başlıkları
        for col in columns:
            self.categories_tree.heading(col, text=col)
            self.categories_tree.column(col, width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.categories_tree.yview)
        self.categories_tree.configure(yscrollcommand=scrollbar.set)

        self.categories_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_emissions_tab(self) -> None:
        """Emisyonlar sekmesi"""
        emissions_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(emissions_frame, text=self.lm.tr('tab_emissions', "️ Emisyonlar"))

        # Üst butonlar
        btn_frame = tk.Frame(emissions_frame, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=15)

        ttk.Button(btn_frame, text=self.lm.tr('btn_new_emission', " Yeni Emisyon Kaydı"), style='Primary.TButton', command=self.show_add_emission_form).pack(side='left', padx=5)

        ttk.Button(btn_frame, text=self.lm.tr('btn_import_excel', " Excel'den İçe Aktar"), style='Primary.TButton', command=self.import_emissions_excel).pack(side='left', padx=5)

        ttk.Button(btn_frame, text=self.lm.tr('btn_export_excel', " Excel'e Aktar"), style='Primary.TButton', command=self.export_emissions_excel).pack(side='left', padx=5)

        # Emisyonlar listesi
        list_frame = tk.Frame(emissions_frame, bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Treeview oluştur
        columns = (
            self.lm.tr('col_category', 'Kategori'),
            self.lm.tr('col_activity_data', 'Aktivite Verisi'),
            self.lm.tr('col_emission_factor', 'Emisyon Faktörü'),
            self.lm.tr('col_total_emissions', 'Toplam Emisyon'),
            self.lm.tr('col_period', 'Dönem'),
            self.lm.tr('col_source', 'Kaynak')
        )
        self.emissions_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        # Sütun başlıkları
        for col in columns:
            self.emissions_tree.heading(col, text=col)
            self.emissions_tree.column(col, width=120)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.emissions_tree.yview)
        self.emissions_tree.configure(yscrollcommand=scrollbar.set)

        self.emissions_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_targets_tab(self) -> None:
        """Hedefler sekmesi"""
        targets_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(targets_frame, text=self.lm.tr('tab_targets', " Hedefler"))

        # Üst butonlar
        btn_frame = tk.Frame(targets_frame, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=15)

        ttk.Button(btn_frame, text=self.lm.tr('btn_new_target', " Yeni Hedef"), style='Primary.TButton', command=self.show_add_target_form).pack(side='left', padx=5)

        # Hedefler listesi
        list_frame = tk.Frame(targets_frame, bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Treeview oluştur
        columns = (
            self.lm.tr('col_category', 'Kategori'),
            self.lm.tr('col_target_type', 'Hedef Tipi'),
            self.lm.tr('col_baseline_year', 'Baz Yılı'),
            self.lm.tr('col_target_year', 'Hedef Yılı'),
            self.lm.tr('col_reduction', 'Azaltım (%)'),
            self.lm.tr('col_status', 'Durum')
        )
        self.targets_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        # Sütun başlıkları
        for col in columns:
            self.targets_tree.heading(col, text=col)
            self.targets_tree.column(col, width=120)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.targets_tree.yview)
        self.targets_tree.configure(yscrollcommand=scrollbar.set)

        self.targets_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_reports_tab(self) -> None:
        """Raporlar sekmesi"""
        reports_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(reports_frame, text=self.lm.tr('tab_reports', " Raporlar"))

        # Üst butonlar
        btn_frame = tk.Frame(reports_frame, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=15)

        generate_btn = ttk.Button(btn_frame, text=self.lm.tr('btn_create_report', " Rapor Oluştur"), style='Primary.TButton', command=self.generate_report)
        generate_btn.pack(side='left', padx=5)
        try:
            add_tooltip(generate_btn, self.lm.tr('tooltip_create_report', 'Scope 3 rapor dosyası oluşturur'))
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        # Raporlar listesi
        list_frame = tk.Frame(reports_frame, bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Treeview oluştur
        columns = (
            self.lm.tr('col_report_name', 'Rapor Adı'),
            self.lm.tr('col_format', 'Format'),
            self.lm.tr('col_created_date', 'Oluşturulma Tarihi'),
            self.lm.tr('col_size', 'Boyut'),
            self.lm.tr('col_status', 'Durum')
        )
        self.reports_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        # Sütun başlıkları
        for col in columns:
            self.reports_tree.heading(col, text=col)
            self.reports_tree.column(col, width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.reports_tree.yview)
        self.reports_tree.configure(yscrollcommand=scrollbar.set)

        self.reports_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        preview_open_frame = tk.Frame(reports_frame, bg='white')
        preview_open_frame.pack(fill='x', padx=20, pady=(10, 20))
        ttk.Button(preview_open_frame, text=self.lm.tr('preview_and_outputs', " Önizleme ve Çıkışlar"), style='Primary.TButton', command=self._scope3_open_preview_window).pack(side='left')

    def load_data(self) -> None:
        """Verileri yükle"""
        self.load_categories()
        self.load_emissions()
        self.load_targets()
        self.load_summary()

    def _scope3_open_preview_window(self) -> None:
        try:
            win = tk.Toplevel(self.parent)
            win.title(self.lm.tr('scope3_preview_title', 'Scope 3 Önizleme ve Çıkışlar'))
            win.geometry('900x600')
            top = tk.Frame(win, bg='white')
            top.pack(fill='x', padx=10, pady=6)
            ttk.Button(top, text=self.lm.tr('btn_back', ' Geri'), command=win.destroy).pack(side='left')
            top_controls = tk.Frame(win, bg='white')
            top_controls.pack(fill='x', padx=10, pady=6)
            tk.Label(top_controls, text=self.lm.tr('report_period', 'Raporlama Dönemi:'), bg='white').pack(side='left')
            self.scope3_report_period_var = tk.StringVar(value=datetime.now().strftime('%Y'))
            period_entry = tk.Entry(top_controls, textvariable=self.scope3_report_period_var, width=10)
            period_entry.pack(side='left', padx=8)
            try:
                add_rich_tooltip(period_entry, title=self.lm.tr('report_year', 'Rapor Yılı'), text=self.lm.tr('tooltip_report_year', 'Scope 3 rapor yılı (YYYY).'), example=self.lm.tr('example_year', 'Örn: 2025'))
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
            self.scope3_report_text = tk.Text(win, height=20, wrap='word')
            preview_scroll = ttk.Scrollbar(win, orient='vertical', command=self.scope3_report_text.yview)
            self.scope3_report_text.configure(yscrollcommand=preview_scroll.set)
            self.scope3_report_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
            preview_scroll.pack(side='right', fill='y', pady=10)
            tools = tk.Frame(win, bg='white')
            tools.pack(fill='x', padx=10, pady=(0,10))
            ttk.Button(tools, text=self.lm.tr('btn_fill_preview', ' Önizlemeyi Doldur'), style='Primary.TButton', command=self._scope3_fill_preview_text).pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('btn_open', ' Aç'), style='Primary.TButton', command=self._scope3_open_last_report).pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('btn_save_txt', ' Kaydet (.txt)'), style='Primary.TButton', command=self._scope3_save_preview_text).pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('btn_save_docx', ' Farklı Kaydet (DOCX)'), style='Primary.TButton', command=self._scope3_export_preview_docx).pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('btn_print', ' Yazdır'), style='Primary.TButton', command=self._scope3_print_preview_text).pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('btn_copy_clipboard', ' Panoya Kopyala'), style='Primary.TButton', command=self._scope3_copy_preview_to_clipboard).pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('btn_share', ' Paylaş'), style='Primary.TButton', command=self._scope3_share_dialog).pack(side='left', padx=4)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('error_preview_window', 'Önizleme penceresi hatası')}: {e}")

    def load_categories(self) -> None:
        """Kategorileri yükle"""
        self.categories_tree.delete(*self.categories_tree.get_children())
        categories = self.manager.get_categories()

        for category in categories:
            cat_text = self.lm.tr('category_format', 'Kategori {number}: {name}').format(
                number=category['category_number'], 
                name=category['category_name']
            )
            self.categories_tree.insert('', 'end', values=(
                cat_text,
                category['description'][:50] + "..." if len(category['description']) > 50 else category['description'],
                category['scope_type'],
                "" if category['is_upstream'] else "",
                "" if category['is_downstream'] else ""
            ))

    def load_emissions(self) -> None:
        """Emisyonları yükle"""
        self.emissions_tree.delete(*self.emissions_tree.get_children())
        emissions = self.manager.get_emission_data(self.company_id)

        for emission in emissions:
            cat_text = self.lm.tr('category_format', 'Kategori {number}: {name}').format(
                number=emission['category_number'], 
                name=emission['category_name']
            )
            self.emissions_tree.insert('', 'end', values=(
                cat_text,
                f"{emission['activity_data']} {emission['activity_unit']}" if emission['activity_data'] else "—",
                f"{emission['emission_factor']} {emission['emission_factor_unit']}" if emission['emission_factor'] else "—",
                f"{emission['total_emissions']:.2f} tCO2e" if emission['total_emissions'] else "—",
                emission['reporting_period'] or "—",
                emission['data_source'] or "—"
            ))

    def load_targets(self) -> None:
        """Hedefleri yükle"""
        self.targets_tree.delete(*self.targets_tree.get_children())
        targets = self.manager.get_target_data(self.company_id)

        for target in targets:
            cat_text = self.lm.tr('category_format', 'Kategori {number}: {name}').format(
                number=target['category_number'], 
                name=target['category_name']
            )
            self.targets_tree.insert('', 'end', values=(
                cat_text,
                target['target_type'],
                target['baseline_year'],
                target['target_year'],
                f"{target['reduction_percentage']:.1f}%" if target['reduction_percentage'] else "—",
                target['status']
            ))

    def load_summary(self) -> None:
        """Özet istatistikleri yükle"""
        # Önceki istatistikleri temizle
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Özet verileri al
        summary = self.manager.get_emissions_summary(self.company_id)
        categories = self.manager.get_categories()

        # İstatistik kartları
        stats_cards = [
            ("", self.lm.tr('total_emissions', "Toplam Emisyon"), f"{summary['total_emissions']:.2f} tCO2e", "#27ae60"),
            (Icons.UP, self.lm.tr('upstream', "Upstream"), f"{summary['upstream_emissions']:.2f} tCO2e", "#3498db"),
            (Icons.DOWN, self.lm.tr('downstream', "Downstream"), f"{summary['downstream_emissions']:.2f} tCO2e", "#e74c3c"),
            ("", self.lm.tr('total_categories', "Toplam Kategori"), f"{len(categories)}", "#9b59b6")
        ]

        for i, (icon, title, value, color) in enumerate(stats_cards):
            card = tk.Frame(self.stats_frame, bg=color, relief='raised', bd=2)
            card.grid(row=0, column=i, padx=5, pady=5, sticky='ew')
            self.stats_frame.grid_columnconfigure(i, weight=1)

            tk.Label(card, text=icon, font=('Segoe UI', 16), fg='white', bg=color).pack(pady=(5, 0))
            tk.Label(card, text=title, font=('Segoe UI', 10, 'bold'), fg='white', bg=color).pack()
            tk.Label(card, text=value, font=('Segoe UI', 12, 'bold'), fg='white', bg=color).pack(pady=(0, 5))

        # Kategori dağılımı
        if summary['category_breakdown']:
            tk.Label(self.chart_frame, text=self.lm.tr('category_emission_distribution', "Kategori Bazında Emisyon Dağılımı"),
                    font=('Segoe UI', 12, 'bold'), bg='white').pack(pady=(0, 10))

            for category, emissions in sorted(summary['category_breakdown'].items(),
                                            key=lambda x: x[1], reverse=True)[:10]:
                if emissions > 0:
                    row = tk.Frame(self.chart_frame, bg='white')
                    row.pack(fill='x', pady=2)

                    tk.Label(row, text=category[:30], font=('Segoe UI', 9),
                            bg='white', width=25, anchor='w').pack(side='left')

                    # Progress bar benzeri gösterim
                    progress_frame = tk.Frame(row, bg='#ecf0f1', height=20)
                    progress_frame.pack(side='right', fill='x', expand=True, padx=(10, 0))

                    max_emission = max(summary['category_breakdown'].values())
                    width = int((emissions / max_emission) * 200) if max_emission > 0 else 0

                    progress_bar = tk.Frame(progress_frame, bg='#27ae60', width=width, height=20)
                    progress_bar.pack(side='left', fill='y')

                    tk.Label(row, text=f"{emissions:.1f} tCO2e", font=('Segoe UI', 9),
                            bg='white', width=12).pack(side='right')
        else:
            tk.Label(self.chart_frame, text=self.lm.tr('no_emission_data', "Henüz emisyon verisi bulunmuyor"),
                    font=('Segoe UI', 12), fg='#7f8c8d', bg='white').pack(pady=50)

    def refresh_categories(self) -> None:
        """Kategorileri yenile"""
        self.load_categories()
        messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('categories_refreshed', "Kategoriler yenilendi!"))

    def show_add_emission_form(self) -> None:
        """Yeni emisyon kaydı formu göster"""
        # Form penceresi
        form_window = tk.Toplevel(self.parent)
        form_window.title(self.lm.tr('title_add_emission', " Yeni Emisyon Kaydı Ekle"))
        form_window.geometry("600x700")
        form_window.configure(bg='#f8f9fa')
        form_window.grab_set()

        # Başlık
        header_frame = tk.Frame(form_window, bg='#27ae60', height=50)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text=self.lm.tr('header_add_emission', " Yeni Scope 3 Emisyon Kaydı"),
                font=('Segoe UI', 14, 'bold'), fg='white', bg='#27ae60').pack(expand=True)

        # Ana içerik
        main_frame = tk.Frame(form_window, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Form alanları
        form_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        form_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Scope 3 Kategorisi
        tk.Label(form_frame, text=self.lm.tr('lbl_scope3_category', "Scope 3 Kategorisi:"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(20, 5))
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=category_var, width=50)
        category_combo['values'] = [
            self.lm.tr('cat1_purchased_goods', '1. Satın Alınan Mal ve Hizmetler'),
            self.lm.tr('cat2_capital_goods', '2. Sermaye Malları'),
            self.lm.tr('cat3_fuel_energy', '3. Yakıt ve Enerji Faaliyetleri'),
            self.lm.tr('cat4_upstream_transport', '4. Nakliye ve Dağıtım'),
            self.lm.tr('cat5_waste_generated', '5. Üretilen Ürünlerin Kullanımı'),
            self.lm.tr('cat6_business_travel', '6. İş Seyahatleri'),
            self.lm.tr('cat7_employee_commuting', '7. Çalışanların İşe Gidiş-Gelişleri'),
            self.lm.tr('cat8_upstream_leased', '8. Kiralanan Varlıklar'),
            self.lm.tr('cat9_downstream_transport', '9. Yatırımlar'),
            self.lm.tr('cat10_processing_sold', '10. Tedarik Zinciri Dışı Nakliye'),
            self.lm.tr('cat11_use_of_sold', '11. İşlenmiş Ürünlerin Kullanımı'),
            self.lm.tr('cat12_end_of_life', '12. Tedarik Zinciri Dışı Dağıtım'),
            self.lm.tr('cat13_downstream_leased', '13. Satılan Ürünlerin Bertarafı'),
            self.lm.tr('cat14_franchises', '14. Kiralanan Varlıkların Kullanımı'),
            self.lm.tr('cat15_investments', '15. Franchising')
        ]
        category_combo.pack(anchor='w', padx=20, pady=(0, 15))

        # Aktivite Verisi
        tk.Label(form_frame, text=self.lm.tr('lbl_activity_data', "Aktivite Verisi:"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        activity_var = tk.StringVar()
        activity_entry = tk.Entry(form_frame, textvariable=activity_var, font=('Segoe UI', 11), width=50)
        activity_entry.pack(anchor='w', padx=20, pady=(0, 15))

        # Aktivite Birimi
        tk.Label(form_frame, text=self.lm.tr('lbl_activity_unit', "Aktivite Birimi:"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        unit_var = tk.StringVar()
        unit_combo = ttk.Combobox(form_frame, textvariable=unit_var, width=50)
        unit_combo['values'] = [
            'TL', 'USD', 'EUR',
            'km', 'ton', 'kg', 'm³', 'kWh', 'MWh',
            self.lm.tr('unit_piece', 'adet'), self.lm.tr('unit_liter', 'litre'), 'm²', 'm³',
            self.lm.tr('unit_day', 'gün'), self.lm.tr('unit_person', 'kişi'), self.lm.tr('unit_trip', 'sefer')
        ]
        unit_combo.pack(anchor='w', padx=20, pady=(0, 15))

        # Emisyon Faktörü
        tk.Label(form_frame, text=self.lm.tr('lbl_emission_factor_unit', "Emisyon Faktörü (tCO2e/birim):"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        factor_var = tk.StringVar()
        factor_entry = tk.Entry(form_frame, textvariable=factor_var, font=('Segoe UI', 11), width=50)
        factor_entry.pack(anchor='w', padx=20, pady=(0, 15))

        # Toplam Emisyon
        tk.Label(form_frame, text=self.lm.tr('lbl_total_emission_unit', "Toplam Emisyon (tCO2e):"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        emission_var = tk.StringVar()
        emission_entry = tk.Entry(form_frame, textvariable=emission_var, font=('Segoe UI', 11), width=50)
        emission_entry.pack(anchor='w', padx=20, pady=(0, 15))

        # Dönem
        tk.Label(form_frame, text=self.lm.tr('lbl_reporting_period', "Raporlama Dönemi:"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        period_var = tk.StringVar(value="2024")
        period_entry = tk.Entry(form_frame, textvariable=period_var, font=('Segoe UI', 11), width=50)
        period_entry.pack(anchor='w', padx=20, pady=(0, 15))

        # Veri Kaynağı
        tk.Label(form_frame, text=self.lm.tr('lbl_data_source', "Veri Kaynağı:"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        source_var = tk.StringVar()
        source_combo = ttk.Combobox(form_frame, textvariable=source_var, width=50)
        source_combo['values'] = [
            self.lm.tr('source_accounting', 'Muhasebe Sistemi'),
            self.lm.tr('source_purchasing', 'Satın Alma Sistemi'),
            self.lm.tr('source_hr', 'İnsan Kaynakları'),
            self.lm.tr('source_financial', 'Mali Raporlar'),
            self.lm.tr('source_supplier', 'Tedarikçi Beyanları'),
            self.lm.tr('source_third_party', 'Üçüncü Taraf Verileri'),
            self.lm.tr('source_estimation', 'Tahmin/Hesaplama'),
            self.lm.tr('source_other', 'Diğer')
        ]
        source_combo.pack(anchor='w', padx=20, pady=(0, 15))

        # Notlar
        tk.Label(form_frame, text=self.lm.tr('lbl_notes', "Notlar:"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        notes_text = tk.Text(form_frame, height=4, width=50, font=('Segoe UI', 11))
        notes_text.pack(anchor='w', padx=20, pady=(0, 20))

        # Butonlar
        button_frame = tk.Frame(form_window, bg='#f8f9fa')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))

        def save_emission() -> None:
            """Emisyon verisini kaydet"""
            try:
                # Form verilerini al
                category = category_var.get().strip()
                activity = activity_var.get().strip()
                unit = unit_var.get().strip()
                factor = factor_var.get().strip()
                emission = emission_var.get().strip()
                period = period_var.get().strip()
                source = source_var.get().strip()
                notes = notes_text.get(1.0, tk.END).strip()

                # Validasyon
                if not all([category, activity, unit, factor, emission, period, source]):
                    messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('error_missing_fields', "Lütfen tüm zorunlu alanları doldurun!"))
                    return

                # Sayısal değerleri kontrol et
                try:
                    factor_val = float(factor)
                    emission_val = float(emission)
                except ValueError:
                    messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('error_numeric_fields', "Emisyon faktörü ve toplam emisyon sayısal olmalıdır!"))
                    return

                # Emisyon verisini kaydet
                emission_data = {
                    'company_id': self.company_id,
                    'category': category,
                    'activity_data': activity,
                    'unit': unit,
                    'emission_factor': factor_val,
                    'total_emission': emission_val,
                    'period': period,
                    'source': source,
                    'notes': notes
                }

                result = self.manager.add_emission_record(emission_data)

                if result:
                    messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('success_emission_added', "Emisyon kaydı başarıyla eklendi!"))
                    form_window.destroy()
                    self.load_data()  # Verileri yenile
                else:
                    messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('error_emission_add_failed', "Emisyon kaydı eklenirken hata oluştu!"))

            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_save', 'Kaydetme hatası')}: {e}")

        def cancel_form() -> None:
            """Formu iptal et"""
            form_window.destroy()

        # Butonlar
        ttk.Button(button_frame, text=self.lm.tr('btn_save', " Kaydet"), style='Primary.TButton', command=save_emission).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text=self.lm.tr('btn_cancel', " İptal"), command=cancel_form).pack(side='left')

    def import_emissions_excel(self) -> None:
        """Excel'den emisyon verilerini içe aktar"""
        try:
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                title=self.lm.tr("import_excel", "Excel İçe Aktar"),
                filetypes=[(self.lm.tr("file_excel", "Excel Dosyası"), "*.xlsx"), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")]
            )
            if filename:
                # Burada içe aktarma mantığı olacak
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('import_success', "İçe aktarma başarılı:\n{path}").format(path=filename))
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("import_error", "İçe aktarma hatası: {e}").format(e=e))

    def export_emissions_excel(self) -> None:
        """Emisyon verilerini Excel'e aktar"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                title=self.lm.tr("export_excel", "Excel Dışa Aktar"),
                defaultextension=".xlsx",
                filetypes=[(self.lm.tr("file_excel", "Excel Dosyası"), "*.xlsx"), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")]
            )
            if filename:
                # Burada dışa aktarma mantığı olacak
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('export_success', "Dışa aktarma başarılı:\n{path}").format(path=filename))
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("export_error", "Dışa aktarma hatası: {e}").format(e=e))

    def show_add_target_form(self) -> None:
        """Yeni hedef formu göster"""
        # Form penceresi
        form_window = tk.Toplevel(self.parent)
        form_window.title(self.lm.tr('title_add_target', " Yeni Scope 3 Hedefi Ekle"))
        form_window.geometry("600x650")
        form_window.configure(bg='#f8f9fa')
        form_window.grab_set()

        # Başlık
        header_frame = tk.Frame(form_window, bg='#e74c3c', height=50)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text=self.lm.tr('header_add_target', " Yeni Scope 3 Hedefi"),
                font=('Segoe UI', 14, 'bold'), fg='white', bg='#e74c3c').pack(expand=True)

        # Ana içerik
        main_frame = tk.Frame(form_window, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Form alanları
        form_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        form_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Scope 3 Kategorisi
        tk.Label(form_frame, text=self.lm.tr('lbl_scope3_category', "Scope 3 Kategorisi:"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(20, 5))
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=category_var, width=50)
        category_combo['values'] = [
            self.lm.tr('cat1_purchased_goods', '1. Satın Alınan Mal ve Hizmetler'),
            self.lm.tr('cat2_capital_goods', '2. Sermaye Malları'),
            self.lm.tr('cat3_fuel_energy', '3. Yakıt ve Enerji Faaliyetleri'),
            self.lm.tr('cat4_upstream_transport', '4. Nakliye ve Dağıtım'),
            self.lm.tr('cat5_waste_generated', '5. Üretilen Ürünlerin Kullanımı'),
            self.lm.tr('cat6_business_travel', '6. İş Seyahatleri'),
            self.lm.tr('cat7_employee_commuting', '7. Çalışanların İşe Gidiş-Gelişleri'),
            self.lm.tr('cat8_upstream_leased', '8. Kiralanan Varlıklar'),
            self.lm.tr('cat9_downstream_transport', '9. Yatırımlar'),
            self.lm.tr('cat10_processing_sold', '10. Tedarik Zinciri Dışı Nakliye'),
            self.lm.tr('cat11_use_of_sold', '11. İşlenmiş Ürünlerin Kullanımı'),
            self.lm.tr('cat12_end_of_life', '12. Tedarik Zinciri Dışı Dağıtım'),
            self.lm.tr('cat13_downstream_leased', '13. Satılan Ürünlerin Bertarafı'),
            self.lm.tr('cat14_franchises', '14. Kiralanan Varlıkların Kullanımı'),
            self.lm.tr('cat15_investments', '15. Franchising')
        ]
        category_combo.pack(anchor='w', padx=20, pady=(0, 15))

        # Hedef Tipi
        tk.Label(form_frame, text=self.lm.tr('lbl_target_type', "Hedef Tipi:"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        target_type_var = tk.StringVar()
        target_type_combo = ttk.Combobox(form_frame, textvariable=target_type_var, width=50)
        target_type_combo['values'] = [
            self.lm.tr('target_absolute_reduction', 'Mutlak Emisyon Azaltımı'),
            self.lm.tr('target_intensity_reduction', 'Yoğunluk Azaltımı'),
            self.lm.tr('target_renewable_energy', 'Yenilenebilir Enerji Oranı'),
            self.lm.tr('target_sustainable_procurement', 'Sürdürülebilir Satın Alma'),
            self.lm.tr('target_supplier_compliance', 'Tedarikçi Uyumluluğu'),
            self.lm.tr('target_circular_economy', 'Döngüsel Ekonomi'),
            self.lm.tr('target_carbon_neutral', 'Karbon Nötr'),
            self.lm.tr('target_net_zero', 'Net Sıfır')
        ]
        target_type_combo.pack(anchor='w', padx=20, pady=(0, 15))

        # Baz Yılı
        tk.Label(form_frame, text=self.lm.tr('lbl_baseline_year', "Baz Yılı:"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        baseline_year_var = tk.StringVar(value="2024")
        baseline_year_entry = tk.Entry(form_frame, textvariable=baseline_year_var, font=('Segoe UI', 11), width=50)
        baseline_year_entry.pack(anchor='w', padx=20, pady=(0, 15))

        # Hedef Yılı
        tk.Label(form_frame, text=self.lm.tr('lbl_target_year', "Hedef Yılı:"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        target_year_var = tk.StringVar(value="2030")
        target_year_entry = tk.Entry(form_frame, textvariable=target_year_var, font=('Segoe UI', 11), width=50)
        target_year_entry.pack(anchor='w', padx=20, pady=(0, 15))

        # Baz Emisyon
        tk.Label(form_frame, text=self.lm.tr('lbl_baseline_emission', "Baz Emisyon (tCO2e):"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        baseline_emission_var = tk.StringVar()
        baseline_emission_entry = tk.Entry(form_frame, textvariable=baseline_emission_var, font=('Segoe UI', 11), width=50)
        baseline_emission_entry.pack(anchor='w', padx=20, pady=(0, 15))

        # Hedef Emisyon
        tk.Label(form_frame, text=self.lm.tr('lbl_target_emission', "Hedef Emisyon (tCO2e):"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        target_emission_var = tk.StringVar()
        target_emission_entry = tk.Entry(form_frame, textvariable=target_emission_var, font=('Segoe UI', 11), width=50)
        target_emission_entry.pack(anchor='w', padx=20, pady=(0, 15))

        # Azaltım Yüzdesi
        tk.Label(form_frame, text=self.lm.tr('lbl_reduction_percentage', "Azaltım Yüzdesi (%):"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        reduction_var = tk.StringVar()
        reduction_entry = tk.Entry(form_frame, textvariable=reduction_var, font=('Segoe UI', 11), width=50)
        reduction_entry.pack(anchor='w', padx=20, pady=(0, 15))

        # Hedef Açıklaması
        tk.Label(form_frame, text=self.lm.tr('lbl_target_description', "Hedef Açıklaması:"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        description_text = tk.Text(form_frame, height=4, width=50, font=('Segoe UI', 11))
        description_text.pack(anchor='w', padx=20, pady=(0, 20))

        # Butonlar
        button_frame = tk.Frame(form_window, bg='#f8f9fa')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))

        def save_target() -> None:
            """Hedef verisini kaydet"""
            try:
                # Form verilerini al
                category = category_var.get().strip()
                target_type = target_type_var.get().strip()
                baseline_year = baseline_year_var.get().strip()
                target_year = target_year_var.get().strip()
                baseline_emission = baseline_emission_var.get().strip()
                target_emission = target_emission_var.get().strip()
                reduction = reduction_var.get().strip()
                description = description_text.get(1.0, tk.END).strip()

                # Validasyon
                if not all([category, target_type, baseline_year, target_year]):
                    messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('error_missing_fields', "Lütfen zorunlu alanları doldurun!"))
                    return

                # Sayısal değerleri kontrol et
                try:
                    baseline_year_val = int(baseline_year)
                    target_year_val = int(target_year)

                    if baseline_emission:
                        baseline_emission_val = float(baseline_emission)
                    else:
                        baseline_emission_val = None

                    if target_emission:
                        target_emission_val = float(target_emission)
                    else:
                        target_emission_val = None

                    if reduction:
                        reduction_val = float(reduction)
                    else:
                        reduction_val = None

                except ValueError:
                    messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('error_year_numeric', "Yıl sayısal, emisyon ve azaltım değerleri sayısal olmalıdır!"))
                    return

                # Hedef verisini kaydet
                target_data = {
                    'company_id': self.company_id,
                    'category': category,
                    'target_type': target_type,
                    'baseline_year': baseline_year_val,
                    'target_year': target_year_val,
                    'baseline_emissions': baseline_emission_val,
                    'target_emissions': target_emission_val,
                    'reduction_percentage': reduction_val,
                    'target_description': description
                }

                result = self.manager.add_target_record(target_data)

                if result:
                    messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('success_target_added', "Hedef başarıyla eklendi!"))
                    form_window.destroy()
                    self.load_data()  # Verileri yenile
                else:
                    messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('error_target_add_failed', "Hedef eklenirken hata oluştu!"))

            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_save', 'Kaydetme hatası')}: {e}")

        def cancel_form() -> None:
            """Formu iptal et"""
            form_window.destroy()

        # Butonlar
        tk.Button(button_frame, text=self.lm.tr('btn_save', " Kaydet"), command=save_target,
                 font=('Segoe UI', 11, 'bold'), bg='#e74c3c', fg='white',
                 padx=20, pady=10).pack(side='left', padx=(0, 10))

        tk.Button(button_frame, text=self.lm.tr('btn_cancel', " İptal"), command=cancel_form,
                 font=('Segoe UI', 11, 'bold'), bg='#95a5a6', fg='white',
                 padx=20, pady=10).pack(side='left')

    def generate_report(self) -> None:
        """Scope 3 raporu oluştur"""
        # Rapor seçenekleri penceresi
        report_window = tk.Toplevel(self.parent)
        report_window.title(self.lm.tr('scope3_report_title', " Scope 3 Raporu Oluştur"))
        report_window.geometry("500x400")
        report_window.configure(bg='#f8f9fa')
        report_window.grab_set()

        # Başlık
        header_frame = tk.Frame(report_window, bg='#9b59b6', height=50)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text=self.lm.tr('scope3_report_header', " Scope 3 Raporu Oluştur"),
                font=('Segoe UI', 14, 'bold'), fg='white', bg='#9b59b6').pack(expand=True)

        # Ana içerik
        main_frame = tk.Frame(report_window, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Form alanları
        form_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        form_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Rapor Adı
        tk.Label(form_frame, text=self.lm.tr('lbl_report_name', "Rapor Adı:"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(20, 5))
        report_name_var = tk.StringVar(value=self.lm.tr('default_report_name', "Scope 3 Emisyon Raporu 2024"))
        report_name_entry = tk.Entry(form_frame, textvariable=report_name_var, font=('Segoe UI', 11), width=50)
        report_name_entry.pack(anchor='w', padx=20, pady=(0, 15))

        # Rapor Dönemi
        tk.Label(form_frame, text=self.lm.tr('lbl_report_period', "Raporlama Dönemi:"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        period_var = tk.StringVar(value="2024")
        period_entry = tk.Entry(form_frame, textvariable=period_var, font=('Segoe UI', 11), width=50)
        period_entry.pack(anchor='w', padx=20, pady=(0, 15))

        # Rapor Formatı
        tk.Label(form_frame, text=self.lm.tr('lbl_report_format', "Rapor Formatı:"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        format_var = tk.StringVar(value="Excel")
        format_combo = ttk.Combobox(form_frame, textvariable=format_var, width=50)
        format_combo['values'] = ['Excel', 'PDF', 'DOCX', 'CSV']
        format_combo.pack(anchor='w', padx=20, pady=(0, 15))

        # Rapor İçeriği
        tk.Label(form_frame, text=self.lm.tr('lbl_report_content', "Rapor İçeriği:"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(10, 5))

        content_frame = tk.Frame(form_frame, bg='white')
        content_frame.pack(anchor='w', padx=20, pady=(0, 15))

        # Checkbox'lar
        include_emissions_var = tk.BooleanVar(value=True)
        include_targets_var = tk.BooleanVar(value=True)
        include_summary_var = tk.BooleanVar(value=True)
        include_charts_var = tk.BooleanVar(value=False)

        tk.Checkbutton(content_frame, text=self.lm.tr('chk_emission_data', "Emisyon Verileri"), variable=include_emissions_var,
                      bg='white', font=('Segoe UI', 10)).pack(anchor='w')
        tk.Checkbutton(content_frame, text=self.lm.tr('chk_targets', "Hedefler"), variable=include_targets_var,
                      bg='white', font=('Segoe UI', 10)).pack(anchor='w')
        tk.Checkbutton(content_frame, text=self.lm.tr('chk_summary_stats', "Özet İstatistikler"), variable=include_summary_var,
                      bg='white', font=('Segoe UI', 10)).pack(anchor='w')
        tk.Checkbutton(content_frame, text=self.lm.tr('chk_charts', "Grafikler"), variable=include_charts_var,
                      bg='white', font=('Segoe UI', 10)).pack(anchor='w')

        # Butonlar
        button_frame = tk.Frame(report_window, bg='#f8f9fa')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))

        def create_report() -> None:
            """Rapor oluştur"""
            try:
                report_name = report_name_var.get().strip()
                period = period_var.get().strip()
                report_format = format_var.get().strip()

                if not all([report_name, period, report_format]):
                    messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('error_missing_fields', "Lütfen tüm alanları doldurun!"))
                    return

                # Rapor içeriği seçenekleri
                content_options = {
                    'include_emissions': include_emissions_var.get(),
                    'include_targets': include_targets_var.get(),
                    'include_summary': include_summary_var.get(),
                    'include_charts': include_charts_var.get()
                }

                # Rapor oluştur
                result = self.manager.generate_scope3_report(
                    company_id=self.company_id,
                    report_name=report_name,
                    period=period,
                    format_type=report_format,
                    content_options=content_options
                )

                if result:
                    self.last_scope3_report_path = result
                    messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('success_report_created', "Rapor başarıyla oluşturuldu!\nDosya: {result}").format(result=result))
                    report_window.destroy()
                else:
                    messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('error_report_failed', "Rapor oluşturulurken hata oluştu!"))

            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_report_creation', 'Rapor oluşturma hatası')}: {e}")

        def cancel_report() -> None:
            """Rapor oluşturmayı iptal et"""
            report_window.destroy()

        # Butonlar
        ttk.Button(button_frame, text=self.lm.tr('create_report', " Rapor Oluştur"), style='Primary.TButton', command=create_report).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text=self.lm.tr('btn_cancel', " İptal"), command=cancel_report).pack(side='left')

    def open_report_center_scope3(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('karbon')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for karbon: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_report_center_open', 'Rapor Merkezi açılamadı')}:\n{e}")
            logging.error(f"Error opening report center: {e}")

    def _scope3_fill_preview_text(self) -> None:
        try:
            period = self.scope3_report_period_var.get().strip()
            if not period or not period.isdigit() or len(period) != 4:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('warning_invalid_year', "Geçerli bir yıl girin (örn. 2025)"))
                return
            summary = self.manager.get_emissions_summary(self.company_id, period)
            emissions = self.manager.get_emission_data(self.company_id, period)
            self.scope3_report_text.delete('1.0', tk.END)
            self.scope3_report_text.insert(tk.END, f"{self.lm.tr('scope3_report_title_preview', 'Scope 3 Emisyon Raporu')} - {period}\n")
            self.scope3_report_text.insert(tk.END, f"{self.lm.tr('total_emissions', 'Toplam Emisyon')}: {summary.get('total_emissions', 0):.2f} tCO2e\n")
            self.scope3_report_text.insert(tk.END, f"{self.lm.tr('upstream', 'Upstream')}: {summary.get('upstream_emissions', 0):.2f} tCO2e\n")
            self.scope3_report_text.insert(tk.END, f"{self.lm.tr('downstream', 'Downstream')}: {summary.get('downstream_emissions', 0):.2f} tCO2e\n\n")
            for e in emissions[:50]:
                self.scope3_report_text.insert(tk.END, f"{self.lm.tr('category', 'Kategori')} {e.get('category_number')}: {e.get('category_name')}\n")
                self.scope3_report_text.insert(tk.END, f"  {self.lm.tr('activity', 'Aktivite')}: {e.get('activity_data')} {e.get('activity_unit')}\n")
                self.scope3_report_text.insert(tk.END, f"  {self.lm.tr('total_emissions', 'Toplam Emisyon')}: {e.get('total_emissions')} tCO2e\n")
                self.scope3_report_text.insert(tk.END, f"  {self.lm.tr('source', 'Kaynak')}: {e.get('data_source') or '—'}\n\n")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_preview', 'Önizleme hatası')}: {e}")

    def _scope3_save_preview_text(self) -> None:
        try:
            content = self.scope3_report_text.get('1.0', tk.END)
            if not content.strip():
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('warning_empty_preview', 'Önizleme içeriği boş'))
                return
            period = self.scope3_report_period_var.get().strip()
            fp = filedialog.asksaveasfilename(
                defaultextension='.txt',
                filetypes=[(self.lm.tr('text_file', 'Metin'),'*.txt')],
                initialfile=f"scope3_report_{self.company_id}_{period}.txt",
                title=self.lm.tr('save_report', "Raporu Kaydet")
            )
            if not fp:
                return
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo(self.lm.tr('info', 'Bilgi'), f"{self.lm.tr('success_report_saved', 'Rapor metni kaydedildi')}: {fp}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('error_save', 'Kaydetme hatası')}: {e}")

    def _scope3_export_preview_docx(self) -> None:
        try:
            period = self.scope3_report_period_var.get().strip()
            if not period or not period.isdigit() or len(period) != 4:
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('warning_invalid_year', 'Geçerli bir yıl girin (örn. 2025)'))
                return
            result = self.manager.generate_scope3_report(
                company_id=self.company_id,
                report_name=f"{self.lm.tr('scope3_report_title_preview', 'Scope 3 Emisyon Raporu')} {period}",
                period=period,
                format_type='docx',
                content_options={'include_emissions': True, 'include_targets': True, 'include_summary': True}
            )
            if not result:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('error_docx_failed', 'DOCX oluşturulamadı'))
                return
            self.last_scope3_report_path = result
            out = filedialog.asksaveasfilename(
                defaultextension='.docx',
                filetypes=[(self.lm.tr('word_files', 'Word Dosyaları'),'*.docx')],
                initialfile=os.path.basename(result),
                title=self.lm.tr('save_report', "Raporu Kaydet")
            )
            if out:
                try:
                    import shutil
                    shutil.copyfile(result, out)
                    messagebox.showinfo(self.lm.tr('info', 'Bilgi'), f"{self.lm.tr('success_docx_created', 'DOCX raporu oluşturuldu')}: {out}")
                except Exception as e:
                    messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('error_file_copy', 'Dosya kopyalama hatası')}: {e}")
            else:
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), f"{self.lm.tr('success_docx_created', 'DOCX raporu oluşturuldu')}: {result}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('error_docx_creation', 'DOCX oluşturma hatası')}: {e}")

    def _scope3_print_preview_text(self) -> None:
        try:
            import tempfile
            content = self.scope3_report_text.get('1.0', tk.END)
            if not content.strip():
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('warning_empty_preview', 'Önizleme içeriği boş'))
                return
            tmp_dir = tempfile.gettempdir()
            tmp_path = os.path.join(tmp_dir, f"scope3_preview_{self.company_id}_{self.scope3_report_period_var.get()}.txt")
            with open(tmp_path, 'w', encoding='utf-8') as f:
                f.write(content)
            try:
                os.startfile(tmp_path, 'print')
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('info_print_started', 'Yazdırma başlatıldı'))
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('error_print', 'Yazdırma hatası')}: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('error_print_prep', 'Yazdırmaya hazırlık hatası')}: {e}")

    def _scope3_open_last_report(self) -> None:
        try:
            if self.last_scope3_report_path and os.path.exists(self.last_scope3_report_path):
                os.startfile(self.last_scope3_report_path)
            else:
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('warning_no_report', 'Açılacak rapor bulunamadı'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('error_open', 'Açma hatası')}: {e}")

    def _scope3_copy_preview_to_clipboard(self) -> None:
        try:
            content = self.scope3_report_text.get('1.0', tk.END)
            self.parent.clipboard_clear()
            self.parent.clipboard_append(content)
            messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('info_copied_to_clipboard', 'Önizleme metni panoya kopyalandı'))
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def _scope3_share_dialog(self) -> None:
        try:
            dialog = tk.Toplevel(self.parent)
            dialog.title(self.lm.tr('share', 'Paylaş'))
            dialog.geometry('360x180')
            dialog.grab_set()
            tk.Label(dialog, text=self.lm.tr('share_options', 'Paylaşım Seçenekleri'), font=('Segoe UI', 12, 'bold')).pack(pady=10)
            btns = tk.Frame(dialog)
            btns.pack(pady=10)
            def copy_path():
                path = self.last_scope3_report_path
                if path and os.path.exists(path):
                    self.parent.clipboard_clear()
                    self.parent.clipboard_append(path)
                    messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('info_path_copied', 'Dosya yolu panoya kopyalandı'))
                else:
                    messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('warning_no_file_to_share', 'Paylaşılacak dosya bulunamadı'))
            def open_folder():
                path = self.last_scope3_report_path
                if path and os.path.exists(path):
                    os.startfile(os.path.dirname(path))
                else:
                    messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('warning_folder_open_failed', 'Klasör açılamadı'))
            def copy_text():
                content = self.scope3_report_text.get('1.0', tk.END)
                self.parent.clipboard_clear()
                self.parent.clipboard_append(content)
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('info_copied_to_clipboard', 'Önizleme metni panoya kopyalandı'))
            tk.Button(btns, text=self.lm.tr('copy_path', 'Dosya Yolunu Kopyala'), command=copy_path, bg='#0ea5e9', fg='white').pack(side='left', padx=6)
            tk.Button(btns, text=self.lm.tr('open_folder', 'Klasörü Aç'), command=open_folder, bg='#2563eb', fg='white').pack(side='left', padx=6)
            tk.Button(btns, text=self.lm.tr('copy_preview', 'Önizleme Metnini Kopyala'), command=copy_text, bg='#6b7280', fg='white').pack(side='left', padx=6)
            tk.Button(dialog, text=self.lm.tr('btn_close', 'Kapat'), command=dialog.destroy).pack(pady=8)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('error_share', 'Paylaşım hatası')}: {e}")
