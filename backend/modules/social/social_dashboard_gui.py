#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sosyal Performans Dashboard - Tam Fonksiyonel
İK, İSG ve Eğitim metriklerini görselleştirme
"""

import logging
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from typing import Dict

import matplotlib

matplotlib.use('Agg')

from utils.language_manager import LanguageManager

from .hr_metrics import HRMetrics
from .ohs_metrics import OHSMetrics
from .training_metrics import TrainingMetrics
from .social_reporting import SocialReporting
from config.icons import Icons


class SocialDashboardGUI:
    """Sosyal Performans Dashboard GUI"""

    def __init__(self, parent, company_id: int):
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()
        self.reporting = SocialReporting()

        # Modüller
        self.hr = HRMetrics()
        self.ohs = OHSMetrics()
        self.training = TrainingMetrics()

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """UI oluştur"""
        # Ana frame (scrollable)
        outer = tk.Frame(self.parent, bg='white')
        outer.pack(fill='both', expand=True)
        canvas = tk.Canvas(outer, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient='vertical', command=canvas.yview)
        main_frame = tk.Frame(canvas, bg='white')
        main_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=main_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Başlık
        tk.Label(main_frame, text=self.lm.tr('social_dashboard_title', "Sosyal Performans Dashboard"),
                font=('Segoe UI', 15, 'bold'), bg='white').pack(pady=12)

        # Notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True, padx=12, pady=8)

        # Sekmeler
        self.create_overview_tab()
        self.create_hr_tab()
        self.create_ohs_tab()
        self.create_training_tab()
        self.create_reports_tab()

    def create_overview_tab(self) -> None:
        """Genel bakış sekmesi"""
        overview_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(overview_frame, text=self.lm.tr('tab_overview', f"{Icons.REPORT} Genel Bakış"))

        # KPI kartları
        self.kpi_frame = tk.Frame(overview_frame, bg='white')
        self.kpi_frame.pack(fill='x', padx=12, pady=10)

        # Detay bilgiler
        details_frame = tk.Frame(overview_frame, bg='white')
        details_frame.pack(fill='both', expand=True, padx=12, pady=8)

        # 3 kolon: İK, İSG, Eğitim
        self.hr_detail_frame = tk.LabelFrame(details_frame, text=self.lm.tr('grp_hr', f"{Icons.USERS} İnsan Kaynakları"),
                                             font=('Segoe UI', 11, 'bold'), bg='white')
        self.hr_detail_frame.pack(side='left', fill='both', expand=True, padx=5)

        self.ohs_detail_frame = tk.LabelFrame(details_frame, text=self.lm.tr('grp_ohs', "🛡️ İş Sağlığı ve Güvenliği"),
                                              font=('Segoe UI', 11, 'bold'), bg='white')
        self.ohs_detail_frame.pack(side='left', fill='both', expand=True, padx=5)

        self.training_detail_frame = tk.LabelFrame(details_frame, text=self.lm.tr('grp_training', "📚 Eğitim ve Gelişim"),
                                                   font=('Segoe UI', 11, 'bold'), bg='white')
        self.training_detail_frame.pack(side='left', fill='both', expand=True, padx=5)

    def create_hr_tab(self) -> None:
        """İK metrikleri sekmesi"""
        hr_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(hr_frame, text=self.lm.tr('tab_hr', f"{Icons.USERS} İnsan Kaynakları"))

        tk.Label(hr_frame, text=self.lm.tr('hr_metrics_title', "İnsan Kaynakları Metrikleri"),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Alt sekmeler
        hr_notebook = ttk.Notebook(hr_frame)
        hr_notebook.pack(fill='both', expand=True, padx=20, pady=10)

        # Demografik
        demo_frame = tk.Frame(hr_notebook, bg='white')
        hr_notebook.add(demo_frame, text=self.lm.tr('tab_demographic', "Demografik"))
        self.hr_demographic_frame = demo_frame

        # Turnover
        turnover_frame = tk.Frame(hr_notebook, bg='white')
        hr_notebook.add(turnover_frame, text=self.lm.tr('tab_turnover', "İşe Alım & Ayrılma"))
        self.hr_turnover_frame = turnover_frame

        # Ücret Eşitliği
        compensation_frame = tk.Frame(hr_notebook, bg='white')
        hr_notebook.add(compensation_frame, text=self.lm.tr('tab_compensation', "Ücret Eşitliği"))
        self.hr_compensation_frame = compensation_frame

        # Çeşitlilik
        diversity_frame = tk.Frame(hr_notebook, bg='white')
        hr_notebook.add(diversity_frame, text=self.lm.tr('tab_diversity', "Çeşitlilik"))
        self.hr_diversity_frame = diversity_frame

    def create_ohs_tab(self) -> None:
        """İSG metrikleri sekmesi"""
        ohs_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(ohs_frame, text=self.lm.tr('tab_ohs', "🛡️ İSG"))

        tk.Label(ohs_frame, text=self.lm.tr('ohs_metrics_title', "İş Sağlığı ve Güvenliği Metrikleri"),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # İstatistikler frame
        self.ohs_stats_frame = tk.Frame(ohs_frame, bg='white')
        self.ohs_stats_frame.pack(fill='both', expand=True, padx=20, pady=10)

    def create_training_tab(self) -> None:
        """Eğitim metrikleri sekmesi"""
        training_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(training_frame, text=self.lm.tr('tab_training', "📚 Eğitim"))

        tk.Label(training_frame, text=self.lm.tr('training_metrics_title', "Eğitim ve Gelişim Metrikleri"),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Eğitim istatistikleri
        self.training_stats_frame = tk.Frame(training_frame, bg='white')
        self.training_stats_frame.pack(fill='both', expand=True, padx=20, pady=10)

    def create_reports_tab(self) -> None:
        """Raporlar sekmesi"""
        reports_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(reports_frame, text=self.lm.tr('tab_reports', f"{Icons.FILE} Raporlar"))

        tk.Label(reports_frame, text=self.lm.tr('social_reports_title', "Sosyal Performans Raporları"),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=20)

        # Rapor butonları
        btn_frame = tk.Frame(reports_frame, bg='white')
        btn_frame.pack(fill='x', padx=50, pady=20)

        buttons = [
            (self.lm.tr('btn_hr_report', f"{Icons.REPORT} İK Metrikleri Raporu"), self.generate_hr_report, '#3b82f6'),
            (self.lm.tr('btn_ohs_report', "🛡️ İSG Raporu"), self.generate_ohs_report, '#ef4444'),
            (self.lm.tr('btn_training_report', "📚 Eğitim Raporu"), self.generate_training_report, '#8b5cf6'),
            (self.lm.tr('btn_comprehensive_report', f"{Icons.CHART_UP} Kapsamlı Sosyal Rapor"), self.generate_comprehensive_report, '#10b981'),
            (self.lm.tr('btn_export_excel', "📑 Excel Dışa Aktarım"), self.export_to_excel, '#f59e0b')
        ]

        for i, (text, command, color) in enumerate(buttons):
            btn = tk.Button(btn_frame, text=text, command=command,
                           bg=color, fg='white', font=('Segoe UI', 11, 'bold'),
                           padx=15, pady=10, width=30)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='ew')

        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

    def load_data(self) -> None:
        """Tüm verileri yükle"""
        self.load_overview_data()
        self.load_hr_data()
        self.load_ohs_data()
        self.load_training_data()

    def load_overview_data(self) -> None:
        """Genel bakış verilerini yükle"""
        try:
            year = datetime.now().year

            # KPI kartlarını temizle
            for widget in self.kpi_frame.winfo_children():
                widget.destroy()

            # İK KPI
            hr_data = self.hr.get_workforce_summary(self.company_id, year)
            self.create_kpi_card(self.kpi_frame, self.lm.tr('kpi_total_employees', f"{Icons.USERS} Toplam Çalışan"),
                                hr_data.get('total_employees', 0), "#3b82f6", 0, 0)

            # İSG KPI
            ohs_data = self.ohs.get_summary(self.company_id, year)
            self.create_kpi_card(self.kpi_frame, self.lm.tr('kpi_total_incidents', "🛡️ Kaza Sayısı"),
                                ohs_data.get('total_incidents', 0), "#ef4444", 0, 1)

            ltifr = ohs_data.get('ltifr', 0.0)
            self.create_kpi_card(self.kpi_frame, self.lm.tr('kpi_ltifr', f"{Icons.CHART_DOWN} LTIFR"),
                                f"{ltifr:.2f}", '#ef4444' if ltifr > 1.0 else '#10b981', 0, 2)

            # Eğitim KPI
            training_data = self.training.get_summary(self.company_id, year)
            self.create_kpi_card(self.kpi_frame, self.lm.tr('kpi_training_hours', "📚 Eğitim Saati/Kişi"),
                                f"{training_data.get('avg_hours_per_employee', 0):.1f}", "#8b5cf6", 0, 3)

            # Detay bilgileri doldur
            self.fill_hr_details(hr_data)
            self.fill_ohs_details(ohs_data)
            self.fill_training_details(training_data)

        except Exception as e:
            logging.error(f"{self.lm.tr('error_loading_overview', 'Genel bakış yüklenirken hata')}: {e}")

    def create_kpi_card(self, parent, title, value, color, row, col):
        """KPI kartı oluştur"""
        card = tk.Frame(parent, bg=color, relief='raised', bd=2, width=150, height=100)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        card.pack_propagate(False)
        parent.grid_columnconfigure(col, weight=1)

        tk.Label(card, text=title, font=('Segoe UI', 10, 'bold'),
                bg=color, fg='white').pack(pady=(10, 5))
        tk.Label(card, text=str(value), font=('Segoe UI', 18, 'bold'),
                bg=color, fg='white').pack(pady=5)

    def fill_hr_details(self, data: Dict):
        """İK detaylarını doldur"""
        for widget in self.hr_detail_frame.winfo_children():
            widget.destroy()

        details = [
            (self.lm.tr('total_employees', "Toplam Çalışan"), f"{data.get('total_employees', 0)}"),
            (self.lm.tr('female_employees', "Kadın Çalışan"), f"{data.get('female_count', 0)} (%{data.get('female_percentage', 0):.1f})"),
            (self.lm.tr('male_employees', "Erkek Çalışan"), f"{data.get('male_count', 0)} (%{data.get('male_percentage', 0):.1f})"),
            (self.lm.tr('turnover_rate', "Turnover Oranı"), f"%{data.get('turnover_rate', 0):.1f}"),
            (self.lm.tr('new_hires', "Yeni İşe Alım"), f"{data.get('new_hires', 0)}"),
            (self.lm.tr('terminations', "Ayrılma"), f"{data.get('terminations', 0)}")
        ]

        for label, value in details:
            row = tk.Frame(self.hr_detail_frame, bg='white')
            row.pack(fill='x', pady=2, padx=10)

            tk.Label(row, text=f"{label}:", font=('Segoe UI', 9),
                    bg='white', width=15, anchor='w').pack(side='left')
            tk.Label(row, text=value, font=('Segoe UI', 9, 'bold'),
                    bg='white', fg='#3b82f6').pack(side='left')

    def fill_ohs_details(self, data: Dict):
        """İSG detaylarını doldur"""
        for widget in self.ohs_detail_frame.winfo_children():
            widget.destroy()

        details = [
            (self.lm.tr('total_incidents', "Toplam Kaza"), f"{data.get('total_incidents', 0)}"),
            (self.lm.tr('lost_time_incidents', "Kayıp Günlü Kaza"), f"{data.get('lost_time_incidents', 0)}"),
            (self.lm.tr('kpi_ltifr', "LTIFR"), f"{data.get('ltifr', 0):.2f}"),
            (self.lm.tr('trir', "TRIR"), f"{data.get('trir', 0):.2f}"),
            (self.lm.tr('total_lost_days', "Toplam Kayıp Gün"), f"{data.get('total_lost_days', 0)}"),
            (self.lm.tr('ohs_training_hours', "İSG Eğitim Saati"), f"{data.get('training_hours', 0):.1f}")
        ]

        for label, value in details:
            row = tk.Frame(self.ohs_detail_frame, bg='white')
            row.pack(fill='x', pady=2, padx=10)

            tk.Label(row, text=f"{label}:", font=('Segoe UI', 9),
                    bg='white', width=15, anchor='w').pack(side='left')
            tk.Label(row, text=value, font=('Segoe UI', 9, 'bold'),
                    bg='white', fg='#ef4444').pack(side='left')

    def fill_training_details(self, data: Dict):
        """Eğitim detaylarını doldur"""
        for widget in self.training_detail_frame.winfo_children():
            widget.destroy()

        details = [
            (self.lm.tr('total_training_programs', "Toplam Eğitim"), f"{data.get('total_programs', 0)} program"),
            (self.lm.tr('total_participants', "Toplam Katılımcı"), f"{data.get('total_participants', 0)}"),
            (self.lm.tr('total_training_hours', "Toplam Eğitim Saati"), f"{data.get('total_hours', 0):.1f}"),
            (self.lm.tr('avg_hours_per_person', "Kişi Başı Saat"), f"{data.get('avg_hours_per_employee', 0):.1f}"),
            (self.lm.tr('completion_rate', "Tamamlanma Oranı"), f"%{data.get('completion_rate', 0):.1f}"),
            (self.lm.tr('online_training_rate', "Online Eğitim"), f"%{data.get('online_percentage', 0):.1f}")
        ]

        for label, value in details:
            row = tk.Frame(self.training_detail_frame, bg='white')
            row.pack(fill='x', pady=2, padx=10)

            tk.Label(row, text=f"{label}:", font=('Segoe UI', 9),
                    bg='white', width=18, anchor='w').pack(side='left')
            tk.Label(row, text=value, font=('Segoe UI', 9, 'bold'),
                    bg='white', fg='#8b5cf6').pack(side='left')

    def load_hr_data(self) -> None:
        """İK verilerini yükle"""
        try:
            year = datetime.now().year

            # Demografik
            demo_data = self.hr.get_demographic_analysis(self.company_id, year)
            self.show_hr_demographic(demo_data)

            # Turnover
            turnover_data = self.hr.get_turnover_analysis(self.company_id, year)
            self.show_hr_turnover(turnover_data)

            # Ücret
            comp_data = self.hr.get_compensation_analysis(self.company_id, year)
            self.show_hr_compensation(comp_data)

            # Çeşitlilik
            div_data = self.hr.get_diversity_metrics(self.company_id, year)
            self.show_hr_diversity(div_data)

        except Exception as e:
            logging.error(f"{self.lm.tr('error_loading_hr_data', 'İK verileri yüklenirken hata')}: {e}")

    def show_hr_demographic(self, data: Dict):
        """Demografik verileri göster"""
        for widget in self.hr_demographic_frame.winfo_children():
            widget.destroy()

        info_text = f"""
{self.lm.tr('demographic_distribution', 'DEMOGRAFIK DAĞILIM')}

