import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SKDM GUI - Sürdürülebilir Kalkınma Modülü Arayüzü
"""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from utils.language_manager import LanguageManager

from .skdm_manager import SKDMManager
from config.icons import Icons


class SKDMGUI:
    """SKDM Modülü GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.manager = SKDMManager()
        self.lm = LanguageManager()

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """SKDM arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#2E7D32', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=self.lm.tr("skdm_module_title", " SKDM Modülü"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#2E7D32')
        title_label.pack(expand=True)

        # Ana içerik alanı
        content_outer = tk.Frame(main_frame, bg='#f5f5f5')
        content_outer.pack(fill='both', expand=True)
        content_canvas = tk.Canvas(content_outer, bg='#f5f5f5', highlightthickness=0)
        content_scroll = ttk.Scrollbar(content_outer, orient='vertical', command=content_canvas.yview)
        content_frame = tk.Frame(content_canvas, bg='#f5f5f5')
        content_frame.bind('<Configure>', lambda e: content_canvas.configure(scrollregion=content_canvas.bbox('all')))
        content_canvas.create_window((0, 0), window=content_frame, anchor='nw')
        content_canvas.configure(yscrollcommand=content_scroll.set)
        content_canvas.pack(side='left', fill='both', expand=True)
        content_scroll.pack(side='right', fill='y')

        # Sol menü
        self.create_sidebar(content_frame)

        # Sağ içerik alanı
        self.content_area = tk.Frame(content_frame, bg='white', relief='raised', bd=1)
        self.content_area.pack(side='right', fill='both', expand=True, padx=(10, 0))

        # Varsayılan olarak genel bakışı göster
        self.show_overview()

    def create_sidebar(self, parent) -> None:
        """Sol menüyü oluştur"""
        sidebar = tk.Frame(parent, bg='#E8F5E8', width=200)
        sidebar.pack(side='left', fill='y', padx=(0, 10))
        sidebar.pack_propagate(False)

        # Menü başlığı
        menu_title = tk.Label(sidebar, text=self.lm.tr("skdm_module_title", "SKDM Modülü"),
                             font=('Segoe UI', 12, 'bold'), bg='#E8F5E8', fg='#2E7D32')
        menu_title.pack(pady=10)

        # Menü butonları
        buttons = [
            ("", self.lm.tr("skdm_menu_carbon", "Karbon"), self.show_carbon),
            ("", self.lm.tr("skdm_menu_water", "Su Yönetimi"), self.show_water),
            ("️", self.lm.tr("skdm_menu_waste", "Atık Yönetimi"), self.show_waste),
            ("", self.lm.tr("skdm_menu_supply_chain", "Tedarik Zinciri"), self.show_supply_chain),
            ("", self.lm.tr("skdm_menu_scope3", "Scope 3 Kategorileri"), self.show_scope3),
            ("", self.lm.tr("skdm_menu_emission_projects", "Emisyon Azaltma Projeleri"), self.show_emission_projects),
            ("", self.lm.tr("skdm_menu_stakeholders", "Paydaş Yönetimi"), self.show_stakeholders)
        ]

        for icon, text, command in buttons:
            btn = tk.Button(sidebar, text=f"{icon} {text}",
                           font=('Segoe UI', 10), bg='#4CAF50', fg='white',
                           relief='flat', bd=0, padx=20, pady=8,
                           command=command, anchor='w')
            btn.pack(fill='x', padx=10, pady=2)

    def clear_content(self) -> None:
        """İçerik alanını temizle"""
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def show_overview(self) -> None:
        """Genel bakış sayfası"""
        self.clear_content()

        # Başlık
        header = tk.Frame(self.content_area, bg='#4CAF50', height=64)
        header.pack(fill='x')
        header.pack_propagate(False)

        title_label = tk.Label(header, text=self.lm.tr("skdm_overview_title", " Emisyon Azaltma Projeleri"),
                              font=('Segoe UI', 13, 'bold'), fg='white', bg='#4CAF50')
        title_label.pack(expand=True)

        subtitle_label = tk.Label(header, text=self.lm.tr("skdm_overview_subtitle", "Karbon ayak izini azaltan projelerin yönetimi"),
                                 font=('Segoe UI', 9), fg='white', bg='#4CAF50')
        subtitle_label.pack()

        # Tab
        tab_frame = tk.Frame(self.content_area, bg='#E8F5E8', height=26)
        tab_frame.pack(fill='x', pady=(8, 0))
        tab_frame.pack_propagate(False)

        tab_label = tk.Label(tab_frame, text=self.lm.tr("skdm_tab_overview", "Genel Bakış"),
                            font=('Segoe UI', 9), bg='#E8F5E8', fg='#2E7D32',
                            relief='solid', bd=1)
        tab_label.pack(side='left', padx=10, pady=5)

        # İçerik
        content = tk.Frame(self.content_area, bg='white')
        content.pack(fill='both', expand=True, padx=12, pady=10)

        # KPI kartları
        self.create_kpi_cards(content)

        # Proje listesi
        self.create_project_list(content)

    def create_kpi_cards(self, parent) -> None:
        """KPI kartlarını oluştur"""
        kpi_frame = tk.Frame(parent, bg='white')
        kpi_frame.pack(fill='x', pady=(0, 10))

        # KPI verilerini al
        carbon_data = self.manager.get_carbon_summary(self.company_id)
        water_data = self.manager.get_water_summary(self.company_id)
        waste_data = self.manager.get_waste_summary(self.company_id)

        kpis = [
            (self.lm.tr("kpi_total_emissions", "Toplam Emisyon"), f"{carbon_data.get('total_emissions', 0):,.0f} tCO2e", "#FF5722"),
            (self.lm.tr("kpi_water_consumption", "Su Tüketimi"), f"{water_data.get('total_consumption', 0):,.0f} m³", "#2196F3"),
            (self.lm.tr("kpi_waste_production", "Atık Üretimi"), f"{waste_data.get('total_waste', 0):,.0f} ton", "#FF9800"),
            (self.lm.tr("kpi_renewable_energy", "Yenilenebilir Enerji"), f"%{carbon_data.get('renewable_energy', 0):.1f}", "#4CAF50")
        ]

        for i, (title, value, color) in enumerate(kpis):
            card = tk.Frame(kpi_frame, bg=color, relief='raised', bd=1)
            card.pack(side='left', fill='x', expand=True, padx=4)

            title_label = tk.Label(card, text=title, font=('Segoe UI', 9),
                                  bg=color, fg='white')
            title_label.pack(pady=(8, 4))

            value_label = tk.Label(card, text=value, font=('Segoe UI', 11, 'bold'),
                                  bg=color, fg='white')
            value_label.pack(pady=(0, 8))

    def create_project_list(self, parent) -> None:
        """Proje listesini oluştur"""
        projects_frame = tk.LabelFrame(parent, text=self.lm.tr("skdm_active_projects", "Aktif Projeler"),
                                      font=('Segoe UI', 10, 'bold'), bg='white')
        projects_frame.pack(fill='both', expand=True)

        # Proje listesi
        columns = (
            self.lm.tr("col_project_name", 'Proje Adı'),
            self.lm.tr("col_project_type", 'Tip'),
            self.lm.tr("col_start_date", 'Başlangıç'),
            self.lm.tr("col_expected_reduction", 'Beklenen Azalma'),
            self.lm.tr("col_status", 'Durum')
        )
        tree = ttk.Treeview(projects_frame, columns=columns, show='headings', height=8)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        # Scrollbar
        scrollbar = ttk.Scrollbar(projects_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True, padx=8, pady=8)
        scrollbar.pack(side='right', fill='y')

        # Proje verilerini yükle
        projects = self.manager.get_emission_projects(self.company_id)
        for project in projects:
            tree.insert('', 'end', values=(
                project['project_name'],
                project['project_type'],
                project['start_date'],
                f"{project['expected_reduction']:,.0f} tCO2e",
                project['status']
            ))

    def show_carbon(self) -> None:
        """Karbon yönetimi sayfası"""
        self.clear_content()

        # Başlık
        header = tk.Frame(self.content_area, bg='#FF5722', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        title_label = tk.Label(header, text=self.lm.tr("skdm_carbon_title", " Karbon Yönetimi"),
                              font=('Segoe UI', 14, 'bold'), fg='white', bg='#FF5722')
        title_label.pack(expand=True)

        # İçerik
        content = tk.Frame(self.content_area, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)

        # Karbon verilerini göster
        carbon_data = self.manager.get_carbon_summary(self.company_id)

        info_text = f"""
{self.lm.tr("skdm_carbon_summary", "Karbon Yönetimi Özeti")}:

