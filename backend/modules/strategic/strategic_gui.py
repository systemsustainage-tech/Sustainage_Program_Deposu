#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stratejik Modüller GUI
CEO Mesajı, Sürdürülebilirlik Stratejisi, Risk-Fırsatlar, SMART Hedefler
"""

import logging
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from utils.language_manager import LanguageManager
from .ceo_message_dialog import show_ceo_message_dialog
from .ceo_message_manager import CEOMessageManager
from .risk_opportunity_manager import RiskOpportunityManager
from .smart_goals_manager import SMARTGoalsManager
from .strategy_creation_dialog import StrategyCreationDialog
from .sustainability_strategy_manager import SustainabilityStrategyManager


class StrategicGUI:
    """Stratejik modüller ana arayüzü"""

    def __init__(self, parent, company_id: int, user_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.user_id = user_id
        self.lm = LanguageManager()

        # Yöneticiler
        self.ceo_manager = CEOMessageManager()
        self.strategy_manager = SustainabilityStrategyManager()
        self.risk_manager = RiskOpportunityManager()
        self.goals_manager = SMARTGoalsManager()

        self.setup_ui()
        self.load_initial_data()

    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        header_frame = tk.Frame(main_frame, bg='#2c3e50', height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text=f" {self.lm.tr('strategic_center_title', 'Stratejik Yönetim Merkezi')}",
                              font=('Segoe UI', 18, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(side='left', padx=20, pady=20)

        subtitle_label = tk.Label(header_frame, text=self.lm.tr('strategic_center_subtitle', "CEO Mesajları, Stratejiler, Riskler ve Hedefler"),
                                 font=('Segoe UI', 12), fg='#bdc3c7', bg='#2c3e50')
        subtitle_label.pack(side='left')

        # İçerik alanı - Notebook (Sekmeler)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Sekmeler
        self.create_ceo_message_tab()
        self.create_strategy_tab()
        self.create_risk_opportunity_tab()
        self.create_smart_goals_tab()
        self.create_dashboard_tab()

    def create_ceo_message_tab(self) -> None:
        """CEO Mesajları sekmesi"""
        ceo_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(ceo_frame, text=f" {self.lm.tr('ceo_messages_tab', 'CEO Mesajları')}")

        # Sol panel - Mesaj listesi
        left_panel = tk.Frame(ceo_frame, bg='#ecf0f1', width=400)
        left_panel.pack(side='left', fill='y', padx=(10, 5), pady=10)
        left_panel.pack_propagate(False)

        # Sağ panel - Mesaj detayları
        right_panel = tk.Frame(ceo_frame, bg='white')
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 10), pady=10)

        self.build_ceo_message_list(left_panel)
        self.build_ceo_message_details(right_panel)

    def build_ceo_message_list(self, parent) -> None:
        """CEO mesaj listesi"""
        tk.Label(parent, text=f" {self.lm.tr('ceo_messages_title', 'CEO Mesajları')}", font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='#ecf0f1').pack(pady=(0, 20))

        # Yeni mesaj butonu
        new_btn = tk.Button(parent, text=f" {self.lm.tr('new_message_btn', 'Yeni Mesaj')}", font=('Segoe UI', 10, 'bold'),
                           fg='white', bg='#27ae60', relief='flat', cursor='hand2',
                           command=self.create_new_ceo_message)
        new_btn.pack(fill='x', pady=(0, 10))

        # Mesaj listesi
        columns = ('title', 'type', 'year', 'status')
        self.ceo_tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)

        headers = {
            'title': self.lm.tr('col_title', 'Başlık'),
            'type': self.lm.tr('col_type', 'Tür'),
            'year': self.lm.tr('col_year', 'Yıl'),
            'status': self.lm.tr('col_status', 'Durum')
        }

        for col in columns:
            self.ceo_tree.heading(col, text=headers[col])
            self.ceo_tree.column(col, width=90)

        ceo_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.ceo_tree.yview)
        self.ceo_tree.configure(yscrollcommand=ceo_scrollbar.set)

        self.ceo_tree.pack(side="left", fill="both", expand=True)
        ceo_scrollbar.pack(side="right", fill="y")

        self.ceo_tree.bind('<<TreeviewSelect>>', self.on_ceo_message_select)

    def build_ceo_message_details(self, parent) -> None:
        """CEO mesaj detayları"""
        tk.Label(parent, text=f" {self.lm.tr('message_details_title', 'Mesaj Detayları')}", font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='white').pack(pady=(0, 20))

        # Detay alanı
        detail_frame = tk.Frame(parent, bg='#f8f9fa', relief='solid', bd=1)
        detail_frame.pack(fill='both', expand=True)

        self.ceo_detail_text = scrolledtext.ScrolledText(detail_frame, height=20, bg='white',
                                                        font=('Segoe UI', 10), wrap='word', state='disabled')
        self.ceo_detail_text.pack(fill='both', expand=True, padx=10, pady=10)

    def create_strategy_tab(self) -> None:
        """Sürdürülebilirlik Stratejisi sekmesi"""
        strategy_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(strategy_frame, text=f" {self.lm.tr('strategies_tab', 'Stratejiler')}")

        # Sol panel - Strateji listesi
        left_panel = tk.Frame(strategy_frame, bg='#ecf0f1', width=400)
        left_panel.pack(side='left', fill='y', padx=(10, 5), pady=10)
        left_panel.pack_propagate(False)

        # Sağ panel - Strateji detayları
        right_panel = tk.Frame(strategy_frame, bg='white')
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 10), pady=10)

        self.build_strategy_list(left_panel)
        self.build_strategy_details(right_panel)

    def build_strategy_list(self, parent) -> None:
        """Strateji listesi"""
        tk.Label(parent, text=f" {self.lm.tr('strategies_title', 'Sürdürülebilirlik Stratejileri')}", font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='#ecf0f1').pack(pady=(0, 20))

        # Yeni strateji butonu
        new_btn = tk.Button(parent, text=f" {self.lm.tr('new_strategy_btn', 'Yeni Strateji')}", font=('Segoe UI', 10, 'bold'),
                           fg='white', bg='#3498db', relief='flat', cursor='hand2',
                           command=self.create_new_strategy)
        new_btn.pack(fill='x', pady=(0, 10))

        # Strateji listesi
        columns = ('name', 'start_date', 'end_date', 'status')
        self.strategy_tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)

        headers = {
            'name': self.lm.tr('col_strategy_name', 'Strateji Adı'),
            'start_date': self.lm.tr('col_start_date', 'Başlangıç'),
            'end_date': self.lm.tr('col_end_date', 'Bitiş'),
            'status': self.lm.tr('col_status', 'Durum')
        }

        for col in columns:
            self.strategy_tree.heading(col, text=headers[col])
            self.strategy_tree.column(col, width=90)

        strategy_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.strategy_tree.yview)
        self.strategy_tree.configure(yscrollcommand=strategy_scrollbar.set)

        self.strategy_tree.pack(side="left", fill="both", expand=True)
        strategy_scrollbar.pack(side="right", fill="y")

        self.strategy_tree.bind('<<TreeviewSelect>>', self.on_strategy_select)

    def build_strategy_details(self, parent) -> None:
        """Strateji detayları"""
        tk.Label(parent, text=f" {self.lm.tr('strategy_details_title', 'Strateji Detayları ve Hedefler')}", font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='white').pack(pady=(0, 20))

        # Notebook for strategy details
        detail_notebook = ttk.Notebook(parent)
        detail_notebook.pack(fill='both', expand=True)

        # Strateji bilgileri sekmesi
        info_frame = tk.Frame(detail_notebook, bg='white')
        detail_notebook.add(info_frame, text=self.lm.tr('strategy_info_tab', "Strateji Bilgileri"))

        self.strategy_info_text = scrolledtext.ScrolledText(info_frame, height=10, bg='white',
                                                           font=('Segoe UI', 10), wrap='word', state='disabled')
        self.strategy_info_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Hedefler sekmesi
        goals_frame = tk.Frame(detail_notebook, bg='white')
        detail_notebook.add(goals_frame, text=self.lm.tr('strategic_goals_tab', "Stratejik Hedefler"))

        # Hedefler listesi
        goal_columns = ('goal', 'category', 'target_year', 'status')
        self.goals_tree = ttk.Treeview(goals_frame, columns=goal_columns, show='headings', height=12)

        goal_headers = {
            'goal': self.lm.tr('col_goal', 'Hedef'),
            'category': self.lm.tr('col_category', 'Kategori'),
            'target_year': self.lm.tr('col_target_year', 'Hedef Yıl'),
            'status': self.lm.tr('col_status', 'Durum')
        }

        for col in goal_columns:
            self.goals_tree.heading(col, text=goal_headers[col])
            self.goals_tree.column(col, width=120)

        goals_scrollbar = ttk.Scrollbar(goals_frame, orient="vertical", command=self.goals_tree.yview)
        self.goals_tree.configure(yscrollcommand=goals_scrollbar.set)

        self.goals_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        goals_scrollbar.pack(side="right", fill="y")

    def create_risk_opportunity_tab(self) -> None:
        """Risk ve Fırsatlar sekmesi"""
        risk_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(risk_frame, text=f" {self.lm.tr('risk_opportunity_tab', 'Risk & Fırsatlar')}")

        # Notebook for risks and opportunities
        risk_notebook = ttk.Notebook(risk_frame)
        risk_notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Riskler sekmesi
        risks_tab = tk.Frame(risk_notebook, bg='white')
        risk_notebook.add(risks_tab, text=f" {self.lm.tr('risks_tab', 'Riskler')}")

        self.build_risks_panel(risks_tab)

        # Fırsatlar sekmesi
        opportunities_tab = tk.Frame(risk_notebook, bg='white')
        risk_notebook.add(opportunities_tab, text=f" {self.lm.tr('opportunities_tab', 'Fırsatlar')}")

        self.build_opportunities_panel(opportunities_tab)

    def build_risks_panel(self, parent) -> None:
        """Riskler paneli"""
        # Sol panel - Risk listesi
        left_panel = tk.Frame(parent, bg='#ecf0f1', width=500)
        left_panel.pack(side='left', fill='y', padx=(10, 5), pady=10)
        left_panel.pack_propagate(False)

        # Sağ panel - Risk detayları
        right_panel = tk.Frame(parent, bg='white')
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 10), pady=10)

        tk.Label(left_panel, text=f" {self.lm.tr('risks_title', 'Sürdürülebilirlik Riskleri')}", font=('Segoe UI', 14, 'bold'),
                fg='#e74c3c', bg='#ecf0f1').pack(pady=(0, 20))

        # Yeni risk butonu
        new_btn = tk.Button(left_panel, text=f" {self.lm.tr('new_risk_btn', 'Yeni Risk')}", font=('Segoe UI', 10, 'bold'),
                           fg='white', bg='#e74c3c', relief='flat', cursor='hand2',
                           command=self.create_new_risk)
        new_btn.pack(fill='x', pady=(0, 10))

        # Risk listesi
        risk_columns = ('risk', 'category', 'impact', 'probability', 'score')
        self.risks_tree = ttk.Treeview(left_panel, columns=risk_columns, show='headings', height=15)

        risk_headers = {
            'risk': self.lm.tr('col_risk', 'Risk'),
            'category': self.lm.tr('col_category', 'Kategori'),
            'impact': self.lm.tr('col_impact', 'Etki'),
            'probability': self.lm.tr('col_probability', 'Olasılık'),
            'score': self.lm.tr('col_score', 'Skor')
        }

        for col in risk_columns:
            self.risks_tree.heading(col, text=risk_headers[col])
            self.risks_tree.column(col, width=90)

        risks_scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=self.risks_tree.yview)
        self.risks_tree.configure(yscrollcommand=risks_scrollbar.set)

        self.risks_tree.pack(side="left", fill="both", expand=True)
        risks_scrollbar.pack(side="right", fill="y")

        self.risks_tree.bind('<<TreeviewSelect>>', self.on_risk_select)

        # Risk detayları
        tk.Label(right_panel, text=f" {self.lm.tr('risk_details_title', 'Risk Detayları')}", font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='white').pack(pady=(0, 20))

        detail_frame = tk.Frame(right_panel, bg='#f8f9fa', relief='solid', bd=1)
        detail_frame.pack(fill='both', expand=True)

        self.risk_detail_text = scrolledtext.ScrolledText(detail_frame, height=15, bg='white',
                                                         font=('Segoe UI', 10), wrap='word', state='disabled')
        self.risk_detail_text.pack(fill='both', expand=True, padx=10, pady=10)

    def build_opportunities_panel(self, parent) -> None:
        """Fırsatlar paneli"""
        # Sol panel - Fırsat listesi
        left_panel = tk.Frame(parent, bg='#ecf0f1', width=500)
        left_panel.pack(side='left', fill='y', padx=(10, 5), pady=10)
        left_panel.pack_propagate(False)

        # Sağ panel - Fırsat detayları
        right_panel = tk.Frame(parent, bg='white')
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 10), pady=10)

        tk.Label(left_panel, text=f" {self.lm.tr('opportunities_title', 'Sürdürülebilirlik Fırsatları')}", font=('Segoe UI', 14, 'bold'),
                fg='#27ae60', bg='#ecf0f1').pack(pady=(0, 20))

        # Yeni fırsat butonu
        new_btn = tk.Button(left_panel, text=f" {self.lm.tr('new_opportunity_btn', 'Yeni Fırsat')}", font=('Segoe UI', 10, 'bold'),
                           fg='white', bg='#27ae60', relief='flat', cursor='hand2',
                           command=self.create_new_opportunity)
        new_btn.pack(fill='x', pady=(0, 10))

        # Fırsat listesi
        opp_columns = ('opportunity', 'category', 'value', 'probability', 'score')
        self.opportunities_tree = ttk.Treeview(left_panel, columns=opp_columns, show='headings', height=15)

        opp_headers = {
            'opportunity': self.lm.tr('col_opportunity', 'Fırsat'),
            'category': self.lm.tr('col_category', 'Kategori'),
            'value': self.lm.tr('col_value', 'Değer'),
            'probability': self.lm.tr('col_probability', 'Olasılık'),
            'score': self.lm.tr('col_score', 'Skor')
        }

        for col in opp_columns:
            self.opportunities_tree.heading(col, text=opp_headers[col])
            self.opportunities_tree.column(col, width=90)

        opp_scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=self.opportunities_tree.yview)
        self.opportunities_tree.configure(yscrollcommand=opp_scrollbar.set)

        self.opportunities_tree.pack(side="left", fill="both", expand=True)
        opp_scrollbar.pack(side="right", fill="y")

        self.opportunities_tree.bind('<<TreeviewSelect>>', self.on_opportunity_select)

        # Fırsat detayları
        tk.Label(right_panel, text=f" {self.lm.tr('opportunity_details_title', 'Fırsat Detayları')}", font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='white').pack(pady=(0, 20))

        detail_frame = tk.Frame(right_panel, bg='#f8f9fa', relief='solid', bd=1)
        detail_frame.pack(fill='both', expand=True)

        self.opportunity_detail_text = scrolledtext.ScrolledText(detail_frame, height=15, bg='white',
                                                               font=('Segoe UI', 10), wrap='word', state='disabled')
        self.opportunity_detail_text.pack(fill='both', expand=True, padx=10, pady=10)

    def create_smart_goals_tab(self) -> None:
        """SMART Hedefler sekmesi"""
        goals_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(goals_frame, text=f" {self.lm.tr('smart_goals_tab', 'SMART Hedefler')}")

        # Sol panel - Hedef listesi
        left_panel = tk.Frame(goals_frame, bg='#ecf0f1', width=500)
        left_panel.pack(side='left', fill='y', padx=(10, 5), pady=10)
        left_panel.pack_propagate(False)

        # Sağ panel - Hedef detayları
        right_panel = tk.Frame(goals_frame, bg='white')
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 10), pady=10)

        self.build_smart_goals_list(left_panel)
        self.build_smart_goals_details(right_panel)

    def build_smart_goals_list(self, parent) -> None:
        """SMART hedefler listesi"""
        tk.Label(parent, text=f" {self.lm.tr('smart_goals_title', 'SMART Hedefler')}", font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='#ecf0f1').pack(pady=(0, 20))

        # Yeni hedef butonu
        new_btn = tk.Button(parent, text=f" {self.lm.tr('new_goal_btn', 'Yeni Hedef')}", font=('Segoe UI', 10, 'bold'),
                           fg='white', bg='#9b59b6', relief='flat', cursor='hand2',
                           command=self.create_new_smart_goal)
        new_btn.pack(fill='x', pady=(0, 10))

        # Hedef listesi
        goal_columns = ('goal', 'category', 'owner', 'progress', 'status')
        self.smart_goals_tree = ttk.Treeview(parent, columns=goal_columns, show='headings', height=15)

        goal_headers = {
            'goal': self.lm.tr('col_goal', 'Hedef'),
            'category': self.lm.tr('col_category', 'Kategori'),
            'owner': self.lm.tr('col_owner', 'Sahibi'),
            'progress': self.lm.tr('col_progress', 'İlerleme'),
            'status': self.lm.tr('col_status', 'Durum')
        }

        for col in goal_columns:
            self.smart_goals_tree.heading(col, text=goal_headers[col])
            self.smart_goals_tree.column(col, width=90)

        goals_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.smart_goals_tree.yview)
        self.smart_goals_tree.configure(yscrollcommand=goals_scrollbar.set)

        self.smart_goals_tree.pack(side="left", fill="both", expand=True)
        goals_scrollbar.pack(side="right", fill="y")

        self.smart_goals_tree.bind('<<TreeviewSelect>>', self.on_smart_goal_select)

    def build_smart_goals_details(self, parent) -> None:
        """SMART hedef detayları"""
        tk.Label(parent, text=f" {self.lm.tr('goal_details_title', 'Hedef Detayları')}", font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='white').pack(pady=(0, 20))

        # Notebook for goal details
        goal_notebook = ttk.Notebook(parent)
        goal_notebook.pack(fill='both', expand=True)

        # Hedef bilgileri sekmesi
        info_frame = tk.Frame(goal_notebook, bg='white')
        goal_notebook.add(info_frame, text=self.lm.tr('goal_info_tab', "Hedef Bilgileri"))

        self.goal_info_text = scrolledtext.ScrolledText(info_frame, height=10, bg='white',
                                                       font=('Segoe UI', 10), wrap='word', state='disabled')
        self.goal_info_text.pack(fill='both', expand=True, padx=10, pady=10)

        # İlerleme takibi sekmesi
        progress_frame = tk.Frame(goal_notebook, bg='white')
        goal_notebook.add(progress_frame, text=self.lm.tr('progress_tracking_tab', "İlerleme Takibi"))

        # İlerleme listesi
        progress_columns = ('date', 'actual', 'target', 'progress_pct', 'variance')
        self.progress_tree = ttk.Treeview(progress_frame, columns=progress_columns, show='headings', height=12)

        progress_headers = {
            'date': self.lm.tr('col_date', 'Tarih'),
            'actual': self.lm.tr('col_actual', 'Gerçekleşen'),
            'target': self.lm.tr('col_target', 'Hedef'),
            'progress_pct': self.lm.tr('col_progress_pct', 'İlerleme %'),
            'variance': self.lm.tr('col_variance', 'Varyans')
        }

        for col in progress_columns:
            self.progress_tree.heading(col, text=progress_headers[col])
            self.progress_tree.column(col, width=100)

        progress_scrollbar = ttk.Scrollbar(progress_frame, orient="vertical", command=self.progress_tree.yview)
        self.progress_tree.configure(yscrollcommand=progress_scrollbar.set)

        self.progress_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        progress_scrollbar.pack(side="right", fill="y")

        # İlerleme ekleme butonu
        add_progress_btn = tk.Button(progress_frame, text=f" {self.lm.tr('add_progress_btn', 'İlerleme Ekle')}", font=('Segoe UI', 10, 'bold'),
                                    fg='white', bg='#3498db', relief='flat', cursor='hand2',
                                    command=self.add_progress_tracking)
        add_progress_btn.pack(pady=10)

    def create_dashboard_tab(self) -> None:
        """Dashboard sekmesi"""
        dashboard_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(dashboard_frame, text=f" {self.lm.tr('dashboard_tab', 'Dashboard')}")

        # Dashboard içeriği
        tk.Label(dashboard_frame, text=f" {self.lm.tr('strategic_dashboard_title', 'Stratejik Dashboard')}", font=('Segoe UI', 16, 'bold'),
                fg='#2c3e50', bg='white').pack(pady=20)

        # İstatistik kartları
        stats_frame = tk.Frame(dashboard_frame, bg='white')
        stats_frame.pack(fill='x', padx=20, pady=20)

        self.stats_cards = {}
        card_configs = [
            ('ceo_messages', self.lm.tr('card_ceo_messages', 'CEO Mesajları'), '#3498db'),
            ('strategies', self.lm.tr('card_active_strategies', 'Aktif Stratejiler'), '#27ae60'),
            ('risks', self.lm.tr('card_active_risks', 'Aktif Riskler'), '#e74c3c'),
            ('opportunities', self.lm.tr('card_active_opportunities', 'Aktif Fırsatlar'), '#f39c12'),
            ('smart_goals', self.lm.tr('card_smart_goals', 'SMART Hedefler'), '#9b59b6')
        ]

        for i, (key, title, color) in enumerate(card_configs):
            card_frame = tk.Frame(stats_frame, bg=color, relief='raised', bd=2)
            card_frame.pack(side='left', fill='x', expand=True, padx=5)

            title_label = tk.Label(card_frame, text=title, font=('Segoe UI', 10, 'bold'),
                                  fg='white', bg=color)
            title_label.pack(pady=(10, 5))

            value_label = tk.Label(card_frame, text="0", font=('Segoe UI', 16, 'bold'),
                                  fg='white', bg=color)
            value_label.pack(pady=(0, 10))

            self.stats_cards[key] = value_label

    def load_initial_data(self) -> None:
        """Başlangıç verilerini yükle"""
        try:
            # Varsayılan verileri oluştur
            self.ceo_manager.create_default_templates()
            self.strategy_manager.create_default_strategy(self.company_id, self.user_id)
            self.risk_manager.create_default_risks_opportunities(self.company_id, self.user_id)
            self.goals_manager.create_default_smart_goals(self.company_id, self.user_id)

            # Verileri yükle
            self.load_ceo_messages()
            self.load_strategies()
            self.load_risks()
            self.load_opportunities()
            self.load_smart_goals()
            self.update_dashboard_stats()

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_loading_data', 'Veri yükleme hatası')}: {e}")

    def load_ceo_messages(self) -> None:
        """CEO mesajlarını yükle"""
        # Ağacı temizle
        for item in self.ceo_tree.get_children():
            self.ceo_tree.delete(item)

        messages = self.ceo_manager.get_messages(self.company_id)

        for message in messages:
            status = "Yayınlandı" if message['is_published'] else "Taslak"
            self.ceo_tree.insert('', 'end', values=(
                message['title'],
                message['message_type'].title(),
                message['year'],
                status
            ))

    def load_strategies(self) -> None:
        """Stratejileri yükle"""
        # Ağacı temizle
        for item in self.strategy_tree.get_children():
            self.strategy_tree.delete(item)

        strategies = self.strategy_manager.get_strategies(self.company_id)

        for strategy in strategies:
            self.strategy_tree.insert('', 'end', values=(
                strategy['strategy_name'],
                strategy['start_year'],
                strategy['end_year'],
                strategy['status'].title()
            ))

    def load_risks(self) -> None:
        """Riskleri yükle"""
        # Ağacı temizle
        for item in self.risks_tree.get_children():
            self.risks_tree.delete(item)

        risks = self.risk_manager.get_risks(self.company_id)

        for risk in risks:
            self.risks_tree.insert('', 'end', values=(
                risk['risk_title'],
                risk['risk_category'].title(),
                risk['impact_level'].title(),
                risk['probability_level'].title(),
                risk['risk_score']
            ))

    def load_opportunities(self) -> None:
        """Fırsatları yükle"""
        # Ağacı temizle
        for item in self.opportunities_tree.get_children():
            self.opportunities_tree.delete(item)

        opportunities = self.risk_manager.get_opportunities(self.company_id)

        for opp in opportunities:
            self.opportunities_tree.insert('', 'end', values=(
                opp['opportunity_title'],
                opp['opportunity_category'].title(),
                opp['potential_value'].title(),
                opp['probability_level'].title(),
                opp['opportunity_score']
            ))

    def load_smart_goals(self) -> None:
        """SMART hedefleri yükle"""
        # Ağacı temizle
        for item in self.smart_goals_tree.get_children():
            self.smart_goals_tree.delete(item)

        goals = self.goals_manager.get_smart_goals(self.company_id)

        for goal in goals:
            progress = f"{goal['progress_percentage']:.1f}%" if goal['progress_percentage'] else "0%"
            self.smart_goals_tree.insert('', 'end', values=(
                goal['goal_title'],
                goal['goal_category'].title(),
                goal['goal_owner'],
                progress,
                goal['status'].title()
            ))

    def update_dashboard_stats(self) -> None:
        """Dashboard istatistiklerini güncelle"""
        try:
            ceo_messages = len(self.ceo_manager.get_messages(self.company_id))
            strategies = len(self.strategy_manager.get_strategies(self.company_id, status='active'))
            risks = len(self.risk_manager.get_risks(self.company_id, status='active'))
            opportunities = len(self.risk_manager.get_opportunities(self.company_id, status='identified'))
            smart_goals = len(self.goals_manager.get_smart_goals(self.company_id, status='active'))

            self.stats_cards['ceo_messages'].config(text=str(ceo_messages))
            self.stats_cards['strategies'].config(text=str(strategies))
            self.stats_cards['risks'].config(text=str(risks))
            self.stats_cards['opportunities'].config(text=str(opportunities))
            self.stats_cards['smart_goals'].config(text=str(smart_goals))

        except Exception as e:
            logging.error(f"Dashboard güncelleme hatası: {e}")

    # Event handlers
    def on_ceo_message_select(self, event) -> None:
        """CEO mesajı seçimi"""
        selection = self.ceo_tree.selection()
        if not selection:
            return

        # Seçilen mesajın bilgilerini al
        item = self.ceo_tree.item(selection[0])
        title = item['values'][0]
        message_type = item['values'][1]
        year = item['values'][2]

        # Mesaj detaylarını veritabanından al
        messages = self.ceo_manager.get_messages(self.company_id)
        selected_message = None

        for message in messages:
            if (message['title'] == title and
                message['message_type'] == message_type.lower() and
                str(message['year']) == year):
                selected_message = message
                break

        if selected_message:
            self.show_ceo_message_details(selected_message)
        else:
            self.ceo_detail_text.config(state='normal')
            self.ceo_detail_text.delete(1.0, tk.END)
            self.ceo_detail_text.insert(1.0, "Mesaj detayları bulunamadı...")
            self.ceo_detail_text.config(state='disabled')

    def show_ceo_message_details(self, message) -> None:
        """CEO mesajı detaylarını göster"""
        try:
            # Detay metnini oluştur
            detail_parts = []

            detail_parts.append(f"=== {message['title'].upper()} ===")
            detail_parts.append(f"Tür: {message['message_type'].title()}")
            detail_parts.append(f"Yıl: {message['year']}")
            if message['quarter']:
                detail_parts.append(f"Çeyrek: {message['quarter']}")
            detail_parts.append(f"Durum: {'Yayınlandı' if message['is_published'] else 'Taslak'}")
            detail_parts.append(f"Oluşturulma: {message['created_at']}")
            if message['updated_at']:
                detail_parts.append(f"Güncellenme: {message['updated_at']}")
            detail_parts.append("")

            # Mesaj içeriği
            if message['content']:
                detail_parts.append("=== MESAJ İÇERİĞİ ===")
                detail_parts.append(message['content'])
                detail_parts.append("")

            # Ana başarılar
            if message['key_achievements']:
                detail_parts.append("=== ANA BAŞARILAR ===")
                for i, achievement in enumerate(message['key_achievements'], 1):
                    detail_parts.append(f"{i}. {achievement}")
                detail_parts.append("")

            # Zorluklar
            if message['challenges']:
                detail_parts.append("=== KARŞILAŞILAN ZORLUKLAR ===")
                for i, challenge in enumerate(message['challenges'], 1):
                    detail_parts.append(f"{i}. {challenge}")
                detail_parts.append("")

            # Gelecek taahhütleri
            if message['future_commitments']:
                detail_parts.append("=== GELECEK TAAHHÜTLERİ ===")
                for i, commitment in enumerate(message['future_commitments'], 1):
                    detail_parts.append(f"{i}. {commitment}")
                detail_parts.append("")

            # İmza bilgileri
            if message['signature_name'] or message['signature_title']:
                detail_parts.append("=== İMZA ===")
                if message['signature_name']:
                    detail_parts.append(message['signature_name'])
                if message['signature_title']:
                    detail_parts.append(message['signature_title'])
                if message['signature_date']:
                    detail_parts.append(f"Tarih: {message['signature_date']}")

            # Detayları göster
            detail_text = '\n'.join(detail_parts)
            self.ceo_detail_text.config(state='normal')
            self.ceo_detail_text.delete(1.0, tk.END)
            self.ceo_detail_text.insert(1.0, detail_text)
            self.ceo_detail_text.config(state='disabled')

        except Exception as e:
            self.ceo_detail_text.config(state='normal')
            self.ceo_detail_text.delete(1.0, tk.END)
            self.ceo_detail_text.insert(1.0, f"Detay gösterimi hatası: {e}")
            self.ceo_detail_text.config(state='disabled')

    def on_strategy_select(self, event) -> None:
        """Strateji seçimi"""
        selection = self.strategy_tree.selection()
        if not selection:
            return

        # Strateji detaylarını göster (basit versiyon)
        self.strategy_info_text.config(state='normal')
        self.strategy_info_text.delete(1.0, tk.END)
        self.strategy_info_text.insert(1.0, "Strateji detayları burada gösterilecek...")
        self.strategy_info_text.config(state='disabled')

        # Hedefleri yükle
        for item in self.goals_tree.get_children():
            self.goals_tree.delete(item)

        # Örnek hedefler
        sample_goals = [
            ("Karbon Emisyon Azaltma", "Çevresel", "2028", "Aktif"),
            ("İş Güvenliği", "Sosyal", "2028", "Aktif"),
            ("Enerji Verimliliği", "Çevresel", "2028", "Aktif")
        ]

        for goal in sample_goals:
            self.goals_tree.insert('', 'end', values=goal)

    def on_risk_select(self, event) -> None:
        """Risk seçimi"""
        selection = self.risks_tree.selection()
        if not selection:
            return

        # Risk detaylarını göster (basit versiyon)
        self.risk_detail_text.config(state='normal')
        self.risk_detail_text.delete(1.0, tk.END)
        self.risk_detail_text.insert(1.0, "Risk detayları burada gösterilecek...")
        self.risk_detail_text.config(state='disabled')

    def on_opportunity_select(self, event) -> None:
        """Fırsat seçimi"""
        selection = self.opportunities_tree.selection()
        if not selection:
            return

        # Fırsat detaylarını göster (basit versiyon)
        self.opportunity_detail_text.config(state='normal')
        self.opportunity_detail_text.delete(1.0, tk.END)
        self.opportunity_detail_text.insert(1.0, "Fırsat detayları burada gösterilecek...")
        self.opportunity_detail_text.config(state='disabled')

    def on_smart_goal_select(self, event) -> None:
        """SMART hedef seçimi"""
        selection = self.smart_goals_tree.selection()
        if not selection:
            return

        # Hedef detaylarını göster (basit versiyon)
        self.goal_info_text.config(state='normal')
        self.goal_info_text.delete(1.0, tk.END)
        self.goal_info_text.insert(1.0, "SMART hedef detayları burada gösterilecek...")
        self.goal_info_text.config(state='disabled')

        # İlerleme kayıtlarını yükle
        for item in self.progress_tree.get_children():
            self.progress_tree.delete(item)

        # Örnek ilerleme kayıtları
        sample_progress = [
            ("2024-01", "120", "100", "80%", "-20"),
            ("2024-02", "110", "100", "90%", "-10"),
            ("2024-03", "105", "100", "95%", "-5")
        ]

        for progress in sample_progress:
            self.progress_tree.insert('', 'end', values=progress)

    # Yeni kayıt oluşturma metodları (basit versiyonlar)
    def create_new_ceo_message(self) -> None:
        """Yeni CEO mesajı oluştur"""
        try:
            show_ceo_message_dialog(
                parent=self.parent,
                company_id=self.company_id,
                user_id=self.user_id,
                on_save=self.on_ceo_message_saved
            )
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_open_ceo_dialog', 'CEO mesajı dialog\'u açılamadı')}: {e}")

    def on_ceo_message_saved(self) -> None:
        """CEO mesajı kaydedildiğinde"""
        self.load_ceo_messages()
        self.update_dashboard_stats()
        messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('success_ceo_msg_created', "CEO mesajı başarıyla oluşturuldu!"))

    def create_new_strategy(self) -> None:
        """Yeni strateji oluştur"""
        try:
            # Strateji oluşturma dialog'u
            dialog = StrategyCreationDialog(
                parent=self.parent,
                company_id=self.company_id,
                user_id=self.user_id,
                strategy_manager=self.strategy_manager,
                on_save=self.on_strategy_saved
            )
            dialog.show()
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_open_strategy_dialog', 'Strateji oluşturma dialog\'u açılamadı')}: {e}")

    def on_strategy_saved(self) -> None:
        """Strateji kaydedildiğinde"""
        self.load_strategies()
        self.update_dashboard_stats()
        messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('success_strategy_created', "Yeni strateji başarıyla oluşturuldu!"))

    def create_new_risk(self) -> None:
        """Yeni risk oluştur"""
        try:
            # Basit risk oluşturma dialog'u
            risk_data = self.show_risk_creation_dialog()
            if risk_data:
                # Risk oluştur
                risk_id = self.risk_manager.create_risk(
                    company_id=self.company_id,
                    risk_title=risk_data['title'],
                    risk_category=risk_data['category'],
                    risk_description=risk_data['description'],
                    impact_level=risk_data['impact'],
                    probability_level=risk_data['probability'],
                    mitigation_measures=risk_data['mitigation'],
                    created_by=self.user_id
                )

                if risk_id:
                    messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{self.lm.tr('success_risk_created', 'Risk başarıyla oluşturuldu!')}\nID: {risk_id}")
                    self.load_risks()
                    self.update_dashboard_stats()
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_risk_creation', 'Risk oluşturma hatası')}: {e}")

    def show_risk_creation_dialog(self) -> None:
        """Risk oluşturma dialog'u"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(f" {self.lm.tr('new_risk_title', 'Yeni Risk Oluştur')}")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        dialog.configure(bg='#f8f9fa')
        dialog.transient(self.parent)
        dialog.grab_set()

        # Form alanları
        main_frame = tk.Frame(dialog, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        tk.Label(main_frame, text=f" {self.lm.tr('new_risk_title', 'Yeni Risk Oluştur')}", font=('Segoe UI', 14, 'bold'),
                fg='#e74c3c', bg='#f8f9fa').pack(pady=(0, 20))

        # Risk Başlığı
        tk.Label(main_frame, text=f"{self.lm.tr('lbl_risk_title', 'Risk Başlığı')} *", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        title_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=title_var, font=('Segoe UI', 10), width=50).pack(anchor='w', pady=(0, 15))

        # Kategori
        tk.Label(main_frame, text=f"{self.lm.tr('lbl_category', 'Kategori')} *", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(main_frame, textvariable=category_var,
                                     values=[
                                         self.lm.tr('cat_environmental', 'Çevresel'),
                                         self.lm.tr('cat_social', 'Sosyal'),
                                         self.lm.tr('cat_economic', 'Ekonomik'),
                                         self.lm.tr('cat_governance', 'Yönetişim'),
                                         self.lm.tr('cat_operational', 'Operasyonel')
                                     ],
                                     width=47)
        category_combo.pack(anchor='w', pady=(0, 15))

        # Etki Seviyesi
        tk.Label(main_frame, text=f"{self.lm.tr('lbl_impact_level', 'Etki Seviyesi')} *", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        impact_var = tk.StringVar()
        impact_combo = ttk.Combobox(main_frame, textvariable=impact_var,
                                   values=[
                                       self.lm.tr('level_low', 'Düşük'),
                                       self.lm.tr('level_medium', 'Orta'),
                                       self.lm.tr('level_high', 'Yüksek'),
                                       self.lm.tr('level_critical', 'Kritik')
                                   ],
                                   width=47)
        impact_combo.pack(anchor='w', pady=(0, 15))

        # Olasılık Seviyesi
        tk.Label(main_frame, text=f"{self.lm.tr('lbl_probability_level', 'Olasılık Seviyesi')} *", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        probability_var = tk.StringVar()
        probability_combo = ttk.Combobox(main_frame, textvariable=probability_var,
                                        values=[
                                            self.lm.tr('level_low', 'Düşük'),
                                            self.lm.tr('level_medium', 'Orta'),
                                            self.lm.tr('level_high', 'Yüksek'),
                                            self.lm.tr('level_very_high', 'Çok Yüksek')
                                        ],
                                        width=47)
        probability_combo.pack(anchor='w', pady=(0, 15))

        # Açıklama
        tk.Label(main_frame, text=self.lm.tr('lbl_risk_description', "Risk Açıklaması"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        description_text = scrolledtext.ScrolledText(main_frame, height=4, font=('Segoe UI', 10), wrap='word')
        description_text.pack(anchor='w', pady=(0, 15), fill='x')

        # Azaltma Önlemleri
        tk.Label(main_frame, text=self.lm.tr('lbl_mitigation_measures', "Azaltma Önlemleri"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        mitigation_text = scrolledtext.ScrolledText(main_frame, height=3, font=('Segoe UI', 10), wrap='word')
        mitigation_text.pack(anchor='w', pady=(0, 20), fill='x')

        # Sonuç
        result = {'cancelled': True}

        def save_risk() -> None:
            if not title_var.get().strip():
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('error_risk_title_required', "Risk başlığı zorunludur!"))
                return

            result.update({
                'cancelled': False,
                'title': title_var.get().strip(),
                'category': category_var.get().lower() if category_var.get() else 'diğer',
                'description': description_text.get(1.0, tk.END).strip(),
                'impact': impact_var.get().lower() if impact_var.get() else 'orta',
                'probability': probability_var.get().lower() if probability_var.get() else 'orta',
                'mitigation': mitigation_text.get(1.0, tk.END).strip()
            })
            dialog.destroy()

        # Butonlar
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(fill='x', pady=(0, 10))

        tk.Button(button_frame, text=f" {self.lm.tr('btn_cancel', 'İptal')}", font=('Segoe UI', 10, 'bold'),
                 fg='white', bg='#e74c3c', relief='flat', cursor='hand2',
                 command=dialog.destroy).pack(side='right', padx=(10, 0))

        tk.Button(button_frame, text=f" {self.lm.tr('btn_save', 'Kaydet')}", font=('Segoe UI', 10, 'bold'),
                 fg='white', bg='#27ae60', relief='flat', cursor='hand2',
                 command=save_risk).pack(side='right')

        dialog.wait_window()
        return None if result['cancelled'] else result

    def create_new_opportunity(self) -> None:
        """Yeni fırsat oluştur"""
        try:
            # Basit fırsat oluşturma dialog'u
            opportunity_data = self.show_opportunity_creation_dialog()
            if opportunity_data:
                # Fırsat oluştur
                opportunity_id = self.risk_manager.create_opportunity(
                    company_id=self.company_id,
                    opportunity_title=opportunity_data['title'],
                    opportunity_category=opportunity_data['category'],
                    opportunity_description=opportunity_data['description'],
                    potential_value=opportunity_data['value'],
                    probability_level=opportunity_data['probability'],
                    implementation_plan=opportunity_data['plan'],
                    created_by=self.user_id
                )

                if opportunity_id:
                    messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{self.lm.tr('success_opportunity_created', 'Fırsat başarıyla oluşturuldu!')}\nID: {opportunity_id}")
                    self.load_opportunities()
                    self.update_dashboard_stats()
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_opportunity_creation', 'Fırsat oluşturma hatası')}: {e}")

    def show_opportunity_creation_dialog(self) -> None:
        """Fırsat oluşturma dialog'u"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(f" {self.lm.tr('new_opportunity_title', 'Yeni Fırsat Oluştur')}")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        dialog.configure(bg='#f8f9fa')
        dialog.transient(self.parent)
        dialog.grab_set()

        # Form alanları
        main_frame = tk.Frame(dialog, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        tk.Label(main_frame, text=f" {self.lm.tr('new_opportunity_title', 'Yeni Fırsat Oluştur')}", font=('Segoe UI', 14, 'bold'),
                fg='#27ae60', bg='#f8f9fa').pack(pady=(0, 20))

        # Fırsat Başlığı
        tk.Label(main_frame, text=f"{self.lm.tr('lbl_opportunity_title', 'Fırsat Başlığı')} *", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        title_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=title_var, font=('Segoe UI', 10), width=50).pack(anchor='w', pady=(0, 15))

        # Kategori
        tk.Label(main_frame, text=f"{self.lm.tr('lbl_category', 'Kategori')} *", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(main_frame, textvariable=category_var,
                                     values=[
                                         self.lm.tr('cat_environmental', 'Çevresel'),
                                         self.lm.tr('cat_social', 'Sosyal'),
                                         self.lm.tr('cat_economic', 'Ekonomik'),
                                         self.lm.tr('cat_technological', 'Teknolojik'),
                                         self.lm.tr('cat_marketing', 'Pazarlama')
                                     ],
                                     width=47)
        category_combo.pack(anchor='w', pady=(0, 15))

        # Potansiyel Değer
        tk.Label(main_frame, text=f"{self.lm.tr('lbl_potential_value', 'Potansiyel Değer')} *", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        value_var = tk.StringVar()
        value_combo = ttk.Combobox(main_frame, textvariable=value_var,
                                  values=[
                                      self.lm.tr('level_low', 'Düşük'),
                                      self.lm.tr('level_medium', 'Orta'),
                                      self.lm.tr('level_high', 'Yüksek'),
                                      self.lm.tr('level_very_high', 'Çok Yüksek')
                                  ],
                                  width=47)
        value_combo.pack(anchor='w', pady=(0, 15))

        # Olasılık Seviyesi
        tk.Label(main_frame, text=f"{self.lm.tr('lbl_probability_level', 'Olasılık Seviyesi')} *", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        probability_var = tk.StringVar()
        probability_combo = ttk.Combobox(main_frame, textvariable=probability_var,
                                        values=[
                                            self.lm.tr('level_low', 'Düşük'),
                                            self.lm.tr('level_medium', 'Orta'),
                                            self.lm.tr('level_high', 'Yüksek'),
                                            self.lm.tr('level_very_high', 'Çok Yüksek')
                                        ],
                                        width=47)
        probability_combo.pack(anchor='w', pady=(0, 15))

        # Açıklama
        tk.Label(main_frame, text=self.lm.tr('lbl_opportunity_description', "Fırsat Açıklaması"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        description_text = scrolledtext.ScrolledText(main_frame, height=4, font=('Segoe UI', 10), wrap='word')
        description_text.pack(anchor='w', pady=(0, 15), fill='x')

        # Uygulama Planı
        tk.Label(main_frame, text=self.lm.tr('lbl_implementation_plan', "Uygulama Planı"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        plan_text = scrolledtext.ScrolledText(main_frame, height=3, font=('Segoe UI', 10), wrap='word')
        plan_text.pack(anchor='w', pady=(0, 20), fill='x')

        # Sonuç
        result = {'cancelled': True}

        def save_opportunity() -> None:
            if not title_var.get().strip():
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('error_opportunity_title_required', "Fırsat başlığı zorunludur!"))
                return

            result.update({
                'cancelled': False,
                'title': title_var.get().strip(),
                'category': category_var.get().lower() if category_var.get() else 'diğer',
                'description': description_text.get(1.0, tk.END).strip(),
                'value': value_var.get().lower() if value_var.get() else 'orta',
                'probability': probability_var.get().lower() if probability_var.get() else 'orta',
                'plan': plan_text.get(1.0, tk.END).strip()
            })
            dialog.destroy()

        # Butonlar
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(fill='x', pady=(0, 10))

        tk.Button(button_frame, text=f" {self.lm.tr('btn_cancel', 'İptal')}", font=('Segoe UI', 10, 'bold'),
                 fg='white', bg='#e74c3c', relief='flat', cursor='hand2',
                 command=dialog.destroy).pack(side='right', padx=(10, 0))

        tk.Button(button_frame, text=f" {self.lm.tr('btn_save', 'Kaydet')}", font=('Segoe UI', 10, 'bold'),
                 fg='white', bg='#27ae60', relief='flat', cursor='hand2',
                 command=save_opportunity).pack(side='right')

        dialog.wait_window()
        return None if result['cancelled'] else result

    def create_new_smart_goal(self) -> None:
        """Yeni SMART hedef oluştur"""
        try:
            # Basit SMART hedef oluşturma dialog'u
            goal_data = self.show_smart_goal_creation_dialog()
            if goal_data:
                # SMART hedef oluştur
                goal_id = self.goals_manager.create_smart_goal(
                    company_id=self.company_id,
                    goal_title=goal_data['title'],
                    goal_category=goal_data['category'],
                    goal_description=goal_data['description'],
                    specific=goal_data['specific'],
                    measurable=goal_data['measurable'],
                    achievable=goal_data['achievable'],
                    relevant=goal_data['relevant'],
                    time_bound=goal_data['time_bound'],
                    goal_owner=goal_data['owner'],
                    target_value=goal_data['target_value'],
                    unit=goal_data['unit'],
                    created_by=self.user_id
                )

                if goal_id:
                    messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{self.lm.tr('success_smart_goal_created', 'SMART hedef başarıyla oluşturuldu!')}\nID: {goal_id}")
                    self.load_smart_goals()
                    self.update_dashboard_stats()
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_smart_goal_creation', 'SMART hedef oluşturma hatası')}: {e}")

    def show_smart_goal_creation_dialog(self) -> None:
        """SMART hedef oluşturma dialog'u"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(f" {self.lm.tr('new_smart_goal_title', 'Yeni SMART Hedef Oluştur')}")
        dialog.geometry("600x700")
        dialog.resizable(False, False)
        dialog.configure(bg='#f8f9fa')
        dialog.transient(self.parent)
        dialog.grab_set()

        # Form alanları
        main_frame = tk.Frame(dialog, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        tk.Label(main_frame, text=f" {self.lm.tr('new_smart_goal_title', 'Yeni SMART Hedef Oluştur')}", font=('Segoe UI', 14, 'bold'),
                fg='#9b59b6', bg='#f8f9fa').pack(pady=(0, 20))

        # Hedef Başlığı
        tk.Label(main_frame, text=f"{self.lm.tr('lbl_goal_title', 'Hedef Başlığı')} *", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        title_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=title_var, font=('Segoe UI', 10), width=60).pack(anchor='w', pady=(0, 15))

        # Kategori
        tk.Label(main_frame, text=f"{self.lm.tr('lbl_category', 'Kategori')} *", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(main_frame, textvariable=category_var,
                                     values=[
                                         self.lm.tr('cat_environmental', 'Çevresel'),
                                         self.lm.tr('cat_social', 'Sosyal'),
                                         self.lm.tr('cat_economic', 'Ekonomik'),
                                         self.lm.tr('cat_governance', 'Yönetişim'),
                                         self.lm.tr('cat_operational', 'Operasyonel')
                                     ],
                                     width=57)
        category_combo.pack(anchor='w', pady=(0, 15))

        # Hedef Sahibi
        tk.Label(main_frame, text=f"{self.lm.tr('lbl_goal_owner', 'Hedef Sahibi')} *", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        owner_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=owner_var, font=('Segoe UI', 10), width=60).pack(anchor='w', pady=(0, 15))

        # Hedef Değeri
        value_frame = tk.Frame(main_frame, bg='#f8f9fa')
        value_frame.pack(anchor='w', pady=(0, 15), fill='x')

        tk.Label(value_frame, text=self.lm.tr('lbl_target_value', "Hedef Değeri"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(side='left')

        target_value_var = tk.StringVar()
        tk.Entry(value_frame, textvariable=target_value_var, font=('Segoe UI', 10), width=20).pack(side='left', padx=(10, 5))

        tk.Label(value_frame, text=self.lm.tr('lbl_unit', "Birim"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(side='left', padx=(10, 0))

        unit_var = tk.StringVar()
        unit_combo = ttk.Combobox(value_frame, textvariable=unit_var,
                                 values=['%', 'adet', 'TL', 'kg', 'm²', 'saat', 'gün'],
                                 width=15)
        unit_combo.pack(side='left', padx=(10, 0))

        # SMART Kriterleri
        tk.Label(main_frame, text=self.lm.tr('lbl_smart_criteria', "SMART Kriterleri"), font=('Segoe UI', 12, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(20, 10))

        # Specific (Spesifik)
        tk.Label(main_frame, text=self.lm.tr('lbl_smart_specific', "S - Spesifik (Ne yapılacak?)"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        specific_text = scrolledtext.ScrolledText(main_frame, height=2, font=('Segoe UI', 10), wrap='word')
        specific_text.pack(anchor='w', pady=(0, 10), fill='x')

        # Measurable (Ölçülebilir)
        tk.Label(main_frame, text=self.lm.tr('lbl_smart_measurable', "M - Ölçülebilir (Nasıl ölçülecek?)"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        measurable_text = scrolledtext.ScrolledText(main_frame, height=2, font=('Segoe UI', 10), wrap='word')
        measurable_text.pack(anchor='w', pady=(0, 10), fill='x')

        # Achievable (Ulaşılabilir)
        tk.Label(main_frame, text=self.lm.tr('lbl_smart_achievable', "A - Ulaşılabilir (Gerçekçi mi?)"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        achievable_text = scrolledtext.ScrolledText(main_frame, height=2, font=('Segoe UI', 10), wrap='word')
        achievable_text.pack(anchor='w', pady=(0, 10), fill='x')

        # Relevant (İlgili)
        tk.Label(main_frame, text=self.lm.tr('lbl_smart_relevant', "R - İlgili (Neden önemli?)"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        relevant_text = scrolledtext.ScrolledText(main_frame, height=2, font=('Segoe UI', 10), wrap='word')
        relevant_text.pack(anchor='w', pady=(0, 10), fill='x')

        # Time-bound (Zaman Sınırlı)
        tk.Label(main_frame, text=self.lm.tr('lbl_smart_time_bound', "T - Zaman Sınırlı (Ne zaman?)"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        time_bound_text = scrolledtext.ScrolledText(main_frame, height=2, font=('Segoe UI', 10), wrap='word')
        time_bound_text.pack(anchor='w', pady=(0, 15), fill='x')

        # Açıklama
        tk.Label(main_frame, text=self.lm.tr('lbl_general_description', "Genel Açıklama"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        description_text = scrolledtext.ScrolledText(main_frame, height=3, font=('Segoe UI', 10), wrap='word')
        description_text.pack(anchor='w', pady=(0, 20), fill='x')

        # Sonuç
        result = {'cancelled': True}

        def save_goal() -> None:
            if not title_var.get().strip():
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('error_goal_title_required', "Hedef başlığı zorunludur!"))
                return

            result.update({
                'cancelled': False,
                'title': title_var.get().strip(),
                'category': category_var.get().lower() if category_var.get() else 'diğer',
                'owner': owner_var.get().strip(),
                'target_value': target_value_var.get().strip(),
                'unit': unit_var.get().strip(),
                'specific': specific_text.get(1.0, tk.END).strip(),
                'measurable': measurable_text.get(1.0, tk.END).strip(),
                'achievable': achievable_text.get(1.0, tk.END).strip(),
                'relevant': relevant_text.get(1.0, tk.END).strip(),
                'time_bound': time_bound_text.get(1.0, tk.END).strip(),
                'description': description_text.get(1.0, tk.END).strip()
            })
            dialog.destroy()

        # Butonlar
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(fill='x', pady=(0, 10))

        tk.Button(button_frame, text=f" {self.lm.tr('btn_cancel', 'İptal')}", font=('Segoe UI', 10, 'bold'),
                 fg='white', bg='#e74c3c', relief='flat', cursor='hand2',
                 command=dialog.destroy).pack(side='right', padx=(10, 0))

        tk.Button(button_frame, text=f" {self.lm.tr('btn_save', 'Kaydet')}", font=('Segoe UI', 10, 'bold'),
                 fg='white', bg='#27ae60', relief='flat', cursor='hand2',
                 command=save_goal).pack(side='right')

        dialog.wait_window()
        return None if result['cancelled'] else result

    def add_progress_tracking(self) -> None:
        """İlerleme takibi ekle"""
        try:
            # Hedef seçimi dialog'u
            goal_data = self.show_goal_selection_dialog()
            if goal_data:
                # İlerleme ekleme dialog'u
                progress_data = self.show_progress_tracking_dialog(goal_data)
                if progress_data:
                    # İlerleme kaydını oluştur
                    progress_id = self.goals_manager.add_progress_tracking(
                        goal_id=goal_data['id'],
                        reporting_period=progress_data['period'],
                        actual_value=progress_data['actual_value'],
                        target_value=progress_data['target_value'],
                        progress_narrative=progress_data['narrative'],
                        challenges=progress_data['challenges'],
                        actions_taken=progress_data['actions'],
                        next_steps=progress_data['next_steps'],
                        reported_by=self.user_id
                    )

                    if progress_id:
                        messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{self.lm.tr('success_progress_added', 'İlerleme kaydı başarıyla eklendi!')}\nID: {progress_id}")
                        self.load_smart_goals()
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_add_progress', 'İlerleme takibi ekleme hatası')}: {e}")

    def show_goal_selection_dialog(self) -> None:
        """Hedef seçimi dialog'u"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(f" {self.lm.tr('select_goal_title', 'Hedef Seç')}")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.configure(bg='#f8f9fa')
        dialog.transient(self.parent)
        dialog.grab_set()

        main_frame = tk.Frame(dialog, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(main_frame, text=f" {self.lm.tr('select_goal_for_progress', 'İlerleme Takibi için Hedef Seç')}", font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(pady=(0, 20))

        # Hedef listesi
        goals = self.goals_manager.get_smart_goals(self.company_id, status='active')

        if not goals:
            tk.Label(main_frame, text=self.lm.tr('no_active_goals', "Aktif hedef bulunamadı!"), font=('Segoe UI', 12),
                    fg='#e74c3c', bg='#f8f9fa').pack(pady=50)
            tk.Button(main_frame, text=f" {self.lm.tr('btn_close', 'Kapat')}", font=('Segoe UI', 10, 'bold'),
                     fg='white', bg='#e74c3c', relief='flat', cursor='hand2',
                     command=dialog.destroy).pack(pady=20)
            dialog.wait_window()
            return None

        # Hedef listesi
        goal_columns = ('Hedef', 'Kategori', 'Sahibi', 'İlerleme')
        goals_tree = ttk.Treeview(main_frame, columns=goal_columns, show='headings', height=10)
        
        # Sütun başlıkları
        goal_headers = {
            'Hedef': self.lm.tr('col_goal', 'Hedef'),
            'Kategori': self.lm.tr('col_category', 'Kategori'),
            'Sahibi': self.lm.tr('col_owner', 'Sahibi'),
            'İlerleme': self.lm.tr('col_progress', 'İlerleme')
        }

        for col in goal_columns:
            goals_tree.heading(col, text=goal_headers.get(col, col))
            goals_tree.column(col, width=100)

        goals_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=goals_tree.yview)
        goals_tree.configure(yscrollcommand=goals_scrollbar.set)

        goals_tree.pack(side="left", fill="both", expand=True)
        goals_scrollbar.pack(side="right", fill="y")

        # Hedefleri yükle
        for goal in goals:
            progress = f"{goal['progress_percentage']:.1f}%" if goal['progress_percentage'] else "0%"
            goals_tree.insert('', 'end', values=(
                goal['goal_title'],
                goal['goal_category'].title(),
                goal['goal_owner'],
                progress
            ), tags=(goal['id'],))

        result = {'cancelled': True, 'id': None}

        def select_goal() -> None:
            selection = goals_tree.selection()
            if selection:
                item = goals_tree.item(selection[0])
                goal_id = int(item['tags'][0])
                result.update({'cancelled': False, 'id': goal_id})
                dialog.destroy()
            else:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('warning_select_goal', "Lütfen bir hedef seçin!"))

        # Butonlar
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(fill='x', pady=(20, 0))

        tk.Button(button_frame, text=f" {self.lm.tr('btn_cancel', 'İptal')}", font=('Segoe UI', 10, 'bold'),
                 fg='white', bg='#e74c3c', relief='flat', cursor='hand2',
                 command=dialog.destroy).pack(side='right', padx=(10, 0))

        tk.Button(button_frame, text=f" {self.lm.tr('btn_select', 'Seç')}", font=('Segoe UI', 10, 'bold'),
                 fg='white', bg='#27ae60', relief='flat', cursor='hand2',
                 command=select_goal).pack(side='right')

        dialog.wait_window()
        return None if result['cancelled'] else {'id': result['id']}

    def show_progress_tracking_dialog(self, goal_data) -> None:
        """İlerleme takibi dialog'u"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(f" {self.lm.tr('add_progress_title', 'İlerleme Takibi Ekle')}")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        dialog.configure(bg='#f8f9fa')
        dialog.transient(self.parent)
        dialog.grab_set()

        main_frame = tk.Frame(dialog, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(main_frame, text=f" {self.lm.tr('add_progress_title', 'İlerleme Takibi Ekle')}", font=('Segoe UI', 14, 'bold'),
                fg='#3498db', bg='#f8f9fa').pack(pady=(0, 20))

        # Raporlama Dönemi
        tk.Label(main_frame, text=f"{self.lm.tr('lbl_reporting_period', 'Raporlama Dönemi')} *", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        period_var = tk.StringVar()
        period_combo = ttk.Combobox(main_frame, textvariable=period_var,
                                   values=['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06',
                                          '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12'],
                                   width=47)
        period_combo.pack(anchor='w', pady=(0, 15))

        # Gerçekleşen Değer
        tk.Label(main_frame, text=f"{self.lm.tr('lbl_actual_value', 'Gerçekleşen Değer')} *", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        actual_value_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=actual_value_var, font=('Segoe UI', 10), width=50).pack(anchor='w', pady=(0, 15))

        # Hedef Değer
        tk.Label(main_frame, text=self.lm.tr('lbl_target_value', "Hedef Değer"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        target_value_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=target_value_var, font=('Segoe UI', 10), width=50).pack(anchor='w', pady=(0, 15))

        # İlerleme Açıklaması
        tk.Label(main_frame, text=self.lm.tr('lbl_progress_narrative', "İlerleme Açıklaması"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        narrative_text = scrolledtext.ScrolledText(main_frame, height=3, font=('Segoe UI', 10), wrap='word')
        narrative_text.pack(anchor='w', pady=(0, 15), fill='x')

        # Zorluklar
        tk.Label(main_frame, text=self.lm.tr('lbl_challenges', "Karşılaşılan Zorluklar"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        challenges_text = scrolledtext.ScrolledText(main_frame, height=2, font=('Segoe UI', 10), wrap='word')
        challenges_text.pack(anchor='w', pady=(0, 15), fill='x')

        # Alınan Aksiyonlar
        tk.Label(main_frame, text=self.lm.tr('lbl_actions_taken', "Alınan Aksiyonlar"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        actions_text = scrolledtext.ScrolledText(main_frame, height=2, font=('Segoe UI', 10), wrap='word')
        actions_text.pack(anchor='w', pady=(0, 15), fill='x')

        # Sonraki Adımlar
        tk.Label(main_frame, text=self.lm.tr('lbl_next_steps', "Sonraki Adımlar"), font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', pady=(0, 5))
        next_steps_text = scrolledtext.ScrolledText(main_frame, height=2, font=('Segoe UI', 10), wrap='word')
        next_steps_text.pack(anchor='w', pady=(0, 20), fill='x')

        result = {'cancelled': True}

        def save_progress() -> None:
            if not period_var.get().strip() or not actual_value_var.get().strip():
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('error_period_actual_required', "Raporlama dönemi ve gerçekleşen değer zorunludur!"))
                return

            try:
                actual_value = float(actual_value_var.get())
                target_value = float(target_value_var.get()) if target_value_var.get().strip() else None
            except ValueError:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('error_invalid_numeric', "Geçersiz sayısal değer!"))
                return

            result.update({
                'cancelled': False,
                'period': period_var.get().strip(),
                'actual_value': actual_value,
                'target_value': target_value,
                'narrative': narrative_text.get(1.0, tk.END).strip(),
                'challenges': [line.strip() for line in challenges_text.get(1.0, tk.END).strip().split('\n') if line.strip()],
                'actions': [line.strip() for line in actions_text.get(1.0, tk.END).strip().split('\n') if line.strip()],
                'next_steps': [line.strip() for line in next_steps_text.get(1.0, tk.END).strip().split('\n') if line.strip()]
            })
            dialog.destroy()

        # Butonlar
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(fill='x', pady=(0, 10))

        tk.Button(button_frame, text=f" {self.lm.tr('btn_cancel', 'İptal')}", font=('Segoe UI', 10, 'bold'),
                 fg='white', bg='#e74c3c', relief='flat', cursor='hand2',
                 command=dialog.destroy).pack(side='right', padx=(10, 0))

        tk.Button(button_frame, text=f" {self.lm.tr('btn_save', 'Kaydet')}", font=('Segoe UI', 10, 'bold'),
                 fg='white', bg='#27ae60', relief='flat', cursor='hand2',
                 command=save_progress).pack(side='right')

        dialog.wait_window()
        return None if result['cancelled'] else result


if __name__ == "__main__":
    # Test
    root = tk.Tk()
    root.title("Stratejik Modüller Test")
    root.geometry("1400x900")

    gui = StrategicGUI(root, company_id=1, user_id=1)

    root.mainloop()