{self.lm.tr('total_employees', 'Toplam Çalışan')}: {data.get('total', 0)}

{self.lm.tr('gender_distribution', 'Cinsiyet Dağılımı')}:
• {self.lm.tr('female', 'Kadın')}: {data.get('female_count', 0)} (%{data.get('female_pct', 0):.1f})
• {self.lm.tr('male', 'Erkek')}: {data.get('male_count', 0)} (%{data.get('male_pct', 0):.1f})

{self.lm.tr('age_distribution', 'Yaş Dağılımı')}:
• <30: {data.get('age_under_30', 0)}
• 30-50: {data.get('age_30_50', 0)}
• >50: {data.get('age_over_50', 0)}

{self.lm.tr('employment_type', 'İstihdam Tipi')}:
• {self.lm.tr('full_time', 'Tam Zamanlı')}: {data.get('full_time', 0)}
• {self.lm.tr('part_time', 'Yarı Zamanlı')}: {data.get('part_time', 0)}
        """.strip()

        tk.Label(self.hr_demographic_frame, text=info_text,
                font=('Courier New', 9), bg='white',
                justify='left').pack(anchor='w', padx=20, pady=20)

    def show_hr_turnover(self, data: Dict):
        """Turnover verilerini göster"""
        for widget in self.hr_turnover_frame.winfo_children():
            widget.destroy()

        info_text = f"""
{self.lm.tr('recruitment_and_separation', 'İŞE ALIM VE AYRILMA')}

