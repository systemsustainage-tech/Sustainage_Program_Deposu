#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
"""
KARBON OFFSET MODÜLÜ GUI
Offset proje yönetimi, satın alma, net emisyon görüntüleme
"""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from utils.language_manager import LanguageManager
from .offset_calculator import OffsetCalculator
from .offset_manager import OffsetManager
from config.icons import Icons

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class OffsetGUI:
    """Karbon Offset Modülü Arayüzü"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()
        self.offset_manager = OffsetManager()
        self.calculator = OffsetCalculator()

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Offset modülü arayüzü"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Başlık
        header_frame = tk.Frame(main_frame, bg='#27ae60', height=70)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text=f"{Icons.TREE} {self.lm.tr('carbon_offset_management', 'Karbon Offset Yönetimi')}",
                              font=('Segoe UI', 18, 'bold'), fg='white', bg='#27ae60')
        title_label.pack(side='left', padx=20, pady=15)

        subtitle_label = tk.Label(header_frame, text=self.lm.tr('net_zero_path', "Net Sıfır Hedefine Giden Yol"),
                                 font=('Segoe UI', 11), fg='#d5f4e6', bg='#27ae60')
        subtitle_label.pack(side='left')

        # Dashboard Kartları
        self.create_dashboard_cards(main_frame)

        # Ana içerik - Sekmeler
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Sekmeler
        self.create_net_emissions_tab()
        self.create_offset_projects_tab()
        self.create_offset_purchases_tab()
        self.create_budget_planning_tab()
        self.create_certificates_tab()

    def create_dashboard_cards(self, parent) -> None:
        """Dashboard istatistik kartları"""
        stats_frame = tk.Frame(parent, bg='#f5f5f5')
        stats_frame.pack(fill='x', pady=(0, 15))

        # Mevcut dönem için net emisyon al
        current_year = datetime.now().year
        current_period = str(current_year)

        try:
            net_data = self.offset_manager.get_net_emissions(self.company_id, current_period)
            stats = self.offset_manager.get_offset_statistics(self.company_id)
        except Exception:
            net_data = None
            stats = {}

        # Varsayılan değerler
        if net_data:
            total_gross = net_data.get('total_gross', 0)
            total_offset = net_data.get('total_offset', 0)
            total_net = net_data.get('total_net', 0)
            carbon_neutral = net_data.get('carbon_neutral', False)
            offset_pct = net_data.get('offset_percentage', 0)
        else:
            total_gross = 0
            total_offset = 0
            total_net = 0
            carbon_neutral = False
            offset_pct = 0

        total_cost = stats.get('total_cost_usd', 0)
        avg_price = stats.get('avg_unit_price', 0)

        # Kartlar
        cards = [
            (f"{Icons.REPORT} {self.lm.tr('gross_emission', 'Brüt Emisyon')}", f"{total_gross:.1f} tCO2e",
             f"{current_year} {self.lm.tr('period', 'Dönemi')}", "#e74c3c"),
            (f"{Icons.TREE} {self.lm.tr('total_offset', 'Toplam Offset')}", f"{total_offset:.1f} tCO2e",
             f"%{offset_pct:.1f} {self.lm.tr('coverage', 'Kapsama')}", "#27ae60"),
            (self.lm.tr('net_emission', "✨ Net Emisyon"), f"{total_net:.1f} tCO2e",
             self.lm.tr('carbon_neutral', "Karbon Nötr") if carbon_neutral else self.lm.tr('target_continuing', "Hedef Devam Ediyor"),
             "#2ecc71" if carbon_neutral else "#f39c12"),
            (self.lm.tr('total_cost', "💰 Toplam Maliyet"), f"${total_cost:,.0f}",
             f"{self.lm.tr('avg_abbr', 'Ort.')} ${avg_price:.2f}/tCO2e", "#3498db"),
            (self.lm.tr('carbon_neutral_status', "🎯 Karbon Nötr Durum"),
             f"{Icons.SUCCESS} {self.lm.tr('achieved', 'BAŞARILDI')}" if carbon_neutral else f"{Icons.WAIT} {self.lm.tr('continuing', 'Devam Ediyor')}",
             f"{100 - offset_pct:.1f}% {self.lm.tr('missing', 'Eksik')}" if not carbon_neutral else self.lm.tr('target_completed', "Hedef Tamamlandı"),
             "#2ecc71" if carbon_neutral else "#e67e22")
        ]

        for i, (title, value, subtitle, color) in enumerate(cards):
            card = tk.Frame(stats_frame, bg=color, relief='raised', bd=2)
            card.grid(row=0, column=i, padx=5, sticky='ew')
            stats_frame.columnconfigure(i, weight=1)

            tk.Label(card, text=title, font=('Segoe UI', 9),
                    fg='white', bg=color).pack(anchor='w', padx=10, pady=(8, 2))
            tk.Label(card, text=value, font=('Segoe UI', 16, 'bold'),
                    fg='white', bg=color).pack(anchor='w', padx=10)
            tk.Label(card, text=subtitle, font=('Segoe UI', 8),
                    fg='white', bg=color).pack(anchor='w', padx=10, pady=(0, 8))

    # ==================== SEKME 1: NET EMİSYON DASHBOARD ====================

    def create_net_emissions_tab(self) -> None:
        """Net emisyon görselleştirme"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=f"{Icons.REPORT} {self.lm.tr('net_emission_dashboard', 'Net Emisyon Dashboard')}")

        # Dönem seçimi
        control_frame = tk.Frame(tab, bg='white', relief='groove', bd=2)
        control_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(control_frame, text=self.lm.tr('period', "Dönem") + ":", font=('Segoe UI', 10, 'bold')).pack(side='left', padx=10)

        self.period_var = tk.StringVar(value=str(datetime.now().year))
        period_combo = ttk.Combobox(control_frame, textvariable=self.period_var, width=15)
        period_combo['values'] = [str(y) for y in range(2020, 2031)]
        period_combo.pack(side='left', padx=5)

        tk.Button(control_frame, text=f"{Icons.LOADING} {self.lm.tr('btn_refresh', 'Yenile')}", command=self.refresh_net_emissions,
                 bg='#3498db', fg='white', font=('Segoe UI', 9)).pack(side='left', padx=5)

        tk.Button(control_frame, text=self.lm.tr('recalculate', "🔢 Yeniden Hesapla"), command=self.recalculate_net,
                 bg='#e67e22', fg='white', font=('Segoe UI', 9)).pack(side='left', padx=5)

        # Net emisyon kartları
        self.net_cards_frame = tk.Frame(tab, bg='#f5f5f5')
        self.net_cards_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.refresh_net_emissions()

    def refresh_net_emissions(self) -> None:
        """Net emisyon verilerini yenile"""
        # Eski kartları temizle
        for widget in self.net_cards_frame.winfo_children():
            widget.destroy()

        period = self.period_var.get()
        net_data = self.offset_manager.get_net_emissions(self.company_id, period)

        if not net_data:
            tk.Label(self.net_cards_frame,
                    text=f"{Icons.FAIL} {period} {self.lm.tr('no_data_for_period', 'dönemi için veri bulunamadı')}",
                    font=('Segoe UI', 12), fg='red').pack(pady=50)
            return

        # Scope bazlı görselleştirme
        scopes = [
            (self.lm.tr('scope1_direct_emissions', 'Scope 1 - Doğrudan Emisyonlar'),
             net_data.get('scope1_gross', 0),
             net_data.get('scope1_offset', 0),
             net_data.get('scope1_net', 0), '#e74c3c'),
            (self.lm.tr('scope2_indirect_emissions', 'Scope 2 - Dolaylı Emisyonlar'),
             net_data.get('scope2_gross', 0),
             net_data.get('scope2_offset', 0),
             net_data.get('scope2_net', 0), '#f39c12'),
            (self.lm.tr('scope3_value_chain', 'Scope 3 - Değer Zinciri'),
             net_data.get('scope3_gross', 0),
             net_data.get('scope3_offset', 0),
             net_data.get('scope3_net', 0), '#9b59b6'),
            (self.lm.tr('total_upper', 'TOPLAM'),
             net_data.get('total_gross', 0),
             net_data.get('total_offset', 0),
             net_data.get('total_net', 0), '#2c3e50')
        ]

        for i, (scope_name, gross, offset, net, color) in enumerate(scopes):
            scope_frame = tk.Frame(self.net_cards_frame, bg='white', relief='raised', bd=2)
            scope_frame.pack(fill='x', padx=10, pady=5)

            # Başlık
            header = tk.Frame(scope_frame, bg=color, height=40)
            header.pack(fill='x')
            header.pack_propagate(False)
            tk.Label(header, text=scope_name, font=('Segoe UI', 11, 'bold'),
                    fg='white', bg=color).pack(side='left', padx=15, pady=10)

            # İçerik
            content = tk.Frame(scope_frame, bg='white')
            content.pack(fill='x', padx=15, pady=10)

            # Brüt
            col1 = tk.Frame(content, bg='white')
            col1.pack(side='left', expand=True, fill='x')
            tk.Label(col1, text=self.lm.tr('gross_emission', "Brüt Emisyon"), font=('Segoe UI', 9),
                    fg='#7f8c8d', bg='white').pack()
            tk.Label(col1, text=f"{gross:.2f} tCO2e", font=('Segoe UI', 14, 'bold'),
                    fg='#e74c3c', bg='white').pack()

            # Offset
            col2 = tk.Frame(content, bg='white')
            col2.pack(side='left', expand=True, fill='x')
            tk.Label(col2, text=f"(-) {self.lm.tr('offset', 'Offset')}", font=('Segoe UI', 9),
                    fg='#7f8c8d', bg='white').pack()
            tk.Label(col2, text=f"{offset:.2f} tCO2e", font=('Segoe UI', 14, 'bold'),
                    fg='#27ae60', bg='white').pack()

            # Net
            col3 = tk.Frame(content, bg='white')
            col3.pack(side='left', expand=True, fill='x')
            tk.Label(col3, text=f"(=) {self.lm.tr('net_emission', 'Net Emisyon')}", font=('Segoe UI', 9),
                    fg='#7f8c8d', bg='white').pack()
            tk.Label(col3, text=f"{net:.2f} tCO2e", font=('Segoe UI', 14, 'bold'),
                    fg='#2c3e50', bg='white').pack()

            # Progress bar
            if gross > 0:
                reduction_pct = (offset / gross * 100)
                progress_frame = tk.Frame(scope_frame, bg='white')
                progress_frame.pack(fill='x', padx=15, pady=(0, 10))

                canvas = tk.Canvas(progress_frame, height=25, bg='#ecf0f1',
                                  highlightthickness=0)
                canvas.pack(fill='x')

                min(reduction_pct, 100) / 100 * canvas.winfo_reqwidth()
                canvas.create_rectangle(0, 0, 500 * reduction_pct / 100, 25,
                                       fill='#27ae60', outline='')
                canvas.create_text(250, 12, text=f"{self.lm.tr('offset_coverage', 'Offset Kapsaması')}: %{reduction_pct:.1f}",
                                  font=('Segoe UI', 9, 'bold'), fill='#2c3e50')

    def recalculate_net(self) -> None:
        """Net emisyonu yeniden hesapla"""
        period = self.period_var.get()
        result = self.offset_manager.recalculate_net_emissions(self.company_id, period)

        if result:
            messagebox.showinfo(self.lm.tr('success', "Başarılı"),
                              f"{period} {self.lm.tr('net_emissions_recalculated', 'dönemi net emisyonlar yeniden hesaplandı!')}")
            self.refresh_net_emissions()
        else:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('net_emission_calc_error', "Net emisyon hesaplanamadı!"))

    # ==================== SEKME 2: OFFSET PROJELERİ ====================

    def create_offset_projects_tab(self) -> None:
        """Offset projelerini yönet"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=self.lm.tr('offset_projects', "🌲 Offset Projeleri"))

        # Butonlar
        btn_frame = tk.Frame(tab, bg='white')
        btn_frame.pack(fill='x', padx=10, pady=10)

        tk.Button(btn_frame, text=f"{Icons.ADD} {self.lm.tr('add_new_project', 'Yeni Proje Ekle')}", command=self.add_offset_project,
                 bg='#27ae60', fg='white', font=('Segoe UI', 10)).pack(side='left', padx=5)

        tk.Button(btn_frame, text=f"{Icons.LOADING} {self.lm.tr('btn_refresh', 'Yenile')}", command=self.load_offset_projects,
                 bg='#3498db', fg='white', font=('Segoe UI', 10)).pack(side='left', padx=5)

        # Treeview
        tree_frame = tk.Frame(tab)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')

        self.projects_tree = ttk.Treeview(tree_frame,
                                         columns=('Proje Adı', 'Tip', 'Standart', 'Ülke',
                                                 'Yıl', 'Birim Fiyat', 'Doğrulama'),
                                         show='tree headings',
                                         yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.projects_tree.yview)

        # Başlıklar
        self.projects_tree.heading('#0', text=self.lm.tr('col_id', 'ID'))
        self.projects_tree.heading('Proje Adı', text=self.lm.tr('project_name', 'Proje Adı'))
        self.projects_tree.heading('Tip', text=self.lm.tr('project_type', 'Proje Tipi'))
        self.projects_tree.heading('Standart', text=self.lm.tr('standard', 'Standart'))
        self.projects_tree.heading('Ülke', text=self.lm.tr('country', 'Ülke'))
        self.projects_tree.heading('Yıl', text=self.lm.tr('vintage', 'Vintage'))
        self.projects_tree.heading('Birim Fiyat', text=self.lm.tr('col_unit_price_tco2e', '$/tCO2e'))
        self.projects_tree.heading('Doğrulama', text=self.lm.tr('verification', 'Doğrulama'))

        # Genişlikler
        self.projects_tree.column('#0', width=50)
        self.projects_tree.column('Proje Adı', width=200)
        self.projects_tree.column('Tip', width=120)
        self.projects_tree.column('Standart', width=100)
        self.projects_tree.column('Ülke', width=100)
        self.projects_tree.column('Yıl', width=60)
        self.projects_tree.column('Birim Fiyat', width=80)
        self.projects_tree.column('Doğrulama', width=100)

        self.projects_tree.pack(fill='both', expand=True)

        self.load_offset_projects()

    def load_offset_projects(self) -> None:
        """Projeleri yükle"""
        # Temizle
        for item in self.projects_tree.get_children():
            self.projects_tree.delete(item)

        # Yükle
        projects = self.offset_manager.get_offset_projects()

        for project in projects:
            self.projects_tree.insert('', 'end', text=project['id'],
                                     values=(
                                         project['project_name'],
                                         project['project_type'],
                                         project['standard'],
                                         project.get('location_country', 'N/A'),
                                         project.get('vintage_year', 'N/A'),
                                         f"${project.get('unit_price_usd', 0):.2f}",
                                         project.get('verification_status', 'N/A')
                                     ))

    def add_offset_project(self) -> None:
        """Yeni offset projesi ekle"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('new_offset_project', "Yeni Offset Projesi"))
        dialog.geometry("600x700")
        dialog.transient(self.parent)
        dialog.grab_set()

        # Form
        form = tk.Frame(dialog, bg='white', padx=20, pady=20)
        form.pack(fill='both', expand=True)

        # Başlık
        tk.Label(form, text=self.lm.tr('add_new_offset_project', "🌲 Yeni Offset Projesi Ekle"),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=(0, 20))

        # Alanlar
        fields = {}

        row_num = 0
        for label_text, key, field_type in [
            (self.lm.tr('project_name', "Proje Adı") + " *", "project_name", "entry"),
            (self.lm.tr('project_type', "Proje Tipi") + " *", "project_type", "combo"),
            (self.lm.tr('standard', "Standart") + " *", "standard", "combo"),
            (self.lm.tr('registry_cert_no', "Kayıt/Sertifika No"), "registry_id", "entry"),
            (self.lm.tr('country', "Ülke"), "location_country", "entry"),
            (self.lm.tr('region', "Bölge"), "location_region", "entry"),
            (self.lm.tr('vintage_year', "Vintage Yıl"), "vintage_year", "entry"),
            (self.lm.tr('unit_price_usd', "Birim Fiyat ($/tCO2e)"), "unit_price_usd", "entry"),
            (self.lm.tr('supplier', "Tedarikçi"), "supplier_name", "entry"),
            (self.lm.tr('contract_no', "Sözleşme No"), "contract_number", "entry"),
        ]:
            tk.Label(form, text=label_text, font=('Segoe UI', 10),
                    bg='white', anchor='w').grid(row=row_num, column=0, sticky='w', pady=5)

            if field_type == "entry":
                entry = tk.Entry(form, width=40, font=('Segoe UI', 10))
                entry.grid(row=row_num, column=1, sticky='ew', pady=5)
                fields[key] = entry
            elif field_type == "combo":
                combo = ttk.Combobox(form, width=38, font=('Segoe UI', 10))
                if key == "project_type":
                    combo['values'] = list(self.offset_manager.PROJECT_CATEGORIES.keys())
                elif key == "standard":
                    combo['values'] = list(self.offset_manager.OFFSET_STANDARDS.keys())
                combo.grid(row=row_num, column=1, sticky='ew', pady=5)
                fields[key] = combo

            row_num += 1

        form.columnconfigure(1, weight=1)

        # Açıklama (Text area)
        tk.Label(form, text=self.lm.tr('description', "Açıklama"), font=('Segoe UI', 10),
                bg='white', anchor='w').grid(row=row_num, column=0, sticky='nw', pady=5)
        desc_text = tk.Text(form, width=40, height=4, font=('Segoe UI', 10))
        desc_text.grid(row=row_num, column=1, sticky='ew', pady=5)
        fields['project_description'] = desc_text
        row_num += 1

        # Notlar
        tk.Label(form, text=self.lm.tr('notes', "Notlar"), font=('Segoe UI', 10),
                bg='white', anchor='w').grid(row=row_num, column=0, sticky='nw', pady=5)
        notes_text = tk.Text(form, width=40, height=3, font=('Segoe UI', 10))
        notes_text.grid(row=row_num, column=1, sticky='ew', pady=5)
        fields['notes'] = notes_text

        # Butonlar
        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=10)

        def save_project():
            project_data = {}
            for key, widget in fields.items():
                if isinstance(widget, tk.Text):
                    project_data[key] = widget.get('1.0', 'end-1c')
                else:
                    project_data[key] = widget.get()

            # Zorunlu alanlar
            if not project_data.get('project_name'):
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('project_name_required', "Proje adı gerekli!"), parent=dialog)
                return

            # Sayısal değerler
            if project_data.get('vintage_year'):
                try:
                    project_data['vintage_year'] = int(project_data['vintage_year'])
                except Exception as e:
                    logging.error(f'Silent error in offset_gui.py: {str(e)}')

            if project_data.get('unit_price_usd'):
                try:
                    project_data['unit_price_usd'] = float(project_data['unit_price_usd'])
                except Exception as e:
                    logging.error(f'Silent error in offset_gui.py: {str(e)}')

            # Kaydet
            project_id = self.offset_manager.add_offset_project(project_data)

            if project_id:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"),
                                  f"{self.lm.tr('project_added', 'Proje başarıyla eklendi!')} (ID: {project_id})",
                                  parent=dialog)
                dialog.destroy()
                self.load_offset_projects()
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('project_add_error', "Proje eklenemedi!"), parent=dialog)

        tk.Button(btn_frame, text=f"{Icons.SAVE} {self.lm.tr('btn_save', 'Kaydet')}", command=save_project,
                 bg='#27ae60', fg='white', font=('Segoe UI', 10, 'bold'),
                 width=15).pack(side='left', padx=5)

        tk.Button(btn_frame, text=f"{Icons.FAIL} {self.lm.tr('btn_cancel', 'İptal')}", command=dialog.destroy,
                 bg='#e74c3c', fg='white', font=('Segoe UI', 10),
                 width=15).pack(side='left', padx=5)

    # ==================== SEKME 3: OFFSET SATIN ALMA ====================

    def create_offset_purchases_tab(self) -> None:
        """Offset satın alma işlemleri"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=self.lm.tr('offset_purchasing', "💰 Offset Satın Alma"))

        # Butonlar
        btn_frame = tk.Frame(tab, bg='white')
        btn_frame.pack(fill='x', padx=10, pady=10)

        tk.Button(btn_frame, text=self.lm.tr('new_purchase', "🛒 Yeni Satın Alma"), command=self.purchase_offset,
                 bg='#27ae60', fg='white', font=('Segoe UI', 10)).pack(side='left', padx=5)

        tk.Button(btn_frame, text=f"{Icons.LOADING} {self.lm.tr('btn_refresh', 'Yenile')}", command=self.load_offset_transactions,
                 bg='#3498db', fg='white', font=('Segoe UI', 10)).pack(side='left', padx=5)

        # Treeview
        tree_frame = tk.Frame(tab)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')

        self.transactions_tree = ttk.Treeview(tree_frame,
                                             columns=('Tarih', 'Proje', 'Dönem', 'Miktar',
                                                     'Birim Fiyat', 'Toplam', 'Durum'),
                                             show='tree headings',
                                             yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.transactions_tree.yview)

        # Başlıklar
        self.transactions_tree.heading('#0', text=self.lm.tr('col_id', 'ID'))
        self.transactions_tree.heading('Tarih', text=self.lm.tr('transaction_date', 'İşlem Tarihi'))
        self.transactions_tree.heading('Proje', text=self.lm.tr('project', 'Proje'))
        self.transactions_tree.heading('Dönem', text=self.lm.tr('period', 'Dönem'))
        self.transactions_tree.heading('Miktar', text=self.lm.tr('quantity_tco2e', 'Miktar (tCO2e)'))
        self.transactions_tree.heading('Birim Fiyat', text=self.lm.tr('col_unit_price_tco2e', '$/tCO2e'))
        self.transactions_tree.heading('Toplam', text=self.lm.tr('total_usd', 'Toplam ($)'))
        self.transactions_tree.heading('Durum', text=self.lm.tr('status', 'Durum'))

        self.transactions_tree.pack(fill='both', expand=True)

        self.load_offset_transactions()

    def load_offset_transactions(self) -> None:
        """İşlemleri yükle"""
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)

        transactions = self.offset_manager.get_offset_transactions(self.company_id)

        for trans in transactions:
            self.transactions_tree.insert('', 'end', text=trans['id'],
                                         values=(
                                             trans.get('transaction_date', 'N/A'),
                                             trans.get('project_name', 'N/A'),
                                             trans.get('period', 'N/A'),
                                             f"{trans.get('quantity_tco2e', 0):.2f}",
                                             f"${trans.get('unit_price_usd', 0):.2f}",
                                             f"${trans.get('total_cost_usd', 0):,.2f}",
                                             trans.get('retirement_status', 'N/A')
                                         ))

    def purchase_offset(self) -> None:
        """Offset satın al"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('offset_purchasing', "Offset Satın Alma"))
        dialog.geometry("500x600")
        dialog.transient(self.parent)
        dialog.grab_set()

        form = tk.Frame(dialog, bg='white', padx=20, pady=20)
        form.pack(fill='both', expand=True)

        tk.Label(form, text=self.lm.tr('new_offset_purchase', "🛒 Yeni Offset Satın Alma"),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=(0, 20))

        # Proje seçimi
        tk.Label(form, text=self.lm.tr('offset_project', "Offset Projesi") + " *", font=('Segoe UI', 10),
                bg='white', anchor='w').pack(fill='x', pady=(10, 2))

        projects = self.offset_manager.get_offset_projects()
        project_options = {f"{p['project_name']} ({p['standard']})": p['id']
                          for p in projects}

        if not project_options:
            messagebox.showwarning(self.lm.tr('warning', "Uyarı"),
                                 self.lm.tr('add_project_first', "Önce offset projesi eklemelisiniz!"),
                                 parent=dialog)
            dialog.destroy()
            return

        project_var = tk.StringVar()
        project_combo = ttk.Combobox(form, textvariable=project_var,
                                    values=list(project_options.keys()),
                                    font=('Segoe UI', 10), state='readonly')
        project_combo.pack(fill='x', pady=(0, 10))

        # Dönem
        tk.Label(form, text=self.lm.tr('period', "Dönem") + " *", font=('Segoe UI', 10),
                bg='white', anchor='w').pack(fill='x', pady=(10, 2))
        period_var = tk.StringVar(value=str(datetime.now().year))
        period_combo = ttk.Combobox(form, textvariable=period_var,
                                   values=[str(y) for y in range(2020, 2031)],
                                   font=('Segoe UI', 10))
        period_combo.pack(fill='x', pady=(0, 10))

        # Miktar
        tk.Label(form, text=self.lm.tr('quantity_tco2e', "Miktar (tCO2e)") + " *", font=('Segoe UI', 10),
                bg='white', anchor='w').pack(fill='x', pady=(10, 2))
        quantity_entry = tk.Entry(form, font=('Segoe UI', 10))
        quantity_entry.pack(fill='x', pady=(0, 10))

        # Birim fiyat
        tk.Label(form, text=self.lm.tr('unit_price_usd', "Birim Fiyat ($/tCO2e)") + " *", font=('Segoe UI', 10),
                bg='white', anchor='w').pack(fill='x', pady=(10, 2))
        price_entry = tk.Entry(form, font=('Segoe UI', 10))
        price_entry.pack(fill='x', pady=(0, 10))

        # Scope atama
        tk.Label(form, text=self.lm.tr('assign_scope', "Hangi Scope'a Atansın?") + " *", font=('Segoe UI', 10),
                bg='white', anchor='w').pack(fill='x', pady=(10, 2))
        scope_var = tk.StringVar(value='scope1_2')
        scope_combo = ttk.Combobox(form, textvariable=scope_var,
                                  values=['scope1', 'scope2', 'scope3', 'scope1_2'],
                                  font=('Segoe UI', 10), state='readonly')
        scope_combo.pack(fill='x', pady=(0, 10))

        # Amaç
        tk.Label(form, text=self.lm.tr('purpose', "Amaç"), font=('Segoe UI', 10),
                bg='white', anchor='w').pack(fill='x', pady=(10, 2))
        purpose_var = tk.StringVar(value='voluntary')
        purpose_combo = ttk.Combobox(form, textvariable=purpose_var,
                                    values=['voluntary', 'compliance', 'customer_commitment'],
                                    font=('Segoe UI', 10), state='readonly')
        purpose_combo.pack(fill='x', pady=(0, 10))

        # Butonlar
        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=10)

        def save_purchase():
            try:
                quantity = float(quantity_entry.get())
                unit_price = float(price_entry.get())
            except Exception:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('quantity_price_numeric', "Miktar ve fiyat sayısal olmalı!"),
                                     parent=dialog)
                return

            selected_project = project_var.get()
            if not selected_project:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_project', "Proje seçmelisiniz!"), parent=dialog)
                return

            project_id = project_options[selected_project]

            transaction_data = {
                'company_id': self.company_id,
                'project_id': project_id,
                'period': period_var.get(),
                'quantity_tco2e': quantity,
                'unit_price_usd': unit_price,
                'allocated_scope': scope_var.get(),
                'purpose': purpose_var.get(),
                'retirement_status': 'retired'  # Otomatik emekliye ayır
            }

            trans_id = self.offset_manager.purchase_offset(transaction_data)

            if trans_id:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"),
                                  f"{self.lm.tr('offset_purchased', 'Offset başarıyla satın alındı!')}\n"
                                  f"{self.lm.tr('quantity', 'Miktar')}: {quantity:.2f} tCO2e\n"
                                  f"{self.lm.tr('total', 'Toplam')}: ${quantity * unit_price:,.2f}",
                                  parent=dialog)
                dialog.destroy()
                self.load_offset_transactions()
                self.refresh_net_emissions()
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('transaction_save_error', "İşlem kaydedilemedi!"), parent=dialog)

        tk.Button(btn_frame, text=f"{Icons.SAVE} {self.lm.tr('purchase', 'Satın Al')}", command=save_purchase,
                 bg='#27ae60', fg='white', font=('Segoe UI', 10, 'bold'),
                 width=15).pack(side='left', padx=5)

        tk.Button(btn_frame, text=f"{Icons.FAIL} {self.lm.tr('btn_cancel', 'İptal')}", command=dialog.destroy,
                 bg='#e74c3c', fg='white', font=('Segoe UI', 10),
                 width=15).pack(side='left', padx=5)

    # ==================== SEKME 4: BÜTÇE PLANLAMA ====================

    def create_budget_planning_tab(self) -> None:
        """Bütçe planlama"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=self.lm.tr('budget_planning', "💵 Bütçe Planlama"))

        tk.Label(tab, text=self.lm.tr('budget_planning_soon', "🔜 Bütçe planlama modülü yakında..."),
                font=('Segoe UI', 14), fg='#7f8c8d').pack(expand=True)

    # ==================== SEKME 5: SERTİFİKALAR ====================

    def create_certificates_tab(self) -> None:
        """Karbon nötr sertifikaları"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=self.lm.tr('certificates', "🏆 Sertifikalar"))

        tk.Label(tab, text=self.lm.tr('certificates_soon', "🔜 Sertifika oluşturma yakında..."),
                font=('Segoe UI', 14), fg='#7f8c8d').pack(expand=True)

    def load_data(self) -> None:
        """Tüm verileri yükle"""
        try:
            self.load_offset_projects()
            self.load_offset_transactions()
        except Exception as e:
            logging.error(f"Veri yükleme hatası: {e}")


if __name__ == "__main__":
    # Test
    root = tk.Tk()
    root.title("Offset Modülü Test")
    root.geometry("1200x800")

    gui = OffsetGUI(root, company_id=1)

    root.mainloop()
