#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
İleri Seviye Materialite Analizi GUI
Paydaş önceliklendirme, işletme etkisi değerlendirmesi, matris görselleştirme
"""

import logging
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .advanced_materiality_analyzer import AdvancedMaterialityAnalyzer
from config.icons import Icons


class AdvancedMaterialityGUI:
    """İleri Seviye Materialite Analizi GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.analyzer = AdvancedMaterialityAnalyzer()

        # Matplotlib Türkçe font ayarları
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Segoe UI', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Ana arayüzü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Başlık
        header_frame = tk.Frame(main_frame, bg='#8e44ad', height=70)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text=" İleri Seviye Materialite Analizi",
                              font=('Segoe UI', 18, 'bold'), fg='white', bg='#8e44ad')
        title_label.pack(side='left', padx=20, pady=15)

        subtitle_label = tk.Label(header_frame, text="Paydaş Önceliklendirme & İşletme Etkisi Değerlendirmesi",
                                 font=('Segoe UI', 11), fg='#f4ecf7', bg='#8e44ad')
        subtitle_label.pack(side='left')

        # Yıl seçimi
        year_frame = tk.Frame(header_frame, bg='#8e44ad')
        year_frame.pack(side='right', padx=20, pady=15)

        tk.Label(year_frame, text="Değerlendirme Yılı:", font=('Segoe UI', 10, 'bold'),
                fg='white', bg='#8e44ad').pack(side='left')

        self.year_var = tk.StringVar(value=str(datetime.now().year))
        year_combo = ttk.Combobox(year_frame, textvariable=self.year_var, width=8,
                                 values=[str(year) for year in range(2020, 2030)])
        year_combo.pack(side='left', padx=(10, 0))
        year_combo.bind('<<ComboboxSelected>>', self.on_year_changed)

        # Ana notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Sekmeleri oluştur
        self.create_overview_tab()
        self.create_stakeholder_prioritization_tab()
        self.create_business_impact_tab()
        self.create_materiality_matrix_tab()
        self.create_automatic_topics_tab()
        self.create_annual_update_tab()

    def create_overview_tab(self) -> None:
        """Genel bakış sekmesi"""
        overview_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(overview_frame, text=" Genel Bakış")

        # Dashboard kartları
        self.create_dashboard_cards(overview_frame)

        # Materialite özeti
        self.create_materiality_summary(overview_frame)

    def create_dashboard_cards(self, parent) -> None:
        """Dashboard kartlarını oluştur"""
        cards_frame = tk.Frame(parent, bg='white')
        cards_frame.pack(fill='x', padx=20, pady=20)

        # KPI kartları
        kpi_cards = [
            ("Toplam Konu", "12", "#3498db", ""),
            ("Yüksek Materialite", "5", "#e74c3c", ""),
            ("Orta Materialite", "4", "#f39c12", ""),
            ("Düşük Materialite", "3", "#27ae60", ""),
            ("Paydaş Skoru", "7.8", "#9b59b6", ""),
            ("İşletme Etkisi", "6.9", "#e67e22", "")
        ]

        for i, (title, value, color, icon) in enumerate(kpi_cards):
            card = tk.Frame(cards_frame, bg=color, relief='raised', bd=2)
            card.pack(side='left', fill='x', expand=True, padx=5)

            # İkon ve başlık
            header_frame = tk.Frame(card, bg=color)
            header_frame.pack(fill='x', padx=10, pady=(10, 5))

            tk.Label(header_frame, text=icon, font=('Segoe UI', 16),
                    bg=color, fg='white').pack(side='left')
            tk.Label(header_frame, text=title, font=('Segoe UI', 10, 'bold'),
                    bg=color, fg='white').pack(side='left', padx=(5, 0))

            # Değer
            tk.Label(card, text=value, font=('Segoe UI', 20, 'bold'),
                    bg=color, fg='white').pack(pady=(0, 10))

    def create_materiality_summary(self, parent) -> None:
        """Materialite özetini oluştur"""
        summary_frame = tk.LabelFrame(parent, text="Materialite Özeti",
                                     font=('Segoe UI', 12, 'bold'), bg='white')
        summary_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Özet tablosu
        columns = ('Konu', 'Paydaş Skoru', 'İşletme Etkisi', 'Materialite Seviyesi', 'Quadrant')

        self.summary_tree = ttk.Treeview(summary_frame, columns=columns, show='headings', height=8)

        for col in columns:
            self.summary_tree.heading(col, text=col)
            self.summary_tree.column(col, width=150, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(summary_frame, orient='vertical', command=self.summary_tree.yview)
        self.summary_tree.configure(yscrollcommand=scrollbar.set)

        self.summary_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')

    def create_stakeholder_prioritization_tab(self) -> None:
        """Paydaş önceliklendirme sekmesi"""
        stakeholder_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(stakeholder_frame, text=" Paydaş Önceliklendirme")

        # Başlık
        title_frame = tk.Frame(stakeholder_frame, bg='#3498db', height=50)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="Paydaş Önceliklendirme Skorları",
                font=('Segoe UI', 14, 'bold'), fg='white', bg='#3498db').pack(expand=True)

        # Paydaş ağırlık tablosu
        self.create_stakeholder_weights_table(stakeholder_frame)

        # Paydaş skor grafiği
        self.create_stakeholder_scores_chart(stakeholder_frame)

    def create_stakeholder_weights_table(self, parent) -> None:
        """Paydaş ağırlık tablosunu oluştur"""
        weights_frame = tk.LabelFrame(parent, text="Paydaş Ağırlıkları",
                                     font=('Segoe UI', 12, 'bold'), bg='white')
        weights_frame.pack(fill='x', padx=20, pady=20)

        # Tablo
        columns = ('Paydaş Tipi', 'Ağırlık', 'Etki Seviyesi', 'Etkileşim Sıklığı', 'Temel Skor')

        self.weights_tree = ttk.Treeview(weights_frame, columns=columns, show='headings', height=6)

        for col in columns:
            self.weights_tree.heading(col, text=col)
            self.weights_tree.column(col, width=120, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(weights_frame, orient='vertical', command=self.weights_tree.yview)
        self.weights_tree.configure(yscrollcommand=scrollbar.set)

        self.weights_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')

    def create_stakeholder_scores_chart(self, parent) -> None:
        """Paydaş skor grafiğini oluştur"""
        chart_frame = tk.LabelFrame(parent, text="Paydaş Skor Dağılımı",
                                   font=('Segoe UI', 12, 'bold'), bg='white')
        chart_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Matplotlib grafik
        fig, ax = plt.subplots(figsize=(10, 6))

        # Örnek veriler
        stakeholder_types = ['Müşteriler', 'Çalışanlar', 'Yatırımcılar', 'Tedarikçiler',
                           'Yerel Toplum', 'Regülatörler', 'Medya', 'Sivil Toplum']
        scores = [8.5, 8.2, 7.8, 7.1, 6.5, 8.9, 6.2, 5.8]
        colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']

        bars = ax.bar(stakeholder_types, scores, color=colors)
        ax.set_title('Paydaş Önceliklendirme Skorları', fontsize=14, fontweight='bold')
        ax.set_ylabel('Skor (1-10)', fontsize=12)
        ax.set_xlabel('Paydaş Tipi', fontsize=12)
        ax.set_ylim(0, 10)

        # Değerleri çubukların üzerine yaz
        for bar, score in zip(bars, scores):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                   f'{score:.1f}', ha='center', va='bottom', fontweight='bold')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Tkinter'a entegre et
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def create_business_impact_tab(self) -> None:
        """İşletme etkisi sekmesi"""
        impact_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(impact_frame, text=" İşletme Etkisi")

        # Başlık
        title_frame = tk.Frame(impact_frame, bg='#e67e22', height=50)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="İşletme Etkisi Değerlendirmesi",
                font=('Segoe UI', 14, 'bold'), fg='white', bg='#e67e22').pack(expand=True)

        # Etki kategorileri
        self.create_impact_categories(impact_frame)

        # Etki skor grafiği
        self.create_impact_scores_chart(impact_frame)

    def create_impact_categories(self, parent) -> None:
        """Etki kategorilerini oluştur"""
        categories_frame = tk.LabelFrame(parent, text="Etki Kategorileri",
                                        font=('Segoe UI', 12, 'bold'), bg='white')
        categories_frame.pack(fill='x', padx=20, pady=20)

        # Örnek etki faktörleri
        impact_factors = [
            ("Finansal Etki", "9.2", "#e74c3c", Icons.MONEY_BAG, "Gelir, maliyet, karlılık"),
            ("Operasyonel Etki", "8.5", "#3498db", Icons.SETTINGS, "Verimlilik, süreklilik, kalite"),
            ("İtibar Etkisi", "8.1", "#9b59b6", Icons.STAR, "Marka, güven, şeffaflık"),
            ("Yasal Uyum", "9.5", "#2ecc71", Icons.Law if hasattr(Icons, 'Law') else Icons.INFO, "Regülasyonlar, cezalar")
        ]

        for i, (title, score, color, icon, description) in enumerate(impact_factors):
            card = tk.Frame(categories_frame, bg=color, relief='raised', bd=2)
            card.pack(side='left', fill='x', expand=True, padx=5, pady=10)

            # İkon ve başlık
            header_frame = tk.Frame(card, bg=color)
            header_frame.pack(fill='x', padx=10, pady=(10, 5))

            tk.Label(header_frame, text=icon, font=('Segoe UI', 16),
                    bg=color, fg='white').pack(side='left')
            tk.Label(header_frame, text=title, font=('Segoe UI', 10, 'bold'),
                    bg=color, fg='white').pack(side='left', padx=(5, 0))

            # Skor
            tk.Label(card, text=score, font=('Segoe UI', 18, 'bold'),
                    bg=color, fg='white').pack(pady=(0, 5))

            # Açıklama
            tk.Label(card, text=description, font=('Segoe UI', 8),
                    bg=color, fg='#ecf0f1', wraplength=120).pack(pady=(0, 10))

    def create_impact_scores_chart(self, parent) -> None:
        """Etki skor grafiğini oluştur"""
        chart_frame = tk.LabelFrame(parent, text="Etki Skor Dağılımı",
                                   font=('Segoe UI', 12, 'bold'), bg='white')
        chart_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Matplotlib grafik
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

        # Radar chart için veriler
        categories = ['Finansal', 'Operasyonel', 'İtibar', 'Regülatif']
        scores = [7.2, 6.8, 8.1, 7.5]

        # Radar chart
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        radar_scores = scores + scores[:1]  # Kapatmak için
        radar_angles = angles + angles[:1]

        ax1.plot(radar_angles, radar_scores, 'o-', linewidth=2, color='#e67e22')
        ax1.fill(radar_angles, radar_scores, alpha=0.25, color='#e67e22')
        ax1.set_xticks(angles)
        ax1.set_xticklabels(categories)
        ax1.set_ylim(0, 10)
        ax1.set_title('Etki Kategorileri Radar Grafiği', fontweight='bold')
        ax1.grid(True)

        # Bar chart
        colors = ['#e74c3c', '#f39c12', '#9b59b6', '#34495e']
        bars = ax2.bar(categories, scores, color=colors)
        ax2.set_title('Etki Kategorileri Bar Grafiği', fontweight='bold')
        ax2.set_ylabel('Skor (1-10)')
        ax2.set_ylim(0, 10)

        # Değerleri çubukların üzerine yaz
        for bar, score in zip(bars, scores):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{score:.1f}', ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()

        # Tkinter'a entegre et
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def create_materiality_matrix_tab(self) -> None:
        """Materialite matrisi sekmesi"""
        matrix_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(matrix_frame, text=" Materialite Matrisi")

        # Başlık
        title_frame = tk.Frame(matrix_frame, bg='#27ae60', height=50)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="Materialite Matrisi Görselleştirmesi",
                font=('Segoe UI', 14, 'bold'), fg='white', bg='#27ae60').pack(expand=True)

        # Matris grafiği
        self.create_materiality_matrix_chart(matrix_frame)

        # Quadrant dağılımı
        self.create_quadrant_distribution(matrix_frame)

    def create_materiality_matrix_chart(self, parent) -> None:
        """Materialite matrisi grafiğini oluştur"""
        chart_frame = tk.LabelFrame(parent, text="Materialite Matrisi",
                                   font=('Segoe UI', 12, 'bold'), bg='white')
        chart_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Matplotlib grafik
        fig, ax = plt.subplots(figsize=(10, 8))

        # Verileri al
        try:
            year = int(self.year_var.get()) if self.year_var.get() else datetime.now().year
            # Veritabanından verileri çekmeyi dene
            try:
                result = self.analyzer.generate_materiality_matrix(self.company_id, year)
                matrix_data = result.get('matrix_data', [])
            except Exception:
                matrix_data = []

            if matrix_data:
                topics = [d['topic_name'] for d in matrix_data]
                stakeholder_priority = [float(d['stakeholder_priority']) for d in matrix_data]
                business_impact = [float(d['business_impact']) for d in matrix_data]
            else:
                # Veri yoksa örnek veriler göster (Demo Modu)
                topics = ['Veri Gizliliği', 'Çevresel Etki', 'İş Sağlığı', 'Müşteri Memnuniyeti',
                         'Tedarik Zinciri', 'Enerji Verimliliği', 'Sosyal Sorumluluk', 'Finansal Şeffaflık']
                stakeholder_priority = [8.2, 7.5, 8.8, 9.1, 6.8, 7.2, 6.5, 8.5]
                business_impact = [8.5, 8.9, 7.8, 8.2, 7.1, 6.8, 6.2, 8.7]

        except Exception as e:
            logging.error(f"Veri hazırlama hatası: {e}")
            # Hata durumunda güvenli varsayılanlar
            topics = ['Örnek Konu']
            stakeholder_priority = [5.0]
            business_impact = [5.0]

        # Boyut kontrolü ve eşitleme (Hata önleme)
        min_len = min(len(topics), len(stakeholder_priority), len(business_impact))
        if min_len == 0:
            topics = ['Veri Yok']
            stakeholder_priority = [0]
            business_impact = [0]
            min_len = 1
        else:
            topics = topics[:min_len]
            stakeholder_priority = stakeholder_priority[:min_len]
            business_impact = business_impact[:min_len]

        # Renkler (materialite seviyesine göre)
        colors = []
        for i in range(min_len):
            avg_score = (stakeholder_priority[i] + business_impact[i]) / 2
            if avg_score >= 7.5:
                colors.append('#e74c3c')  # Yüksek - Kırmızı
            elif avg_score >= 5.0:
                colors.append('#f39c12')  # Orta - Turuncu
            else:
                colors.append('#27ae60')  # Düşük - Yeşil

        # Scatter plot
        try:
            ax.scatter(stakeholder_priority, business_impact, c=colors, s=200, alpha=0.7, edgecolors='black')

            # Konu isimlerini ekle
            for i, topic in enumerate(topics):
                ax.annotate(topic, (stakeholder_priority[i], business_impact[i]),
                           xytext=(5, 5), textcoords='offset points', fontsize=9, fontweight='bold')
        except Exception as e:
            logging.error(f"Plot çizim hatası: {e}")
            ax.text(5, 5, "Grafik çizilemedi", ha='center')

        # Quadrant çizgileri
        ax.axhline(y=5, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=5, color='gray', linestyle='--', alpha=0.5)

        # Quadrant etiketleri
        ax.text(7.5, 8.5, 'Yüksek Öncelik', fontsize=12, fontweight='bold',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='#e74c3c', alpha=0.7))
        ax.text(2.5, 8.5, 'Paydaş Odaklı', fontsize=12, fontweight='bold',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='#f39c12', alpha=0.7))
        ax.text(7.5, 2.5, 'İşletme Odaklı', fontsize=12, fontweight='bold',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='#9b59b6', alpha=0.7))
        ax.text(2.5, 2.5, 'Düşük Öncelik', fontsize=12, fontweight='bold',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='#27ae60', alpha=0.7))

        ax.set_xlabel('Paydaş Önceliği', fontsize=12, fontweight='bold')
        ax.set_ylabel('İşletme Etkisi', fontsize=12, fontweight='bold')
        ax.set_title(f'Materialite Matrisi ({self.year_var.get()})', fontsize=14, fontweight='bold')
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.grid(True, alpha=0.3)

        # Legend
        legend_elements = [
            plt.scatter([], [], c='#e74c3c', s=100, label='Yüksek Materialite'),
            plt.scatter([], [], c='#f39c12', s=100, label='Orta Materialite'),
            plt.scatter([], [], c='#27ae60', s=100, label='Düşük Materialite')
        ]
        ax.legend(handles=legend_elements, loc='upper right')

        plt.tight_layout()

        # Tkinter'a entegre et
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)


    def create_quadrant_distribution(self, parent) -> None:
        """Quadrant dağılımını oluştur"""
        distribution_frame = tk.LabelFrame(parent, text="Quadrant Dağılımı",
                                          font=('Segoe UI', 12, 'bold'), bg='white')
        distribution_frame.pack(fill='x', padx=20, pady=(0, 20))

        # Quadrant kartları
        quadrants = [
            ("Yüksek Öncelik", "3", "#e74c3c", ""),
            ("Paydaş Odaklı", "2", "#f39c12", ""),
            ("İşletme Odaklı", "2", "#9b59b6", ""),
            ("Düşük Öncelik", "1", "#27ae60", "")
        ]

        for i, (title, count, color, icon) in enumerate(quadrants):
            card = tk.Frame(distribution_frame, bg=color, relief='raised', bd=2)
            card.pack(side='left', fill='x', expand=True, padx=5, pady=10)

            # İkon ve başlık
            header_frame = tk.Frame(card, bg=color)
            header_frame.pack(fill='x', padx=10, pady=(10, 5))

            tk.Label(header_frame, text=icon, font=('Segoe UI', 16),
                    bg=color, fg='white').pack(side='left')
            tk.Label(header_frame, text=title, font=('Segoe UI', 10, 'bold'),
                    bg=color, fg='white').pack(side='left', padx=(5, 0))

            # Sayı
            tk.Label(card, text=count, font=('Segoe UI', 18, 'bold'),
                    bg=color, fg='white').pack(pady=(0, 10))

    def create_automatic_topics_tab(self) -> None:
        """Otomatik konu belirleme sekmesi"""
        topics_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(topics_frame, text=" Otomatik Konu Belirleme")

        # Başlık
        title_frame = tk.Frame(topics_frame, bg='#9b59b6', height=50)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="Otomatik Materialite Konu Belirleme",
                font=('Segoe UI', 14, 'bold'), fg='white', bg='#9b59b6').pack(expand=True)

        # Sektör seçimi
        sector_frame = tk.Frame(topics_frame, bg='white')
        sector_frame.pack(fill='x', padx=20, pady=20)

        tk.Label(sector_frame, text="Sektör:", font=('Segoe UI', 12, 'bold')).pack(side='left')

        self.sector_var = tk.StringVar(value="Teknoloji")
        sector_combo = ttk.Combobox(sector_frame, textvariable=self.sector_var, width=15,
                                   values=["Teknoloji", "Üretim", "Finans", "Hizmet", "Enerji"])
        sector_combo.pack(side='left', padx=(10, 0))

        # Önerilen konular
        self.create_recommended_topics(topics_frame)

    def create_recommended_topics(self, parent) -> None:
        """Önerilen konuları oluştur"""
        topics_frame = tk.LabelFrame(parent, text="Önerilen Materialite Konuları",
                                    font=('Segoe UI', 12, 'bold'), bg='white')
        topics_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Konu listesi
        topics_listbox = tk.Listbox(topics_frame, font=('Segoe UI', 10), height=12)
        topics_listbox.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(topics_frame, orient='vertical', command=topics_listbox.yview)
        topics_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # Örnek konular
        sample_topics = [
            "Veri Gizliliği ve Güvenliği",
            "Yapay Zeka Etik Kuralları",
            "Dijital Erişilebilirlik",
            "E-atık Yönetimi",
            "Enerji Verimliliği",
            "İnsan Hakları ve Çalışma Koşulları",
            "Çevresel Etki",
            "İş Sağlığı ve Güvenliği",
            "Tedarik Zinciri Sürdürülebilirliği",
            "Su Yönetimi",
            "Atık Azaltma",
            "Finansal Şeffaflık"
        ]

        for topic in sample_topics:
            topics_listbox.insert(tk.END, f"• {topic}")

    def create_annual_update_tab(self) -> None:
        """Yıllık güncelleme sekmesi"""
        update_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(update_frame, text=" Yıllık Güncelleme")

        # Başlık
        title_frame = tk.Frame(update_frame, bg='#34495e', height=50)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="Yıllık Materialite Güncellemesi",
                font=('Segoe UI', 14, 'bold'), fg='white', bg='#34495e').pack(expand=True)

        # Güncelleme butonları
        self.create_update_buttons(update_frame)

        # Değişiklik analizi
        self.create_change_analysis(update_frame)

    def create_update_buttons(self, parent) -> None:
        """Güncelleme butonlarını oluştur"""
        buttons_frame = tk.Frame(parent, bg='white')
        buttons_frame.pack(fill='x', padx=20, pady=20)

        # Güncelleme butonu
        ttk.Button(buttons_frame, text=" Materialite Güncellemesi Yap",
                   style='Primary.TButton',
                   command=self.run_annual_update).pack(side='left', padx=10)

        # Rapor oluştur butonu
        ttk.Button(buttons_frame, text=" Rapor Oluştur",
                   style='Primary.TButton',
                   command=self.generate_report).pack(side='left', padx=10)

        # Excel export butonu
        ttk.Button(buttons_frame, text=" Excel'e Aktar",
                   style='Primary.TButton',
                   command=self.export_to_excel).pack(side='left', padx=10)

    def create_change_analysis(self, parent) -> None:
        """Değişiklik analizini oluştur"""
        analysis_frame = tk.LabelFrame(parent, text="Değişiklik Analizi",
                                      font=('Segoe UI', 12, 'bold'), bg='white')
        analysis_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Değişiklik tablosu
        columns = ('Konu', 'Önceki Skor', 'Mevcut Skor', 'Değişim', 'Durum')

        self.changes_tree = ttk.Treeview(analysis_frame, columns=columns, show='headings', height=8)

        for col in columns:
            self.changes_tree.heading(col, text=col)
            self.changes_tree.column(col, width=120, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(analysis_frame, orient='vertical', command=self.changes_tree.yview)
        self.changes_tree.configure(yscrollcommand=scrollbar.set)

        self.changes_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            year = int(self.year_var.get())

            # Materialite özetini yükle
            summary = self.analyzer.get_materiality_summary(self.company_id, year)

            # Özet tablosunu güncelle
            self.update_summary_table(summary)

            # Paydaş ağırlıklarını yükle
            self.load_stakeholder_weights()

        except Exception as e:
            logging.error(f"[HATA] Veriler yuklenemedi: {e}")

    def update_summary_table(self, summary: Dict[str, Any]) -> None:
        """Özet tablosunu güncelle"""
        # Mevcut verileri temizle
        for item in self.summary_tree.get_children():
            self.summary_tree.delete(item)

        # Yeni verileri ekle
        for data in summary.get('matrix_data', []):
            self.summary_tree.insert('', 'end', values=(
                data['topic_name'],
                f"{data['stakeholder_priority']:.1f}",
                f"{data['business_impact']:.1f}",
                data['materiality_level'],
                data['quadrant']
            ))

    def load_stakeholder_weights(self) -> None:
        """Paydaş ağırlıklarını yükle"""
        # Mevcut verileri temizle
        for item in self.weights_tree.get_children():
            self.weights_tree.delete(item)

        # Örnek veriler
        sample_weights = [
            ("Müşteriler", "0.25", "Yüksek", "Günlük", "8.5"),
            ("Çalışanlar", "0.20", "Yüksek", "Günlük", "8.2"),
            ("Yatırımcılar", "0.15", "Yüksek", "Aylık", "7.8"),
            ("Tedarikçiler", "0.12", "Orta", "Haftalık", "7.1"),
            ("Yerel Toplum", "0.10", "Orta", "Aylık", "6.5"),
            ("Regülatörler", "0.08", "Yüksek", "Çeyreklik", "8.9")
        ]

        for weight_data in sample_weights:
            self.weights_tree.insert('', 'end', values=weight_data)

    def on_year_changed(self, event=None) -> None:
        """Yıl değiştiğinde çağrılır"""
        self.load_data()

    def run_annual_update(self) -> None:
        """Yıllık güncelleme çalıştır"""
        try:
            year = int(self.year_var.get())
            result = self.analyzer.update_materiality_annually(self.company_id, year)

            if result['update_status'] == 'Başarılı':
                messagebox.showinfo("Başarılı", "Materialite güncellemesi başarıyla tamamlandı!")
                self.load_data()
            else:
                messagebox.showerror("Hata", f"Güncelleme hatası: {result.get('error', 'Bilinmeyen hata')}")

        except Exception as e:
            messagebox.showerror("Hata", f"Güncelleme sırasında hata oluştu: {e}")

    def generate_report(self) -> None:
        """Rapor oluştur"""
        try:
            year = int(self.year_var.get())
            summary = self.analyzer.get_materiality_summary(self.company_id, year)

            # Rapor dosyası yolu
            report_path = f"reports/materiality_report_{year}.txt"

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"MATERIALITE ANALİZİ RAPORU - {year}\n")
                f.write("=" * 50 + "\n\n")

                f.write(f"Toplam Konu Sayısı: {summary['total_topics']}\n")
                f.write(f"Yüksek Materialite: {summary['high_materiality_count']}\n")
                f.write(f"Orta Materialite: {summary['medium_materiality_count']}\n")
                f.write(f"Düşük Materialite: {summary['low_materiality_count']}\n\n")

                f.write("QUADRANT DAĞILIMI:\n")
                for quadrant, count in summary['quadrant_distribution'].items():
                    f.write(f"- {quadrant}: {count}\n")

                f.write("\nDETAYLI ANALİZ:\n")
                for data in summary['matrix_data']:
                    f.write(f"\n{data['topic_name']}:\n")
                    f.write(f"  Paydaş Skoru: {data['stakeholder_priority']:.1f}\n")
                    f.write(f"  İşletme Etkisi: {data['business_impact']:.1f}\n")
                    f.write(f"  Materialite Seviyesi: {data['materiality_level']}\n")
                    f.write(f"  Quadrant: {data['quadrant']}\n")

            messagebox.showinfo("Başarılı", f"Rapor oluşturuldu: {report_path}")

        except Exception as e:
            messagebox.showerror("Hata", f"Rapor oluşturulurken hata oluştu: {e}")

    def export_to_excel(self) -> None:
        """Excel'e aktar"""
        try:
            year = int(self.year_var.get())
            summary = self.analyzer.get_materiality_summary(self.company_id, year)

            # Excel dosyası yolu
            excel_path = f"reports/materiality_analysis_{year}.xlsx"

            import pandas as pd

            # DataFrame oluştur
            df_data = []
            for data in summary['matrix_data']:
                df_data.append({
                    'Konu': data['topic_name'],
                    'Paydaş Skoru': data['stakeholder_priority'],
                    'İşletme Etkisi': data['business_impact'],
                    'Materialite Seviyesi': data['materiality_level'],
                    'Quadrant': data['quadrant']
                })

            df = pd.DataFrame(df_data)
            df.to_excel(excel_path, index=False, engine='openpyxl')

            messagebox.showinfo("Başarılı", f"Excel dosyası oluşturuldu: {excel_path}")

        except Exception as e:
            messagebox.showerror("Hata", f"Excel aktarımında hata oluştu: {e}")
