import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detaylı İnsan Kaynakları Metrikleri GUI
GRI 401, 402, 404, 405, 406
"""

import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib

from utils.language_manager import LanguageManager
from utils.ui_theme import apply_theme

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .hr_manager import HRManager
from .hr_metrics import HRMetrics


class HRMetricsGUI:
    """İnsan Kaynakları Metrikleri detaylı arayüz"""

    def __init__(self, parent, db_path: str, company_id: int, year: int = 2024) -> None:
        self.parent = parent
        self.db_path = db_path
        self.company_id = company_id
        self.year = year
        self.lm = LanguageManager()
        self.hr_metrics = HRMetrics(db_path)
        self.hr_manager = HRManager(db_path)

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        apply_theme(self.parent)
        # Başlık
        header = tk.Frame(self.parent, bg='#2c3e50', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(header, text=self.lm.tr('hr_metrics_detail_title', " Detaylı İnsan Kaynakları Metrikleri"),
                font=('Segoe UI', 16, 'bold'), fg='white', bg='#2c3e50').pack(side='left', padx=20, pady=20)

        tk.Label(header, text=self.lm.tr('hr_metrics_subtitle', "Demografik Analiz, Çeşitlilik, Ücret Eşitliği ve İstihdam Metrikleri"),
                font=('Segoe UI', 10), fg='#ecf0f1', bg='#2c3e50').pack(side='left')

        # Kontrol paneli
        control_frame = tk.Frame(self.parent, bg='white')
        control_frame.pack(fill='x', padx=20, pady=15)

        tk.Label(control_frame, text=self.lm.tr('year', "Yıl:"), font=('Segoe UI', 10), bg='white').pack(side='left', padx=5)
        self.year_var = tk.StringVar(value=str(self.year))
        year_combo = ttk.Combobox(control_frame, textvariable=self.year_var,
                                  values=[str(y) for y in range(2020, 2026)],
                                  width=10, state='readonly')
        year_combo.pack(side='left', padx=5)
        year_combo.bind('<<ComboboxSelected>>', lambda e: self.load_data())

        ttk.Button(control_frame, text=self.lm.tr('btn_refresh', " Yenile"), style='Primary.TButton', command=self.load_data).pack(side='left', padx=10)
        ttk.Button(control_frame, text=self.lm.tr('generate_report', " Rapor Oluştur"), style='Primary.TButton', command=self.generate_report).pack(side='left', padx=5)
        ttk.Button(control_frame, text=self.lm.tr('add_data', " Veri Ekle"), style='Primary.TButton', command=self.add_data_dialog).pack(side='left', padx=5)

        toolbar = ttk.Frame(self.parent)
        toolbar.pack(fill='x', padx=20, pady=(0, 10))
        ttk.Button(toolbar, text=self.lm.tr('btn_report_center', " Rapor Merkezi"), style='Primary.TButton', command=self.open_report_center_hr).pack(side='left', padx=6)

        # Notebook
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Sekmeler
        self.overview_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.overview_frame, text=self.lm.tr('tab_overview', " Genel Bakış"))

        self.demographics_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.demographics_frame, text=self.lm.tr('tab_demographic', " Demografik Analiz"))

        self.turnover_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.turnover_frame, text=self.lm.tr('tab_turnover', " İşe Alım & Ayrılma"))

        self.compensation_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.compensation_frame, text=self.lm.tr('tab_compensation', " Ücret Eşitliği"))

        self.diversity_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.diversity_frame, text=self.lm.tr('tab_diversity', " Çeşitlilik & Kapsayıcılık"))

        self.build_overview_tab()
        self.build_demographics_tab()
        self.build_turnover_tab()
        self.build_compensation_tab()
        self.build_diversity_tab()

    def build_overview_tab(self) -> None:
        """Genel bakış sekmesi"""
        # KPI Kartları
        cards_frame = tk.Frame(self.overview_frame, bg='white')
        cards_frame.pack(fill='x', padx=20, pady=20)

        self.kpi_labels = {}
        kpis = [
            ('total_employees', self.lm.tr('total_employees', 'Toplam Çalışan'), '#3498db'),
            ('new_hires', self.lm.tr('new_hires', 'Yeni İşe Alım'), '#27ae60'),
            ('turnover_rate', self.lm.tr('turnover_rate', 'Devir Hızı (%)'), '#e67e22'),
            ('gender_ratio', self.lm.tr('gender_ratio', 'Kadın/Erkek Oranı'), '#9b59b6'),
            ('avg_age', self.lm.tr('avg_age', 'Ortalama Yaş'), '#1abc9c')
        ]

        for key, label, color in kpis:
            card = tk.Frame(cards_frame, bg=color, relief='raised', bd=2)
            card.pack(side='left', fill='both', expand=True, padx=5)

            tk.Label(card, text=label, font=('Segoe UI', 9, 'bold'),
                    bg=color, fg='white').pack(pady=(10, 5))

            value_label = tk.Label(card, text="0", font=('Segoe UI', 16, 'bold'),
                                  bg=color, fg='white')
            value_label.pack(pady=(0, 10))
            self.kpi_labels[key] = value_label

        # Grafik alanı
        graph_frame = tk.LabelFrame(self.overview_frame, text=self.lm.tr('employee_trend_analysis', " Çalışan Trend Analizi"),
                                    bg='white', font=('Segoe UI', 11, 'bold'))
        graph_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        self.overview_canvas_frame = tk.Frame(graph_frame, bg='white')
        self.overview_canvas_frame.pack(fill='both', expand=True, padx=10, pady=10)

    def build_demographics_tab(self) -> None:
        """Demografik analiz sekmesi"""
        # Sol panel - Yaş dağılımı
        left_panel = tk.LabelFrame(self.demographics_frame, text=self.lm.tr('age_distribution', " Yaş Dağılımı"),
                                   bg='white', font=('Segoe UI', 11, 'bold'))
        left_panel.pack(side='left', fill='both', expand=True, padx=(20, 10), pady=20)

        self.age_canvas_frame = tk.Frame(left_panel, bg='white')
        self.age_canvas_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Sağ panel - Cinsiyet dağılımı
        right_panel = tk.LabelFrame(self.demographics_frame, text=self.lm.tr('gender_distribution', " Cinsiyet Dağılımı"),
                                    bg='white', font=('Segoe UI', 11, 'bold'))
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 20), pady=20)

        self.gender_canvas_frame = tk.Frame(right_panel, bg='white')
        self.gender_canvas_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Alt panel - Detay tablo
        table_frame = tk.LabelFrame(self.demographics_frame, text=self.lm.tr('detailed_demographic_data', " Detaylı Demografik Veriler"),
                                    bg='white', font=('Segoe UI', 11, 'bold'))
        table_frame.pack(fill='x', side='bottom', padx=20, pady=(0, 20))

        columns = (
            self.lm.tr('age_group', 'Yaş Grubu'),
            self.lm.tr('gender', 'Cinsiyet'),
            self.lm.tr('employment_type', 'İstihdam Tipi'),
            self.lm.tr('department', 'Departman'),
            self.lm.tr('count', 'Sayı'),
            self.lm.tr('ratio_percent', 'Oran %')
        )
        self.demo_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)

        for col in columns:
            self.demo_tree.heading(col, text=col)
            self.demo_tree.column(col, width=100 if col != self.lm.tr('department', 'Departman') else 150)

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.demo_tree.yview)
        self.demo_tree.configure(yscrollcommand=scrollbar.set)

        self.demo_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

    def build_turnover_tab(self) -> None:
        """İşe alım ve ayrılma sekmesi"""
        # Üst panel - Özet kartlar
        summary_frame = tk.Frame(self.turnover_frame, bg='white')
        summary_frame.pack(fill='x', padx=20, pady=20)

        self.turnover_labels = {}
        metrics = [
            ('new_hires_total', self.lm.tr('new_hires', 'Yeni İşe Alımlar'), '#27ae60'),
            ('terminations_total', self.lm.tr('separations', 'Ayrılmalar'), '#e74c3c'),
            ('voluntary', self.lm.tr('voluntary_separation', 'Gönüllü Ayrılma'), '#f39c12'),
            ('involuntary', self.lm.tr('involuntary_separation', 'Zorunlu Ayrılma'), '#95a5a6')
        ]

        for key, label, color in metrics:
            card = tk.Frame(summary_frame, bg=color, relief='groove', bd=2)
            card.pack(side='left', fill='both', expand=True, padx=5)

            tk.Label(card, text=label, font=('Segoe UI', 10, 'bold'),
                    bg=color, fg='white').pack(pady=(10, 5))

            value_label = tk.Label(card, text="0", font=('Segoe UI', 18, 'bold'),
                                  bg=color, fg='white')
            value_label.pack(pady=(0, 10))
            self.turnover_labels[key] = value_label

        # Grafik
        graph_frame = tk.LabelFrame(self.turnover_frame, text=self.lm.tr('turnover_trend', " İşe Alım/Ayrılma Trendi"),
                                    bg='white', font=('Segoe UI', 11, 'bold'))
        graph_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        self.turnover_canvas_frame = tk.Frame(graph_frame, bg='white')
        self.turnover_canvas_frame.pack(fill='both', expand=True, padx=10, pady=10)

    def build_compensation_tab(self) -> None:
        """Ücret eşitliği sekmesi"""
        # Ücret oranı göstergesi
        ratio_frame = tk.LabelFrame(self.compensation_frame, text=self.lm.tr('gender_pay_ratio', "️ Cinsiyet Bazlı Ücret Oranı"),
                                    bg='white', font=('Segoe UI', 12, 'bold'))
        ratio_frame.pack(fill='x', padx=20, pady=20)

        self.wage_ratio_label = tk.Label(ratio_frame, text=f"{self.lm.tr('female_male', 'Kadın/Erkek')}: 1:1",
                                         font=('Segoe UI', 20, 'bold'), bg='white', fg='#27ae60')
        self.wage_ratio_label.pack(pady=30)

        # Detay tablo
        table_frame = tk.LabelFrame(self.compensation_frame, text=self.lm.tr('position_wage_analysis', " Pozisyon Bazlı Ücret Analizi"),
                                    bg='white', font=('Segoe UI', 11, 'bold'))
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        columns = (
            self.lm.tr('position', 'Pozisyon'),
            self.lm.tr('gender', 'Cinsiyet'),
            self.lm.tr('avg_salary', 'Ort. Maaş'),
            self.lm.tr('min_salary', 'Min. Maaş'),
            self.lm.tr('max_salary', 'Max. Maaş'),
            self.lm.tr('employee_count', 'Çalışan Sayısı')
        )
        self.comp_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.comp_tree.heading(col, text=col)
            self.comp_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.comp_tree.yview)
        self.comp_tree.configure(yscrollcommand=scrollbar.set)

        self.comp_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

    def build_diversity_tab(self) -> None:
        """Çeşitlilik ve kapsayıcılık sekmesi"""
        # Çeşitlilik skorları
        scores_frame = tk.Frame(self.diversity_frame, bg='white')
        scores_frame.pack(fill='x', padx=20, pady=20)

        self.diversity_scores = {}
        scores = [
            ('gender_diversity', self.lm.tr('gender_diversity', 'Cinsiyet Çeşitliliği'), '#9b59b6'),
            ('age_diversity', self.lm.tr('age_diversity', 'Yaş Çeşitliliği'), '#3498db'),
            ('management_diversity', self.lm.tr('management_diversity', 'Yönetim Çeşitliliği'), '#e67e22')
        ]

        for key, label, color in scores:
            score_card = tk.Frame(scores_frame, bg=color, relief='raised', bd=3)
            score_card.pack(side='left', fill='both', expand=True, padx=5)

            tk.Label(score_card, text=label, font=('Segoe UI', 10, 'bold'),
                    bg=color, fg='white').pack(pady=(15, 5))

            score_label = tk.Label(score_card, text=self.lm.tr('lbl_zero_percent', '0%'), font=('Segoe UI', 20, 'bold'),
                                  bg=color, fg='white')
            score_label.pack(pady=(0, 15))
            self.diversity_scores[key] = score_label

        # Kapsayıcılık programları
        programs_frame = tk.LabelFrame(self.diversity_frame, text=self.lm.tr('inclusion_programs', " Kapsayıcılık Programları ve İnisiyatifler"),
                                       bg='white', font=('Segoe UI', 11, 'bold'))
        programs_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        columns = (
            self.lm.tr('program_name', 'Program Adı'),
            self.lm.tr('category', 'Kategori'),
            self.lm.tr('participant_count', 'Katılımcı Sayısı'),
            self.lm.tr('impact_score', 'Etki Skoru'),
            self.lm.tr('status', 'Durum')
        )
        self.diversity_tree = ttk.Treeview(programs_frame, columns=columns, show='headings', height=12)

        for col in columns:
            self.diversity_tree.heading(col, text=col)
            self.diversity_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(programs_frame, orient='vertical', command=self.diversity_tree.yview)
        self.diversity_tree.configure(yscrollcommand=scrollbar.set)

        self.diversity_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

    def load_data(self) -> None:
        """Tüm verileri yükle"""
        try:
            year = int(self.year_var.get())
            self.year = year

            # Genel bakış verilerini yükle
            self.load_overview_data()

            # Demografik verileri yükle
            self.load_demographics_data()

            # İşe alım/ayrılma verilerini yükle
            self.load_turnover_data()

            # Ücret verilerini yükle
            self.load_compensation_data()

            # Çeşitlilik verilerini yükle
            self.load_diversity_data()

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('data_load_error', 'Veri yükleme hatası')}: {e}")

    def load_overview_data(self) -> None:
        """Genel bakış verilerini yükle"""
        try:
            # HRManager'dan özet verileri al
            summary = self.hr_manager.get_hr_summary(self.company_id, self.year)

            # KPI değerlerini al
            total_employees = int(summary.get('average_employees', 0))
            new_hires = int(summary.get('new_hires', 0))
            turnover_rate = summary.get('turnover_rate', 0.0)
            
            # Cinsiyet oranı
            gender_dist = summary.get('gender_distribution', {})
            male_count = gender_dist.get('Erkek', {}).get('count', 0) if gender_dist else 0
            female_count = gender_dist.get('Kadın', {}).get('count', 0) if gender_dist else 0
            
            if male_count > 0 and female_count > 0:
                gender_ratio = f"{female_count}:{male_count}"
            else:
                gender_ratio = self.lm.tr('no_data', "Veri Yok")
                
            # Ortalama yaş (yaklaşık hesap)
            # HRManager get_hr_summary yaş dağılımını dönüyor, ortalama yaşı tam vermiyor olabilir.
            # Şimdilik varsayılan veya hesaplanmış bir değer gösterelim.
            # Age distribution: {'<30': {'count': 10, ...}, ...}
            age_dist = summary.get('age_distribution', {})
            avg_age = 0
            total_count_age = 0
            if age_dist:
                for age_group, data in age_dist.items():
                    count = data.get('count', 0)
                    if count > 0:
                        # Grupların orta noktalarını baz alalım
                        if '<30' in age_group: age_val = 25
                        elif '30-50' in age_group: age_val = 40
                        elif '50+' in age_group: age_val = 55
                        else: age_val = 35
                        
                        avg_age += age_val * count
                        total_count_age += count
                
                if total_count_age > 0:
                    avg_age = avg_age / total_count_age
            
            # KPI kartlarını güncelle
            self.kpi_labels['total_employees'].config(text=str(total_employees))
            self.kpi_labels['new_hires'].config(text=str(new_hires))
            self.kpi_labels['turnover_rate'].config(text=f"{turnover_rate:.1f}%")
            self.kpi_labels['gender_ratio'].config(text=gender_ratio)
            self.kpi_labels['avg_age'].config(text=f"{avg_age:.0f}")

        except Exception as e:
            logging.error(f"{self.lm.tr('error_loading_overview', 'Genel bakış veri yükleme hatası')}: {e}")
            # Varsayılan değerler
            self.kpi_labels['total_employees'].config(text="0")
            self.kpi_labels['new_hires'].config(text="0")
            self.kpi_labels['turnover_rate'].config(text=self.lm.tr('lbl_zero_percent_decimal', '0.0%'))
            self.kpi_labels['gender_ratio'].config(text=self.lm.tr('no_data', "Veri Yok"))
            self.kpi_labels['avg_age'].config(text="0")

        # Grafik çiz
        self.draw_employee_trend()

    def load_demographics_data(self) -> None:
        """Demografik verileri yükle"""
        demographics = self.hr_manager.get_demographics(self.company_id, self.year)

        # Tablo doldur
        for item in self.demo_tree.get_children():
            self.demo_tree.delete(item)

        total = sum(d['count'] for d in demographics)
        for demo in demographics:
            percentage = (demo['count'] / total * 100) if total > 0 else 0
            self.demo_tree.insert('', 'end', values=(
                demo['age_group'],
                demo['gender'],
                demo.get('employment_type', '-'),
                demo.get('department', self.lm.tr('no_data', "Veri Yok")),
                demo['count'],
                f"{percentage:.1f}%"
            ))

        # Grafikler
        self.draw_age_distribution(demographics)
        self.draw_gender_distribution(demographics)

    def load_turnover_data(self) -> None:
        """İşe alım/ayrılma verilerini yükle"""
        turnover = self.hr_manager.get_turnover(self.company_id, self.year)

        new_hires = sum(t['new_hires'] for t in turnover)
        terminations = sum(t['terminations'] for t in turnover)
        voluntary = sum(t.get('voluntary_exits', 0) for t in turnover)
        involuntary = sum(t.get('involuntary_exits', 0) for t in turnover)

        self.turnover_labels['new_hires_total'].config(text=str(new_hires))
        self.turnover_labels['terminations_total'].config(text=str(terminations))
        self.turnover_labels['voluntary'].config(text=str(voluntary))
        self.turnover_labels['involuntary'].config(text=str(involuntary))

        # Grafik
        self.draw_turnover_trend(turnover)

    def load_compensation_data(self) -> None:
        """Ücret verilerini yükle"""
        compensation = self.hr_manager.get_compensation(self.company_id, self.year)

        # Cinsiyet bazlı ücret oranı hesapla
        ratio = self.hr_manager.calculate_gender_pay_ratio(self.company_id, self.year)
        self.wage_ratio_label.config(text=f"{self.lm.tr('female_male', 'Kadın/Erkek')}: {ratio}")

        # Renk kodlama
        if '1:1' in ratio or '0.9' in ratio:
            color = '#27ae60'
        elif '0.8' in ratio:
            color = '#f39c12'
        else:
            color = '#e74c3c'
        self.wage_ratio_label.config(fg=color)

        # Tablo doldur
        for item in self.comp_tree.get_children():
            self.comp_tree.delete(item)

        for comp in compensation:
            self.comp_tree.insert('', 'end', values=(
                comp['position_level'],
                comp['gender'],
                f"{comp.get('avg_salary', 0):,.0f} {self.lm.tr('currency_symbol', 'TL')}",
                f"{comp.get('min_salary', 0):,.0f} {self.lm.tr('currency_symbol', 'TL')}",
                f"{comp.get('max_salary', 0):,.0f} {self.lm.tr('currency_symbol', 'TL')}",
                comp.get('employee_count', 0)
            ))

    def load_diversity_data(self) -> None:
        """Çeşitlilik verilerini yükle"""
        diversity = self.hr_manager.get_diversity_details(self.company_id, self.year)

        # Skorları güncelle
        for metric in diversity:
            if metric['category'] == 'gender_diversity':
                self.diversity_scores['gender_diversity'].config(text=f"{metric['value']:.0f}%")

            elif metric['category'] == 'age_diversity':
                self.diversity_scores['age_diversity'].config(text=f"{metric['value']:.0f}%")
            elif metric['category'] == 'management_diversity':
                self.diversity_scores['management_diversity'].config(text=f"{metric['value']:.0f}%")

        # Tabloyu temizle
        for item in self.diversity_tree.get_children():
            self.diversity_tree.delete(item)

        # Gerçek verileri yükle
        programs = self.hr_manager.get_diversity_programs(self.company_id, self.year)
        
        for prog in programs:
            self.diversity_tree.insert('', 'end', values=(
                prog.get('name', '-'),
                prog.get('category', '-'),
                prog.get('participants', 0),
                f"{prog.get('success_rate', 0):.0f}%",
                self.lm.tr(prog.get('status', 'active'), prog.get('status', 'active'))
            ))

    def draw_employee_trend(self) -> None:
        """Çalışan trend grafiği"""
        try:
            for widget in self.overview_canvas_frame.winfo_children():
                widget.destroy()

            fig = Figure(figsize=(10, 4), dpi=80)
            ax = fig.add_subplot(111)

            # Gerçek verileri çek
            trend_data = self.hr_manager.get_monthly_employee_trend(self.company_id, self.year)
            months_data = trend_data.get('months', [])
            employees_data = trend_data.get('employees', [])

            # Ay isimleri
            month_names = [self.lm.tr('jan', 'Oca'), self.lm.tr('feb', 'Şub'), self.lm.tr('mar', 'Mar'), 
                          self.lm.tr('apr', 'Nis'), self.lm.tr('may', 'May'), self.lm.tr('jun', 'Haz'), 
                          self.lm.tr('jul', 'Tem'), self.lm.tr('aug', 'Ağu'), self.lm.tr('sep', 'Eyl'), 
                          self.lm.tr('oct', 'Eki'), self.lm.tr('nov', 'Kas'), self.lm.tr('dec', 'Ara')]

            # Eğer veri yoksa boş grafik (sıfır değerleri)
            if not months_data:
                employees = [0] * 12
            else:
                # 12 aylık veri dizisi oluştur
                employees = [0] * 12
                for m, e in zip(months_data, employees_data):
                    if 1 <= m <= 12:
                        employees[m-1] = e

            ax.plot(month_names, employees, marker='o', linewidth=2, color='#3498db')
            ax.set_title(self.lm.tr('employee_count_trend', 'Çalışan Sayısı Trendi'), fontsize=12, weight='bold')
            ax.set_xlabel(self.lm.tr('month', 'Ay'))
            ax.set_ylabel(self.lm.tr('employee_count', 'Çalışan Sayısı'))
            ax.grid(True, alpha=0.3)
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, self.overview_canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def draw_age_distribution(self, demographics) -> None:
        """Yaş dağılımı grafiği"""
        try:
            for widget in self.age_canvas_frame.winfo_children():
                widget.destroy()

            fig = Figure(figsize=(4, 4), dpi=80)
            ax = fig.add_subplot(111)

            age_groups = {}
            for demo in demographics:
                age_group = demo['age_group']
                age_groups[age_group] = age_groups.get(age_group, 0) + demo['count']

            if age_groups:
                ax.pie(age_groups.values(), labels=age_groups.keys(), autopct='%1.1f%%',
                      colors=['#3498db', '#27ae60', '#e67e22', '#9b59b6'])
                ax.set_title(self.lm.tr('age_distribution', 'Yaş Dağılımı'), fontsize=11, weight='bold')

            canvas = FigureCanvasTkAgg(fig, self.age_canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def draw_gender_distribution(self, demographics) -> None:
        """Cinsiyet dağılımı grafiği"""
        try:
            for widget in self.gender_canvas_frame.winfo_children():
                widget.destroy()

            fig = Figure(figsize=(4, 4), dpi=80)
            ax = fig.add_subplot(111)

            genders = {}
            for demo in demographics:
                gender = demo['gender']
                genders[gender] = genders.get(gender, 0) + demo['count']

            if genders:
                ax.pie(genders.values(), labels=genders.keys(), autopct='%1.1f%%',
                      colors=['#3498db', '#e74c3c', '#95a5a6'])
                ax.set_title(self.lm.tr('gender_distribution', 'Cinsiyet Dağılımı'), fontsize=11, weight='bold')

            canvas = FigureCanvasTkAgg(fig, self.gender_canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def draw_turnover_trend(self, turnover_data) -> None:
        """İşe alım/ayrılma trend grafiği"""
        try:
            for widget in self.turnover_canvas_frame.winfo_children():
                widget.destroy()

            fig = Figure(figsize=(10, 4), dpi=80)
            ax = fig.add_subplot(111)

            months = list(range(1, 13))
            new_hires = [t['new_hires'] for t in turnover_data[:12]]
            terminations = [t['terminations'] for t in turnover_data[:12]]

            if not new_hires:
                new_hires = [0] * 12
                terminations = [0] * 12

            ax.plot(months, new_hires, marker='o', label=self.lm.tr('new_hires', 'Yeni İşe Alımlar'), color='#27ae60')
            ax.plot(months, terminations, marker='s', label=self.lm.tr('separations', 'Ayrılmalar'), color='#e74c3c')
            ax.set_title(self.lm.tr('recruitment_separation_trend', 'İşe Alım ve Ayrılma Trendi'), fontsize=12, weight='bold')
            ax.set_xlabel(self.lm.tr('month', 'Ay'))
            ax.set_ylabel(self.lm.tr('count', 'Kişi Sayısı'))
            ax.legend()
            ax.grid(True, alpha=0.3)
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, self.turnover_canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def add_data_dialog(self) -> None:
        """Veri ekleme dialog - İŞLEVSEL"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('data_entry', "Veri Girişi"))
        dialog.geometry("600x500")
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.resizable(False, False)

        # Başlık
        tk.Label(dialog, text=self.lm.tr('hr_metrics_data_entry', " İK Metrikleri Veri Girişi"),
                font=('Segoe UI', 16, 'bold'), fg='#2c3e50').pack(pady=20)

        # Veri türü seçimi
        type_frame = tk.Frame(dialog)
        type_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(type_frame, text=self.lm.tr('data_type', "Veri Türü:"), font=('Segoe UI', 12, 'bold')).pack(anchor='w')

        self.data_type_var = tk.StringVar(value="employee")
        data_types = [
            (self.lm.tr('employee_info', "Çalışan Bilgileri"), "employee"),
            (self.lm.tr('recruitment_data', "İşe Alım Verileri"), "recruitment"),
            (self.lm.tr('separation_data', "Ayrılma Verileri"), "separation"),
            (self.lm.tr('salary_info', "Ücret Bilgileri"), "salary"),
            (self.lm.tr('training_data', "Eğitim Verileri"), "training")
        ]

        for text, value in data_types:
            tk.Radiobutton(type_frame, text=text, variable=self.data_type_var,
                          value=value, font=('Segoe UI', 10)).pack(anchor='w', pady=2)

        # Form alanları
        form_frame = tk.Frame(dialog)
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Çalışan bilgileri formu
        self.employee_frame = tk.Frame(form_frame)
        self.employee_frame.pack(fill='both', expand=True)

        self.create_employee_form(self.employee_frame)

        # Butonlar
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill='x', padx=20, pady=20)

        ttk.Button(button_frame, text=self.lm.tr('btn_save', " Kaydet"), style='Primary.TButton', command=self.save_data).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text=self.lm.tr('btn_cancel', " İptal"), command=dialog.destroy).pack(side='left')

        # Veri türü değiştiğinde formu güncelle
        self.data_type_var.trace('w', lambda *args: self.update_form())

    def create_employee_form(self, parent):
        """Çalışan bilgileri formu oluştur"""
        # Form alanlarını temizle
        for widget in parent.winfo_children():
            widget.destroy()

        # Ad Soyad
        tk.Label(parent, text=self.lm.tr('name_surname', "Ad Soyad:"), font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar()
        tk.Entry(parent, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky='ew', pady=5)

        # Pozisyon
        tk.Label(parent, text=self.lm.tr('position', "Pozisyon:"), font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        self.position_var = tk.StringVar()
        tk.Entry(parent, textvariable=self.position_var, width=30).grid(row=1, column=1, sticky='ew', pady=5)

        # Departman
        tk.Label(parent, text=self.lm.tr('department', "Departman:"), font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=5)
        self.department_var = tk.StringVar()
        dept_combo = ttk.Combobox(parent, textvariable=self.department_var,
                                 values=["İnsan Kaynakları", "Muhasebe", "Satış", "Pazarlama", "Üretim", "IT", "Yönetim"])
        dept_combo.grid(row=2, column=1, sticky='ew', pady=5)

        # Cinsiyet
        tk.Label(parent, text=self.lm.tr('gender', "Cinsiyet:"), font=('Segoe UI', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=5)
        self.gender_var = tk.StringVar(value="Erkek")
        gender_frame = tk.Frame(parent)
        gender_frame.grid(row=3, column=1, sticky='ew', pady=5)
        tk.Radiobutton(gender_frame, text=self.lm.tr('male', "Erkek"), variable=self.gender_var, value="Erkek").pack(side='left')
        tk.Radiobutton(gender_frame, text=self.lm.tr('female', "Kadın"), variable=self.gender_var, value="Kadın").pack(side='left', padx=(20, 0))

        # Yaş
        tk.Label(parent, text=self.lm.tr('age', "Yaş:"), font=('Segoe UI', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=5)
        self.age_var = tk.StringVar()
        tk.Entry(parent, textvariable=self.age_var, width=30).grid(row=4, column=1, sticky='ew', pady=5)

        # Maaş
        tk.Label(parent, text=self.lm.tr('salary_tl', "Maaş (TL):"), font=('Segoe UI', 10, 'bold')).grid(row=5, column=0, sticky='w', pady=5)
        self.salary_var = tk.StringVar()
        tk.Entry(parent, textvariable=self.salary_var, width=30).grid(row=5, column=1, sticky='ew', pady=5)

        # İşe Başlama Tarihi
        tk.Label(parent, text=self.lm.tr('start_date', "İşe Başlama:"), font=('Segoe UI', 10, 'bold')).grid(row=6, column=0, sticky='w', pady=5)
        self.start_date_var = tk.StringVar()
        tk.Entry(parent, textvariable=self.start_date_var, width=30).grid(row=6, column=1, sticky='ew', pady=5)

        # Grid yapılandırması
        parent.grid_columnconfigure(1, weight=1)

    def update_form(self):
        """Formu veri türüne göre güncelle"""
        data_type = self.data_type_var.get()

        if data_type == "employee":
            self.create_employee_form(self.employee_frame)
        # Diğer veri türleri için formlar eklenebilir

    def save_data(self):
        """Veri kaydet"""
        data_type = self.data_type_var.get()

        if data_type == "employee":
            self.save_employee_data()

    def save_employee_data(self):
        """Çalışan verisini kaydet"""
        try:
            # Veri doğrulama
            if not self.name_var.get().strip():
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('error_name_empty', "Ad Soyad boş olamaz!"))
                return

            if not self.age_var.get().strip():
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('error_age_empty', "Yaş boş olamaz!"))
                return

            # Veri hazırla
            employee_data = {
                'name': self.name_var.get().strip(),
                'position': self.position_var.get().strip(),
                'department': self.department_var.get().strip(),
                'gender': self.gender_var.get(),
                'age': int(self.age_var.get()) if self.age_var.get().isdigit() else 0,
                'salary': float(self.salary_var.get()) if self.salary_var.get().replace('.', '').isdigit() else 0,
                'start_date': self.start_date_var.get().strip(),
                'company_id': self.company_id,
                'year': self.year
            }

            # Veritabanına kaydet
            success = self.hr_manager.add_employee(employee_data)

            if success:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('employee_saved', "Çalışan verisi başarıyla kaydedildi!"))
                self.load_data()  # Verileri yenile
                # Formu temizle
                self.name_var.set("")
                self.position_var.set("")
                self.department_var.set("")
                self.gender_var.set("Erkek")
                self.age_var.set("")
                self.salary_var.set("")
                self.start_date_var.set("")
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('error_save_failed', "Veri kaydedilemedi!"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_saving_data', 'Veri kaydedilirken hata oluştu')}: {e}")

    def generate_report(self) -> None:
        """İK raporu oluştur"""
        try:
            report = self.hr_metrics.generate_hr_report(self.company_id, self.year)

            # Rapor penceresi
            report_window = tk.Toplevel(self.parent)
            report_window.title(f"{self.lm.tr('hr_metrics_report', 'İK Metrikleri Raporu')} - {self.year}")
            report_window.geometry("800x600")

            from tkinter import scrolledtext
            report_text = scrolledtext.ScrolledText(report_window, font=('Courier', 10), wrap='word')
            report_text.pack(fill='both', expand=True, padx=10, pady=10)
            report_text.insert('1.0', report)
            report_text.config(state='disabled')

            ttk.Button(report_window, text=self.lm.tr('btn_close', " Kapat"), command=report_window.destroy).pack(pady=(0, 10))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('report_generation_error', 'Rapor oluşturma hatası')}: {e}")

    def open_report_center_hr(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('sosyal')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for sosyal: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('report_center_error', 'Rapor Merkezi açılamadı')}:\n{e}")
            logging.error(f"Error opening report center: {e}")