{self.lm.tr('new_hires', 'Yeni İşe Alım')}: {data.get('new_hires', 0)}
{self.lm.tr('separations', 'Ayrılma')}: {data.get('terminations', 0)}

{self.lm.tr('turnover_rate', 'Turnover Oranı')}: %{data.get('turnover_rate', 0):.1f}

{self.lm.tr('hiring_rate', 'İşe Alım Oranı')}: %{data.get('hire_rate', 0):.1f}
        """.strip()

        tk.Label(self.hr_turnover_frame, text=info_text,
                font=('Courier New', 9), bg='white',
                justify='left').pack(anchor='w', padx=20, pady=20)

    def show_hr_compensation(self, data: Dict):
        """Ücret verilerini göster"""
        for widget in self.hr_compensation_frame.winfo_children():
            widget.destroy()

        info_text = f"""
{self.lm.tr('pay_equity_analysis', 'ÜCRET EŞİTLİĞİ ANALİZİ (GRI 405-2)')}

{self.lm.tr('gender_pay_ratio', 'Kadın/Erkek Ücret Oranı')}: {data.get('gender_pay_ratio', 1.0):.2f}

{self.lm.tr('explanation', 'Açıklama')}:
• 1.00 = {self.lm.tr('perfect_equality', 'Tam eşitlik')}
• <1.00 = {self.lm.tr('female_pay_lower', 'Kadın ücretleri düşük')}
• >1.00 = {self.lm.tr('female_pay_higher', 'Kadın ücretleri yüksek')}