{self.lm.tr("kpi_total_emissions", "Toplam Emisyon")}: {carbon_data.get('total_emissions', 0):,.0f} tCO2e
Scope 1: {carbon_data.get('scope1', 0):,.0f} tCO2e
Scope 2: {carbon_data.get('scope2', 0):,.0f} tCO2e
Scope 3: {carbon_data.get('scope3', 0):,.0f} tCO2e

{self.lm.tr("skdm_reduction_target", "Azaltma Hedefi")}: {carbon_data.get('reduction_target', 0):,.0f} tCO2e
{self.lm.tr("skdm_reduction_achieved", "Gerçekleşen Azalma")}: {carbon_data.get('reduction_achieved', 0):,.0f} tCO2e

{self.lm.tr("skdm_carbon_price", "Karbon Fiyatı")}: {carbon_data.get('carbon_price', 0):,.2f} €/tCO2e
{self.lm.tr("skdm_offset_purchased", "Satın Alınan Offset")}: {carbon_data.get('offset_purchased', 0):,.0f} tCO2e
{self.lm.tr("kpi_renewable_energy", "Yenilenebilir Enerji")}: %{carbon_data.get('renewable_energy', 0):.1f}
        """

        text_widget = tk.Text(content, wrap='word', font=('Segoe UI', 11),
                             bg='#f8f9fa', relief='flat', padx=20, pady=20)
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', info_text)
        text_widget.config(state='disabled')

    def show_water(self) -> None:
        """Su yönetimi sayfası"""
        self.clear_content()

        # Başlık
        header = tk.Frame(self.content_area, bg='#2196F3', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        title_label = tk.Label(header, text=self.lm.tr("skdm_water_title", " Su Yönetimi"),
                              font=('Segoe UI', 14, 'bold'), fg='white', bg='#2196F3')
        title_label.pack(expand=True)

        # İçerik
        content = tk.Frame(self.content_area, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)

        # Su verilerini göster
        water_data = self.manager.get_water_summary(self.company_id)

        info_text = f"""
{self.lm.tr("skdm_water_summary", "Su Yönetimi Özeti")}:

