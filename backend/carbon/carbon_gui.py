#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KARBON MODÜLÜ GUI
Scope 1, 2, 3 emisyon veri girişi, analiz ve raporlama arayüzü
"""

import logging
import csv
import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from typing import Dict

from utils.language_manager import LanguageManager
from .carbon_manager import CarbonManager
from config.icons import Icons

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CarbonGUI:
    """Karbon Hesaplama Modülü GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()
        self.manager = CarbonManager()

        # Veritabanı tablolarını oluştur
        self.manager.create_tables()

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Karbon modülü arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        header_frame = tk.Frame(main_frame, bg='#f0f2f5')
        header_frame.pack(fill='x', pady=(0, 20))

        title_label = tk.Label(header_frame, text=self.lm.tr('carbon_module_title', "Karbon Hesaplama Modülü"),
                              font=('Segoe UI', 20, 'bold'), fg='#1e293b', bg='#f0f2f5')
        title_label.pack(side='left')

        subtitle_label = tk.Label(header_frame, text=self.lm.tr('carbon_module_subtitle', "GHG Protocol Uyumlu Emisyon İzleme"),
                                 font=('Segoe UI', 12), fg='#64748b', bg='#f0f2f5')
        subtitle_label.pack(side='left', padx=(10, 0), pady=(8, 0))

        # Dashboard kartları
        self.create_stats_frame(main_frame)

        # Ana içerik - Notebook (Sekmeler)
        style = ttk.Style()
        style.configure("TNotebook", background="#f0f2f5", borderwidth=0)
        style.configure("TNotebook.Tab", padding=[12, 8], font=('Segoe UI', 10))

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Sekmeler
        self.create_scope1_tab()
        self.create_scope2_tab()
        self.create_scope3_tab()
        self.create_targets_tab()
        self.create_initiatives_tab()
        self.create_offset_tab()        # YENİ: Offset Yönetimi
        self.create_reports_tab()

    def create_stats_frame(self, parent) -> None:
        """İstatistik kartları"""
        self.stats_frame = tk.Frame(parent, bg='#f0f2f5')
        self.stats_frame.pack(fill='x', pady=(0, 20))
        self.refresh_stats()

    def create_scope1_tab(self) -> None:
        """Scope 1 sekmesi - Doğrudan Emisyonlar"""
        scope1_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(scope1_frame, text=f"🏭 {self.lm.tr('scope1', 'Scope 1')} - {self.lm.tr('direct_emissions', 'Doğrudan Emisyonlar')}")

        # Alt sekmeler
        scope1_notebook = ttk.Notebook(scope1_frame)
        scope1_notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Sabit Yakma
        stationary_frame = tk.Frame(scope1_notebook, bg='white')
        scope1_notebook.add(stationary_frame, text=f"{Icons.FIRE} {self.lm.tr('stationary_combustion', 'Sabit Yakma')}")
        self.create_stationary_form(stationary_frame)

        # Mobil Yakma
        mobile_frame = tk.Frame(scope1_notebook, bg='white')
        scope1_notebook.add(mobile_frame, text=f"🚗 {self.lm.tr('mobile_combustion', 'Araç Filosu')}")
        self.create_mobile_form(mobile_frame)

        # Kaçak Emisyonlar
        fugitive_frame = tk.Frame(scope1_notebook, bg='white')
        scope1_notebook.add(fugitive_frame, text=f"❄️ {self.lm.tr('fugitive_emissions', 'Kaçak Emisyonlar')}")
        self.create_fugitive_form(fugitive_frame)

    def create_stationary_form(self, parent) -> None:
        """Sabit yakma formu"""
        # Form alanı
        form_frame = tk.Frame(parent, bg='white')
        form_frame.pack(fill='x', padx=20, pady=20)

        tk.Label(form_frame, text=self.lm.tr('stationary_combustion_data_entry', "Sabit Yakma Kaynakları Veri Girişi"),
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').grid(
            row=0, column=0, columnspan=3, pady=(0, 20))

        # Dönem
        tk.Label(form_frame, text=self.lm.tr('period', "Dönem:"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.s1_stat_period = tk.Entry(form_frame, width=15)
        self.s1_stat_period.insert(0, str(datetime.now().year))
        self.s1_stat_period.grid(row=1, column=1, sticky='w', pady=5)

        # Yakıt Türü
        tk.Label(form_frame, text=self.lm.tr('fuel_type', "Yakıt Türü:"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.s1_stat_fuel_type = ttk.Combobox(form_frame, width=20, state='readonly')
        self.s1_stat_fuel_type.grid(row=2, column=1, sticky='w', pady=5)
        self.s1_stat_fuel_type['values'] = [
            f"natural_gas - {self.lm.tr('natural_gas', 'Doğalgaz')} (m³)",
            f"diesel - {self.lm.tr('diesel', 'Dizel')} (litre)",
            f"fuel_oil - {self.lm.tr('fuel_oil', 'Fuel Oil')} (litre)",
            f"lpg - {self.lm.tr('lpg', 'LPG')} (kg)",
            f"coal - {self.lm.tr('coal', 'Kömür')} (ton)"
        ]
        self.s1_stat_fuel_type.current(0)

        # Miktar
        tk.Label(form_frame, text=self.lm.tr('quantity', "Miktar:"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=3, column=0, sticky='w', pady=5)
        self.s1_stat_quantity = tk.Entry(form_frame, width=15)
        self.s1_stat_quantity.grid(row=3, column=1, sticky='w', pady=5)
        tk.Label(form_frame, text=self.lm.tr('unit_auto', "(Birim otomatik)"), font=('Segoe UI', 9),
                fg='#666', bg='white').grid(row=3, column=2, sticky='w', padx=(5, 0))

        # Veri Kalitesi
        tk.Label(form_frame, text=self.lm.tr('data_quality', "Veri Kalitesi:"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=4, column=0, sticky='w', pady=5)
        self.s1_stat_quality = ttk.Combobox(form_frame, width=20, state='readonly')
        self.s1_stat_quality.grid(row=4, column=1, sticky='w', pady=5)
        self.s1_stat_quality['values'] = [
            f"measured - {self.lm.tr('measured', 'Ölçülmüş')}",
            f"estimated - {self.lm.tr('estimated', 'Tahmin')}",
            f"default - {self.lm.tr('default', 'Varsayılan')}"
        ]
        self.s1_stat_quality.current(0)

        # Notlar
        tk.Label(form_frame, text=self.lm.tr('notes', "Notlar:"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=5, column=0, sticky='nw', pady=5)
        self.s1_stat_notes = tk.Text(form_frame, width=40, height=3)
        self.s1_stat_notes.grid(row=5, column=1, columnspan=2, sticky='w', pady=5)

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=f"{Icons.SAVE} {self.lm.tr('save_and_calculate', 'Kaydet ve Hesapla')}",
                            font=('Segoe UI', 11, 'bold'), bg='#27ae60', fg='white',
                            relief='flat', cursor='hand2', padx=20, pady=10,
                            command=self.save_scope1_stationary)
        save_btn.grid(row=6, column=1, sticky='w', pady=20)

        # Kayıtlı veriler listesi
        list_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        tk.Label(list_frame, text=self.lm.tr('saved_stationary_data', "Kaydedilmiş Sabit Yakma Verileri"),
                font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white').pack(pady=10)

        # Treeview
        columns = ('period', 'fuel_type', 'quantity', 'co2e', 'quality')
        self.s1_stat_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)

        self.s1_stat_tree.heading('period', text=self.lm.tr('period', 'Dönem'))
        self.s1_stat_tree.heading('fuel_type', text=self.lm.tr('fuel_type', 'Yakıt Türü'))
        self.s1_stat_tree.heading('quantity', text=self.lm.tr('quantity', 'Miktar'))
        self.s1_stat_tree.heading('co2e', text=self.lm.tr('tco2e', 'tCO2e'))
        self.s1_stat_tree.heading('quality', text=self.lm.tr('data_quality', 'Kalite'))

        self.s1_stat_tree.column('period', width=80)
        self.s1_stat_tree.column('fuel_type', width=150)
        self.s1_stat_tree.column('quantity', width=100)
        self.s1_stat_tree.column('co2e', width=100)
        self.s1_stat_tree.column('quality', width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.s1_stat_tree.yview)
        self.s1_stat_tree.configure(yscrollcommand=scrollbar.set)

        self.s1_stat_tree.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        scrollbar.pack(side='right', fill='y', pady=(0, 10))

    def create_mobile_form(self, parent) -> None:
        """Mobil yakma formu (Araç filosu)"""
        form_frame = tk.Frame(parent, bg='white')
        form_frame.pack(fill='x', padx=20, pady=20)

        tk.Label(form_frame, text=self.lm.tr('mobile_combustion_entry', "Araç Filosu Veri Girişi"),
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').grid(
            row=0, column=0, columnspan=3, pady=(0, 20))

        # Dönem
        tk.Label(form_frame, text=self.lm.tr('period', "Dönem:"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.s1_mobile_period = tk.Entry(form_frame, width=15)
        self.s1_mobile_period.insert(0, str(datetime.now().year))
        self.s1_mobile_period.grid(row=1, column=1, sticky='w', pady=5)

        # Yakıt Türü
        tk.Label(form_frame, text=self.lm.tr('fuel_type', "Yakıt Türü:"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.s1_mobile_fuel_type = ttk.Combobox(form_frame, width=20, state='readonly')
        self.s1_mobile_fuel_type.grid(row=2, column=1, sticky='w', pady=5)
        self.s1_mobile_fuel_type['values'] = [
            f"gasoline - {self.lm.tr('gasoline', 'Benzin')} (litre)",
            f"diesel_vehicle - {self.lm.tr('diesel', 'Dizel')} (litre)"
        ]
        self.s1_mobile_fuel_type.current(0)

        # Miktar
        tk.Label(form_frame, text=self.lm.tr('fuel_quantity', "Yakıt Miktarı:"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=3, column=0, sticky='w', pady=5)
        self.s1_mobile_quantity = tk.Entry(form_frame, width=15)
        self.s1_mobile_quantity.grid(row=3, column=1, sticky='w', pady=5)

        # Araç Sayısı
        tk.Label(form_frame, text=self.lm.tr('vehicle_count', "Araç Sayısı:"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=4, column=0, sticky='w', pady=5)
        self.s1_mobile_vehicle_count = tk.Entry(form_frame, width=15)
        self.s1_mobile_vehicle_count.grid(row=4, column=1, sticky='w', pady=5)

        # Kaydet
        save_btn = tk.Button(form_frame, text=f"{Icons.SAVE} {self.lm.tr('btn_save', 'Kaydet')}",
                            font=('Segoe UI', 11, 'bold'), bg='#27ae60', fg='white',
                            relief='flat', cursor='hand2', padx=20, pady=10,
                            command=self.save_scope1_mobile)
        save_btn.grid(row=5, column=1, sticky='w', pady=20)

        # Liste
        list_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        columns = ('period', 'fuel_type', 'quantity', 'vehicles', 'co2e')
        self.s1_mobile_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)

        self.s1_mobile_tree.heading('period', text=self.lm.tr('period', 'Dönem'))
        self.s1_mobile_tree.heading('fuel_type', text=self.lm.tr('fuel', 'Yakıt'))
        self.s1_mobile_tree.heading('quantity', text=self.lm.tr('quantity_liter', 'Miktar (L)'))
        self.s1_mobile_tree.heading('vehicles', text=self.lm.tr('vehicle_count_short', 'Araç Sayısı'))
        self.s1_mobile_tree.heading('co2e', text=self.lm.tr('tco2e', 'tCO2e'))

        self.s1_mobile_tree.pack(fill='both', expand=True, padx=10, pady=10)

    def create_fugitive_form(self, parent) -> None:
        """Kaçak emisyonlar formu (Soğutucu gazlar)"""
        form_frame = tk.Frame(parent, bg='white')
        form_frame.pack(fill='x', padx=20, pady=20)

        tk.Label(form_frame, text=self.lm.tr('fugitive_emissions_title', "Kaçak Emisyonlar (Soğutucu Gazlar)"),
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').grid(
            row=0, column=0, columnspan=3, pady=(0, 20))

        # Dönem
        tk.Label(form_frame, text=self.lm.tr('period', "Dönem:"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.s1_fug_period = tk.Entry(form_frame, width=15)
        self.s1_fug_period.insert(0, str(datetime.now().year))
        self.s1_fug_period.grid(row=1, column=1, sticky='w', pady=5)

        # Soğutucu Gaz Türü
        tk.Label(form_frame, text=self.lm.tr('refrigerant_gas', "Soğutucu Gaz:"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.s1_fug_type = ttk.Combobox(form_frame, width=20, state='readonly')
        self.s1_fug_type.grid(row=2, column=1, sticky='w', pady=5)
        self.s1_fug_type['values'] = [
            f"r134a - R-134a (HFC) ({self.lm.tr('r134a', 'R-134a')})",
            f"r404a - R-404A (HFC) ({self.lm.tr('r404a', 'R-404A')})",
            f"r410a - R-410A (HFC) ({self.lm.tr('r410a', 'R-410A')})"
        ]
        self.s1_fug_type.current(0)

        # Kaçak Miktar (kg)
        tk.Label(form_frame, text=self.lm.tr('fugitive_amount_kg', "Kaçak Miktar (kg):"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=3, column=0, sticky='w', pady=5)
        self.s1_fug_quantity = tk.Entry(form_frame, width=15)
        self.s1_fug_quantity.grid(row=3, column=1, sticky='w', pady=5)

        # Kaydet
        save_btn = tk.Button(form_frame, text=f"{Icons.SAVE} {self.lm.tr('btn_save', 'Kaydet')}",
                            font=('Segoe UI', 11, 'bold'), bg='#27ae60', fg='white',
                            relief='flat', cursor='hand2', padx=20, pady=10,
                            command=self.save_scope1_fugitive)
        save_btn.grid(row=4, column=1, sticky='w', pady=20)

        # Bilgi
        info_label = tk.Label(form_frame,
                            text=f"{Icons.LIGHTBULB} {self.lm.tr('fugitive_hint', 'İpucu: Klima sistemlerindeki soğutucu gaz kaçaklarını kaydedin.')}",
                            font=('Segoe UI', 9), fg='#3498db', bg='white', wraplength=500, justify='left')
        info_label.grid(row=5, column=0, columnspan=3, sticky='w', pady=(10, 0))

    def create_scope2_tab(self) -> None:
        """Scope 2 sekmesi - Dolaylı Emisyonlar"""
        scope2_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(scope2_frame, text=f"⚡ {self.lm.tr('scope2_title', 'Scope 2 - Satın Alınan Enerji')}")

        # Alt sekmeler
        scope2_notebook = ttk.Notebook(scope2_frame)
        scope2_notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Elektrik
        electricity_frame = tk.Frame(scope2_notebook, bg='white')
        scope2_notebook.add(electricity_frame, text=f"{Icons.LIGHTBULB} {self.lm.tr('electricity', 'Elektrik')}")
        self.create_electricity_form(electricity_frame)

        # Isıtma/Soğutma
        heating_frame = tk.Frame(scope2_notebook, bg='white')
        scope2_notebook.add(heating_frame, text=f"{Icons.FIRE} {self.lm.tr('heating_cooling', 'Isıtma/Soğutma')}")
        self.create_heating_form(heating_frame)

    def create_electricity_form(self, parent) -> None:
        """Elektrik tüketimi formu"""
        form_frame = tk.Frame(parent, bg='white')
        form_frame.pack(fill='x', padx=20, pady=20)

        tk.Label(form_frame, text=self.lm.tr('electricity_purchased', "Satın Alınan Elektrik"),
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').grid(
            row=0, column=0, columnspan=3, pady=(0, 20))

        # Dönem
        tk.Label(form_frame, text=self.lm.tr('period', "Dönem:"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.s2_elec_period = tk.Entry(form_frame, width=15)
        self.s2_elec_period.insert(0, str(datetime.now().year))
        self.s2_elec_period.grid(row=1, column=1, sticky='w', pady=5)

        # Şebeke Türü
        tk.Label(form_frame, text=self.lm.tr('grid_type', "Şebeke Türü:"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.s2_elec_grid = ttk.Combobox(form_frame, width=25, state='readonly')
        self.s2_elec_grid.grid(row=2, column=1, sticky='w', pady=5)
        self.s2_elec_grid['values'] = [
            f"turkey - {self.lm.tr('turkey_grid', 'Türkiye Şebekesi')}",
            f"renewable - {self.lm.tr('renewable_energy', 'Yenilenebilir Enerji')}",
            f"eu_average - {self.lm.tr('eu_average', 'AB Ortalama')}",
            f"usa_average - {self.lm.tr('usa_average', 'ABD Ortalama')}"
        ]
        self.s2_elec_grid.current(0)

        # Tüketim (kWh)
        tk.Label(form_frame, text=self.lm.tr('consumption_kwh', "Tüketim (kWh):"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=3, column=0, sticky='w', pady=5)
        self.s2_elec_quantity = tk.Entry(form_frame, width=15)
        self.s2_elec_quantity.grid(row=3, column=1, sticky='w', pady=5)

        # Kaydet
        save_btn = tk.Button(form_frame, text=f"{Icons.SAVE} {self.lm.tr('save_and_calculate', 'Kaydet ve Hesapla')}",
                            font=('Segoe UI', 11, 'bold'), bg='#27ae60', fg='white',
                            relief='flat', cursor='hand2', padx=20, pady=10,
                            command=self.save_scope2_electricity)
        save_btn.grid(row=4, column=1, sticky='w', pady=20)

        # Hesaplama örneği
        example = tk.Label(form_frame,
                          text=f"{Icons.REPORT} {self.lm.tr('calculation_example', 'Örnek: 100,000 kWh × 0.000475 tCO2/kWh = 47.5 tCO2e')}",
                          font=('Segoe UI', 9), fg='#27ae60', bg='white')
        example.grid(row=5, column=0, columnspan=3, sticky='w')

        # Kayıtlı veriler listesi
        list_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        tk.Label(list_frame, text=self.lm.tr('saved_electricity_data', "Kaydedilmiş Elektrik Verileri"),
                font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white').pack(pady=10)

        # Treeview
        columns = ('period', 'grid_type', 'quantity', 'co2e')
        self.s2_elec_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=6)

        self.s2_elec_tree.heading('period', text=self.lm.tr('period', 'Dönem'))
        self.s2_elec_tree.heading('grid_type', text=self.lm.tr('grid_type', 'Şebeke Türü'))
        self.s2_elec_tree.heading('quantity', text=self.lm.tr('quantity_kwh', 'Miktar (kWh)'))
        self.s2_elec_tree.heading('co2e', text=self.lm.tr('tco2e', 'tCO2e'))

        self.s2_elec_tree.pack(fill='both', expand=True, padx=10, pady=10)

    def create_heating_form(self, parent) -> None:
        """Isıtma/soğutma formu"""
        form_frame = tk.Frame(parent, bg='white')
        form_frame.pack(fill='x', padx=20, pady=20)

        tk.Label(form_frame, text=self.lm.tr('heating_cooling_purchased', "Satın Alınan Isıtma/Soğutma"),
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(pady=(0, 20))

        tk.Label(form_frame, text=self.lm.tr('heating_cooling_desc', "Bu bölüm bölgesel ısıtma veya satın alınan buhar için kullanılır."),
                font=('Segoe UI', 10), fg='#666', bg='white').pack()

        # Henüz nadir kullanım - basit form

    def create_scope3_tab(self) -> None:
        """Scope 3 sekmesi - Değer Zinciri"""
        scope3_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(scope3_frame, text=f"{Icons.LINK} {self.lm.tr('scope3_title', 'Scope 3 - Değer Zinciri')}")

        # Bilgi
        info_frame = tk.Frame(scope3_frame, bg='#ecf0f1', relief='solid', bd=1)
        info_frame.pack(fill='x', padx=20, pady=20)

        tk.Label(info_frame, text=f"{Icons.CLIPBOARD} {self.lm.tr('scope3_categories_title', 'Scope 3 Kategorileri (GHG Protocol)')}",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='#ecf0f1').pack(pady=15)

        tk.Label(info_frame,
                text=self.lm.tr('scope3_desc', "Scope 3, değer zincirinizde gerçekleşen dolaylı emisyonları kapsar.\n15 standart kategori bulunmaktadır. En yaygın kategoriler:"),
                font=('Segoe UI', 10), fg='#34495e', bg='#ecf0f1', justify='left').pack(padx=20)

        categories_text = f"""
• {self.lm.tr('cat1', 'Kategori 1: Satın Alınan Mallar ve Hizmetler')}
• {self.lm.tr('cat6', 'Kategori 6: İş Seyahatleri')}
• {self.lm.tr('cat7', 'Kategori 7: Çalışan İşe Gidiş-Geliş')}
• {self.lm.tr('cat5', 'Kategori 5: Operasyonlarda Oluşan Atık')}
• {self.lm.tr('cat4', 'Kategori 4: Upstream Taşıma ve Dağıtım')}
• {self.lm.tr('cat9', 'Kategori 9: Downstream Taşıma ve Dağıtım')}
        """

        tk.Label(info_frame, text=categories_text,
                font=('Segoe UI', 9), fg='#2c3e50', bg='#ecf0f1', justify='left').pack(padx=40, pady=(5, 15))

        # İş Seyahatleri formu
        form_frame = tk.Frame(scope3_frame, bg='white', relief='solid', bd=1)
        form_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(form_frame, text=f"📍 {self.lm.tr('cat6_business_travel', 'Kategori 6: İş Seyahatleri')}",
                 font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white').pack(pady=10)

        grid = tk.Frame(form_frame, bg='white')
        grid.pack(padx=20, pady=(0, 15))

        row = 0
        # Dönem
        tk.Label(grid, text=self.lm.tr('period_year', "Dönem (Yıl):"), font=('Segoe UI', 10, 'bold'), bg='white').grid(row=row, column=0, sticky='w', pady=5, padx=(0,10))
        self.s3_bt_period = tk.Entry(grid, width=10)
        self.s3_bt_period.insert(0, str(datetime.now().year))
        self.s3_bt_period.grid(row=row, column=1, sticky='w', pady=5)
        row += 1

        # Seyahat Tipi
        tk.Label(grid, text=self.lm.tr('travel_type', "Seyahat Tipi:"), font=('Segoe UI', 10, 'bold'), bg='white').grid(row=row, column=0, sticky='w', pady=5, padx=(0,10))
        self.s3_bt_type = ttk.Combobox(grid, width=30, state='readonly')
        self.s3_bt_type.grid(row=row, column=1, sticky='w', pady=5)
        self.s3_bt_type['values'] = [
            f"flight_short - {self.lm.tr('flight_short', 'Kısa uçuş')} {self.lm.tr('flight_short_desc', '(<500 km)')}",
            f"flight_medium - {self.lm.tr('flight_medium', 'Orta uçuş')} {self.lm.tr('flight_medium_desc', '(500-3700 km)')}",
            f"flight_long - {self.lm.tr('flight_long', 'Uzun uçuş')} {self.lm.tr('flight_long_desc', '(>3700 km)')}",
            f"car - {self.lm.tr('car', 'Araç')}",
            f"train - {self.lm.tr('train', 'Tren')}"
        ]
        self.s3_bt_type.current(1)
        row += 1

        # Mesafe (km)
        tk.Label(grid, text=self.lm.tr('distance_km', "Mesafe (km):"), font=('Segoe UI', 10, 'bold'), bg='white').grid(row=row, column=0, sticky='w', pady=5, padx=(0,10))
        self.s3_bt_distance = tk.Entry(grid, width=15)
        self.s3_bt_distance.insert(0, '1000')
        self.s3_bt_distance.grid(row=row, column=1, sticky='w', pady=5)
        row += 1

        # Notlar
        tk.Label(grid, text=self.lm.tr('notes', "Notlar:"), font=('Segoe UI', 10, 'bold'), bg='white').grid(row=row, column=0, sticky='nw', pady=5, padx=(0,10))
        self.s3_bt_notes = tk.Text(grid, width=45, height=3)
        self.s3_bt_notes.grid(row=row, column=1, sticky='w', pady=5)
        row += 1

        save_btn = tk.Button(form_frame, text=f"🛫 {self.lm.tr('save_business_travel', 'İş Seyahati Kaydet')}",
                             font=('Segoe UI', 11, 'bold'), bg='#3498db', fg='white',
                             relief='flat', cursor='hand2', padx=20, pady=8,
                             command=self.save_scope3_business_travel)
        save_btn.pack(pady=(0, 15))

        # Harcama bazlı giriş
        spend_frame = tk.Frame(form_frame, bg='#f9f9f9', relief='solid', bd=1)
        spend_frame.pack(fill='x', padx=20, pady=(0, 15))
        tk.Label(spend_frame, text=f"💳 {self.lm.tr('spend_based_entry', 'Harcamaya Dayalı Kayıt (USD)')}",
                 font=('Segoe UI', 11, 'bold'), fg='#2c3e50', bg='#f9f9f9').pack(pady=8)
        sf_grid = tk.Frame(spend_frame, bg='#f9f9f9')
        sf_grid.pack(padx=10, pady=5)
        tk.Label(sf_grid, text=self.lm.tr('period_year', "Dönem (Yıl):"), font=('Segoe UI', 10, 'bold'), bg='#f9f9f9').grid(row=0, column=0, sticky='w', pady=5, padx=(0,10))
        self.s3_spend_period = tk.Entry(sf_grid, width=10)
        self.s3_spend_period.insert(0, str(datetime.now().year))
        self.s3_spend_period.grid(row=0, column=1, sticky='w', pady=5)
        tk.Label(sf_grid, text=self.lm.tr('spend_usd', "Harcama (USD):"), font=('Segoe UI', 10, 'bold'), bg='#f9f9f9').grid(row=1, column=0, sticky='w', pady=5, padx=(0,10))
        self.s3_spend_usd = tk.Entry(sf_grid, width=15)
        self.s3_spend_usd.insert(0, '1000')
        self.s3_spend_usd.grid(row=1, column=1, sticky='w', pady=5)
        tk.Label(sf_grid, text=self.lm.tr('notes', "Notlar:"), font=('Segoe UI', 10, 'bold'), bg='#f9f9f9').grid(row=2, column=0, sticky='nw', pady=5, padx=(0,10))
        self.s3_spend_notes = tk.Text(sf_grid, width=45, height=3)
        self.s3_spend_notes.grid(row=2, column=1, sticky='w', pady=5)
        tk.Button(spend_frame, text=f"{Icons.SAVE} {self.lm.tr('save_spend_based', 'Harcama Bazlı Kaydet')}",
                  font=('Segoe UI', 10, 'bold'), bg='#8e44ad', fg='white',
                  relief='flat', cursor='hand2', padx=18, pady=6,
                  command=self.save_scope3_business_travel_spend).pack(pady=8)

        # Kayıt listesi
        list_frame = tk.Frame(scope3_frame, bg='white', relief='solid', bd=1)
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        tk.Label(list_frame, text=self.lm.tr('business_travel_records', "İş Seyahatleri Kayıtları"),
                 font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white').pack(pady=10)

        columns = ('period', 'travel_type', 'distance_km', 'co2e', 'notes')
        self.scope3_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        self.scope3_tree.heading('period', text=self.lm.tr('period', 'Dönem'))
        self.scope3_tree.heading('travel_type', text=self.lm.tr('travel_type', 'Seyahat Tipi'))
        self.scope3_tree.heading('distance_km', text=self.lm.tr('amount_km_usd', 'Miktar (km/USD)'))
        self.scope3_tree.heading('co2e', text=self.lm.tr('tco2e', 'tCO2e'))
        self.scope3_tree.heading('notes', text=self.lm.tr('notes', 'Notlar'))
        self.scope3_tree.pack(fill='both', expand=True, padx=10, pady=(0,10))

        # Toplu giriş ve CSV içe/dışa aktarım
        bulk_frame = tk.Frame(scope3_frame, bg='white', relief='solid', bd=1)
        bulk_frame.pack(fill='x', padx=20, pady=(0, 20))
        tk.Label(bulk_frame, text=self.lm.tr('bulk_business_travel_entry', "Toplu İş Seyahati Girişi"),
                 font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white').pack(pady=8)
        bulk_controls = tk.Frame(bulk_frame, bg='white')
        bulk_controls.pack(fill='x', padx=10, pady=5)
        tk.Button(bulk_controls, text=f"{Icons.ADD} {self.lm.tr('add_row', 'Satır Ekle')}", width=15, command=self.add_scope3_input_row,
                  bg='#2ecc71', fg='white', relief='flat').pack(side='left', padx=5)
        tk.Button(bulk_controls, text=f"{Icons.REMOVE} {self.lm.tr('delete_selected_row', 'Seçili Satırı Sil')}", width=18, command=self.remove_scope3_input_row,
                  bg='#e74c3c', fg='white', relief='flat').pack(side='left', padx=5)
        tk.Button(bulk_controls, text=f"{Icons.SAVE} {self.lm.tr('save_bulk', 'Toplu Kaydet')}", width=16, command=self.save_scope3_bulk,
                  bg='#3498db', fg='white', relief='flat').pack(side='left', padx=5)
        tk.Button(bulk_controls, text=f"📥 {self.lm.tr('import_csv', 'CSV İçe Aktar')}", width=16, command=self.import_scope3_csv,
                  bg='#8e44ad', fg='white', relief='flat').pack(side='left', padx=5)
        tk.Button(bulk_controls, text=f"{Icons.OUTBOX} {self.lm.tr('export_csv', 'CSV Dışa Aktar')}", width=16, command=self.export_scope3_csv,
                  bg='#34495e', fg='white', relief='flat').pack(side='left', padx=5)

        columns_in = ('period', 'travel_type', 'distance_km', 'notes')
        self.scope3_input_tree = ttk.Treeview(bulk_frame, columns=columns_in, show='headings', height=6)
        for c, t in zip(columns_in, [self.lm.tr('period', 'Dönem'), self.lm.tr('travel_type', 'Seyahat Tipi'), self.lm.tr('distance_km', 'Mesafe (km)'), self.lm.tr('notes', 'Notlar')]):
            self.scope3_input_tree.heading(c, text=t)
        self.scope3_input_tree.pack(fill='x', padx=10, pady=(0,10))

        # İlk yükleme
        self.load_scope3_data()

    def create_targets_tab(self) -> None:
        """Hedefler sekmesi"""
        targets_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(targets_frame, text=f"🎯 {self.lm.tr('carbon_targets', 'Karbon Hedefleri')}")

        # Form
        form_frame = tk.Frame(targets_frame, bg='white', relief='solid', bd=1)
        form_frame.pack(fill='x', padx=20, pady=20)

        tk.Label(form_frame, text=self.lm.tr('new_carbon_target', "Yeni Karbon Azaltma Hedefi"),
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(pady=15)

        # Grid formu
        grid_frame = tk.Frame(form_frame, bg='white')
        grid_frame.pack(padx=20, pady=(0, 20))

        row = 0

        # Hedef Adı
        tk.Label(grid_frame, text=self.lm.tr('target_name', "Hedef Adı:"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=row, column=0, sticky='w', pady=5, padx=(0, 10))
        self.target_name = tk.Entry(grid_frame, width=40)
        self.target_name.grid(row=row, column=1, sticky='w', pady=5)
        row += 1

        # Kapsam
        tk.Label(grid_frame, text=self.lm.tr('scope', "Kapsam:"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=row, column=0, sticky='w', pady=5, padx=(0, 10))
        self.target_scope = ttk.Combobox(grid_frame, width=25, state='readonly')
        self.target_scope.grid(row=row, column=1, sticky='w', pady=5)
        self.target_scope['values'] = [
            f"scope1 - {self.lm.tr('scope1', 'Scope 1')}",
            f"scope1_2 - {self.lm.tr('scope1_2', 'Scope 1+2')}",
            f"scope1_2_3 - {self.lm.tr('scope1_2_3', 'Scope 1+2+3')}"
        ]
        self.target_scope.current(1)
        row += 1

        # Baz Yıl
        tk.Label(grid_frame, text=self.lm.tr('baseline_year', "Baz Yıl:"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=row, column=0, sticky='w', pady=5, padx=(0, 10))
        self.target_baseline_year = tk.Entry(grid_frame, width=10)
        self.target_baseline_year.insert(0, str(datetime.now().year - 1))
        self.target_baseline_year.grid(row=row, column=1, sticky='w', pady=5)
        row += 1

        # Baz Yıl Emisyon
        tk.Label(grid_frame, text=self.lm.tr('baseline_emission_co2e', "Baz Yıl Emisyon (tCO2e):"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=row, column=0, sticky='w', pady=5, padx=(0, 10))
        self.target_baseline_co2e = tk.Entry(grid_frame, width=15)
        self.target_baseline_co2e.grid(row=row, column=1, sticky='w', pady=5)
        row += 1

        # Hedef Yıl
        tk.Label(grid_frame, text=self.lm.tr('target_year', "Hedef Yıl:"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=row, column=0, sticky='w', pady=5, padx=(0, 10))
        self.target_year = tk.Entry(grid_frame, width=10)
        self.target_year.insert(0, str(datetime.now().year + 10))
        self.target_year.grid(row=row, column=1, sticky='w', pady=5)
        row += 1

        # Hedef Azaltma (%)
        tk.Label(grid_frame, text=self.lm.tr('target_reduction_pct', "Hedef Azaltma (%):"), font=('Segoe UI', 10, 'bold'),
                bg='white').grid(row=row, column=0, sticky='w', pady=5, padx=(0, 10))
        self.target_reduction_pct = tk.Entry(grid_frame, width=10)
        self.target_reduction_pct.insert(0, "50")
        self.target_reduction_pct.grid(row=row, column=1, sticky='w', pady=5)
        row += 1

        # Kaydet
        save_btn = tk.Button(form_frame, text=f"🎯 {self.lm.tr('save_target', 'Hedef Kaydet')}",
                            font=('Segoe UI', 11, 'bold'), bg='#3498db', fg='white',
                            relief='flat', cursor='hand2', padx=20, pady=10,
                            command=self.save_carbon_target)
        save_btn.pack(pady=(0, 20))

        # Hedefler listesi
        list_frame = tk.Frame(targets_frame, bg='white', relief='solid', bd=1)
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        tk.Label(list_frame, text=self.lm.tr('defined_carbon_targets', "Tanımlı Karbon Hedefleri"),
                font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white').pack(pady=10)

        columns = ('target_name', 'scope', 'baseline', 'target', 'reduction_pct', 'status')
        self.targets_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)

        self.targets_tree.heading('target_name', text=self.lm.tr('target_name', 'Hedef Adı'))
        self.targets_tree.heading('scope', text=self.lm.tr('scope', 'Kapsam'))
        self.targets_tree.heading('baseline', text=self.lm.tr('baseline_emission', 'Baz Emisyon'))
        self.targets_tree.heading('target', text=self.lm.tr('target_emission', 'Hedef Emisyon'))
        self.targets_tree.heading('reduction_pct', text=self.lm.tr('reduction_pct', 'Azaltma %'))
        self.targets_tree.heading('status', text=self.lm.tr('status', 'Durum'))

        self.targets_tree.pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def create_initiatives_tab(self) -> None:
        """Azaltma girişimleri sekmesi"""
        init_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(init_frame, text=f"{Icons.LEAF} {self.lm.tr('reduction_initiatives', 'Azaltma Girişimleri')}")

        tk.Label(init_frame, text=self.lm.tr('emission_reduction_projects', "Emisyon Azaltma Projeleri"),
                font=('Segoe UI', 16, 'bold'), fg='#27ae60', bg='white').pack(pady=20)

        # Form placeholder
        tk.Label(init_frame,
                text=self.lm.tr('initiatives_desc', "Bu bölümde emisyon azaltma projelerinizi kaydedebilir,\nbeklenen/gerçekleşen azaltmaları takip edebilirsiniz."),
                font=('Segoe UI', 11), fg='#666', bg='white', justify='center').pack(pady=10)

    def create_offset_tab(self) -> None:
        """Offset yönetimi sekmesi - OffsetGUI entegrasyonu"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=f"{Icons.TREE} {self.lm.tr('offset_management', 'Offset Yönetimi')}")

        try:
            from .offset_gui import OffsetGUI
            OffsetGUI(tab, self.company_id)
        except Exception as e:
            error_frame = tk.Frame(tab, bg='white')
            error_frame.pack(fill='both', expand=True, padx=20, pady=20)

            tk.Label(error_frame, text=f"{Icons.WARNING} {self.lm.tr('offset_module_load_error', 'Offset Modülü Yüklenemedi')}",
                    font=('Segoe UI', 14, 'bold'), fg='#e74c3c', bg='white').pack(pady=10)
            tk.Label(error_frame, text=f"{self.lm.tr('error', 'Hata')}: {str(e)}",
                    font=('Segoe UI', 10), fg='#7f8c8d', bg='white').pack(pady=5)

    def create_reports_tab(self) -> None:
        """Raporlar ve analiz sekmesi"""
        reports_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(reports_frame, text=f"{Icons.REPORT} {self.lm.tr('reports_and_analysis', 'Raporlar ve Analiz')}")

        # Rapor oluşturma bölümü
        report_gen_frame = tk.Frame(reports_frame, bg='#f8f9fa', relief='solid', bd=1)
        report_gen_frame.pack(fill='x', padx=20, pady=20)

        tk.Label(report_gen_frame, text=f"{Icons.FILE} {self.lm.tr('create_emission_report', 'Emisyon Raporu Oluştur')}",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='#f8f9fa').pack(pady=15)

        # Dönem seçimi
        period_frame = tk.Frame(report_gen_frame, bg='#f8f9fa')
        period_frame.pack(pady=10)

        tk.Label(period_frame, text=self.lm.tr('report_period', "Rapor Dönemi:"), font=('Segoe UI', 10, 'bold'),
                bg='#f8f9fa').pack(side='left', padx=10)
        self.report_period = tk.Entry(period_frame, width=10)
        self.report_period.insert(0, str(datetime.now().year))
        self.report_period.pack(side='left')

        # Scope 3 dahil et
        self.report_include_scope3 = tk.BooleanVar(value=False)
        tk.Checkbutton(period_frame, text=self.lm.tr('include_scope3', "Scope 3 Dahil Et"),
                      variable=self.report_include_scope3,
                      font=('Segoe UI', 10), bg='#f8f9fa').pack(side='left', padx=20)

        # Rapor oluştur butonu
        generate_btn = tk.Button(report_gen_frame, text=f"{Icons.REPORT} {self.lm.tr('create_summary_report', 'Özet Rapor Oluştur')}",
                                font=('Segoe UI', 12, 'bold'), bg='#3498db', fg='white',
                                relief='flat', cursor='hand2', padx=30, pady=12,
                                command=self.generate_summary_report)
        generate_btn.pack(pady=(10, 20))

        # Rapor sonuçları alanı
        self.report_results_frame = tk.Frame(reports_frame, bg='white')
        self.report_results_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

    # ==================== EVENT HANDLERS ====================

    def save_scope1_stationary(self) -> None:
        """Scope 1 sabit yakma kaydet"""
        try:
            # Form verilerini al
            period = self.s1_stat_period.get().strip()
            fuel_type = self.s1_stat_fuel_type.get().split(' - ')[0]
            quantity = float(self.s1_stat_quantity.get())
            quality = self.s1_stat_quality.get().split(' - ')[0]
            notes = self.s1_stat_notes.get('1.0', tk.END).strip()

            # Unit'i faktörden al
            factor_info = self.manager.emission_factors.get_emission_factor(
                'scope1', 'stationary', fuel_type
            )
            unit = factor_info['unit'] if factor_info else 'unit'

            # Kaydet
            emission_id = self.manager.save_emission_record(
                company_id=self.company_id,
                period=period,
                scope='scope1',
                category='stationary',
                fuel_type=fuel_type,
                quantity=quantity,
                unit=unit,
                data_quality=quality,
                notes=notes
            )

            if emission_id:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('scope1_stationary_saved', "Scope 1 sabit yakma verisi kaydedildi!"))
                # Formu temizle
                self.s1_stat_quantity.delete(0, tk.END)
                self.s1_stat_notes.delete('1.0', tk.END)
                # Listeyi yenile
                self.load_scope1_data()
                # İstatistikleri güncelle
                self.refresh_stats()
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('data_not_saved', "Veri kaydedilemedi!"))

        except ValueError as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('invalid_amount_error', 'Geçersiz miktar değeri')}: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('save_error', 'Kaydetme hatası')}: {e}")

    def save_scope1_mobile(self) -> None:
        """Scope 1 mobil yakma kaydet"""
        try:
            period = self.s1_mobile_period.get().strip()
            fuel_type = self.s1_mobile_fuel_type.get().split(' - ')[0]
            quantity = float(self.s1_mobile_quantity.get())

            emission_id = self.manager.save_emission_record(
                company_id=self.company_id,
                period=period,
                scope='scope1',
                category='mobile',
                fuel_type=fuel_type,
                quantity=quantity,
                unit='litre',
                source=f"{self.s1_mobile_vehicle_count.get()} {self.lm.tr('vehicle_unit', 'araç')}"
            )

            if emission_id:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('scope1_mobile_saved', "Araç filosu verisi kaydedildi!"))
                self.load_data()
                self.refresh_stats()

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('save_error', 'Kaydetme hatası')}: {e}")

    def save_scope1_fugitive(self) -> None:
        """Scope 1 kaçak emisyon kaydet"""
        try:
            period = self.s1_fug_period.get().strip()
            ref_type = self.s1_fug_type.get().split(' - ')[0]
            quantity = float(self.s1_fug_quantity.get())

            emission_id = self.manager.save_emission_record(
                company_id=self.company_id,
                period=period,
                scope='scope1',
                category='fugitive',
                fuel_type=ref_type,
                quantity=quantity,
                unit='kg'
            )

            if emission_id:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('scope1_fugitive_saved', "Kaçak emisyon verisi kaydedildi!"))
                self.load_data()
                self.refresh_stats()

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('save_error', 'Kaydetme hatası')}: {e}")

    def save_scope2_electricity(self) -> None:
        """Scope 2 elektrik kaydet"""
        try:
            period = self.s2_elec_period.get().strip()
            grid_type = self.s2_elec_grid.get().split(' - ')[0]
            quantity = float(self.s2_elec_quantity.get())

            emission_id = self.manager.save_emission_record(
                company_id=self.company_id,
                period=period,
                scope='scope2',
                category='electricity',
                fuel_type=grid_type,
                quantity=quantity,
                unit='kWh'
            )

            if emission_id:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('scope2_electricity_saved', "Elektrik tüketimi kaydedildi!"))
                self.s2_elec_quantity.delete(0, tk.END)
                self.load_data()
                self.refresh_stats()

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('save_error', 'Kaydetme hatası')}: {e}")

    def save_carbon_target(self) -> None:
        """Karbon hedefini kaydet"""
        try:
            baseline_co2e = float(self.target_baseline_co2e.get())
            reduction_pct = float(self.target_reduction_pct.get())

            # Hedef emisyonu hesapla
            target_co2e = baseline_co2e * (1 - reduction_pct / 100)

            target_data = {
                'target_name': self.target_name.get().strip(),
                'scope_coverage': self.target_scope.get().split(' - ')[0],
                'baseline_year': int(self.target_baseline_year.get()),
                'baseline_co2e': baseline_co2e,
                'target_year': int(self.target_year.get()),
                'target_co2e': target_co2e,
                'target_reduction_pct': reduction_pct
            }

            target_id = self.manager.save_carbon_target(self.company_id, target_data)

            if target_id:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"),
                    f"{self.lm.tr('carbon_target_saved', 'Karbon hedefi kaydedildi!')}\n\n"
                    f"{self.lm.tr('baseline', 'Baz')}: {baseline_co2e:.1f} tCO2e\n"
                    f"{self.lm.tr('target', 'Hedef')}: {target_co2e:.1f} tCO2e\n"
                    f"{self.lm.tr('reduction', 'Azaltma')}: %{reduction_pct}")
                self.load_targets_data()

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('target_save_error', 'Hedef kaydetme hatası')}: {e}")

    def generate_summary_report(self) -> None:
        """Emisyon özet raporu oluştur"""
        try:
            period = self.report_period.get().strip()
            include_scope3 = self.report_include_scope3.get()

            # Rapor hesapla
            summary = self.manager.generate_emissions_summary(
                company_id=self.company_id,
                period=period,
                include_scope3=include_scope3
            )

            # Sonuçları göster
            self.display_report_results(summary)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('report_generation_error', 'Rapor oluşturma hatası')}: {e}")

    def save_scope3_business_travel(self) -> None:
        """Scope 3 - İş Seyahatleri kaydet"""
        try:
            period = self.s3_bt_period.get().strip()
            travel_type = self.s3_bt_type.get().split(' - ')[0]
            distance = float(self.s3_bt_distance.get())
            notes = self.s3_bt_notes.get('1.0', tk.END).strip()

            # Emisyon faktörünü al ve co2e hesapla
            category_info = self.manager.emission_factors.SCOPE3_CATEGORIES.get('business_travel', {})
            factor = 0.0
            if 'factors' in category_info:
                factor = category_info['factors'].get(travel_type, 0.0)
            co2e = distance * factor

            # data_json: hesaplayıcı tarafından okunur
            data_json = json.dumps({
                'travel_type': travel_type,
                'distance_km': distance
            })

            emission_id = self.manager.save_emission_record(
                company_id=self.company_id,
                period=period,
                scope='scope3',
                category='business_travel',
                fuel_type=travel_type,
                quantity=distance,
                unit='km',
                calculation_method='distance_based',
                data_quality='estimated',
                data_json=data_json,
                notes=notes,
                emission_factor_source=category_info.get('source', 'DEFRA'),
                co2e_emission=co2e  # otomatik hesap yerine manuel co2e
            )

            if emission_id:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('business_travel_saved', "İş seyahati verisi kaydedildi!"))
                # Formu temizle
                self.s3_bt_distance.delete(0, tk.END)
                self.s3_bt_notes.delete('1.0', tk.END)
                # Listeyi yenile ve istatistikleri güncelle
                self.load_scope3_data()
                self.refresh_stats()
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('data_not_saved', "Veri kaydedilemedi!"))

        except ValueError as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('invalid_value_error', 'Geçersiz değer')}: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('save_error', 'Kaydetme hatası')}: {e}")

    def save_scope3_business_travel_spend(self) -> None:
        """Scope 3 - İş Seyahatleri (harcamaya dayalı) kaydet"""
        try:
            period = self.s3_spend_period.get().strip()
            spend_str = self.s3_spend_usd.get().strip()
            notes = self.s3_spend_notes.get('1.0', tk.END).strip()

            if not period or not spend_str:
                messagebox.showwarning(self.lm.tr('missing_info', "Eksik Bilgi"), self.lm.tr('fill_period_spend_fields', "Dönem ve harcama alanlarını doldurun."))
                return
            spend = float(spend_str)

            sf = 0.000200
            co2e = spend * sf

            data_json = json.dumps({
                'spend_usd': spend,
                'notes': notes
            })

            emission_id = self.manager.save_emission_record(
                company_id=self.company_id,
                period=period,
                scope='scope3',
                category='business_travel',
                fuel_type='spend_usd',
                quantity=spend,
                unit='USD',
                calculation_method='spend_based',
                data_quality='estimated',
                data_json=data_json,
                notes=notes,
                emission_factor_source='EEIO',
                co2e_emission=co2e
            )

            if emission_id:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('spend_based_business_travel_saved', "Harcama bazlı iş seyahati kaydedildi!"))
                self.s3_spend_usd.delete(0, tk.END)
                self.s3_spend_notes.delete('1.0', tk.END)
                self.load_scope3_data()
                self.refresh_stats()
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('data_not_saved', "Veri kaydedilemedi!"))

        except ValueError as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('invalid_value_error', 'Geçersiz değer')}: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('save_error', 'Kaydetme hatası')}: {e}")

    def add_scope3_input_row(self) -> None:
        self.scope3_input_tree.insert('', 'end', values=(str(datetime.now().year), 'flight_medium', '0', ''))

    def remove_scope3_input_row(self) -> None:
        sel = self.scope3_input_tree.selection()
        for s in sel:
            self.scope3_input_tree.delete(s)

    def save_scope3_bulk(self) -> None:
        try:
            rows = [self.scope3_input_tree.item(i, 'values') for i in self.scope3_input_tree.get_children()]
            if not rows:
                messagebox.showwarning(self.lm.tr('empty', "Boş"), self.lm.tr('no_rows_to_save', "Kaydedilecek satır yok."))
                return
            
            # Kategori bilgisini al
            category_info = self.manager.emission_factors.SCOPE3_CATEGORIES.get('business_travel', {})
            factors = category_info.get('factors', {})

            saved = 0
            for period, travel_type, distance_km, notes in rows:
                try:
                    distance = float(distance_km)
                except Exception:
                    continue
                
                # Faktörü manager'dan al
                factor = factors.get(travel_type, 0.0)
                
                co2e = distance * factor
                data_json = json.dumps({
                    'travel_type': travel_type,
                    'distance_km': distance,
                    'notes': notes
                })
                self.manager.save_emission_record(
                    company_id=self.company_id,
                    period=period,
                    scope='scope3',
                    category='business_travel',
                    fuel_type=travel_type,
                    quantity=distance,
                    unit='km',
                    calculation_method='distance_based',
                    data_quality='estimated',
                    data_json=data_json,
                    notes=notes,
                    emission_factor_source=category_info.get('source', 'DEFRA'),
                    co2e_emission=co2e
                )
                saved += 1
            messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{self.lm.tr('bulk_save_completed', 'Toplu kayıt tamamlandı')}. {saved} {self.lm.tr('rows_added', 'satır eklendi')}.")
            self.scope3_input_tree.delete(*self.scope3_input_tree.get_children())
            self.load_scope3_data()
            self.refresh_stats()
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('bulk_save_error', 'Toplu kayıt hatası')}: {e}")

    def import_scope3_csv(self) -> None:
        try:
            # Firma bazlı varsayılan klasör
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            company_imports = os.path.join(base_dir, 'data', 'companies', str(self.company_id), 'imports')
            os.makedirs(company_imports, exist_ok=True)
            file_path = filedialog.askopenfilename(title=self.lm.tr('import_csv', "CSV İçe Aktar"), initialdir=company_imports, filetypes=[(self.lm.tr('csv_files', 'CSV Dosyaları'), '*.csv')])
            if not file_path:
                return
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                required = {'period', 'travel_type', 'distance_km', 'notes'}
                if not required.issubset(set(reader.fieldnames or [])):
                    messagebox.showwarning(self.lm.tr('header_error', "Başlık Hatası"), self.lm.tr('csv_header_error_msg', "CSV başlıkları: period, travel_type, distance_km, notes olmalı"))
                    return
                for row in reader:
                    self.scope3_input_tree.insert('', 'end', values=(row.get('period',''), row.get('travel_type',''), row.get('distance_km','0'), row.get('notes','')))
            messagebox.showinfo(self.lm.tr('imported', "İçe Aktarıldı"), self.lm.tr('csv_data_loaded', "CSV verileri yüklendi. Toplu kaydedebilirsiniz."))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('csv_import_error', 'CSV içe aktarma hatası')}: {e}")

    def export_scope3_csv(self) -> None:
        try:
            # Firma bazlı varsayılan klasör
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            company_exports = os.path.join(base_dir, 'data', 'companies', str(self.company_id), 'exports')
            os.makedirs(company_exports, exist_ok=True)
            file_path = filedialog.asksaveasfilename(title=self.lm.tr('export_csv', "CSV Dışa Aktar"), initialdir=company_exports, initialfile='scope3_business_travel.csv', defaultextension='.csv', filetypes=[(self.lm.tr('csv_files', 'CSV Dosyaları'), '*.csv')])
            if not file_path:
                return
            emissions = self.manager.get_emissions(self.company_id, scope='scope3')
            rows = []
            for em in emissions:
                if em['category'] != 'business_travel':
                    continue
                try:
                    dj = json.loads(em.get('data_json') or '{}')
                except Exception:
                    dj = {}
                rows.append({
                    'period': em.get('period',''),
                    'travel_type': em.get('fuel_type',''),
                    'distance_km': em['quantity'] if em.get('unit') == 'km' else dj.get('distance_km', ''),
                    'notes': dj.get('notes','')
                })
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['period','travel_type','distance_km','notes'])
                writer.writeheader()
                writer.writerows(rows)
            messagebox.showinfo(self.lm.tr('exported', "Dışa Aktarıldı"), os.path.basename(file_path) + " " + self.lm.tr('saved', "kaydedildi."))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('csv_export_error', 'CSV dışa aktarma hatası')}: {e}")

    def display_report_results(self, summary: Dict) -> None:
        """Rapor sonuçlarını görüntüle"""
        # Mevcut içeriği temizle
        for widget in self.report_results_frame.winfo_children():
            widget.destroy()

        # Başlık
        tk.Label(self.report_results_frame,
                text=f"{Icons.REPORT} {self.lm.tr('emissions_summary_report', 'Emisyon Özet Raporu')} - {summary['period']}",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(pady=15)

        # Sonuçlar
        results_frame = tk.Frame(self.report_results_frame, bg='#ecf0f1', relief='solid', bd=1)
        results_frame.pack(fill='x', padx=40, pady=10)

        result_text = f"""
📍 {self.lm.tr('scope1_direct', 'Scope 1 (Doğrudan)')}: {summary['scope1_total']:.2f} tCO2e
📍 {self.lm.tr('scope2_indirect', 'Scope 2 (Dolaylı)')}: {summary['scope2_total']:.2f} tCO2e
📍 {self.lm.tr('scope1_2_total', 'Scope 1+2 Toplam')}: {summary['scope1_2_total']:.2f} tCO2e
        """

        if 'scope3_total' in summary and summary['scope3_total'] > 0:
            result_text += f"\n📍 {self.lm.tr('scope3_value_chain', 'Scope 3 (Değer Zinciri)')}: {summary['scope3_total']:.2f} tCO2e"
            result_text += f"\n\n🎯 {self.lm.tr('total_emissions_caps', 'TOPLAM EMİSYON')}: {summary['total_co2e']:.2f} tCO2e"
        else:
            result_text += f"\n\n🎯 {self.lm.tr('total_emissions_caps', 'TOPLAM EMİSYON')} (Scope 1+2): {summary['total_co2e']:.2f} tCO2e"

        result_text += f"\n\nIcons.CALENDAR {self.lm.tr('calculation_date', 'Hesaplama Tarihi')}: {summary['calculated_at'][:10]}"

        # Sonuçları görüntüle - Scrollable Text
        text_frame = tk.Frame(results_frame, bg='#ecf0f1')
        text_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Text widget with scrollbar
        result_text_widget = tk.Text(text_frame,
                                    font=('Segoe UI', 11),
                                    fg='#2c3e50',
                                    bg='white',
                                    wrap='word',
                                    height=8,
                                    width=50)
        result_text_widget.pack(side='left', fill='both', expand=True)

        # Scrollbar
        scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=result_text_widget.yview)
        scrollbar.pack(side='right', fill='y')

        # Configure text widget
        result_text_widget.config(yscrollcommand=scrollbar.set)
        result_text_widget.insert('1.0', result_text)
        result_text_widget.config(state='disabled')  # Read-only

        # Scope 3 dağılımı
        if summary.get('scope3_breakdown'):
            br_frame = tk.Frame(self.report_results_frame, bg='white', relief='solid', bd=1)
            br_frame.pack(fill='x', padx=40, pady=10)
            tk.Label(br_frame, text=self.lm.tr('scope3_category_breakdown', "Scope 3 Kategori Dağılımı"), font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white').pack(pady=8)
            columns = ('category', 'co2e')
            tv = ttk.Treeview(br_frame, columns=columns, show='headings', height=6)
            tv.heading('category', text=self.lm.tr('category', "Kategori"))
            tv.heading('co2e', text=self.lm.tr('tco2e', "tCO2e"))
            tv.pack(fill='x', padx=10, pady=(0,10))
            for cat, val in summary['scope3_breakdown'].items():
                tv.insert('', 'end', values=(cat, f"{val:.3f}"))

        # Kaydet butonu
        save_btn = tk.Button(self.report_results_frame, text=f"{Icons.SAVE} {self.lm.tr('save_report_to_db', 'Raporu Veritabanına Kaydet')}",
                            font=('Segoe UI', 10, 'bold'), bg='#27ae60', fg='white',
                            relief='flat', cursor='hand2', padx=20, pady=8,
                            command=lambda: self.save_report_to_db(summary))
        save_btn.pack(pady=10)

    def save_report_to_db(self, summary: Dict) -> None:
        """Raporu veritabanına kaydet"""
        try:
            report_id = self.manager.save_carbon_report(
                company_id=self.company_id,
                period=summary['period'],
                footprint_data=summary
            )

            if report_id:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('emission_report_saved', "Emisyon raporu kaydedildi!"))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('report_save_error', 'Rapor kaydetme hatası')}: {e}")

    def load_scope3_data(self) -> None:
        """Scope 3 - İş Seyahatleri kayıtlarını yükle"""
        try:
            # Ağacı temizle
            for i in self.scope3_tree.get_children():
                self.scope3_tree.delete(i)

            emissions = self.manager.get_emissions(self.company_id, scope='scope3')
            for em in emissions:
                if em['category'] != 'business_travel':
                    continue
                period = em['period']
                travel_type = em['fuel_type']
                amount = f"{em['quantity']} {em.get('unit','')}"
                co2e = em['co2e_emissions']
                notes = em.get('notes', '')
                self.scope3_tree.insert('', 'end', values=(period, travel_type, amount, round(co2e, 3), notes))
        except Exception as e:
            logging.error(f"Scope 3 verisi yükleme hatası: {e}")

    # ==================== YARDIMCI METODLAR ====================

    def load_data(self) -> None:
        """Tüm verileri yükle"""
        self.load_scope1_data()
        self.load_scope2_data()
        self.load_targets_data()

    def load_scope1_data(self) -> None:
        """Scope 1 verilerini listele"""
        try:
            emissions = self.manager.get_emissions(
                company_id=self.company_id,
                scope='scope1'
            )

            # Treeview'ları temizle
            for item in self.s1_stat_tree.get_children():
                self.s1_stat_tree.delete(item)
            
            if hasattr(self, 's1_mobile_tree'):
                for item in self.s1_mobile_tree.get_children():
                    self.s1_mobile_tree.delete(item)

            # Verileri ekle
            for em in emissions:
                category = em.get('category')
                fuel_key = em.get('fuel_type', '')
                fuel_display = self.lm.tr(fuel_key, fuel_key)
                unit_key = em.get('unit', '')
                unit_display = self.lm.tr(unit_key, unit_key)

                if category == 'stationary':
                    quality_key = em.get('data_quality', '')
                    quality_display = self.lm.tr(quality_key, quality_key)
                    
                    self.s1_stat_tree.insert('', 'end', values=(
                        em['period'],
                        fuel_display,
                        f"{em['quantity']:.1f} {unit_display}",
                        f"{em['co2e_emissions']:.2f}",
                        quality_display
                    ))
                elif category == 'mobile' and hasattr(self, 's1_mobile_tree'):
                    # columns = ('period', 'fuel_type', 'quantity', 'vehicles', 'co2e')
                    source = em.get('source', '')
                    self.s1_mobile_tree.insert('', 'end', values=(
                        em['period'],
                        fuel_display,
                        f"{em['quantity']:.1f} {unit_display}",
                        source,
                        f"{em['co2e_emissions']:.2f}"
                    ))

        except Exception as e:
            logging.error(f"Scope 1 veri yükleme hatası: {e}")

    def load_scope2_data(self) -> None:
        """Scope 2 verilerini listele"""
        # Benzer şekilde Scope 2 için
        pass

    def load_targets_data(self) -> None:
        """Hedefleri listele"""
        try:
            targets = self.manager.get_carbon_targets(self.company_id)

            # Treeview'ı temizle
            for item in self.targets_tree.get_children():
                self.targets_tree.delete(item)

            # Verileri ekle
            for target in targets:
                self.targets_tree.insert('', 'end', values=(
                    target['target_name'],
                    target['scope_coverage'],
                    f"{target['baseline_co2e']:.1f} tCO2e",
                    f"{target['target_co2e']:.1f} tCO2e",
                    f"%{target['target_reduction_pct']:.0f}",
                    target['status']
                ))

        except Exception as e:
            logging.error(f"Hedef yükleme hatası: {e}")

    def refresh_stats(self) -> None:
        """İstatistik kartlarını yenile"""
        if not hasattr(self, 'stats_frame') or not self.stats_frame.winfo_exists():
            return

        # Mevcut kartları temizle
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        # Dashboard verilerini al
        try:
            stats = self.manager.get_dashboard_stats(self.company_id)
        except Exception:
            stats = {
                'current_total_co2e': 0,
                'scope1_total': 0,
                'scope2_total': 0,
                'scope3_total': 0,
                'year_over_year_change_pct': 0,
                'active_targets_count': 0
            }

        # Kartlar
        cards = [
            (f"{Icons.REPORT} {self.lm.tr('total_emissions', 'Toplam Emisyon')}", f"{stats['current_total_co2e']:.1f} tCO2e",
             f"{self.lm.tr('year', 'Yıl')}: {stats.get('current_year', datetime.now().year)}", "#3498db"),
            (f"🏭 {self.lm.tr('scope1', 'Scope 1')}", f"{stats['scope1_total']:.1f} tCO2e",
             self.lm.tr('direct_emissions', "Doğrudan Emisyonlar"), "#e74c3c"),
            (f"⚡ {self.lm.tr('scope2', 'Scope 2')}", f"{stats['scope2_total']:.1f} tCO2e",
             self.lm.tr('indirect_emissions', "Dolaylı Emisyonlar"), "#f39c12"),
            (f"{Icons.LINK} {self.lm.tr('scope3', 'Scope 3')}", f"{stats['scope3_total']:.1f} tCO2e",
             self.lm.tr('value_chain', "Değer Zinciri"), "#9b59b6"),
            (f"{Icons.CHART_UP} {self.lm.tr('yearly_change', 'Yıllık Değişim')}", f"{stats['year_over_year_change_pct']:+.1f}%",
             self.lm.tr('vs_previous_year', "Önceki Yıla Göre"), "#27ae60" if stats['year_over_year_change_pct'] > 0 else "#e67e22"),
            (f"🎯 {self.lm.tr('active_targets', 'Aktif Hedefler')}", f"{stats['active_targets_count']}",
             self.lm.tr('target_count', "Hedef Sayısı"), "#16a085")
        ]

        for i, (title, value, subtitle, color) in enumerate(cards):
            card = tk.Frame(self.stats_frame, bg=color, relief='raised', bd=2)
            card.grid(row=0, column=i, padx=8, pady=5, sticky='ew')
            self.stats_frame.grid_columnconfigure(i, weight=1)

            tk.Label(card, text=title, font=('Segoe UI', 10, 'bold'),
                    fg='white', bg=color).pack(pady=(12, 5))
            tk.Label(card, text=value, font=('Segoe UI', 16, 'bold'),
                    fg='white', bg=color).pack()
            tk.Label(card, text=subtitle, font=('Segoe UI', 8),
                    fg='white', bg=color).pack(pady=(2, 12))

    def load_data(self) -> None:
        """Başlangıç verilerini yükle"""
        self.load_scope1_data()
        self.load_targets_data()