{self.lm.tr('current_status', 'Mevcut Durum')}: {f"{Icons.SUCCESS} {self.lm.tr('equal_pay', 'Eşit ücret')}" if 0.98 <= data.get('gender_pay_ratio', 1.0) <= 1.02 else f"{Icons.WARNING} {self.lm.tr('pay_gap_warning', 'Fark var')}"}
        """.strip()

        tk.Label(self.hr_compensation_frame, text=info_text,
                font=('Courier New', 9), bg='white',
                justify='left').pack(anchor='w', padx=20, pady=20)

    def show_hr_diversity(self, data: Dict):
        """Çeşitlilik verilerini göster"""
        for widget in self.hr_diversity_frame.winfo_children():
            widget.destroy()

        info_text = f"""
{self.lm.tr('diversity_inclusion', 'ÇEŞİTLİLİK VE KAPSAYICILIK')}

{self.lm.tr('gender_diversity', 'Cinsiyet Çeşitliliği')}: %{data.get('gender_diversity', 0):.1f}
{self.lm.tr('age_diversity', 'Yaş Çeşitliliği')}: %{data.get('age_diversity', 0):.1f}

{self.lm.tr('women_in_management', 'Üst Yönetimde Kadın')}: %{data.get('female_in_management', 0):.1f}
{self.lm.tr('women_on_board', 'Yönetim Kurulunda Kadın')}: %{data.get('female_in_board', 0):.1f}