{self.lm.tr("skdm_total_water_consumption", "Toplam Su Tüketimi")}: {water_data.get('total_consumption', 0):,.0f} m³
{self.lm.tr("skdm_water_recycling_rate", "Su Geri Dönüşüm Oranı")}: %{water_data.get('reuse_percentage', 0):.1f}
{self.lm.tr("skdm_water_efficiency_score", "Su Verimlilik Skoru")}: {water_data.get('efficiency_score', 0)}/100
{self.lm.tr("skdm_water_risk_level", "Su Risk Seviyesi")}: {water_data.get('risk_level', self.lm.tr('unknown', 'Bilinmiyor'))}

{self.lm.tr("skdm_conservation_projects", "Koruma Projeleri")}: {water_data.get('conservation_projects', 0)} {self.lm.tr('unit_pieces', 'adet')}
{self.lm.tr("skdm_wastewater_treatment_rate", "Atık Su Arıtma Oranı")}: %{water_data.get('treatment_percentage', 0):.1f}
        """

        text_widget = tk.Text(content, wrap='word', font=('Segoe UI', 11),
                             bg='#f8f9fa', relief='flat', padx=20, pady=20)
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', info_text)
        text_widget.config(state='disabled')

    def show_waste(self) -> None:
        """Atık yönetimi sayfası"""
        self.clear_content()

        # Başlık
        header = tk.Frame(self.content_area, bg='#FF9800', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        title_label = tk.Label(header, text=self.lm.tr("skdm_waste_title", "️ Atık Yönetimi"),
                              font=('Segoe UI', 14, 'bold'), fg='white', bg='#FF9800')
        title_label.pack(expand=True)

        # İçerik
        content = tk.Frame(self.content_area, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)

        # Atık verilerini göster
        waste_data = self.manager.get_waste_summary(self.company_id)

        info_text = f"""
{self.lm.tr("skdm_waste_summary", "Atık Yönetimi Özeti")}:

{self.lm.tr("skdm_total_waste_production", "Toplam Atık Üretimi")}: {waste_data.get('total_waste', 0):,.0f} ton
{self.lm.tr("skdm_recycling_rate", "Geri Dönüşüm Oranı")}: %{waste_data.get('recycled_percentage', 0):.1f}
{self.lm.tr("skdm_waste_reduction_rate", "Atık Azaltma Oranı")}: %{waste_data.get('reduced_percentage', 0):.1f}
{self.lm.tr("skdm_hazardous_waste_rate", "Tehlikeli Atık Oranı")}: %{waste_data.get('hazardous_percentage', 0):.1f}

{self.lm.tr("skdm_circular_economy_score", "Döngüsel Ekonomi Skoru")}: {waste_data.get('circular_score', 0)}/100
{self.lm.tr("skdm_waste_to_energy_rate", "Atıktan Enerji Oranı")}: %{waste_data.get('waste_to_energy', 0):.1f}
        """

        text_widget = tk.Text(content, wrap='word', font=('Segoe UI', 11),
                             bg='#f8f9fa', relief='flat', padx=20, pady=20)
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', info_text)
        text_widget.config(state='disabled')

    def show_supply_chain(self) -> None:
        """Tedarik zinciri sayfası"""
        self.clear_content()

        # Başlık
        header = tk.Frame(self.content_area, bg='#9C27B0', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        title_label = tk.Label(header, text=self.lm.tr("skdm_supply_chain_title", " Tedarik Zinciri"),
                              font=('Segoe UI', 14, 'bold'), fg='white', bg='#9C27B0')
        title_label.pack(expand=True)

        # İçerik
        content = tk.Frame(self.content_area, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)

        # Tedarik zinciri verilerini göster
        supply_data = self.manager.get_supply_chain_summary(self.company_id)

        info_text = f"""
{self.lm.tr("skdm_supply_chain_summary", "Tedarik Zinciri Özeti")}:

