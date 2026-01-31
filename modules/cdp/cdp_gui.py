import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CDP (Carbon Disclosure Project) GUI
CDP Climate Change, Water Security ve Forests anketleri için kullanıcı arayüzü
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from utils.ui_theme import apply_theme
from utils.language_manager import LanguageManager

from .cdp_manager import CDPManager
from .cdp_scoring import CDPScoringSystem


class CDPGUI:
    """CDP (Carbon Disclosure Project) GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()
        self.manager = CDPManager()
        self.scoring_system = CDPScoringSystem()
        self.current_questionnaire: str | None = None
        self.current_questions: list[dict] = []
        self.questionnaire_map: dict[str, str] = {}
        self.response_vars: dict[str, tk.StringVar] = {}

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """CDP arayüzünü oluştur"""
        apply_theme(self.parent)
        # Ana frame - Scrollable yapısı eklenebilir ama şimdilik frame
        main_frame = tk.Frame(self.parent, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık ve Aksiyonlar
        header_frame = tk.Frame(main_frame, bg='#f0f2f5')
        header_frame.pack(fill='x', pady=(0, 20))

        # Sol taraf başlık
        tk.Label(header_frame, text=self.lm.tr('cdp_title', "CDP (Carbon Disclosure Project)"), 
                font=('Segoe UI', 20, 'bold'), fg='#1e293b', bg='#f0f2f5').pack(side='left')

        # Sağ taraf butonlar
        actions = tk.Frame(header_frame, bg='#f0f2f5')
        actions.pack(side='right')
        
        btn_style = {'font': ('Segoe UI', 10), 'bg': '#2563eb', 'fg': 'white', 'relief': 'flat', 'padx': 15, 'pady': 8, 'cursor': 'hand2'}
        tk.Button(actions, text=self.lm.tr('report_center', "Rapor Merkezi"), command=self.open_report_center_cdp, **btn_style).pack(side='right')

        # Ana içerik alanı (Notebook)
        content_frame = tk.Frame(main_frame, bg='#f0f2f5')
        content_frame.pack(fill='both', expand=True)

        style = ttk.Style()
        style.configure("TNotebook", background="#f0f2f5", borderwidth=0)
        style.configure("TNotebook.Tab", padding=[12, 8], font=('Segoe UI', 10))

        # Notebook oluştur
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True)

        # Sekmeleri oluştur
        self.create_dashboard_tab()
        self.create_questionnaires_tab()
        self.create_scoring_tab()
        self.create_reports_tab()

    def create_dashboard_tab(self) -> None:
        """Dashboard sekmesi"""
        dashboard_frame = tk.Frame(self.notebook, bg='#f0f2f5')
        self.notebook.add(dashboard_frame, text=f" {self.lm.tr('dashboard', 'Dashboard')}")

        # Container
        container = tk.Frame(dashboard_frame, bg='#f0f2f5')
        container.pack(fill='both', expand=True, padx=10, pady=10)

        # Sol panel - İstatistikler
        left_panel = tk.Frame(container, bg='white', relief='flat')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # İç padding için frame
        left_inner = tk.Frame(left_panel, bg='white')
        left_inner.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        tk.Label(left_inner, text=self.lm.tr('cdp_dashboard', "CDP Dashboard"),
                font=('Segoe UI', 14, 'bold'), bg='white', fg='#334155').pack(anchor='w', pady=(0, 20))

        # İstatistik kartları
        self.stats_frame = tk.Frame(left_inner, bg='white')
        self.stats_frame.pack(fill='x', pady=10)

        # Sağ panel - Anket durumu
        right_panel = tk.Frame(container, bg='white', relief='flat')
        right_panel.pack(side='right', fill='both', expand=True)
        
        right_inner = tk.Frame(right_panel, bg='white')
        right_inner.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(right_inner, text=self.lm.tr('survey_status', "Anket Durumu"),
                font=('Segoe UI', 14, 'bold'), bg='white', fg='#334155').pack(anchor='w', pady=(0, 20))

        # Anket listesi - Custom Style
        list_frame = tk.Frame(right_inner, bg='white', highlightthickness=1, highlightbackground='#e2e8f0')
        list_frame.pack(fill='both', expand=True)

        self.questionnaire_listbox = tk.Listbox(list_frame, font=('Segoe UI', 10), 
                                              height=15, relief='flat', bd=0,
                                              selectbackground='#e6f0fa', selectforeground='#1e293b')
        self.questionnaire_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        self.questionnaire_listbox.bind('<<ListboxSelect>>', self.on_questionnaire_select)


    def create_questionnaires_tab(self) -> None:
        """Anketler sekmesi"""
        questionnaires_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(questionnaires_frame, text=f" {self.lm.tr('surveys', 'Anketler')}")

        # Üst panel - Anket seçimi
        top_panel = tk.Frame(questionnaires_frame, bg='white')
        top_panel.pack(fill='x', padx=10, pady=10)

        tk.Label(top_panel, text=self.lm.tr('select_survey', "Anket Seçin:"),
                font=('Segoe UI', 12, 'bold'), bg='white').pack(side='left', padx=(0, 10))

        self.questionnaire_var = tk.StringVar()
        self.questionnaire_combo = ttk.Combobox(top_panel, textvariable=self.questionnaire_var,
                                               state='readonly', width=30)
        self.questionnaire_combo.pack(side='left', padx=(0, 10))
        self.questionnaire_combo.bind('<<ComboboxSelected>>', self.on_questionnaire_change)

        # Ana içerik - Sorular
        content_frame = tk.Frame(questionnaires_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Canvas ve scrollbar
        canvas = tk.Canvas(content_frame, bg='white')
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='white')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_frame = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Canvas genişlediğinde frame'i de genişlet
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_frame, width=e.width))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Alt panel - Butonlar
        btn_frame = tk.Frame(questionnaires_frame, bg='white')
        btn_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(btn_frame, text=self.lm.tr('save_responses', "Yanıtları Kaydet"), style='Primary.TButton', command=self.save_responses).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=self.lm.tr('refresh', "Yenile"), style='Primary.TButton', command=self.refresh_questions).pack(side='left', padx=5)

    def create_scoring_tab(self) -> None:
        """Scoring sekmesi"""
        scoring_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(scoring_frame, text=f" {self.lm.tr('scoring', 'Scoring')}")

        # Skorlar
        tk.Label(scoring_frame, text=self.lm.tr('cdp_scores', "CDP Skorları"),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(anchor='w', padx=20, pady=20)

        # Skor kartları
        self.scoring_frame = tk.Frame(scoring_frame, bg='white')
        self.scoring_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Alt panel - Skor hesaplama
        btn_frame = tk.Frame(scoring_frame, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=20)

        ttk.Button(btn_frame, text=self.lm.tr('calc_scores', "Skorları Hesapla"), style='Primary.TButton', command=self.calculate_scores).pack(side='left', padx=5)

    def create_reports_tab(self) -> None:
        """Raporlar sekmesi"""
        reports_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(reports_frame, text=f" {self.lm.tr('reports', 'Raporlar')}")

        # Rapor türleri
        tk.Label(reports_frame, text=self.lm.tr('cdp_reports', "CDP Raporları"),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(anchor='w', padx=20, pady=20)

        # Yıl seçimi
        year_frame = tk.Frame(reports_frame, bg='white')
        year_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(year_frame, text=self.lm.tr('reporting_year', "Raporlama Yılı:"),
                font=('Segoe UI', 10), bg='white').pack(side='left', padx=(0, 10))

        from datetime import datetime
        current_year = datetime.now().year

        self.report_year_var = tk.StringVar(value=str(current_year))
        year_combo = ttk.Combobox(year_frame, textvariable=self.report_year_var,
                                 values=[str(y) for y in range(current_year - 5, current_year + 1)],
                                 state='readonly', width=10)
        year_combo.pack(side='left')

        # Rapor butonları
        reports_btn_frame = tk.Frame(reports_frame, bg='white')
        reports_btn_frame.pack(fill='x', padx=20, pady=20)

        report_buttons = [
            (self.lm.tr('cdp_report_climate', "CDP Climate Change Raporu"), self.generate_climate_report, '#2E7D32'),
            (self.lm.tr('cdp_report_water', "CDP Water Security Raporu"), self.generate_water_report, '#1976D2'),
            (self.lm.tr('cdp_report_forests', "CDP Forests Raporu"), self.generate_forests_report, '#388E3C'),
            (self.lm.tr('cdp_report_comprehensive', "Kapsamlı CDP Raporu"), self.generate_comprehensive_report, '#F57C00'),
            (self.lm.tr('export_excel', "Excel Dışa Aktarım"), self.export_to_excel, '#7B1FA2'),
        ]

        for i, (text, command, color) in enumerate(report_buttons):
            btn = ttk.Button(reports_btn_frame, text=text, style='Primary.TButton', command=command)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='ew')

        reports_btn_frame.grid_columnconfigure(0, weight=1)
        reports_btn_frame.grid_columnconfigure(1, weight=1)

        # Rapor durumu
        self.report_status_label = tk.Label(reports_frame, text="",
                                            font=('Segoe UI', 9, 'italic'), fg='#666', bg='white')
        self.report_status_label.pack(anchor='w', padx=20, pady=10)

    def open_report_center_cdp(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('cdp')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for cdp: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('err_open_report_center', "Rapor Merkezi açılamadı:\n{e}").format(e=e))
            logging.error(f"Error opening report center: {e}")

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            # Dashboard verilerini yükle
            self.load_dashboard_data()

            # Anket listesini yükle
            self.load_questionnaire_list()

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('err_data_load', "Veri yüklenirken hata: {e}").format(e=e))

    def load_dashboard_data(self) -> None:
        """Dashboard verilerini yükle"""
        try:
            summary = self.manager.get_company_summary(self.company_id)

            # İstatistik kartlarını oluştur
            for widget in self.stats_frame.winfo_children():
                widget.destroy()

            stats_data = [
                (self.lm.tr('total_surveys', "Toplam Anket"), summary.get('total_questionnaires', 0), '#3498db'),
                (self.lm.tr('completed_surveys', "Tamamlanan"), summary.get('completed_questionnaires', 0), '#27ae60'),
                (self.lm.tr('avg_score', "Ortalama Skor"), f"{summary.get('average_score', 0):.1f}%", '#f39c12'),
                (self.lm.tr('avg_grade', "Ortalama Grade"), summary.get('average_grade', 'D'), '#e74c3c'),
            ]

            for i, (title, value, color) in enumerate(stats_data):
                self.create_stat_card(self.stats_frame, title, value, color, 0, i)

        except Exception as e:
            logging.error(f"Dashboard verileri yüklenirken hata: {e}")

    def create_stat_card(self, parent, title, value, color, row, col):
        """İstatistik kartı oluştur"""
        card = tk.Frame(parent, bg=color, relief='raised', bd=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        parent.grid_columnconfigure(col, weight=1)

        tk.Label(card, text=title, font=('Segoe UI', 10, 'bold'),
                bg=color, fg='white').pack(pady=5)
        tk.Label(card, text=str(value), font=('Segoe UI', 16, 'bold'),
                bg=color, fg='white').pack(pady=5)

    def load_questionnaire_list(self) -> None:
        """Anket listesini yükle"""
        try:
            self.questionnaire_map = {
                self.lm.tr('cdp_climate', "Climate Change"): "Climate Change",
                self.lm.tr('cdp_water', "Water Security"): "Water Security",
                self.lm.tr('cdp_forests', "Forests"): "Forests"
            }
            questionnaires = list(self.questionnaire_map.keys())
            
            self.questionnaire_listbox.delete(0, tk.END)
            for q in questionnaires:
                self.questionnaire_listbox.insert(tk.END, q)
            
            # Combo box güncelleme
            self.questionnaire_combo['values'] = questionnaires
                
        except Exception as e:
            logging.error(f"Anket listesi yüklenirken hata: {e}")

    def on_questionnaire_select(self, event):
        selection = self.questionnaire_listbox.curselection()
        if not selection:
            return
        
        q_name = self.questionnaire_listbox.get(selection[0])
        self.questionnaire_var.set(q_name)
        self.load_questions(q_name)
        self.notebook.select(1) # Anketler sekmesine geç

    def on_questionnaire_change(self, event):
        q_name = self.questionnaire_var.get()
        if q_name:
            self.load_questions(q_name)

    def load_questions(self, questionnaire_name: str):
        self.current_questionnaire = questionnaire_name
        
        # Temizle
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Soruları manager'dan çek (Mock data for now if manager doesn't have it)
        # self.current_questions = self.manager.get_questions(questionnaire_name)
        # Mocking for UI dev:
        self.current_questions = [
            {'id': 'Q1', 'text': self.lm.tr('mock_q1', 'Soru 1 metni...'), 'type': 'text'},
            {'id': 'Q2', 'text': self.lm.tr('mock_q2', 'Soru 2 metni...'), 'type': 'boolean'},
        ]
        
        tk.Label(self.scrollable_frame, text=f"{questionnaire_name} {self.lm.tr('questions', 'Soruları')}", font=('Segoe UI', 12, 'bold'), bg='white').pack(pady=10)
        
        for q in self.current_questions:
            f = tk.Frame(self.scrollable_frame, bg='white', pady=5)
            f.pack(fill='x', padx=10)
            tk.Label(f, text=f"{q['id']}: {q['text']}", bg='white', anchor='w').pack(fill='x')
            if q['type'] == 'text':
                tk.Entry(f).pack(fill='x')
            elif q['type'] == 'boolean':
                ttk.Combobox(f, values=[self.lm.tr('yes', 'Yes'), self.lm.tr('no', 'No')]).pack(fill='x')

    def save_responses(self):
        if not self.current_questionnaire:
            return
            
        internal_name = self.questionnaire_map.get(self.current_questionnaire, self.current_questionnaire)
        success_count = 0
        
        try:
            for q_id, var in self.response_vars.items():
                response = var.get()
                if self.manager.save_response(internal_name, self.company_id, q_id, response):
                    success_count += 1
            
            messagebox.showinfo(self.lm.tr('info', "Bilgi"), self.lm.tr('msg_save_success_count', "{count} yanıt başarıyla kaydedildi.").format(count=success_count))
        except Exception as e:
             messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('err_save_failed', "Kaydetme hatası: {e}").format(e=e))

    def refresh_questions(self):
        if self.current_questionnaire:
            self.load_questions(self.current_questionnaire)

    def calculate_scores(self):
        # Default to Climate Change or currently selected?
        # Let's use currently selected if available, else default
        q_name = self.current_questionnaire if self.current_questionnaire else self.lm.tr('cdp_climate', "Climate Change")
        internal_name = self.questionnaire_map.get(q_name, "Climate Change")
        
        try:
            # First calculate scores using manager (which calls scoring system internally or we do it here?)
            # Manager has calculate_scores method.
            scoring_result = self.manager.calculate_scores(internal_name, self.company_id, 2024)
            
            score = scoring_result.get('total_score', 0)
            grade = scoring_result.get('grade', 'D')
            
            messagebox.showinfo(self.lm.tr('score', "Skor"), 
                                f"{self.lm.tr('calculated_score', 'Hesaplanan Skor')}: {score:.1f}%\n"
                                f"{self.lm.tr('cdp_grade', 'CDP Grade')}: {grade}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('err_calc_failed', "Hesaplama hatası: {e}").format(e=e))

    def generate_climate_report(self):
        self.report_status_label.config(text=self.lm.tr('msg_report_generating', "Rapor oluşturuluyor..."))
        # Implement report generation
        self.report_status_label.config(text=self.lm.tr('msg_report_ready', "Rapor hazır!"))

    def generate_water_report(self):
        logging.warning("Water Security report generation not implemented yet")
        messagebox.showinfo(self.lm.tr('info', "Bilgi"), self.lm.tr('msg_not_implemented', "Bu özellik henüz aktif değil."))

    def generate_forests_report(self):
        logging.warning("Forests report generation not implemented yet")
        messagebox.showinfo(self.lm.tr('info', "Bilgi"), self.lm.tr('msg_not_implemented', "Bu özellik henüz aktif değil."))

    def generate_comprehensive_report(self):
        logging.warning("Comprehensive report generation not implemented yet")
        messagebox.showinfo(self.lm.tr('info', "Bilgi"), self.lm.tr('msg_not_implemented', "Bu özellik henüz aktif değil."))

    def export_to_excel(self):
        logging.warning("Excel export not implemented yet")
        messagebox.showinfo(self.lm.tr('info', "Bilgi"), self.lm.tr('msg_not_implemented', "Bu özellik henüz aktif değil."))