{self.lm.tr('disabled_employees', 'Engelli Çalışan')}: {data.get('disabled_employees', 0)}
        """.strip()

        tk.Label(self.hr_diversity_frame, text=info_text,
                font=('Courier New', 9), bg='white',
                justify='left').pack(anchor='w', padx=20, pady=20)

    def load_ohs_data(self) -> None:
        """İSG verilerini yükle"""
        try:
            year = datetime.now().year
            ohs_data = self.ohs.get_summary(self.company_id, year)

            for widget in self.ohs_stats_frame.winfo_children():
                widget.destroy()

            # Tablo
            info_text = f"""
{self.lm.tr('ohs_statistics', 'İŞ SAĞLIĞI VE GÜVENLİĞİ İSTATİSTİKLERİ')}

{self.lm.tr('total_incidents', 'Toplam Kaza')}: {ohs_data.get('total_incidents', 0)}
{self.lm.tr('lost_time_incidents', 'Kayıp Günlü Kaza')}: {ohs_data.get('lost_time_incidents', 0)}
{self.lm.tr('fatalities', 'Ölümlü Kaza')}: {ohs_data.get('fatalities', 0)}

LTIFR (Lost Time Injury Frequency Rate): {ohs_data.get('ltifr', 0):.2f}
TRIR (Total Recordable Incident Rate): {ohs_data.get('trir', 0):.2f}