{self.lm.tr("skdm_suppliers_assessed", "Değerlendirilen Tedarikçi")}: {supply_data.get('suppliers_assessed', 0)} {self.lm.tr('unit_pieces', 'adet')}
{self.lm.tr("skdm_sustainable_supplier_rate", "Sürdürülebilir Tedarikçi Oranı")}: %{supply_data.get('sustainable_percentage', 0):.1f}
{self.lm.tr("skdm_supply_chain_emissions", "Tedarik Zinciri Emisyonları")}: {supply_data.get('supply_chain_emissions', 0):,.0f} tCO2e
{self.lm.tr("skdm_supplier_audits", "Tedarikçi Denetimleri")}: {supply_data.get('audits', 0)} {self.lm.tr('unit_pieces', 'adet')}

{self.lm.tr("skdm_ethical_sourcing_score", "Etik Tedarik Skoru")}: {supply_data.get('ethical_score', 0)}/100
{self.lm.tr("skdm_local_sourcing_rate", "Yerel Tedarik Oranı")}: %{supply_data.get('local_sourcing', 0):.1f}
        """

        text_widget = tk.Text(content, wrap='word', font=('Segoe UI', 11),
                             bg='#f8f9fa', relief='flat', padx=20, pady=20)
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', info_text)
        text_widget.config(state='disabled')

    def show_scope3(self) -> None:
        """Scope 3 kategorileri sayfası"""
        self.clear_content()

        # Başlık
        header = tk.Frame(self.content_area, bg='#607D8B', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        title_label = tk.Label(header, text=self.lm.tr("skdm_scope3_title", " Scope 3 Kategorileri"),
                              font=('Segoe UI', 14, 'bold'), fg='white', bg='#607D8B')
        title_label.pack(expand=True)

        # İçerik
        content = tk.Frame(self.content_area, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)

        # Scope 3 kategorilerini göster
        categories = self.manager.get_scope3_categories(self.company_id)

        if categories:
            # Tablo oluştur
            columns = (
                self.lm.tr("col_category", 'Kategori'),
                self.lm.tr("col_emissions", 'Emisyon (tCO2e)'),
                self.lm.tr("col_data_quality", 'Veri Kalitesi'),
                self.lm.tr("col_status", 'Durum')
            )
            tree = ttk.Treeview(content, columns=columns, show='headings', height=10)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150)

            for category in categories:
                tree.insert('', 'end', values=(
                    category['category_name'],
                    f"{category['emissions']:,.0f}",
                    category['data_quality'],
                    category['verification_status']
                ))

            tree.pack(fill='both', expand=True)
        else:
            no_data_label = tk.Label(content, text=self.lm.tr("skdm_scope3_no_data", "Scope 3 kategorisi verisi bulunamadı"),
                                   font=('Segoe UI', 12), fg='gray')
            no_data_label.pack(expand=True)

    def show_emission_projects(self) -> None:
        """Emisyon azaltma projeleri sayfası"""
        self.clear_content()

        # Başlık
        header = tk.Frame(self.content_area, bg='#4CAF50', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        title_label = tk.Label(header, text=self.lm.tr("skdm_emission_projects_title", " Emisyon Azaltma Projeleri"),
                              font=('Segoe UI', 14, 'bold'), fg='white', bg='#4CAF50')
        title_label.pack(expand=True)

        # İçerik
        content = tk.Frame(self.content_area, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)

        # Proje listesi
        projects = self.manager.get_emission_projects(self.company_id)

        if projects:
            # Tablo oluştur
            columns = (
                self.lm.tr("col_project_name", 'Proje Adı'),
                self.lm.tr("col_project_type", 'Tip'),
                self.lm.tr("col_start_date", 'Başlangıç'),
                self.lm.tr("col_expected_reduction", 'Beklenen Azalma'),
                self.lm.tr("col_investment", 'Yatırım'),
                self.lm.tr("col_status", 'Durum')
            )
            tree = ttk.Treeview(content, columns=columns, show='headings', height=10)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)

            for project in projects:
                tree.insert('', 'end', values=(
                    project['project_name'],
                    project['project_type'],
                    project['start_date'],
                    f"{project['expected_reduction']:,.0f} tCO2e",
                    f"{project['investment_amount']:,.0f} €",
                    project['status']
                ))

            tree.pack(fill='both', expand=True)
        else:
            no_data_label = tk.Label(content, text=self.lm.tr("skdm_no_projects", "Emisyon azaltma projesi bulunamadı"),
                                   font=('Segoe UI', 12), fg='gray')
            no_data_label.pack(expand=True)

    def show_stakeholders(self) -> None:
        """Paydaş yönetimi sayfası"""
        self.clear_content()

        # Başlık
        header = tk.Frame(self.content_area, bg='#795548', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        title_label = tk.Label(header, text=self.lm.tr("skdm_stakeholder_title", " Paydaş Yönetimi"),
                              font=('Segoe UI', 14, 'bold'), fg='white', bg='#795548')
        title_label.pack(expand=True)

        # İçerik
        content = tk.Frame(self.content_area, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)

        # Toolbar
        toolbar = tk.Frame(content, bg='white')
        toolbar.pack(fill='x', pady=(0, 10))

        tk.Button(toolbar, text=f"{Icons.ADD} {self.lm.tr('btn_add_new_stakeholder', 'Yeni Paydaş Ekle')}",
                 command=self.add_stakeholder_dialog,
                 bg='#4CAF50', fg='white', font=('Segoe UI', 10, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=(0, 5))

        tk.Button(toolbar, text=f"{Icons.EDIT} {self.lm.tr('btn_edit', 'Düzenle')}",
                 command=lambda: self.edit_stakeholder_dialog(self.stakeholder_tree),
                 bg='#2196F3', fg='white', font=('Segoe UI', 10, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=5)

        tk.Button(toolbar, text=f"{Icons.DELETE} {self.lm.tr('btn_delete', 'Sil')}",
                 command=lambda: self.delete_stakeholder_confirm(self.stakeholder_tree),
                 bg='#F44336', fg='white', font=('Segoe UI', 10, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=5)

        tk.Button(toolbar, text=f"{Icons.LOADING} {self.lm.tr('btn_refresh', 'Yenile')}",
                 command=self.show_stakeholders,
                 bg='#9E9E9E', fg='white', font=('Segoe UI', 10, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=5)

        tk.Button(toolbar, text=self.lm.tr("btn_import_excel", "📥 Excel'den İçe Aktar"),
                 command=self.import_stakeholders_from_excel,
                 bg='#FF9800', fg='white', font=('Segoe UI', 10, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=5)

        # Paydaş listesi
        list_frame = tk.Frame(content, bg='white')
        list_frame.pack(fill='both', expand=True)

        stakeholders = self.manager.get_stakeholders(self.company_id)

        # Tablo oluştur (her durumda)
        columns = (
            self.lm.tr("col_id", "ID"),
            self.lm.tr("col_stakeholder_name", 'Paydaş Adı'),
            self.lm.tr("col_type", 'Tip'),
            self.lm.tr("col_engagement_level", 'Etkileşim Seviyesi'),
            self.lm.tr("col_satisfaction", 'Memnuniyet'),
            self.lm.tr("col_last_contact", 'Son İletişim')
        )
        self.stakeholder_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)

        self.stakeholder_tree.heading(self.lm.tr("col_id", "ID"), text=self.lm.tr("col_id", "ID"))
        self.stakeholder_tree.heading(self.lm.tr("col_stakeholder_name", 'Paydaş Adı'), text=self.lm.tr("col_stakeholder_name", 'Paydaş Adı'))
        self.stakeholder_tree.heading(self.lm.tr("col_type", 'Tip'), text=self.lm.tr("col_type", 'Tip'))
        self.stakeholder_tree.heading(self.lm.tr("col_engagement_level", 'Etkileşim Seviyesi'), text=self.lm.tr("col_engagement_level", 'Etkileşim'))
        self.stakeholder_tree.heading(self.lm.tr("col_satisfaction", 'Memnuniyet'), text=self.lm.tr("col_satisfaction", 'Memnuniyet'))
        self.stakeholder_tree.heading(self.lm.tr("col_last_contact", 'Son İletişim'), text=self.lm.tr("col_last_contact", 'Son İletişim'))

        self.stakeholder_tree.column(self.lm.tr("col_id", "ID"), width=50)
        self.stakeholder_tree.column(self.lm.tr("col_stakeholder_name", 'Paydaş Adı'), width=200)
        self.stakeholder_tree.column(self.lm.tr("col_type", 'Tip'), width=120)
        self.stakeholder_tree.column(self.lm.tr("col_engagement_level", 'Etkileşim Seviyesi'), width=120)
        self.stakeholder_tree.column(self.lm.tr("col_satisfaction", 'Memnuniyet'), width=100)
        self.stakeholder_tree.column(self.lm.tr("col_last_contact", 'Son İletişim'), width=120)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.stakeholder_tree.yview)
        self.stakeholder_tree.configure(yscrollcommand=scrollbar.set)

        self.stakeholder_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Verileri yükle
        if stakeholders:
            for i, stakeholder in enumerate(stakeholders, 1):
                self.stakeholder_tree.insert('', 'end', values=(
                    i,  # ID olarak sıra numarası
                    stakeholder['stakeholder_name'],
                    stakeholder['stakeholder_type'],
                    stakeholder['engagement_level'],
                    f"{stakeholder['satisfaction_score']}/10",
                    stakeholder['last_contact_date'] or self.lm.tr('unknown', 'Bilinmiyor')
                ), tags=(str(i),))
        else:
            # Boş liste mesajı
            info_label = tk.Label(list_frame,
                                text=f"\n\n{Icons.CLIPBOARD} {self.lm.tr('msg_no_stakeholders', 'Henüz paydaş eklenmemiş')}\n\n" +
                                     f"{self.lm.tr('msg_add_stakeholder_hint', 'Yeni paydaş eklemek için yukarıdaki')}\n" +
                                     f"'{Icons.ADD} {self.lm.tr('btn_add_new_stakeholder', 'Yeni Paydaş Ekle')}' {self.lm.tr('msg_use_button', 'butonunu kullanın')}",
                                font=('Segoe UI', 11), fg='#666', bg='white')
            info_label.pack(expand=True)

    def add_stakeholder_dialog(self) -> None:
        """Yeni paydaş ekleme dialogu"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr("title_add_stakeholder", "Yeni Paydaş Ekle"))
        dialog.geometry("500x450")
        dialog.configure(bg='white')

        # Başlık
        header = tk.Frame(dialog, bg='#795548')
        header.pack(fill='x')
        tk.Label(header, text=self.lm.tr("title_add_stakeholder", " Yeni Paydaş Ekle"),
                font=('Segoe UI', 14, 'bold'), fg='white', bg='#795548').pack(pady=10)

        # Form
        form_frame = tk.Frame(dialog, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Paydaş Adı
        tk.Label(form_frame, text=self.lm.tr("lbl_stakeholder_name", "Paydaş Adı:"), font=('Segoe UI', 10),
                bg='white').grid(row=0, column=0, sticky='w', pady=5)
        name_entry = tk.Entry(form_frame, width=40, font=('Segoe UI', 10))
        name_entry.grid(row=0, column=1, pady=5, padx=(10, 0))

        # Paydaş Tipi
        tk.Label(form_frame, text=self.lm.tr("lbl_stakeholder_type", "Paydaş Tipi:"), font=('Segoe UI', 10),
                bg='white').grid(row=1, column=0, sticky='w', pady=5)
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(form_frame, textvariable=type_var, width=37,
                                 values=[
                                     self.lm.tr("type_employee", "Çalışan"),
                                     self.lm.tr("type_customer", "Müşteri"),
                                     self.lm.tr("type_supplier", "Tedarikçi"),
                                     self.lm.tr("type_investor", "Yatırımcı"),
                                     self.lm.tr("type_ngo", "STK"),
                                     self.lm.tr("type_community", "Topluluk"),
                                     self.lm.tr("type_regulatory", "Düzenleyici Kurum"),
                                     self.lm.tr("type_media", "Medya"),
                                     self.lm.tr("type_other", "Diğer")
                                 ],
                                 state='readonly')
        type_combo.grid(row=1, column=1, pady=5, padx=(10, 0))

        # Etkileşim Seviyesi
        tk.Label(form_frame, text=self.lm.tr("lbl_engagement_level", "Etkileşim Seviyesi:"), font=('Segoe UI', 10),
                bg='white').grid(row=2, column=0, sticky='w', pady=5)
        engagement_var = tk.StringVar(value=self.lm.tr("level_medium", "Orta"))
        engagement_combo = ttk.Combobox(form_frame, textvariable=engagement_var, width=37,
                                       values=[
                                           self.lm.tr("level_low", "Düşük"),
                                           self.lm.tr("level_medium", "Orta"),
                                           self.lm.tr("level_high", "Yüksek"),
                                           self.lm.tr("level_very_high", "Çok Yüksek")
                                       ],
                                       state='readonly')
        engagement_combo.grid(row=2, column=1, pady=5, padx=(10, 0))

        # Memnuniyet Skoru
        tk.Label(form_frame, text=self.lm.tr("lbl_satisfaction_score", "Memnuniyet Skoru (1-10):"), font=('Segoe UI', 10),
                bg='white').grid(row=3, column=0, sticky='w', pady=5)
        satisfaction_var = tk.IntVar(value=7)
        satisfaction_spin = tk.Spinbox(form_frame, from_=1, to=10, textvariable=satisfaction_var,
                                      width=38, font=('Segoe UI', 10))
        satisfaction_spin.grid(row=3, column=1, pady=5, padx=(10, 0))

        # Son İletişim Tarihi
        tk.Label(form_frame, text=self.lm.tr("lbl_last_contact_date", "Son İletişim Tarihi:"), font=('Segoe UI', 10),
                bg='white').grid(row=4, column=0, sticky='w', pady=5)
        last_contact_entry = tk.Entry(form_frame, width=40, font=('Segoe UI', 10))
        last_contact_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        last_contact_entry.grid(row=4, column=1, pady=5, padx=(10, 0))

        # Sonraki İletişim Tarihi
        tk.Label(form_frame, text=self.lm.tr("lbl_next_contact_date", "Sonraki İletişim Tarihi:"), font=('Segoe UI', 10),
                bg='white').grid(row=5, column=0, sticky='w', pady=5)
        next_contact_entry = tk.Entry(form_frame, width=40, font=('Segoe UI', 10))
        next_contact_entry.grid(row=5, column=1, pady=5, padx=(10, 0))

        # Önemli Konular
        tk.Label(form_frame, text=self.lm.tr("lbl_key_concerns", "Önemli Konular:"), font=('Segoe UI', 10),
                bg='white').grid(row=6, column=0, sticky='nw', pady=5)
        concerns_text = tk.Text(form_frame, width=40, height=4, font=('Segoe UI', 9))
        concerns_text.grid(row=6, column=1, pady=5, padx=(10, 0))

        # Butonlar
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.grid(row=7, column=0, columnspan=2, pady=20)

        def save_stakeholder():
            name = name_entry.get().strip()
            stakeholder_type = type_var.get().strip()

            if not name or not stakeholder_type:
                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("msg_name_type_required", "Paydaş adı ve tipi zorunludur!"))
                return

            stakeholder_data = {
                'stakeholder_name': name,
                'stakeholder_type': stakeholder_type,
                'engagement_level': engagement_var.get(),
                'satisfaction_score': satisfaction_var.get(),
                'last_contact_date': last_contact_entry.get().strip() or None,
                'next_contact_date': next_contact_entry.get().strip() or None,
                'key_concerns': concerns_text.get('1.0', 'end').strip()
            }

            if self.manager.add_stakeholder(self.company_id, stakeholder_data):
                messagebox.showinfo(self.lm.tr("success", "Başarılı"), f"{self.lm.tr('msg_stakeholder_added', 'Paydaş eklendi')}: {name}")
                dialog.destroy()
                self.show_stakeholders()  # Listeyi yenile
            else:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("msg_stakeholder_add_error", "Paydaş eklenemedi!"))

        tk.Button(btn_frame, text=f"{Icons.SAVE} {self.lm.tr('btn_save', 'Kaydet')}", command=save_stakeholder,
                 bg='#4CAF50', fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=8).pack(side='left', padx=5)

        tk.Button(btn_frame, text=f"{Icons.FAIL} {self.lm.tr('btn_cancel', 'İptal')}", command=dialog.destroy,
                 bg='#9E9E9E', fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=8).pack(side='left', padx=5)

    def edit_stakeholder_dialog(self, tree) -> None:
        """Paydaş düzenleme dialogu"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("msg_select_stakeholder_edit", "Lütfen düzenlenecek paydaşı seçin!"))
            return

        # Seçili paydaş bilgilerini al
        item = tree.item(selected[0])
        values = item['values']
        stakeholder_id = values[0]
        current_name = values[1]
        current_type = values[2]
        current_contact = values[3] if len(values) > 3 else ""
        current_priority = values[4] if len(values) > 4 else self.lm.tr("level_medium", "Orta")

        # Düzenleme dialogu
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr("title_edit_stakeholder", "Paydaş Düzenle"))
        dialog.geometry("500x400")
        dialog.transient(self.parent)
        dialog.grab_set()

        # Form frame
        form_frame = ttk.LabelFrame(dialog, text=self.lm.tr("lbl_stakeholder_info", "Paydaş Bilgileri"), padding=20)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Paydaş Adı
        ttk.Label(form_frame, text=self.lm.tr("lbl_stakeholder_name", "Paydaş Adı:")).grid(row=0, column=0, sticky='w', pady=10)
        name_var = tk.StringVar(value=current_name)
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=0, column=1, sticky='ew', pady=10)

        # Paydaş Tipi
        ttk.Label(form_frame, text=self.lm.tr("lbl_stakeholder_type", "Paydaş Tipi:")).grid(row=1, column=0, sticky='w', pady=10)
        type_var = tk.StringVar(value=current_type)
        type_combo = ttk.Combobox(form_frame, textvariable=type_var, width=28,
                                  values=[
                                     self.lm.tr("type_employee", "Çalışan"),
                                     self.lm.tr("type_customer", "Müşteri"),
                                     self.lm.tr("type_supplier", "Tedarikçi"),
                                     self.lm.tr("type_investor", "Yatırımcı"),
                                     self.lm.tr("type_ngo", "STK"),
                                     self.lm.tr("type_community", "Topluluk"),
                                     self.lm.tr("type_regulatory", "Düzenleyici Kurum"),
                                     self.lm.tr("type_media", "Medya"),
                                     self.lm.tr("type_other", "Diğer")
                                 ], state='readonly')
        type_combo.grid(row=1, column=1, sticky='ew', pady=10)

        # İletişim
        ttk.Label(form_frame, text=self.lm.tr("lbl_contact", "İletişim:")).grid(row=2, column=0, sticky='w', pady=10)
        contact_var = tk.StringVar(value=current_contact)
        ttk.Entry(form_frame, textvariable=contact_var, width=30).grid(row=2, column=1, sticky='ew', pady=10)

        # Öncelik
        ttk.Label(form_frame, text=self.lm.tr("lbl_priority", "Öncelik:")).grid(row=3, column=0, sticky='w', pady=10)
        priority_var = tk.StringVar(value=current_priority)
        priority_combo = ttk.Combobox(form_frame, textvariable=priority_var, width=28,
                                     values=[
                                           self.lm.tr("level_low", "Düşük"),
                                           self.lm.tr("level_medium", "Orta"),
                                           self.lm.tr("level_high", "Yüksek"),
                                           self.lm.tr("level_critical", "Kritik")
                                       ], state='readonly')
        priority_combo.grid(row=3, column=1, sticky='ew', pady=10)

        form_frame.columnconfigure(1, weight=1)

        def save_changes():
            """Değişiklikleri kaydet"""
            new_data = {
                'name': name_var.get().strip(),
                'type': type_var.get(),
                'contact': contact_var.get().strip(),
                'priority': priority_var.get()
            }

            if not new_data['name']:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("msg_stakeholder_name_required", "Paydaş adı boş olamaz!"))
                return

            if self.manager.update_stakeholder(stakeholder_id, new_data):
                messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("msg_stakeholder_updated", "Paydaş güncellendi!"))
                dialog.destroy()
                self.show_stakeholders()
            else:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("msg_stakeholder_update_error", "Paydaş güncellenemedi!"))

        # Butonlar
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill='x', padx=20, pady=20)

        ttk.Button(button_frame, text=self.lm.tr("btn_save", "Kaydet"), command=save_changes).pack(side='left', padx=5)
        ttk.Button(button_frame, text=self.lm.tr("btn_cancel", "İptal"), command=dialog.destroy).pack(side='left', padx=5)

    def delete_stakeholder_confirm(self, tree) -> None:
        """Paydaş silme onayı"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("msg_select_stakeholder_delete", "Lütfen silinecek paydaşı seçin!"))
            return

        item = tree.item(selected[0])
        values = item['values']
        stakeholder_id = values[0]
        stakeholder_name = values[1]  # Paydaş adı

        msg_confirm = self.lm.tr('msg_delete_stakeholder_confirm', 'paydaşını silmek istediğinizden emin misiniz?')
        msg_undo = self.lm.tr('msg_operation_cannot_be_undone', 'Bu işlem geri alınamaz!')
        
        if messagebox.askyesno(self.lm.tr("confirmation", "Onay"), f"'{stakeholder_name}' {msg_confirm}\n\n{msg_undo}"):
            if self.manager.delete_stakeholder(stakeholder_id):
                msg_deleted = self.lm.tr('msg_deleted', 'silindi')
                messagebox.showinfo(self.lm.tr("success", "Başarılı"), f"'{stakeholder_name}' {msg_deleted}!")
                self.show_stakeholders()  # Listeyi yenile
            else:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("msg_stakeholder_delete_error", "Paydaş silinemedi!"))

    def import_stakeholders_from_excel(self) -> None:
        """Excel'den paydaş içe aktarma"""
        from tkinter import filedialog

        filepath = filedialog.askopenfilename(
            title=self.lm.tr("title_excel_file", "Paydaş Listesi Excel Dosyası"),
            filetypes=[(self.lm.tr("file_excel", "Excel Dosyası"), "*.xlsx"), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")]
        )

        if not filepath:
            return

        try:
            import openpyxl
            wb = openpyxl.load_workbook(filepath)
            ws = wb.active

            # Başlık satırını atla, veriler 2. satırdan başlar
            added_count = 0
            for row in ws.iter_rows(min_row=2, values_only=True):
                if not row[0]:  # Boş satır
                    continue

                stakeholder_data = {
                    'stakeholder_name': str(row[0]) if row[0] else '',
                    'stakeholder_type': str(row[1]) if row[1] else self.lm.tr('type_other', 'Diğer'),
                    'engagement_level': str(row[2]) if row[2] else self.lm.tr('level_medium', 'Orta'),
                    'satisfaction_score': int(row[3]) if row[3] else 7,
                    'last_contact_date': str(row[4]) if row[4] else None,
                    'next_contact_date': str(row[5]) if row[5] else None,
                    'key_concerns': str(row[6]) if row[6] else ''
                }

                if self.manager.add_stakeholder(self.company_id, stakeholder_data):
                    added_count += 1

            messagebox.showinfo(self.lm.tr("success", "Başarılı"), f"{added_count} {self.lm.tr('msg_stakeholders_imported', 'paydaş içe aktarıldı')}!")
            self.show_stakeholders()  # Listeyi yenile

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('msg_excel_import_error', 'Excel içe aktarılamadı')}:\n{str(e)}")

    def load_data(self) -> None:
        """Verileri yükle"""
        # Bu fonksiyon gerekirse veri yükleme işlemleri için kullanılabilir
        pass
