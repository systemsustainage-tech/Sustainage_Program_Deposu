import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG İlerleme Takibi GUI
Görsel raporlar ve ilerleme takibi
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Dict, List

from utils.language_manager import LanguageManager

from .sdg_progress_tracking import SDGProgressTracking


class SDGProgressGUI:
    """SDG İlerleme Takibi GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.progress_tracking = SDGProgressTracking()
        self.lm = LanguageManager()

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """İlerleme takibi arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Başlık
        header_frame = tk.Frame(main_frame, bg='#3498db', height=70)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)

        title_frame = tk.Frame(header_frame, bg='#3498db')
        title_frame.pack(side='left', padx=20, pady=15)

        title_label = tk.Label(title_frame, text=self.lm.tr("sdg_progress_title", "SDG İlerleme Takibi"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#3498db')
        title_label.pack(side='left')

        subtitle_label = tk.Label(title_frame, text=self.lm.tr("sdg_progress_subtitle", "Görsel raporlar ve performans analizi"),
                                 font=('Segoe UI', 11), fg='#e8f4fd', bg='#3498db')
        subtitle_label.pack(side='left', padx=(10, 0))

        # Yenile butonu
        refresh_btn = tk.Button(header_frame, text=self.lm.tr("btn_refresh", " Yenile"),
                               font=('Segoe UI', 10, 'bold'), bg='#2980b9', fg='white',
                               relief='flat', bd=0, padx=15, pady=10,
                               command=self.refresh_data)
        refresh_btn.pack(side='right', padx=20, pady=15)

        # Ana içerik - Tabbed interface
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Genel Bakış sekmesi
        self.overview_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(self.overview_frame, text=self.lm.tr("tab_overview", " Genel Bakış"))
        self.setup_overview_tab()

        # Hedef Detayları sekmesi
        self.goals_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(self.goals_frame, text=self.lm.tr("tab_goal_details", " Hedef Detayları"))
        self.setup_goals_tab()

        # Trend Analizi sekmesi
        self.trends_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(self.trends_frame, text=self.lm.tr("tab_trend_analysis", " Trend Analizi"))
        self.setup_trends_tab()

        # Performans Metrikleri sekmesi
        self.metrics_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(self.metrics_frame, text=self.lm.tr("tab_performance_metrics", " Performans Metrikleri"))
        self.setup_metrics_tab()

    def back_to_sdg(self) -> None:
        """SDG ana ekranına geri dön"""
        try:
            for widget in self.parent.winfo_children():
                widget.destroy()
            from .sdg_gui import SDGGUI
            SDGGUI(self.parent, self.company_id)
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), 
                               self.lm.tr("err_return_back", "Geri dönme işleminde hata: {error}").format(error=str(e)))

    def setup_overview_tab(self) -> None:
        """Genel bakış sekmesini oluştur"""
        # Üst panel - Özet kartları
        summary_frame = tk.Frame(self.overview_frame, bg='#f8f9fa')
        summary_frame.pack(fill='x', padx=10, pady=10)

        # Genel ilerleme kartı
        self.overall_card = self.create_summary_card(summary_frame, self.lm.tr("card_overall_progress", "Genel İlerleme"), "0%", "#27ae60")
        self.overall_card.pack(side='left', padx=5)

        # Tamamlanan hedefler kartı
        self.completed_card = self.create_summary_card(summary_frame, self.lm.tr("card_completed_goals", "Tamamlanan Hedefler"), "0/17", "#2ecc71")
        self.completed_card.pack(side='left', padx=5)

        # Devam eden hedefler kartı
        self.in_progress_card = self.create_summary_card(summary_frame, self.lm.tr("card_ongoing_goals", "Devam Eden Hedefler"), "0/17", "#f39c12")
        self.in_progress_card.pack(side='left', padx=5)

        # Başlanmamış hedefler kartı
        self.not_started_card = self.create_summary_card(summary_frame, self.lm.tr("card_not_started_goals", "Başlanmamış Hedefler"), "0/17", "#e74c3c")
        self.not_started_card.pack(side='left', padx=5)

        # Alt panel - Hedef listesi
        goals_list_frame = tk.Frame(self.overview_frame, bg='white', relief='raised', bd=1)
        goals_list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Hedef listesi başlığı
        goals_title = tk.Label(goals_list_frame, text=self.lm.tr("goals_list_title", "SDG Hedefleri İlerleme Durumu"),
                              font=('Segoe UI', 12, 'bold'), bg='white', fg='#2c3e50')
        goals_title.pack(pady=10)

        # Hedef listesi Treeview
        columns = (
            self.lm.tr("col_sdg", "SDG"), 
            self.lm.tr("col_goal", "Hedef"), 
            self.lm.tr("col_indicators", "Göstergeler"), 
            self.lm.tr("col_completed", "Tamamlanan"), 
            self.lm.tr("col_ongoing", "Devam Eden"), 
            self.lm.tr("col_not_started", "Başlanmamış"), 
            self.lm.tr("col_progress", "İlerleme %")
        )
        self.goals_tree = ttk.Treeview(goals_list_frame, columns=columns, show='headings', height=15)

        # Sütun başlıkları
        for col in columns:
            self.goals_tree.heading(col, text=col)

        # Sütun genişlikleri
        self.goals_tree.column(columns[0], width=60)
        self.goals_tree.column(columns[1], width=200)
        self.goals_tree.column(columns[2], width=80)
        self.goals_tree.column(columns[3], width=80)
        self.goals_tree.column(columns[4], width=80)
        self.goals_tree.column(columns[5], width=80)
        self.goals_tree.column(columns[6], width=80)

        # Scrollbar
        goals_scrollbar = ttk.Scrollbar(goals_list_frame, orient="vertical", command=self.goals_tree.yview)
        self.goals_tree.configure(yscrollcommand=goals_scrollbar.set)

        self.goals_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        goals_scrollbar.pack(side='right', fill='y', pady=10)

    def setup_goals_tab(self) -> None:
        """Hedef detayları sekmesini oluştur"""
        # Sol panel - Hedef seçimi
        left_panel = tk.Frame(self.goals_frame, bg='white', relief='raised', bd=1)
        left_panel.pack(side='left', fill='both', expand=True, padx=(10, 5), pady=10)

        # Hedef seçimi
        goal_selection_frame = tk.Frame(left_panel, bg='white')
        goal_selection_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(goal_selection_frame, text=self.lm.tr("lbl_select_sdg_goal", "SDG Hedefi Seçin:"),
                font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w')

        self.goal_var = tk.StringVar()
        self.goal_combo = ttk.Combobox(goal_selection_frame, textvariable=self.goal_var,
                                      state='readonly', width=30)
        self.goal_combo.pack(fill='x', pady=5)
        self.goal_combo.bind('<<ComboboxSelected>>', self.on_goal_selected)

        # Hedef bilgileri
        self.goal_info_frame = tk.Frame(left_panel, bg='#ecf0f1', relief='solid', bd=1)
        self.goal_info_frame.pack(fill='x', padx=10, pady=10)

        self.goal_info_label = tk.Label(self.goal_info_frame,
                                       text=self.lm.tr("lbl_please_select_goal", "Lütfen bir hedef seçin"),
                                       font=('Segoe UI', 10), bg='#ecf0f1', fg='#2c3e50')
        self.goal_info_label.pack(pady=10)

        # Sağ panel - Gösterge detayları
        right_panel = tk.Frame(self.goals_frame, bg='white', relief='raised', bd=1)
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 10), pady=10)

        # Gösterge listesi başlığı
        indicators_title = tk.Label(right_panel, text=self.lm.tr("lbl_indicator_details", "Gösterge Detayları"),
                                   font=('Segoe UI', 12, 'bold'), bg='white', fg='#2c3e50')
        indicators_title.pack(pady=10)

        # Gösterge listesi Treeview
        columns = (
            self.lm.tr("col_code", "Kod"), 
            self.lm.tr("col_definition", "Tanım"), 
            self.lm.tr("col_q1", "Soru 1"), 
            self.lm.tr("col_q2", "Soru 2"), 
            self.lm.tr("col_q3", "Soru 3"), 
            self.lm.tr("col_progress", "İlerleme %"), 
            self.lm.tr("col_status", "Durum")
        )
        self.indicators_tree = ttk.Treeview(right_panel, columns=columns, show='headings', height=15)

        # Sütun başlıkları
        for col in columns:
            self.indicators_tree.heading(col, text=col)

        # Sütun genişlikleri
        self.indicators_tree.column(columns[0], width=80)
        self.indicators_tree.column(columns[1], width=250)
        self.indicators_tree.column(columns[2], width=60)
        self.indicators_tree.column(columns[3], width=60)
        self.indicators_tree.column(columns[4], width=60)
        self.indicators_tree.column(columns[5], width=80)
        self.indicators_tree.column(columns[6], width=100)

        # Scrollbar
        indicators_scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.indicators_tree.yview)
        self.indicators_tree.configure(yscrollcommand=indicators_scrollbar.set)

        self.indicators_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        indicators_scrollbar.pack(side='right', fill='y', pady=10)

    def setup_trends_tab(self) -> None:
        """Trend analizi sekmesini oluştur"""
        # Trend seçimi
        trend_selection_frame = tk.Frame(self.trends_frame, bg='#f8f9fa')
        trend_selection_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(trend_selection_frame, text=self.lm.tr("lbl_trend_analysis", "Trend Analizi:"),
                font=('Segoe UI', 12, 'bold'), bg='#f8f9fa').pack(side='left')

        self.trend_goal_var = tk.StringVar()
        self.trend_goal_combo = ttk.Combobox(trend_selection_frame, textvariable=self.trend_goal_var,
                                            state='readonly', width=20)
        self.trend_goal_combo.pack(side='left', padx=10)
        self.trend_goal_combo.bind('<<ComboboxSelected>>', self.on_trend_goal_selected)

        # Tüm hedefler seçeneği
        self.trend_goal_combo['values'] = [self.lm.tr("opt_all_goals", "Tüm Hedefler")] + [f"SDG {i}" for i in range(1, 18)]
        self.trend_goal_combo.set(self.lm.tr("opt_all_goals", "Tüm Hedefler"))

        # Trend grafik alanı
        trend_display_frame = tk.Frame(self.trends_frame, bg='white', relief='raised', bd=1)
        trend_display_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Basit trend gösterimi (metin tabanlı)
        self.trend_text = tk.Text(trend_display_frame, height=20, width=80,
                                 font=('Courier', 9), bg='#f8f9fa')
        self.trend_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Scrollbar
        trend_scrollbar = ttk.Scrollbar(trend_display_frame, orient="vertical", command=self.trend_text.yview)
        self.trend_text.configure(yscrollcommand=trend_scrollbar.set)
        trend_scrollbar.pack(side='right', fill='y')

    def setup_metrics_tab(self) -> None:
        """Performans metrikleri sekmesini oluştur"""
        # Metrik ekleme
        add_metric_frame = tk.Frame(self.metrics_frame, bg='#f8f9fa')
        add_metric_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(add_metric_frame, text=self.lm.tr("lbl_performance_metrics", "Performans Metrikleri:"),
                font=('Segoe UI', 12, 'bold'), bg='#f8f9fa').pack(side='left')

        # Metrik ekleme butonu
        add_metric_btn = tk.Button(add_metric_frame, text=self.lm.tr("btn_add_metric", "+ Metrik Ekle"),
                                  font=('Segoe UI', 10), bg='#27ae60', fg='white',
                                  relief='flat', bd=0, padx=15, pady=5,
                                  command=self.add_metric_dialog)
        add_metric_btn.pack(side='right')

        # Metrik listesi
        metrics_list_frame = tk.Frame(self.metrics_frame, bg='white', relief='raised', bd=1)
        metrics_list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Metrik listesi Treeview
        columns = (
            self.lm.tr("col_metric_name", "Metrik Adı"), 
            self.lm.tr("col_value", "Değer"), 
            self.lm.tr("col_unit", "Birim"), 
            self.lm.tr("col_date", "Tarih"), 
            self.lm.tr("col_sdg", "SDG"), 
            self.lm.tr("col_indicator", "Gösterge")
        )
        self.metrics_tree = ttk.Treeview(metrics_list_frame, columns=columns, show='headings', height=15)

        # Sütun başlıkları
        for col in columns:
            self.metrics_tree.heading(col, text=col)

        # Sütun genişlikleri
        self.metrics_tree.column(columns[0], width=150)
        self.metrics_tree.column(columns[1], width=100)
        self.metrics_tree.column(columns[2], width=80)
        self.metrics_tree.column(columns[3], width=100)
        self.metrics_tree.column(columns[4], width=60)
        self.metrics_tree.column(columns[5], width=100)

        # Scrollbar
        metrics_scrollbar = ttk.Scrollbar(metrics_list_frame, orient="vertical", command=self.metrics_tree.yview)
        self.metrics_tree.configure(yscrollcommand=metrics_scrollbar.set)

        self.metrics_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        metrics_scrollbar.pack(side='right', fill='y', pady=10)

    def create_summary_card(self, parent, title, value, color) -> tk.Frame:
        """Özet kartı oluştur"""
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
            # Genel bakış verilerini yükle
            self.load_overview_data()

            # Hedef detayları için SDG listesini yükle
            self.load_goals_list()

            # Trend analizi için verileri yükle
            self.load_trend_data()

            # Performans metriklerini yükle
            self.load_metrics_data()

        except Exception as e:
            messagebox.showerror(self.lm.tr("title_error", "Hata"), 
                               self.lm.tr("err_data_load", "Veriler yüklenirken hata oluştu: {error}").format(error=str(e)))

    def load_overview_data(self) -> None:
        """Genel bakış verilerini yükle"""
        try:
            # Tüm hedeflerin ilerlemesini al
            all_progress: Dict[str, Any] = self.progress_tracking.get_all_goals_progress(self.company_id)

            # Özet kartlarını güncelle
            overall_completion = all_progress['overall_completion']
            total_completed = all_progress['total_completed']
            total_in_progress = all_progress['total_in_progress']
            total_not_started = all_progress['total_not_started']

            # Kartları güncelle
            self.update_summary_card(self.overall_card, f"{overall_completion}%")
            self.update_summary_card(self.completed_card, f"{total_completed}/17")
            self.update_summary_card(self.in_progress_card, f"{total_in_progress}/17")
            self.update_summary_card(self.not_started_card, f"{total_not_started}/17")

            # Hedef listesini güncelle
            self.update_goals_tree(all_progress['goals'])

        except Exception as e:
            logging.error(f"Genel bakış verileri yüklenirken hata: {e}")

    def update_summary_card(self, card, value) -> None:
        """Özet kartını güncelle"""
        for widget in card.winfo_children():
            if isinstance(widget, tk.Label):
                font_val = str(widget.cget('font'))
                if 'Segoe UI' in font_val and '16' in font_val:
                    widget.config(text=value)
                    break

    def update_goals_tree(self, goals: List[Dict[str, Any]]) -> None:
        """Hedef listesini güncelle"""
        # Mevcut verileri temizle
        for item in self.goals_tree.get_children():
            self.goals_tree.delete(item)

        # Hedefleri ekle
        for goal in goals:
            self.goals_tree.insert('', 'end', values=(
                f"SDG {goal['sdg_no']}",
                goal['sdg_title'][:30] + '...' if len(goal['sdg_title']) > 30 else goal['sdg_title'],
                goal['total_indicators'],
                goal['completed_indicators'],
                goal['in_progress_indicators'],
                goal['not_started_indicators'],
                f"{goal['completion_percentage']}%"
            ))

    def load_goals_list(self) -> None:
        """Hedef listesini yükle"""
        try:
            # SDG hedeflerini al
            conn = self.progress_tracking.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, code, title_tr FROM sdg_goals ORDER BY code")
            goals = cursor.fetchall()
            conn.close()

            # ComboBox'a ekle
            goal_options = [f"SDG {goal[1]}: {goal[2]}" for goal in goals]
            self.goal_combo['values'] = goal_options

        except Exception as e:
            logging.error(f"Hedef listesi yüklenirken hata: {e}")

    def on_goal_selected(self, event) -> None:
        """Hedef seçildiğinde"""
        try:
            selected_text = self.goal_var.get()
            if not selected_text:
                return

            # SDG numarasını çıkar
            sdg_no = int(selected_text.split(':')[0].split()[-1])

            # Hedef bilgilerini göster
            self.show_goal_info(sdg_no)

            # Gösterge detaylarını yükle
            self.load_indicators_for_goal(sdg_no)

        except Exception as e:
            logging.error(f"Hedef seçimi işlenirken hata: {e}")

    def show_goal_info(self, sdg_no: int) -> None:
        """Hedef bilgilerini göster"""
        try:
            progress = self.progress_tracking.calculate_goal_progress(self.company_id, sdg_no)

            info_text = f"SDG {sdg_no}: {progress['sdg_title']}\n"
            info_text += f"{self.lm.tr('lbl_total_indicators', 'Toplam Gösterge:')} {progress['total_indicators']}\n"
            info_text += f"{self.lm.tr('lbl_completed', 'Tamamlanan:')} {progress['completed_indicators']}\n"
            info_text += f"{self.lm.tr('lbl_ongoing', 'Devam Eden:')} {progress['in_progress_indicators']}\n"
            info_text += f"{self.lm.tr('lbl_not_started', 'Başlanmamış:')} {progress['not_started_indicators']}\n"
            info_text += f"{self.lm.tr('lbl_progress', 'İlerleme:')} {progress['completion_percentage']}%"

            self.goal_info_label.config(text=info_text)

        except Exception as e:
            logging.error(f"Hedef bilgileri gösterilirken hata: {e}")

    def load_indicators_for_goal(self, sdg_no: int) -> None:
        """Hedef için gösterge detaylarını yükle"""
        try:
            # Mevcut verileri temizle
            for item in self.indicators_tree.get_children():
                self.indicators_tree.delete(item)

            # Gösterge detaylarını al
            progress = self.progress_tracking.calculate_goal_progress(self.company_id, sdg_no)

            for indicator in progress['indicators']:
                # Soru durumları
                q1_status = "" if indicator['question_1_answered'] else ""
                q2_status = "" if indicator['question_2_answered'] else ""
                q3_status = "" if indicator['question_3_answered'] else ""

                # Durum metni
                status = indicator['status']
                status_text = {
                    'completed': self.lm.tr('status_completed', 'Tamamlandı'),
                    'in_progress': self.lm.tr('status_in_progress', 'Devam Ediyor'),
                    'not_started': self.lm.tr('status_not_started', 'Başlanmadı')
                }.get(status, self.lm.tr('status_unknown', 'Bilinmiyor'))

                self.indicators_tree.insert('', 'end', values=(
                    indicator['indicator_code'],
                    indicator['indicator_title'][:40] + '...' if len(indicator['indicator_title']) > 40 else indicator['indicator_title'],
                    q1_status,
                    q2_status,
                    q3_status,
                    f"{indicator['completion_percentage']}%",
                    status_text
                ))

        except Exception as e:
            logging.error(f"Gösterge detayları yüklenirken hata: {e}")

    def load_trend_data(self) -> None:
        """Trend verilerini yükle"""
        try:
            self.on_trend_goal_selected(None)
        except Exception as e:
            logging.error(f"Trend verileri yüklenirken hata: {e}")

    def on_trend_goal_selected(self, event) -> None:
        """Trend hedefi seçildiğinde"""
        try:
            selected_text = self.trend_goal_var.get()
            if not selected_text:
                return

            # Trend verilerini al
            if selected_text == self.lm.tr("opt_all_goals", "Tüm Hedefler"):
                trends = self.progress_tracking.get_progress_trends(self.company_id, days=30)
            else:
                sdg_no = int(selected_text.split()[-1])
                trends = self.progress_tracking.get_progress_trends(self.company_id, sdg_no, 30)

            # Trend metnini oluştur
            self.trend_text.delete('1.0', tk.END)

            if not trends:
                self.trend_text.insert('1.0', self.lm.tr("msg_trend_not_found", "Trend verisi bulunamadı"))
                return

            trend_text = f"{self.lm.tr('title_trend_analysis_30days', 'İlerleme Trend Analizi - Son 30 Gün')}\n"
            trend_text += "=" * 50 + "\n\n"

            for trend in trends:
                date_str = trend['date'][:10]  # Sadece tarih kısmı
                completion = trend['completion_percentage']
                answered = trend['answered_questions']
                total = trend['total_questions']
                new_answers = trend.get('new_answers', 0)

                trend_text += f"{date_str}: {completion:.1f}% ({answered}/{total})"
                if new_answers > 0:
                    trend_text += f" [+{new_answers} {self.lm.tr('lbl_new_answer', 'yeni yanıt')}]"
                trend_text += "\n"

            self.trend_text.insert('1.0', trend_text)

        except Exception as e:
            logging.error(f"Trend analizi işlenirken hata: {e}")

    def load_metrics_data(self) -> None:
        """Performans metriklerini yükle"""
        try:
            # Mevcut verileri temizle
            for item in self.metrics_tree.get_children():
                self.metrics_tree.delete(item)

            # Metrikleri al
            metrics = self.progress_tracking.get_performance_metrics(self.company_id)

            for metric in metrics:
                date_str = metric['measurement_date'][:10]  # Sadece tarih kısmı
                sdg_text = f"SDG {metric.get('sdg_no', self.lm.tr('lbl_no_data', 'Veri Yok'))}" if metric.get('sdg_no') else self.lm.tr('lbl_no_data', 'Veri Yok')
                indicator_text = metric.get('indicator_code', self.lm.tr('lbl_no_data', 'Veri Yok'))

                self.metrics_tree.insert('', 'end', values=(
                    metric['metric_name'],
                    f"{metric['metric_value']:.2f}",
                    metric['metric_unit'] or self.lm.tr('lbl_no_data', 'Veri Yok'),
                    date_str,
                    sdg_text,
                    indicator_text
                ))

        except Exception as e:
            logging.error(f"Performans metrikleri yüklenirken hata: {e}")

    def add_metric_dialog(self) -> None:
        """Metrik ekleme dialogu"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr("title_add_metric", "Performans Metriği Ekle"))
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()

        # Metrik adı
        tk.Label(dialog, text=self.lm.tr("lbl_metric_name", "Metrik Adı:"), font=('Segoe UI', 10, 'bold')).pack(pady=5)
        metric_name_entry = tk.Entry(dialog, width=40)
        metric_name_entry.pack(pady=5)

        # Metrik değeri
        tk.Label(dialog, text=self.lm.tr("lbl_value", "Değer:"), font=('Segoe UI', 10, 'bold')).pack(pady=5)
        metric_value_entry = tk.Entry(dialog, width=40)
        metric_value_entry.pack(pady=5)

        # Birim
        tk.Label(dialog, text=self.lm.tr("lbl_unit_optional", "Birim (opsiyonel):"), font=('Segoe UI', 10, 'bold')).pack(pady=5)
        metric_unit_entry = tk.Entry(dialog, width=40)
        metric_unit_entry.pack(pady=5)

        # SDG numarası
        tk.Label(dialog, text=self.lm.tr("lbl_sdg_no_optional", "SDG Numarası (opsiyonel):"), font=('Segoe UI', 10, 'bold')).pack(pady=5)
        sdg_no_entry = tk.Entry(dialog, width=40)
        sdg_no_entry.pack(pady=5)

        # Gösterge kodu
        tk.Label(dialog, text=self.lm.tr("lbl_indicator_code_optional", "Gösterge Kodu (opsiyonel):"), font=('Segoe UI', 10, 'bold')).pack(pady=5)
        indicator_code_entry = tk.Entry(dialog, width=40)
        indicator_code_entry.pack(pady=5)

        # Butonlar
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)

        def save_metric() -> None:
            try:
                metric_name = metric_name_entry.get().strip()
                metric_value = float(metric_value_entry.get())
                metric_unit = metric_unit_entry.get().strip() or None
                sdg_no = int(sdg_no_entry.get()) if sdg_no_entry.get().strip() else None
                indicator_code = indicator_code_entry.get().strip() or None

                if not metric_name:
                    messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("err_metric_name_required", "Metrik adı gerekli"))
                    return

                success = self.progress_tracking.add_performance_metric(
                    self.company_id, metric_name, metric_value, metric_unit, sdg_no, indicator_code
                )

                if success:
                    messagebox.showinfo(self.lm.tr("title_success", "Başarılı"), self.lm.tr("msg_metric_added", "Metrik başarıyla eklendi"))
                    dialog.destroy()
                    self.load_metrics_data()
                else:
                    messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("err_metric_add_failed", "Metrik eklenemedi"))

            except ValueError:
                messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("err_invalid_value", "Geçersiz değer"))
            except Exception as e:
                messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("err_adding_metric", "Metrik eklenirken hata: {error}").format(error=str(e)))

        tk.Button(button_frame, text=self.lm.tr("btn_save", "Kaydet"), command=save_metric,
                 bg='#27ae60', fg='white', relief='flat', padx=20).pack(side='left', padx=5)
        tk.Button(button_frame, text=self.lm.tr("btn_cancel", "İptal"), command=dialog.destroy,
                 bg='#e74c3c', fg='white', relief='flat', padx=20).pack(side='left', padx=5)

    def refresh_data(self) -> None:
        """Verileri yenile"""
        try:
            self.load_data()
            messagebox.showinfo(self.lm.tr("title_success", "Başarılı"), self.lm.tr("msg_data_refreshed", "Veriler yenilendi"))
        except Exception as e:
            messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("err_refreshing_data", "Veriler yenilenirken hata oluştu: {error}").format(error=str(e)))

if __name__ == "__main__":
    # Test
    root = tk.Tk()
    root.title("SDG İlerleme Takibi")
    app = SDGProgressGUI(root, 1)
    root.mainloop()
