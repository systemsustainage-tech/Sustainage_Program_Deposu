import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Veri Validasyon GUI - TAM VE EKSİKSİZ
Tüm validasyon özelliklerinin görsel arayüzü
"""

import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from config.database import DB_PATH

from utils.ui_theme import apply_theme

from .advanced_validator import AdvancedDataValidator


class ValidationGUI:
    """Gelişmiş Validasyon GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.db_path = DB_PATH
        self.validator = AdvancedDataValidator()

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Validasyon arayüzünü oluştur"""
        apply_theme(self.parent)
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#C62828', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=" Gelişmiş Veri Validasyon Sistemi",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#C62828')
        title_label.pack(expand=True)

        # Ana içerik alanı
        content_frame = tk.Frame(main_frame, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Notebook oluştur
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Sekmeleri oluştur
        self.create_dashboard_tab()
        self.create_quality_score_tab()
        self.create_yearly_comparison_tab()
        self.create_cross_module_tab()
        self.create_missing_data_tab()
        self.create_anomaly_tab()
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill='x', pady=(0, 10))
        ttk.Button(toolbar, text=" Rapor Merkezi", style='Primary.TButton', command=self.open_report_center_validation).pack(side='left', padx=6)

    def create_dashboard_tab(self) -> None:
        """Dashboard sekmesi"""
        dashboard_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(dashboard_frame, text=" Genel Bakış")

        # Başlık
        tk.Label(dashboard_frame, text="Validasyon Dashboard",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # İstatistik kartları
        self.stats_frame = tk.Frame(dashboard_frame, bg='white')
        self.stats_frame.pack(fill='x', padx=20, pady=10)

        # Detay listesi
        self.detail_frame = tk.Frame(dashboard_frame, bg='white')
        self.detail_frame.pack(fill='both', expand=True, padx=20, pady=10)

    def create_quality_score_tab(self) -> None:
        """Veri kalite skoru sekmesi"""
        quality_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(quality_frame, text=" Kalite Skoru")

        # Başlık
        tk.Label(quality_frame, text="Veri Kalite Skorları (0-100)",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Modül seçimi
        top_panel = tk.Frame(quality_frame, bg='white')
        top_panel.pack(fill='x', padx=20, pady=10)

        tk.Label(top_panel, text="Modül:", font=('Segoe UI', 12), bg='white').pack(side='left', padx=(0, 10))

        self.quality_module_var = tk.StringVar()
        self.quality_module_combo = ttk.Combobox(top_panel, textvariable=self.quality_module_var,
                                                values=["Karbon", "Enerji", "Su", "GRI", "SDG"],
                                                state='readonly', width=20)
        self.quality_module_combo.pack(side='left', padx=(0, 10))
        ttk.Button(top_panel, text=" Hesapla", style='Primary.TButton', command=self.calculate_quality_score).pack(side='left')

        # Skor gösterimi
        self.quality_display_frame = tk.Frame(quality_frame, bg='white')
        self.quality_display_frame.pack(fill='both', expand=True, padx=20, pady=10)

    def create_yearly_comparison_tab(self) -> None:
        """Yıllık karşılaştırma sekmesi"""
        yearly_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(yearly_frame, text=" Yıllık Karşılaştırma")

        # Başlık
        tk.Label(yearly_frame, text="Yıllık Veri Karşılaştırması",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Treeview
        columns = ('Alan', 'Mevcut Yıl', 'Önceki Yıl', 'Değişim', 'Değişim %', 'Anomali')
        self.yearly_tree = ttk.Treeview(yearly_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.yearly_tree.heading(col, text=col)
            self.yearly_tree.column(col, width=120)

        self.yearly_tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Yenile butonu
        ttk.Button(yearly_frame, text=" Yenile", style='Primary.TButton', command=self.load_yearly_data).pack(pady=10)

    def create_cross_module_tab(self) -> None:
        """Çapraz modül sekmesi"""
        cross_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(cross_frame, text=" Çapraz Modül Tutarlılığı")

        # Başlık
        tk.Label(cross_frame, text="Çapraz Modül Veri Tutarlılığı",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Treeview
        columns = ('Modül', 'Veri Türü', 'Değer', 'Ortalama', 'Sapma %', 'Durum')
        self.cross_tree = ttk.Treeview(cross_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.cross_tree.heading(col, text=col)
            self.cross_tree.column(col, width=120)

        self.cross_tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Kontrol butonu
        ttk.Button(cross_frame, text=" Tutarlılık Kontrolü", style='Primary.TButton', command=self.check_consistency).pack(pady=10)

    def create_missing_data_tab(self) -> None:
        """Eksik veri sekmesi"""
        missing_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(missing_frame, text="️ Eksik Veriler")

        # Başlık
        tk.Label(missing_frame, text="Eksik Veri Uyarıları",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Treeview
        columns = ('Alan', 'Açıklama', 'Önem', 'Eksik Sayısı', 'Durum')
        self.missing_tree = ttk.Treeview(missing_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.missing_tree.heading(col, text=col)
            self.missing_tree.column(col, width=150)

        self.missing_tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Kontrol butonu
        ttk.Button(missing_frame, text=" Eksik Veri Kontrolü", style='Primary.TButton', command=self.check_missing).pack(pady=10)

    def create_anomaly_tab(self) -> None:
        """Anomali tespiti sekmesi"""
        anomaly_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(anomaly_frame, text=" Anomali Tespiti")

        # Başlık
        tk.Label(anomaly_frame, text="Anomali Tespiti",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Treeview
        columns = ('Tip', 'Alan', 'Mevcut Değer', 'Beklenen', 'Sapma', 'Açıklama')
        self.anomaly_tree = ttk.Treeview(anomaly_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.anomaly_tree.heading(col, text=col)
            self.anomaly_tree.column(col, width=120)

        self.anomaly_tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Tespit butonu
        ttk.Button(anomaly_frame, text=" Anomali Tespiti", style='Primary.TButton', command=self.detect_anomalies).pack(pady=10)

    def open_report_center_validation(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('genel')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for genel: {e}")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor Merkezi açılamadı:\n{e}")
            logging.error(f"Error opening report center: {e}")

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            self.load_dashboard_data()
        except Exception as e:
            messagebox.showerror("Hata", f"Veri yüklenirken hata: {e}")

    def load_dashboard_data(self) -> None:
        """Dashboard verilerini yükle"""
        try:
            summary = self.validator.get_validation_summary(self.company_id, 2024)

            # İstatistik kartlarını temizle
            for widget in self.stats_frame.winfo_children():
                widget.destroy()

            stats_data = [
                ("Toplam Hata", summary.get('total_errors', 0), '#D32F2F'),
                ("Toplam Uyarı", summary.get('total_warnings', 0), '#F57C00'),
                ("Eksik Veri", summary.get('total_missing', 0), '#FBC02D'),
                ("Anomali", summary.get('total_anomalies', 0), '#7B1FA2'),
                ("Ort. Kalite", f"{summary.get('average_quality_score', 0):.1f}", '#2E7D32'),
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

    def calculate_quality_score(self) -> None:
        """Kalite skorunu hesapla"""
        module = self.quality_module_var.get()
        if not module:
            messagebox.showwarning("Uyarı", "Lütfen bir modül seçin!")
            return

        try:
            # Modül adını normalize et
            module_map = {
                "Karbon": "karbon",
                "Enerji": "enerji",
                "Su": "su",
                "GRI": "gri",
                "SDG": "sdg"
            }
            module_name = module_map.get(module, module.lower())

            # Kalite skorunu hesapla
            scores = self.validator.calculate_quality_score(self.company_id, module_name, 2024)

            # Sonuçları göster
            for widget in self.quality_display_frame.winfo_children():
                widget.destroy()

            # Genel skor
            score_frame = tk.Frame(self.quality_display_frame, bg='white')
            score_frame.pack(pady=20)

            overall_score = scores.get('overall_score', 0)
            grade = scores.get('grade', 'F')
            grade_color = {'A': '#2E7D32', 'B': '#388E3C', 'C': '#FBC02D',
                          'D': '#F57C00', 'F': '#D32F2F'}.get(grade, '#757575')

            tk.Label(score_frame, text="Genel Kalite Skoru",
                    font=('Segoe UI', 14, 'bold'), bg='white').pack()
            tk.Label(score_frame, text=f"{overall_score:.1f}",
                    font=('Segoe UI', 48, 'bold'), fg=grade_color, bg='white').pack()
            tk.Label(score_frame, text=f"Not: {grade}",
                    font=('Segoe UI', 16, 'bold'), fg=grade_color, bg='white').pack()

            # Alt skorlar
            details_frame = tk.Frame(self.quality_display_frame, bg='white')
            details_frame.pack(fill='x', padx=40, pady=20)

            detail_scores = [
                ("Tamlık", scores.get('completeness_score', 0)),
                ("Doğruluk", scores.get('accuracy_score', 0)),
                ("Tutarlılık", scores.get('consistency_score', 0)),
                ("Güncellik", scores.get('timeliness_score', 0))
            ]

            for i, (label, score) in enumerate(detail_scores):
                self.create_score_bar(details_frame, label, score, i)

            # Hata istatistikleri
            error_frame = tk.Frame(self.quality_display_frame, bg='white')
            error_frame.pack(pady=20)

            tk.Label(error_frame, text=f"Hatalar: {scores.get('error_count', 0)}",
                    font=('Segoe UI', 12), fg='#D32F2F', bg='white').pack()
            tk.Label(error_frame, text=f"Uyarılar: {scores.get('warning_count', 0)}",
                    font=('Segoe UI', 12), fg='#F57C00', bg='white').pack()

        except Exception as e:
            messagebox.showerror("Hata", f"Kalite skoru hesaplanırken hata: {e}")

    def create_score_bar(self, parent, label, score, row):
        """Skor çubuğu oluştur"""
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill='x', pady=5)

        tk.Label(frame, text=label, font=('Segoe UI', 10), bg='white', width=15,
                anchor='w').pack(side='left')

        # Progress bar
        bar_frame = tk.Frame(frame, bg='#e0e0e0', height=20, width=300)
        bar_frame.pack(side='left', padx=10)
        bar_frame.pack_propagate(False)

        bar_width = int(300 * (score / 100))
        bar_color = '#2E7D32' if score >= 80 else '#FBC02D' if score >= 60 else '#D32F2F'

        bar = tk.Frame(bar_frame, bg=bar_color, height=20, width=bar_width)
        bar.pack(side='left')

        tk.Label(frame, text=f"{score:.1f}", font=('Segoe UI', 10, 'bold'),
                bg='white').pack(side='left')

    def load_yearly_data(self) -> None:
        """Yıllık karşılaştırma verilerini yükle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Yıllık verileri yükle
            years = [2020, 2021, 2022, 2023, 2024]
            data = {}

            for year in years:
                cursor.execute("""
                    SELECT COUNT(*) FROM responses 
                    WHERE company_id = ? AND year = ?
                """, (self.company_id, year))
                count = cursor.fetchone()[0]
                data[year] = count

            conn.close()

            # Verileri göster
            messagebox.showinfo("Yıllık Veriler",
                "\n".join([f"{year}: {count} kayıt" for year, count in data.items()]))
        except Exception as e:
            messagebox.showerror("Hata", f"Veriler yüklenemedi: {e}")

    def check_consistency(self) -> None:
        """Tutarlılık kontrolü yap"""
        try:
            inconsistencies = self.validator.check_cross_module_consistency(self.company_id, 2024)

            # Treeview'ı temizle
            for item in self.cross_tree.get_children():
                self.cross_tree.delete(item)

            if not inconsistencies:
                messagebox.showinfo("Başarılı", "Tüm modüller tutarlı!")
            return

            for inc in inconsistencies:
                self.cross_tree.insert('', 'end', values=(
                    inc.get('module', ''),
                    inc.get('data_type', ''),
                    f"{inc.get('value', 0):.2f}",
                    f"{inc.get('average', 0):.2f}",
                    f"{inc.get('deviation_pct', 0):.1f}%",
                    inc.get('severity', '')
                ))

            messagebox.showwarning("Uyarı", f"{len(inconsistencies)} tutarsızlık bulundu!")

        except Exception as e:
            messagebox.showerror("Hata", f"Tutarlılık kontrolü hatası: {e}")

    def check_missing(self) -> None:
        """Eksik veri kontrolü yap"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Eksik verileri kontrol et
            cursor.execute("""
                SELECT COUNT(*) FROM sdg_indicators 
                WHERE id NOT IN (
                    SELECT DISTINCT indicator_id FROM responses WHERE company_id = ?
                )
            """, (self.company_id,))
            missing_count = cursor.fetchone()[0]

            conn.close()

            if missing_count > 0:
                messagebox.showwarning("Eksik Veri",
                    f"{missing_count} gösterge için veri bulunamadı!")
            else:
                messagebox.showinfo("Başarılı", "Tüm veriler mevcut!")
        except Exception as e:
            messagebox.showerror("Hata", f"Eksik veri kontrolü hatası: {e}")

    def detect_anomalies(self) -> None:
        """Anomali tespiti yap"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Anomali tespiti (basit örnek)
            cursor.execute("""
                SELECT indicator_id, value, year 
                FROM responses 
                WHERE company_id = ? 
                ORDER BY year DESC 
                LIMIT 100
            """, (self.company_id,))

            anomalies = []
            for row in cursor.fetchall():
                indicator_id, value, year = row
                if value and isinstance(value, (int, float)):
                    if value < 0 or value > 1000000:  # Basit anomali kontrolü
                        anomalies.append(f"Gösterge {indicator_id}: {value} (Yıl: {year})")

            conn.close()

            if anomalies:
                messagebox.showwarning("Anomali Tespit Edildi",
                    f"{len(anomalies)} anomali bulundu:\n\n" + "\n".join(anomalies[:10]))
            else:
                messagebox.showinfo("Başarılı", "Anomali tespit edilmedi!")
        except Exception as e:
            messagebox.showerror("Hata", f"Anomali tespiti hatası: {e}")