{self.lm.tr('total_lost_days', 'Toplam Kayıp Gün')}: {ohs_data.get('total_lost_days', 0)}
{self.lm.tr('hours_worked', 'Çalışılan Saat')}: {ohs_data.get('total_hours_worked', 0):,}

{self.lm.tr('ohs_training', 'İSG Eğitimi')}:
• {self.lm.tr('total_training_hours', 'Toplam Eğitim Saati')}: {ohs_data.get('training_hours', 0):.1f}
• {self.lm.tr('employees_trained', 'Eğitime Katılan')}: {ohs_data.get('trained_employees', 0)}

{self.lm.tr('status', 'Durum')}: {self.lm.tr('status_safe', f"{Icons.SUCCESS} Güvenli") if ohs_data.get('ltifr', 999) < 1.0 else self.lm.tr('status_needs_improvement', f"{Icons.WARNING} İyileştirme gerekli")}
            """.strip()

            tk.Label(self.ohs_stats_frame, text=info_text,
                    font=('Courier New', 10), bg='white',
                    justify='left').pack(anchor='w', padx=30, pady=20)

        except Exception as e:
            logging.error(f"İSG verileri yüklenirken hata: {e}")

    def load_training_data(self) -> None:
        """Eğitim verilerini yükle"""
        try:
            year = datetime.now().year
            training_data = self.training.get_summary(self.company_id, year)

            for widget in self.training_stats_frame.winfo_children():
                widget.destroy()

            info_text = f"""
{self.lm.tr('training_development_stats', 'EĞİTİM VE GELİŞİM İSTATİSTİKLERİ')}

{self.lm.tr('total_programs', 'Toplam Program')}: {training_data.get('total_programs', 0)}
{self.lm.tr('total_participants', 'Toplam Katılımcı')}: {training_data.get('total_participants', 0)}
{self.lm.tr('total_training_hours', 'Toplam Eğitim Saati')}: {training_data.get('total_hours', 0):.1f}

{self.lm.tr('avg_hours_per_person', 'Kişi Başı Ortalama')}: {training_data.get('avg_hours_per_employee', 0):.1f} {self.lm.tr('hours', 'saat')}

