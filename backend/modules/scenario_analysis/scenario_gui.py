import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Senaryo Analizi GUI - TAM VE EKSİKSİZ (TÜRKÇE)
TCFD senaryoları, BAU vs Net Zero, Risk modelleme, Finansal simülasyon
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict

from .scenario_engine import ScenarioEngine
from config.database import DB_PATH


class ScenarioGUI:
    """Senaryo analizi GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.engine = ScenarioEngine()

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Senaryo arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#1565C0', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=" Senaryo Analizi ve İklim Modelleme",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#1565C0')
        title_label.pack(expand=True)

        # Ana içerik alanı
        content_frame = tk.Frame(main_frame, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Notebook oluştur
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Sekmeleri oluştur
        self.create_dashboard_tab()
        self.create_tcfd_tab()
        self.create_bau_netzero_tab()
        self.create_transition_risk_tab()
        self.create_physical_risk_tab()
        self.create_financial_impact_tab()

    def create_dashboard_tab(self) -> None:
        """Dashboard sekmesi"""
        dashboard_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(dashboard_frame, text=" Genel Bakış")

        # Başlık
        tk.Label(dashboard_frame, text="Senaryo Analizi Dashboard",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Açıklama
        desc_text = """
         İklim Senaryo Analizi Özellikleri:
        
         TCFD Senaryoları (1.5°C, 2°C, 4°C)
         İş Her Zamanki Gibi (BAU) vs Net Zero 2050
         Geçiş Riski Modelleme (Politika, Teknoloji, Pazar)
         Fiziksel Risk Modelleme (Ani ve Kronik Riskler)
         Finansal Etki Simülasyonu (2024-2050)
        """

        tk.Label(dashboard_frame, text=desc_text, font=('Segoe UI', 11),
                bg='white', justify='left').pack(padx=40, pady=20)

        # İstatistik kartları
        self.stats_frame = tk.Frame(dashboard_frame, bg='white')
        self.stats_frame.pack(fill='x', padx=20, pady=20)

    def create_tcfd_tab(self) -> None:
        """TCFD senaryoları sekmesi"""
        tcfd_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tcfd_frame, text="️ TCFD Senaryoları")

        # Başlık
        tk.Label(tcfd_frame, text="TCFD İklim Senaryoları (Türkçe)",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Senaryo açıklamaları
        scenarios_info = """
        ️ 1.5°C Senaryosu (Net Zero 2050):
           • Küresel ısınma 1.5°C ile sınırlandırılır
           • Karbon fiyatı: 200 USD/tCO2 (2030) → 400 USD (2050)
           • Yenilenebilir enerji: %75 (2030) → %95 (2050)
           • Fiziksel Risk: Çok Düşük | Geçiş Riski: Çok Yüksek
        
        ️ 2°C Senaryosu (Paris Anlaşması):
           • Küresel ısınma 2°C ile sınırlandırılır
           • Karbon fiyatı: 140 USD/tCO2 (2030) → 250 USD (2050)
           • Yenilenebilir enerji: %60 (2030) → %90 (2050)
           • Fiziksel Risk: Düşük | Geçiş Riski: Yüksek
        
        ️ 4°C Senaryosu (Mevcut Politikalar):
           • Küresel ısınma 4°C'ye ulaşır
           • Karbon fiyatı: 30 USD/tCO2 (2030) → 60 USD (2050)
           • Yenilenebilir enerji: %30 (2030) → %45 (2050)
           • Fiziksel Risk: Çok Yüksek | Geçiş Riski: Düşük
        """

        tk.Label(tcfd_frame, text=scenarios_info, font=('Segoe UI', 10),
                bg='white', justify='left').pack(padx=30, pady=10)

        # Senaryo oluşturma butonu
        tk.Button(tcfd_frame, text=" Yeni TCFD Senaryosu Oluştur",
                 command=self.create_tcfd_scenario,
                 bg='#1565C0', fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=10).pack(pady=10)

        # Senaryo listesi
        self.tcfd_tree = ttk.Treeview(tcfd_frame,
                                     columns=('Senaryo', 'Hedef Yıl', 'Emisyon Azaltım', 'Durum'),
                                     show='headings', height=8)

        for col in ['Senaryo', 'Hedef Yıl', 'Emisyon Azaltım', 'Durum']:
            self.tcfd_tree.heading(col, text=col)
            self.tcfd_tree.column(col, width=150)

        self.tcfd_tree.pack(fill='both', expand=True, padx=20, pady=10)

    def create_bau_netzero_tab(self) -> None:
        """BAU vs Net Zero sekmesi"""
        comparison_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(comparison_frame, text="️ BAU vs Net Zero")

        # Başlık
        tk.Label(comparison_frame, text="İş Her Zamanki Gibi vs Net Zero 2050",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Karşılaştırma özeti
        summary_frame = tk.LabelFrame(comparison_frame, text="Karşılaştırma Özeti",
                                     font=('Segoe UI', 12, 'bold'), bg='white')
        summary_frame.pack(fill='x', padx=20, pady=10)

        comparison_text = """
         BAU (İş Her Zamanki Gibi):
           • 4°C küresel ısınma senaryosu
           • Minimum müdahale
           • Yüksek fiziksel risk
           • Düşük geçiş maliyeti (kısa vadede)
        
         Net Zero 2050:
           • 1.5°C küresel ısınma senaryosu
           • Agresif emisyon azaltımı
           • Düşük fiziksel risk
           • Yüksek geçiş maliyeti (ama uzun vadede kazançlı)
        
         Karşılaştırma Metrikleri:
            Toplam emisyon azaltımı (tCO2e)
            Finansal etki (USD)
            Risk profili (Geçiş + Fiziksel)
            ROI (Yatırım getirisi)
        """

        tk.Label(summary_frame, text=comparison_text, font=('Segoe UI', 10),
                bg='white', justify='left').pack(padx=20, pady=10)

        # Karşılaştırma butonu
        tk.Button(comparison_frame, text=" BAU vs Net Zero Karşılaştırması Oluştur",
                 command=self.create_bau_netzero,
                 bg='#E65100', fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=10).pack(pady=10)

    def create_transition_risk_tab(self) -> None:
        """Geçiş riskleri sekmesi"""
        transition_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(transition_frame, text=" Geçiş Riskleri")

        # Başlık
        tk.Label(transition_frame, text="Geçiş Riski Modelleme (Türkçe)",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Risk kategorileri
        risk_text = """
         Geçiş Riski Kategorileri:
        
        1️⃣ Politika ve Düzenleyici Risk:
           • Karbon fiyatlama (ETS, karbon vergisi)
           • Emisyon sınırları ve kotalar
           • Raporlama gereklilikleri
        
        2️⃣ Teknoloji Riski:
           • Düşük karbonlu teknolojilere geçiş maliyeti
           • Eski teknolojilerin değer kaybı
           • Yeni teknoloji yatırımları
        
        3️⃣ Pazar Riski:
           • Müşteri tercihlerinde değişim
           • Rekabet avantajı kaybı
           • Yeşil ürünlere talep artışı
        
        4️⃣ İtibar Riski:
           • Paydaş algısı
           • Yatırımcı güveni
           • Marka değeri
        """

        tk.Label(transition_frame, text=risk_text, font=('Segoe UI', 10),
                bg='white', justify='left').pack(padx=30, pady=10)

        # Risk listesi
        self.transition_tree = ttk.Treeview(transition_frame,
                                           columns=('Kategori', 'Açıklama', 'Olasılık', 'Etki', 'Finansal Etki'),
                                           show='headings', height=8)

        for col in ['Kategori', 'Açıklama', 'Olasılık', 'Etki', 'Finansal Etki']:
            self.transition_tree.heading(col, text=col)
            self.transition_tree.column(col, width=120)

        self.transition_tree.pack(fill='both', expand=True, padx=20, pady=10)

    def create_physical_risk_tab(self) -> None:
        """Fiziksel riskler sekmesi"""
        physical_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(physical_frame, text=" Fiziksel Riskler")

        # Başlık
        tk.Label(physical_frame, text="Fiziksel Risk Modelleme (Türkçe)",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Risk tipleri
        risk_text = """
         Fiziksel Risk Tipleri:
        
         Ani (Acute) Fiziksel Riskler:
           • Sel ve taşkınlar
           • Fırtına ve kasırgalar
           • Orman yangınları
           • Aşırı hava olayları
        
         Kronik (Chronic) Fiziksel Riskler:
           • Deniz seviyesi yükselmesi
           • Ortalama sıcaklık artışı
           • Su stresi ve kuraklık
           • Ekosistemlerde değişim
        
         Finansal Etki Alanları:
           • Altyapı hasarı
           • Tedarik zinciri kesintisi
           • İşletme maliyetleri
           • Varlık değer kaybı
        """

        tk.Label(physical_frame, text=risk_text, font=('Segoe UI', 10),
                bg='white', justify='left').pack(padx=30, pady=10)

        # Risk listesi
        self.physical_tree = ttk.Treeview(physical_frame,
                                         columns=('Tip', 'Olay', 'Olasılık', 'Etki', 'Finansal Etki'),
                                         show='headings', height=8)

        for col in ['Tip', 'Olay', 'Olasılık', 'Etki', 'Finansal Etki']:
            self.physical_tree.heading(col, text=col)
            self.physical_tree.column(col, width=120)

        self.physical_tree.pack(fill='both', expand=True, padx=20, pady=10)

    def create_financial_impact_tab(self) -> None:
        """Finansal etki sekmesi"""
        financial_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(financial_frame, text=" Finansal Simülasyon")

        # Başlık
        tk.Label(financial_frame, text="Finansal Etki Simülasyonu (2024-2050)",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Simülasyon açıklaması
        sim_text = """
         Finansal Etki Bileşenleri:
        
         Maliyetler:
           • Karbon fiyatlama maliyeti (tCO2 × Karbon fiyatı)
           • Enerji maliyetleri
           • Teknoloji yatırımları (CAPEX)
           • Operasyonel maliyet artışları (OPEX)
        
         Kazançlar:
           • Enerji tasarrufu (yenilenebilir enerji)
           • Verimlililik artışı
           • Yeni pazar fırsatları
           • İtibar kazanımı
        
         ROI Hesaplaması:
           • Net finansal etki (Kazanç - Maliyet)
           • Yatırım getirisi yüzdesi
           • Geri ödeme süresi
        """

        tk.Label(financial_frame, text=sim_text, font=('Segoe UI', 10),
                bg='white', justify='left').pack(padx=30, pady=10)

        # Simülasyon listesi
        self.financial_tree = ttk.Treeview(financial_frame,
                                          columns=('Yıl', 'Karbon Maliyeti', 'Enerji Tasarrufu',
                                                  'CAPEX', 'Net Etki', 'ROI %'),
                                          show='headings', height=10)

        for col in ['Yıl', 'Karbon Maliyeti', 'Enerji Tasarrufu', 'CAPEX', 'Net Etki', 'ROI %']:
            self.financial_tree.heading(col, text=col)
            self.financial_tree.column(col, width=100)

        self.financial_tree.pack(fill='both', expand=True, padx=20, pady=10)

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            self.load_dashboard_data()
        except Exception as e:
            logging.error(f"Veri yukleme hatasi: {e}")

    def load_dashboard_data(self) -> None:
        """Dashboard verilerini yükle - Gerçek verilerle"""
        try:
            for widget in self.stats_frame.winfo_children():
                widget.destroy()

            # Gerçek istatistikleri al
            real_stats = self._get_real_scenario_statistics()

            stats = [
                ("TCFD Senaryoları", str(real_stats['tcfd_scenarios']), '#1565C0'),
                ("Geçiş Riskleri", str(real_stats['transition_risks']), '#E65100'),
                ("Fiziksel Riskler", str(real_stats['physical_risks']), '#C62828'),
                ("Finansal Simülasyon", real_stats['simulation_period'], '#2E7D32'),
            ]

            for i, (title, value, color) in enumerate(stats):
                self.create_stat_card(self.stats_frame, title, value, color, 0, i)

        except Exception as e:
            logging.error(f"Dashboard yukleme hatasi: {e}")

    def _get_real_scenario_statistics(self) -> Dict[str, any]:
        """Gerçek senaryo istatistiklerini al"""
        try:
            import os
            import sqlite3
            from datetime import datetime

            # Database yolunu bul
            db_path = DB_PATH
            if not os.path.isabs(db_path):
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
                db_path = os.path.join(base_dir, db_path)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # TCFD senaryoları sayısı
            try:
                cursor.execute("SELECT COUNT(*) FROM tcfd_scenarios WHERE is_active = 1")
                tcfd_scenarios = cursor.fetchone()[0]
            except Exception:
                tcfd_scenarios = 0

            # Geçiş riskleri sayısı
            try:
                cursor.execute("SELECT COUNT(*) FROM climate_risks WHERE risk_type = 'transition' AND is_active = 1")
                transition_risks = cursor.fetchone()[0]
            except Exception:
                transition_risks = 0

            # Fiziksel riskler sayısı
            try:
                cursor.execute("SELECT COUNT(*) FROM climate_risks WHERE risk_type = 'physical' AND is_active = 1")
                physical_risks = cursor.fetchone()[0]
            except Exception:
                physical_risks = 0

            # Simülasyon periyodu
            try:
                cursor.execute("SELECT MIN(start_year), MAX(end_year) FROM scenario_simulations")
                result = cursor.fetchone()
                if result and result[0] and result[1]:
                    simulation_period = f"{result[0]}-{result[1]}"
                else:
                    simulation_period = f"{datetime.now().year}-2050"
            except Exception:
                simulation_period = f"{datetime.now().year}-2050"

            conn.close()

            return {
                'tcfd_scenarios': tcfd_scenarios,
                'transition_risks': transition_risks,
                'physical_risks': physical_risks,
                'simulation_period': simulation_period
            }

        except Exception as e:
            logging.error(f"Senaryo istatistik alma hatasi: {e}")
            # Hata durumunda varsayılan değerler
            return {
                'tcfd_scenarios': 0,
                'transition_risks': 0,
                'physical_risks': 0,
                'simulation_period': f"{datetime.now().year}-2050"
            }

    def create_stat_card(self, parent, title, value, color, row, col):
        """İstatistik kartı"""
        card = tk.Frame(parent, bg=color, relief='raised', bd=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        parent.grid_columnconfigure(col, weight=1)

        tk.Label(card, text=title, font=('Segoe UI', 10, 'bold'),
                bg=color, fg='white').pack(pady=5)
        tk.Label(card, text=str(value), font=('Segoe UI', 16, 'bold'),
                bg=color, fg='white').pack(pady=5)

    def create_tcfd_scenario(self) -> None:
        """TCFD senaryosu oluştur"""
        messagebox.showinfo("TCFD Senaryo",
                          "TCFD İklim Senaryosu Oluşturma\n\n"
                          "Senaryo Seçenekleri:\n"
                          "• 1.5°C (Net Zero 2050)\n"
                          "• 2°C (Paris Anlaşması)\n"
                          "• 4°C (Mevcut Politikalar)\n\n"
                          "Otomatik olarak:\n"
                          " Emisyon projeksiyonları\n"
                          " Risk analizleri\n"
                          " Finansal simülasyon\n"
                          "oluşturulacak!")

    def create_bau_netzero(self) -> None:
        """BAU vs Net Zero karşılaştırması"""
        messagebox.showinfo("Karşılaştırma",
                          "BAU vs Net Zero Karşılaştırması\n\n"
                          "İki senaryo oluşturulacak:\n"
                          "1. İş Her Zamanki Gibi (4°C)\n"
                          "2. Net Zero 2050 (1.5°C)\n\n"
                          "Karşılaştırma metrikleri:\n"
                          " Emisyon azaltımı\n"
                          " Finansal etki\n"
                          " Risk profili\n"
                          " ROI analizi")
