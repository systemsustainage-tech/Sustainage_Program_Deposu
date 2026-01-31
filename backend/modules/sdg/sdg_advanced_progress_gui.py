import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG Gelişmiş İlerleme Takibi GUI
Hedef bazında ilerleme hesaplama, gösterge detayları takibi, trend analizi, performans metrikleri
"""

import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib
from utils.language_manager import LanguageManager

from .sdg_advanced_analytics import SDGAdvancedAnalytics
from .sdg_progress_tracking import SDGProgressTracking

matplotlib.use('TkAgg')  # Tkinter için optimize backend
import matplotlib.pyplot as plt

# Performans ayarları
plt.style.use('fast')
matplotlib.rcParams['path.simplify'] = True
matplotlib.rcParams['path.simplify_threshold'] = 1.0
matplotlib.rcParams['agg.path.chunksize'] = 10000
matplotlib.rcParams['figure.max_open_warning'] = 0  # Figure warning'i kapat

class SDGAdvancedProgressGUI:
    """SDG Gelişmiş İlerleme Takibi GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.lm = LanguageManager()
        self.parent = parent
        self.company_id = company_id
        self.analytics = SDGAdvancedAnalytics()
        self.progress_tracking = SDGProgressTracking()

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Gelişmiş ilerleme takibi arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Başlık
        header_frame = tk.Frame(main_frame, bg='#8e44ad', height=70)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)

        # Geri butonu
        back_btn = tk.Button(header_frame, text=f" {self.lm.tr('btn_back', 'Geri')}",
                             font=('Segoe UI', 10, 'bold'), bg='#7d3c98', fg='white',
                             relief='flat', bd=0, padx=15, pady=10,
                             command=self.back_to_sdg)
        back_btn.pack(side='left', padx=15, pady=15)

        title_frame = tk.Frame(header_frame, bg='#8e44ad')
        title_frame.pack(side='left', padx=20, pady=15)

        title_label = tk.Label(title_frame, text=self.lm.tr("title_advanced_progress", "SDG Gelişmiş İlerleme Takibi"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#8e44ad')
        title_label.pack(side='left')

        subtitle_label = tk.Label(title_frame, text=self.lm.tr("subtitle_advanced_progress", "Hedef bazında analiz, trend takibi ve performans metrikleri"),
                                 font=('Segoe UI', 11), fg='#e8d5f2', bg='#8e44ad')
        subtitle_label.pack(side='left', padx=(10, 0))

        # Yenile butonu
        refresh_btn = tk.Button(header_frame, text=f" {self.lm.tr('btn_refresh', 'Yenile')}",
                               font=('Segoe UI', 10, 'bold'), bg='#7d3c98', fg='white',
                               relief='flat', bd=0, padx=15, pady=10,
                               command=self.refresh_data)
        refresh_btn.pack(side='right', padx=20, pady=15)

        # Ana içerik - Tabbed interface
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Hedef Performans Analizi sekmesi
        self.performance_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(self.performance_frame, text=f" {self.lm.tr('tab_performance_analysis', 'Hedef Performans Analizi')}")
        self.setup_performance_tab()

        # Gösterge Detay Analizi sekmesi
        self.indicators_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(self.indicators_frame, text=f" {self.lm.tr('tab_indicator_analysis', 'Gösterge Detay Analizi')}")
        self.setup_indicators_tab()

        # Trend Analizi sekmesi
        self.trends_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(self.trends_frame, text=f" {self.lm.tr('tab_trend_analysis', 'Gelişmiş Trend Analizi')}")
        self.setup_trends_tab()

        # Risk Analizi sekmesi
        self.risks_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(self.risks_frame, text=f" {self.lm.tr('tab_risk_analysis', 'Risk Analizi')}")
        self.setup_risks_tab()

        # Performans Metrikleri sekmesi
        self.metrics_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(self.metrics_frame, text=f" {self.lm.tr('tab_performance_metrics', 'Performans Metrikleri')}")
        self.setup_metrics_tab()

    def back_to_sdg(self) -> None:
        """SDG ana ekranına geri dön"""
        try:
            for widget in self.parent.winfo_children():
                widget.destroy()
            from .sdg_gui import SDGGUI
            SDGGUI(self.parent, self.company_id)
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('err_back_process', 'Geri dönme işleminde hata')}: {str(e)}")

    def setup_performance_tab(self) -> None:
        """Hedef performans analizi sekmesini oluştur"""
        # Üst panel - SDG seçimi
        selection_frame = tk.Frame(self.performance_frame, bg='#f8f9fa')
        selection_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(selection_frame, text=self.lm.tr("lbl_select_sdg", "SDG Hedefi Seçin:"),
                font=('Segoe UI', 12, 'bold'), bg='#f8f9fa').pack(side='left')

        self.performance_sdg_var = tk.StringVar()
        self.performance_sdg_combo = ttk.Combobox(selection_frame, textvariable=self.performance_sdg_var,
                                                 state='readonly', width=30)
        self.performance_sdg_combo.pack(side='left', padx=10)
        self.performance_sdg_combo.bind('<<ComboboxSelected>>', self.on_performance_sdg_selected)

        # Analiz butonu
        analyze_btn = tk.Button(selection_frame, text=f" {self.lm.tr('btn_analyze', 'Analiz Et')}",
                               font=('Segoe UI', 10, 'bold'), bg='#8e44ad', fg='white',
                               relief='flat', bd=0, padx=15, pady=5,
                               command=self.analyze_performance)
        analyze_btn.pack(side='left', padx=10)

        # Alt panel - Performans kartları
        cards_frame = tk.Frame(self.performance_frame, bg='#f8f9fa')
        cards_frame.pack(fill='x', padx=10, pady=10)

        # Performans skoru kartı
        self.performance_score_card = self.create_performance_card(cards_frame, self.lm.tr("card_performance_score", "Performans Skoru"), "0.0", "#27ae60")
        self.performance_score_card.pack(side='left', padx=5)

        # İyileşme oranı kartı
        self.improvement_card = self.create_performance_card(cards_frame, self.lm.tr("card_improvement_rate", "İyileşme Oranı"), "0.0%", "#f39c12")
        self.improvement_card.pack(side='left', padx=5)

        # Benchmark karşılaştırması kartı
        self.benchmark_card = self.create_performance_card(cards_frame, self.lm.tr("card_benchmark", "Benchmark"), "0.0", "#3498db")
        self.benchmark_card.pack(side='left', padx=5)

        # Endüstri ortalaması kartı
        self.industry_card = self.create_performance_card(cards_frame, self.lm.tr("card_industry_avg", "Endüstri Ort."), "0.0", "#e74c3c")
        self.industry_card.pack(side='left', padx=5)

        # Alt panel - Detaylı analiz
        details_frame = tk.Frame(self.performance_frame, bg='white', relief='raised', bd=1)
        details_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Detaylı analiz başlığı
        details_title = tk.Label(details_frame, text=self.lm.tr("title_detailed_analysis", "Detaylı Performans Analizi"),
                                font=('Segoe UI', 12, 'bold'), bg='white', fg='#2c3e50')
        details_title.pack(pady=10)

        # Analiz sonuçları metin alanı
        self.performance_text = tk.Text(details_frame, height=15, width=80,
                                       font=('Courier', 9), bg='#f8f9fa')
        self.performance_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Scrollbar
        performance_scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=self.performance_text.yview)
        self.performance_text.configure(yscrollcommand=performance_scrollbar.set)
        performance_scrollbar.pack(side='right', fill='y')

    def setup_indicators_tab(self) -> None:
        """Gösterge detay analizi sekmesini oluştur"""
        # Üst panel - SDG seçimi
        selection_frame = tk.Frame(self.indicators_frame, bg='#f8f9fa')
        selection_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(selection_frame, text=self.lm.tr("lbl_select_sdg", "SDG Hedefi Seçin:"),
                font=('Segoe UI', 12, 'bold'), bg='#f8f9fa').pack(side='left')

        self.indicators_sdg_var = tk.StringVar()
        self.indicators_sdg_combo = ttk.Combobox(selection_frame, textvariable=self.indicators_sdg_var,
                                                state='readonly', width=30)
        self.indicators_sdg_combo.pack(side='left', padx=10)
        self.indicators_sdg_combo.bind('<<ComboboxSelected>>', self.on_indicators_sdg_selected)

        # Analiz butonu
        analyze_btn = tk.Button(selection_frame, text=f" {self.lm.tr('btn_analyze_indicators', 'Gösterge Analizi')}",
                               font=('Segoe UI', 10, 'bold'), bg='#8e44ad', fg='white',
                               relief='flat', bd=0, padx=15, pady=5,
                               command=self.analyze_indicators)
        analyze_btn.pack(side='left', padx=10)

        # Alt panel - Gösterge analiz tablosu
        analysis_frame = tk.Frame(self.indicators_frame, bg='white', relief='raised', bd=1)
        analysis_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Gösterge analiz tablosu
        columns = (
            self.lm.tr("col_indicator", "Gösterge"),
            self.lm.tr("col_completion", "Tamamlanma"),
            self.lm.tr("col_quality", "Kalite"),
            self.lm.tr("col_timeliness", "Zamanında"),
            self.lm.tr("col_consistency", "Tutarlılık"),
            self.lm.tr("col_overall", "Genel"),
            self.lm.tr("col_trend", "Trend"),
            self.lm.tr("col_risk", "Risk"),
            self.lm.tr("col_priority", "Öncelik")
        )
        self.indicators_analysis_tree = ttk.Treeview(analysis_frame, columns=columns, show='headings', height=15)

        # Sütun başlıkları
        for col in columns:
            self.indicators_analysis_tree.heading(col, text=col)

        # Sütun genişlikleri
        self.indicators_analysis_tree.column(columns[0], width=100)
        self.indicators_analysis_tree.column(columns[1], width=80)
        self.indicators_analysis_tree.column(columns[2], width=60)
        self.indicators_analysis_tree.column(columns[3], width=70)
        self.indicators_analysis_tree.column(columns[4], width=70)
        self.indicators_analysis_tree.column(columns[5], width=60)
        self.indicators_analysis_tree.column(columns[6], width=60)
        self.indicators_analysis_tree.column(columns[7], width=60)
        self.indicators_analysis_tree.column(columns[8], width=70)

        # Scrollbar
        indicators_scrollbar = ttk.Scrollbar(analysis_frame, orient="vertical", command=self.indicators_analysis_tree.yview)
        self.indicators_analysis_tree.configure(yscrollcommand=indicators_scrollbar.set)

        self.indicators_analysis_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        indicators_scrollbar.pack(side='right', fill='y', pady=10)

    def setup_trends_tab(self) -> None:
        """Gelişmiş trend analizi sekmesini oluştur"""
        # Üst panel - Trend seçimi
        selection_frame = tk.Frame(self.trends_frame, bg='#f8f9fa')
        selection_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(selection_frame, text=self.lm.tr("lbl_trend_analysis", "Trend Analizi:"),
                font=('Segoe UI', 12, 'bold'), bg='#f8f9fa').pack(side='left')

        self.trend_sdg_var = tk.StringVar()
        self.trend_sdg_combo = ttk.Combobox(selection_frame, textvariable=self.trend_sdg_var,
                                           state='readonly', width=20)
        self.trend_sdg_combo.pack(side='left', padx=10)
        self.trend_sdg_combo.bind('<<ComboboxSelected>>', self.on_trend_sdg_selected)

        # Analiz butonu
        analyze_btn = tk.Button(selection_frame, text=f" {self.lm.tr('btn_analyze_trends', 'Trend Analizi')}",
                               font=('Segoe UI', 10, 'bold'), bg='#8e44ad', fg='white',
                               relief='flat', bd=0, padx=15, pady=5,
                               command=self.analyze_trends)
        analyze_btn.pack(side='left', padx=10)

        # Alt panel - Trend grafikleri
        trend_display_frame = tk.Frame(self.trends_frame, bg='white', relief='raised', bd=1)
        trend_display_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Trend analizi sonuçları
        self.trend_analysis_text = tk.Text(trend_display_frame, height=20, width=80,
                                          font=('Courier', 9), bg='#f8f9fa')
        self.trend_analysis_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Scrollbar
        trend_scrollbar = ttk.Scrollbar(trend_display_frame, orient="vertical", command=self.trend_analysis_text.yview)
        self.trend_analysis_text.configure(yscrollcommand=trend_scrollbar.set)
        trend_scrollbar.pack(side='right', fill='y')

    def setup_risks_tab(self) -> None:
        """Risk analizi sekmesini oluştur"""
        # Üst panel - Risk seçimi
        selection_frame = tk.Frame(self.risks_frame, bg='#f8f9fa')
        selection_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(selection_frame, text=self.lm.tr("lbl_risk_analysis", "Risk Analizi:"),
                font=('Segoe UI', 12, 'bold'), bg='#f8f9fa').pack(side='left')

        self.risk_sdg_var = tk.StringVar()
        self.risk_sdg_combo = ttk.Combobox(selection_frame, textvariable=self.risk_sdg_var,
                                          state='readonly', width=20)
        self.risk_sdg_combo.pack(side='left', padx=10)
        self.risk_sdg_combo.bind('<<ComboboxSelected>>', self.on_risk_sdg_selected)

        # Analiz butonu
        analyze_btn = tk.Button(selection_frame, text=f" {self.lm.tr('btn_analyze_risks', 'Risk Analizi')}",
                               font=('Segoe UI', 10, 'bold'), bg='#e74c3c', fg='white',
                               relief='flat', bd=0, padx=15, pady=5,
                               command=self.analyze_risks)
        analyze_btn.pack(side='left', padx=10)

        # Alt panel - Risk tablosu
        risk_frame = tk.Frame(self.risks_frame, bg='white', relief='raised', bd=1)
        risk_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Risk analiz tablosu
        columns = (
            self.lm.tr("col_indicator", "Gösterge"),
            self.lm.tr("col_risk_type", "Risk Türü"),
            self.lm.tr("col_risk_level", "Risk Seviyesi"),
            self.lm.tr("col_risk_score", "Risk Skoru"),
            self.lm.tr("col_description", "Açıklama"),
            self.lm.tr("col_mitigation", "Azaltma Stratejisi")
        )
        self.risks_tree = ttk.Treeview(risk_frame, columns=columns, show='headings', height=15)

        # Sütun başlıkları
        for col in columns:
            self.risks_tree.heading(col, text=col)

        # Sütun genişlikleri
        self.risks_tree.column(columns[0], width=100)
        self.risks_tree.column(columns[1], width=120)
        self.risks_tree.column(columns[2], width=100)
        self.risks_tree.column(columns[3], width=80)
        self.risks_tree.column(columns[4], width=200)
        self.risks_tree.column(columns[5], width=200)

        # Scrollbar
        risks_scrollbar = ttk.Scrollbar(risk_frame, orient="vertical", command=self.risks_tree.yview)
        self.risks_tree.configure(yscrollcommand=risks_scrollbar.set)

        self.risks_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        risks_scrollbar.pack(side='right', fill='y', pady=10)

    def setup_metrics_tab(self) -> None:
        """Performans metrikleri sekmesini oluştur"""
        # Üst panel - Metrik yönetimi
        management_frame = tk.Frame(self.metrics_frame, bg='#f8f9fa')
        management_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(management_frame, text=self.lm.tr("lbl_performance_metrics", "Performans Metrikleri:"),
                font=('Segoe UI', 12, 'bold'), bg='#f8f9fa').pack(side='left')

        # Metrik ekleme butonu
        add_metric_btn = tk.Button(management_frame, text=self.lm.tr("btn_add_metric", "+ Metrik Ekle"),
                                  font=('Segoe UI', 10), bg='#27ae60', fg='white',
                                  relief='flat', bd=0, padx=15, pady=5,
                                  command=self.add_advanced_metric_dialog)
        add_metric_btn.pack(side='right')

        # Alt panel - Metrik analizi
        metrics_analysis_frame = tk.Frame(self.metrics_frame, bg='white', relief='raised', bd=1)
        metrics_analysis_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Metrik analiz sonuçları
        self.metrics_analysis_text = tk.Text(metrics_analysis_frame, height=20, width=80,
                                            font=('Courier', 9), bg='#f8f9fa')
        self.metrics_analysis_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Scrollbar
        metrics_scrollbar = ttk.Scrollbar(metrics_analysis_frame, orient="vertical", command=self.metrics_analysis_text.yview)
        self.metrics_analysis_text.configure(yscrollcommand=metrics_scrollbar.set)
        metrics_scrollbar.pack(side='right', fill='y')

    def create_performance_card(self, parent, title, value, color) -> tk.Frame:
        """Performans kartı oluştur"""
        card = tk.Frame(parent, bg=color, relief='raised', bd=2, width=150, height=80)
        card.pack_propagate(False)

        title_label = tk.Label(card, text=title, font=('Segoe UI', 9, 'bold'),
                              fg='white', bg=color)
        title_label.pack(pady=(10, 5))

        value_label = tk.Label(card, text=value, font=('Segoe UI', 16, 'bold'),
                              fg='white', bg=color)
        value_label.pack()

        return card

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            # SDG hedeflerini yükle
            self.load_sdg_goals()

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('err_loading_data', 'Veriler yüklenirken hata oluştu')}: {str(e)}")

    def load_sdg_goals(self) -> None:
        """SDG hedeflerini yükle"""
        try:
            # SDG hedeflerini al
            conn = self.analytics.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, code, title_tr FROM sdg_goals ORDER BY code")
            goals = cursor.fetchall()
            conn.close()

            # ComboBox'lara ekle
            goal_options = [f"SDG {goal[1]}: {goal[2]}" for goal in goals]

            self.performance_sdg_combo['values'] = goal_options
            self.indicators_sdg_combo['values'] = goal_options
            self.trend_sdg_combo['values'] = goal_options
            self.risk_sdg_combo['values'] = goal_options

            if goal_options:
                self.performance_sdg_combo.set(goal_options[0])
                self.indicators_sdg_combo.set(goal_options[0])
                self.trend_sdg_combo.set(goal_options[0])
                self.risk_sdg_combo.set(goal_options[0])

        except Exception as e:
            logging.error(f"SDG hedefleri yüklenirken hata: {e}")

    def on_performance_sdg_selected(self, event) -> None:
        """Performans SDG seçildiğinde"""
        self.analyze_performance()

    def on_indicators_sdg_selected(self, event) -> None:
        """Gösterge SDG seçildiğinde"""
        self.analyze_indicators()

    def on_trend_sdg_selected(self, event) -> None:
        """Trend SDG seçildiğinde"""
        self.analyze_trends()

    def on_risk_sdg_selected(self, event) -> None:
        """Risk SDG seçildiğinde"""
        self.analyze_risks()

    def analyze_performance(self) -> None:
        """Hedef performans analizi yap"""
        try:
            selected_text = self.performance_sdg_var.get()
            if not selected_text:
                return

            sdg_no = int(selected_text.split(':')[0].split()[-1])

            # Performans analizi yap
            performance_data = self.analytics.calculate_goal_performance_score(self.company_id, sdg_no)

            # Kartları güncelle
            self.update_performance_card(self.performance_score_card, f"{performance_data['performance_score']}")
            self.update_performance_card(self.improvement_card, f"{performance_data['improvement_rate']}%")
            self.update_performance_card(self.benchmark_card, f"{performance_data['benchmark_score']}")
            self.update_performance_card(self.industry_card, f"{performance_data['industry_average']}")

            # Detaylı analiz metnini oluştur
            analysis_text = f"{self.lm.tr('title_performance_report', 'SDG {no} Hedef Performans Analizi').format(no=sdg_no)}\n"
            analysis_text += "=" * 50 + "\n\n"
            analysis_text += f"{self.lm.tr('card_performance_score', 'Performans Skoru')}: {performance_data['performance_score']}/100\n"
            analysis_text += f"{self.lm.tr('card_improvement_rate', 'İyileşme Oranı')}: {performance_data['improvement_rate']}%\n"
            analysis_text += f"{self.lm.tr('card_benchmark', 'Benchmark Skoru')}: {performance_data['benchmark_score']}/100\n"
            analysis_text += f"{self.lm.tr('card_industry_avg', 'Endüstri Ortalaması')}: {performance_data['industry_average']}/100\n"
            analysis_text += f"{self.lm.tr('lbl_indicators_analyzed', 'Analiz Edilen Gösterge Sayısı: {count}').format(count=performance_data['indicators_analyzed'])}\n"
            analysis_text += f"{self.lm.tr('lbl_calculation_method_report', 'Hesaplama Yöntemi: {method}').format(method=performance_data['calculation_method'])}\n\n"

            # Performans değerlendirmesi
            score = performance_data['performance_score']
            if score >= 90:
                analysis_text += f"{self.lm.tr('msg_eval_excellent', 'Değerlendirme: Mükemmel performans!')} \n"
            elif score >= 80:
                analysis_text += f"{self.lm.tr('msg_eval_very_good', 'Değerlendirme: Çok iyi performans!')} \n"
            elif score >= 70:
                analysis_text += f"{self.lm.tr('msg_eval_good', 'Değerlendirme: İyi performans!')} \n"
            elif score >= 60:
                analysis_text += f"{self.lm.tr('msg_eval_medium', 'Değerlendirme: Orta performans!')} \n"
            else:
                analysis_text += f"{self.lm.tr('msg_eval_improvement', 'Değerlendirme: İyileştirme gerekli!')} \n"

            self.performance_text.delete('1.0', tk.END)
            self.performance_text.insert('1.0', analysis_text)

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("err_performance_analysis", "Performans analizi yapılırken hata: {error}").format(error=str(e)))

    def analyze_indicators(self) -> None:
        """Gösterge detay analizi yap"""
        try:
            selected_text = self.indicators_sdg_var.get()
            if not selected_text:
                return

            sdg_no = int(selected_text.split(':')[0].split()[-1])

            # Gösterge analizi yap
            indicators_data = self.analytics.analyze_indicator_details(self.company_id, sdg_no)

            # Mevcut verileri temizle
            for item in self.indicators_analysis_tree.get_children():
                self.indicators_analysis_tree.delete(item)

            # Göstergeleri ekle
            for indicator in indicators_data:
                self.indicators_analysis_tree.insert('', 'end', values=(
                    indicator['indicator_code'],
                    f"{indicator['completion_score']:.1f}%",
                    f"{indicator['quality_score']:.1f}",
                    f"{indicator['timeliness_score']:.1f}",
                    f"{indicator['consistency_score']:.1f}",
                    f"{indicator['overall_score']:.1f}",
                    indicator['trend_direction'],
                    indicator['risk_level'],
                    indicator['priority_level']
                ))

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("err_indicator_analysis", "Gösterge analizi yapılırken hata: {error}").format(error=str(e)))

    def analyze_trends(self) -> None:
        """Trend analizi yap"""
        try:
            selected_text = self.trend_sdg_var.get()
            if not selected_text:
                return

            sdg_no = int(selected_text.split(':')[0].split()[-1])

            # Trend analizi yap
            trend_data = self.analytics.perform_trend_analysis(self.company_id, sdg_no)

            # Trend analizi metnini oluştur
            trend_text = f"{self.lm.tr('title_trend_analysis_report', 'SDG {no} Trend Analizi').format(no=sdg_no)}\n"
            trend_text += "=" * 50 + "\n\n"
            trend_text += f"{self.lm.tr('lbl_analysis_type', 'Analiz Türü: {type}').format(type=trend_data['trend_type'])}\n"
            trend_text += f"{self.lm.tr('lbl_trend_strength', 'Trend Gücü: {strength}').format(strength=trend_data['trend_strength'])}\n"
            trend_text += f"{self.lm.tr('lbl_trend_direction', 'Trend Yönü: {direction}').format(direction=trend_data['trend_direction'])}\n"
            trend_text += f"{self.lm.tr('lbl_confidence_level', 'Güven Seviyesi: %{confidence}').format(confidence=trend_data['confidence_level'])}\n"
            trend_text += f"{self.lm.tr('lbl_data_points', 'Veri Noktası Sayısı: {count}').format(count=trend_data['data_points'])}\n"
            trend_text += f"{self.lm.tr('lbl_analysis_period', 'Analiz Dönemi: {period}').format(period=trend_data['analysis_period'])}\n"

            if trend_data['forecast_value']:
                trend_text += f"{self.lm.tr('lbl_forecast_value', 'Tahmin Değeri: %{value}').format(value=trend_data['forecast_value'])}\n"

            trend_text += "\n"

            # Trend yorumu
            if trend_data['trend_direction'] == 'improving':
                trend_text += f"{self.lm.tr('msg_trend_positive', 'Yorum: Pozitif trend! Performans artıyor.')} \n"
            elif trend_data['trend_direction'] == 'declining':
                trend_text += f"{self.lm.tr('msg_trend_negative', 'Yorum: Negatif trend! Dikkat edilmeli.')} \n"
            else:
                trend_text += f"{self.lm.tr('msg_trend_stable', 'Yorum: Stabil trend! Mevcut durum korunuyor.')} \n"

            self.trend_analysis_text.delete('1.0', tk.END)
            self.trend_analysis_text.insert('1.0', trend_text)

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("err_trend_analysis", "Trend analizi yapılırken hata: {error}").format(error=str(e)))

    def analyze_risks(self) -> None:
        """Risk analizi yap"""
        try:
            selected_text = self.risk_sdg_var.get()
            if not selected_text:
                return

            sdg_no = int(selected_text.split(':')[0].split()[-1])

            # Risk analizi yap
            risks_data = self.analytics.perform_risk_analysis(self.company_id, sdg_no)

            # Mevcut verileri temizle
            for item in self.risks_tree.get_children():
                self.risks_tree.delete(item)

            # Riskleri ekle
            for risk in risks_data:
                self.risks_tree.insert('', 'end', values=(
                    risk['indicator_code'],
                    risk['risk_type'],
                    risk['risk_level'],
                    f"{risk['risk_score']:.1f}",
                    risk['risk_description'],
                    risk['mitigation_strategy']
                ))

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("err_risk_analysis", "Risk analizi yapılırken hata: {error}").format(error=str(e)))

    def add_advanced_metric_dialog(self) -> None:
        """Gelişmiş metrik ekleme dialogu"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr("title_add_metric", "Gelişmiş Performans Metriği Ekle"))
        dialog.geometry("500x400")
        dialog.transient(self.parent)
        dialog.grab_set()

        # Metrik kategorisi
        tk.Label(dialog, text=self.lm.tr("lbl_metric_category", "Metrik Kategorisi:"), font=('Segoe UI', 10, 'bold')).pack(pady=5)
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(dialog, textvariable=category_var,
                                     values=['Performans', 'Kalite', 'Zamanında', 'Tutarlılık', 'Risk'],
                                     state='readonly', width=40)
        category_combo.pack(pady=5)

        # Metrik adı
        tk.Label(dialog, text=self.lm.tr("lbl_metric_name", "Metrik Adı:"), font=('Segoe UI', 10, 'bold')).pack(pady=5)
        metric_name_entry = tk.Entry(dialog, width=40)
        metric_name_entry.pack(pady=5)

        # Metrik değeri
        tk.Label(dialog, text=self.lm.tr("lbl_value", "Değer:"), font=('Segoe UI', 10, 'bold')).pack(pady=5)
        metric_value_entry = tk.Entry(dialog, width=40)
        metric_value_entry.pack(pady=5)

        # Hedef değer
        tk.Label(dialog, text=self.lm.tr("lbl_target_value", "Hedef Değer:"), font=('Segoe UI', 10, 'bold')).pack(pady=5)
        target_value_entry = tk.Entry(dialog, width=40)
        target_value_entry.pack(pady=5)

        # Birim
        tk.Label(dialog, text=self.lm.tr("lbl_unit", "Birim:"), font=('Segoe UI', 10, 'bold')).pack(pady=5)
        metric_unit_entry = tk.Entry(dialog, width=40)
        metric_unit_entry.pack(pady=5)

        # SDG numarası
        tk.Label(dialog, text=self.lm.tr("lbl_sdg_no", "SDG Numarası:"), font=('Segoe UI', 10, 'bold')).pack(pady=5)
        sdg_no_entry = tk.Entry(dialog, width=40)
        sdg_no_entry.pack(pady=5)

        # Gösterge kodu
        tk.Label(dialog, text=self.lm.tr("lbl_indicator_code", "Gösterge Kodu:"), font=('Segoe UI', 10, 'bold')).pack(pady=5)
        indicator_code_entry = tk.Entry(dialog, width=40)
        indicator_code_entry.pack(pady=5)

        # Hesaplama yöntemi
        tk.Label(dialog, text=self.lm.tr("lbl_calculation_method", "Hesaplama Yöntemi:"), font=('Segoe UI', 10, 'bold')).pack(pady=5)
        method_var = tk.StringVar()
        method_combo = ttk.Combobox(dialog, textvariable=method_var,
                                   values=['weighted_average', 'simple_average', 'custom'],
                                   state='readonly', width=40)
        method_combo.pack(pady=5)

        # Veri kaynağı
        tk.Label(dialog, text=self.lm.tr("lbl_data_source", "Veri Kaynağı:"), font=('Segoe UI', 10, 'bold')).pack(pady=5)
        data_source_entry = tk.Entry(dialog, width=40)
        data_source_entry.pack(pady=5)

        # Butonlar
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)

        def save_advanced_metric() -> None:
            try:
                category = category_var.get().strip()
                metric_name = metric_name_entry.get().strip()
                metric_value = float(metric_value_entry.get())
                target_value = float(target_value_entry.get()) if target_value_entry.get().strip() else None
                metric_unit = metric_unit_entry.get().strip() or None
                sdg_no = int(sdg_no_entry.get()) if sdg_no_entry.get().strip() else None
                indicator_code = indicator_code_entry.get().strip() or None
                method = method_var.get()
                data_source = data_source_entry.get().strip() or None

                if not category or not metric_name:
                    messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("err_category_name_required", "Kategori ve metrik adı gerekli"))
                    return

                # Gerçek vs hedef hesaplama
                actual_vs_target = None
                if target_value is not None:
                    actual_vs_target = (metric_value / target_value) * 100

                # İyileşme oranı (basit hesaplama)
                improvement_rate = 0.0  # Gerçek uygulamada geçmiş verilerle hesaplanır

                # Benchmark değeri (örnek)
                benchmark_value = target_value * 0.8 if target_value else None

                # Endüstri yüzdesi (örnek)
                industry_percentile = 75.0

                success = self.analytics._save_performance_metric_detailed(
                    self.company_id, category, metric_name, metric_value, metric_unit,
                    target_value, actual_vs_target, improvement_rate, benchmark_value,
                    industry_percentile, sdg_no, indicator_code, method, data_source
                )

                if success:
                    messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("msg_metric_added", "Gelişmiş metrik başarıyla eklendi"))
                    dialog.destroy()
                    self.analyze_metrics()
                else:
                    messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("err_metric_add_failed", "Metrik eklenemedi"))

            except ValueError:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("err_invalid_value", "Geçersiz değer"))
            except Exception as e:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("err_adding_metric", "Metrik eklenirken hata: {error}").format(error=str(e)))

        tk.Button(button_frame, text=self.lm.tr("btn_save", "Kaydet"), command=save_advanced_metric,
                 bg='#27ae60', fg='white', relief='flat', padx=20).pack(side='left', padx=5)
        tk.Button(button_frame, text=self.lm.tr("btn_cancel", "İptal"), command=dialog.destroy,
                 bg='#e74c3c', fg='white', relief='flat', padx=20).pack(side='left', padx=5)

    def analyze_metrics(self) -> None:
        """Performans metrikleri analizi yap"""
        try:
            # Metrik analizi yap
            metrics_data = self.analytics.get_performance_metrics_analysis(self.company_id)

            # Metrik analizi metnini oluştur
            metrics_text = f"{self.lm.tr('title_metrics_analysis', 'Performans Metrikleri Analizi')}\n"
            metrics_text += "=" * 50 + "\n\n"
            metrics_text += f"{self.lm.tr('lbl_total_metrics', 'Toplam Metrik Sayısı: {count}').format(count=metrics_data['total_metrics'])}\n"
            metrics_text += f"{self.lm.tr('lbl_avg_performance', 'Ortalama Performans: %{avg}').format(avg=metrics_data['average_performance'])}\n\n"

            # Kategoriler
            metrics_text += f"{self.lm.tr('lbl_categories', 'Kategoriler:')}\n"
            for category, metrics in metrics_data['categories'].items():
                metrics_text += f"{self.lm.tr('lbl_category_count', '- {category}: {count} metrik').format(category=category, count=len(metrics))}\n"

            metrics_text += "\n"

            # En iyi performanslar
            if metrics_data['top_performers']:
                metrics_text += f"{self.lm.tr('lbl_top_performers', 'En İyi Performanslar:')}\n"
                for i, performer in enumerate(metrics_data['top_performers'][:5], 1):
                    metrics_text += f"{i}. {performer['name']} ({performer['category']}): {performer['vs_target']:.1f}%\n"

            metrics_text += "\n"

            # En kötü performanslar
            if metrics_data['underperformers']:
                metrics_text += f"{self.lm.tr('lbl_underperformers', 'İyileştirme Gereken Alanlar:')}\n"
                for i, underperformer in enumerate(metrics_data['underperformers'][:5], 1):
                    metrics_text += f"{i}. {underperformer['name']} ({underperformer['category']}): {underperformer['vs_target']:.1f}%\n"

            self.metrics_analysis_text.delete('1.0', tk.END)
            self.metrics_analysis_text.insert('1.0', metrics_text)

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("err_metrics_analysis", "Metrik analizi yapılırken hata: {error}").format(error=str(e)))

    def update_performance_card(self, card, value) -> None:
        """Performans kartını güncelle"""
        for widget in card.winfo_children():
            if isinstance(widget, tk.Label):
                font_val = str(widget.cget('font'))
                if 'Segoe UI' in font_val and '16' in font_val:
                    widget.config(text=value)
                    break

    def refresh_data(self) -> None:
        """Verileri yenile"""
        try:
            self.load_data()
            messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("msg_data_refreshed", "Veriler yenilendi"))
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("err_data_refresh", "Veriler yenilenirken hata oluştu: {error}").format(error=str(e)))

if __name__ == "__main__":
    # Test
    root = tk.Tk()
    root.title("SDG Gelişmiş İlerleme Takibi")
    app = SDGAdvancedProgressGUI(root, 1)
    root.mainloop()