{self.lm.tr('training_types', 'Eğitim Türleri')}:
• {self.lm.tr('technical_training', 'Teknik Eğitim')}: %{training_data.get('technical_pct', 0):.1f}
• {self.lm.tr('management_training', 'Yönetim Eğitimi')}: %{training_data.get('management_pct', 0):.1f}
• {self.lm.tr('safety_training', 'İSG Eğitimi')}: %{training_data.get('safety_pct', 0):.1f}
• {self.lm.tr('other_training', 'Diğer')}: %{training_data.get('other_pct', 0):.1f}

{self.lm.tr('completion_rate', 'Tamamlanma Oranı')}: %{training_data.get('completion_rate', 0):.1f}
{self.lm.tr('online_training_rate', 'Online Eğitim Oranı')}: %{training_data.get('online_percentage', 0):.1f}

{self.lm.tr('status', 'Durum')}: {f"{Icons.SUCCESS} " + self.lm.tr('target_met', 'Hedef üstünde') if training_data.get('avg_hours_per_employee', 0) >= 8.0 else f"{Icons.WARNING} " + self.lm.tr('target_missed', 'Hedef altında')}
            """.strip()

            tk.Label(self.training_stats_frame, text=info_text,
                    font=('Courier New', 10), bg='white',
                    justify='left').pack(anchor='w', padx=30, pady=20)

        except Exception as e:
            logging.error(f"{self.lm.tr('error_loading_training_data', 'Eğitim verileri yüklenirken hata')}: {e}")

    def generate_hr_report(self) -> None:
        """İK raporu oluştur"""
        try:
            year = datetime.now().year
            filepath = self.reporting.generate_hr_report(self.company_id, year)
            messagebox.showinfo(self.lm.tr('success', "Başarılı"), 
                              self.lm.tr('hr_report_success', "İK raporu oluşturuldu!") + f"\n\n{filepath}")

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), 
                               self.lm.tr('report_error', "Rapor oluşturulamadı: {error}").format(error=str(e)))

    def generate_ohs_report(self) -> None:
        """İSG raporu oluştur"""
        try:
            year = datetime.now().year
            filepath = self.reporting.generate_ohs_report(self.company_id, year)
            messagebox.showinfo(self.lm.tr('success', "Başarılı"), 
                              self.lm.tr('ohs_report_success', "İSG raporu oluşturuldu!") + f"\n\n{filepath}")

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), 
                               self.lm.tr('report_error', "Rapor oluşturulamadı: {error}").format(error=str(e)))

    def generate_training_report(self) -> None:
        """Eğitim raporu oluştur"""
        try:
            year = datetime.now().year
            filepath = self.reporting.generate_training_report(self.company_id, year)
            messagebox.showinfo(self.lm.tr('success', "Başarılı"), 
                              self.lm.tr('training_report_success', "Eğitim raporu oluşturuldu!") + f"\n\n{filepath}")

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), 
                               self.lm.tr('report_error', "Rapor oluşturulamadı: {error}").format(error=str(e)))

    def generate_comprehensive_report(self) -> None:
        """Kapsamlı sosyal rapor"""
        try:
            year = datetime.now().year
            filepath = self.reporting.generate_comprehensive_report(self.company_id, year)
            messagebox.showinfo(self.lm.tr('success', "Başarılı"), 
                              self.lm.tr('comprehensive_report_success', "Kapsamlı sosyal rapor oluşturuldu!") + f"\n\n{filepath}")

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), 
                               self.lm.tr('report_error', "Rapor oluşturulamadı: {error}").format(error=str(e)))

    def export_to_excel(self) -> None:
        """Excel'e aktar"""
        try:
            year = datetime.now().year
            filepath = self.reporting.generate_excel_export(self.company_id, year)
            messagebox.showinfo(self.lm.tr('success', "Başarılı"), 
                              self.lm.tr('excel_export_success', "Excel dosyası oluşturuldu!") + f"\n\n{filepath}")

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), 
                               self.lm.tr('excel_error', "Excel oluşturulamadı: {error}").format(error=str(e)))

