#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veri Kalite Skorlama Sistemi GUI
0-100 kalite skoru ile veri kalitesini değerlendirme
"""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from utils.language_manager import LanguageManager
from .data_quality_scorer import DataQualityScorer


class DataQualityGUI:
    """Veri kalite skorlama arayüzü"""

    def __init__(self, parent, db_path: str, company_id: int) -> None:
        self.parent = parent
        self.db_path = db_path
        self.company_id = company_id
        self.lm = LanguageManager()
        self.scorer = DataQualityScorer(db_path)

        self.setup_ui()
        self.load_quality_data()

    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        # Başlık
        header = tk.Frame(self.parent, bg='#9b59b6', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(header, text=" Veri Kalite Skorlama Sistemi",
                font=('Segoe UI', 16, 'bold'), fg='white', bg='#9b59b6').pack(side='left', padx=20, pady=20)

        tk.Label(header, text="Veri Tamamlık, Tutarlılık ve Güvenilirlik Analizi",
                font=('Segoe UI', 10), fg='#ecf0f1', bg='#9b59b6').pack(side='left')

        # Kontrol paneli
        control_frame = tk.Frame(self.parent, bg='white')
        control_frame.pack(fill='x', padx=20, pady=15)

        tk.Button(control_frame, text=" Yeniden Hesapla", font=('Segoe UI', 10, 'bold'),
                 bg='#27ae60', fg='white', relief='flat', cursor='hand2',
                 padx=15, pady=8, command=self.recalculate_scores).pack(side='left', padx=5)

        tk.Button(control_frame, text=" Rapor Oluştur", font=('Segoe UI', 10, 'bold'),
                 bg='#3498db', fg='white', relief='flat', cursor='hand2',
                 padx=15, pady=8, command=self.generate_report).pack(side='left', padx=5)

        tk.Button(control_frame, text=" Excel'e Aktar", font=('Segoe UI', 10, 'bold'),
                 bg='#e67e22', fg='white', relief='flat', cursor='hand2',
                 padx=15, pady=8, command=self.export_to_excel).pack(side='left', padx=5)

        # Notebook (Sekmeler)
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Genel Bakış sekmesi
        self.overview_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.overview_frame, text=" Genel Bakış")

        # Modül Bazlı sekmesi
        self.module_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.module_frame, text=" Modül Bazlı")

        # Detaylar sekmesi
        self.details_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.details_frame, text=" Detaylar")

        self.build_overview_tab()
        self.build_module_tab()
        self.build_details_tab()

    def build_overview_tab(self) -> None:
        """Genel bakış sekmesi"""
        # Toplam kalite skoru kartı
        score_frame = tk.Frame(self.overview_frame, bg='white')
        score_frame.pack(fill='x', padx=20, pady=20)

        # Ana skor kartı
        main_card = tk.Frame(score_frame, bg='#9b59b6', relief='raised', bd=3, width=400, height=200)
        main_card.pack(side='left', padx=10)
        main_card.pack_propagate(False)

        tk.Label(main_card, text="TOPLAM VERİ KALİTE SKORU",
                font=('Segoe UI', 12, 'bold'), bg='#9b59b6', fg='white').pack(pady=(20, 10))

        self.total_score_label = tk.Label(main_card, text="0", font=('Segoe UI', 48, 'bold'),
                                          bg='#9b59b6', fg='white')
        self.total_score_label.pack()

        self.score_status_label = tk.Label(main_card, text="/ 100", font=('Segoe UI', 14),
                                           bg='#9b59b6', fg='#ecf0f1')
        self.score_status_label.pack(pady=(0, 20))

        # Alt skorlar
        sub_scores_frame = tk.Frame(score_frame, bg='white')
        sub_scores_frame.pack(side='left', fill='both', expand=True, padx=10)

        self.sub_score_labels = {}
        sub_scores = [
            ('completeness', 'Veri Tamamlığı', '#27ae60'),
            ('consistency', 'Veri Tutarlılığı', '#3498db'),
            ('accuracy', 'Veri Doğruluğu', '#e67e22'),
            ('timeliness', 'Veri Güncelliği', '#f39c12')
        ]

        for key, label, color in sub_scores:
            card = tk.Frame(sub_scores_frame, bg=color, relief='groove', bd=2)
            card.pack(fill='x', pady=5)

            tk.Label(card, text=label, font=('Segoe UI', 10, 'bold'),
                    bg=color, fg='white').pack(side='left', padx=15, pady=10)

            score_label = tk.Label(card, text="0", font=('Segoe UI', 16, 'bold'),
                                  bg=color, fg='white')
            score_label.pack(side='right', padx=15)

            self.sub_score_labels[key] = score_label

        # İstatistikler
        stats_frame = tk.LabelFrame(self.overview_frame, text=" Veri Kalite İstatistikleri",
                                    bg='white', font=('Segoe UI', 12, 'bold'))
        stats_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Treeview
        columns = ('Metrik', 'Değer', 'Durum')
        self.stats_tree = ttk.Treeview(stats_frame, columns=columns, show='headings', height=10)

        self.stats_tree.heading('Metrik', text='Metrik')
        self.stats_tree.heading('Değer', text='Değer')
        self.stats_tree.heading('Durum', text='Durum')

        self.stats_tree.column('Metrik', width=300)
        self.stats_tree.column('Değer', width=150, anchor='center')
        self.stats_tree.column('Durum', width=150, anchor='center')

        scrollbar = ttk.Scrollbar(stats_frame, orient='vertical', command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=scrollbar.set)

        self.stats_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

    def build_module_tab(self) -> None:
        """Modül bazlı kalite skoru sekmesi"""
        # Modül listesi
        columns = ('Modül', 'Tamamlık', 'Tutarlılık', 'Doğruluk', 'Güncellik', 'Toplam Skor', 'Seviye')
        self.module_tree = ttk.Treeview(self.module_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.module_tree.heading(col, text=col)
            if col == 'Modül':
                self.module_tree.column(col, width=150)
            elif col == 'Seviye':
                self.module_tree.column(col, width=100, anchor='center')
            else:
                self.module_tree.column(col, width=80, anchor='center')

        scrollbar = ttk.Scrollbar(self.module_frame, orient='vertical', command=self.module_tree.yview)
        self.module_tree.configure(yscrollcommand=scrollbar.set)

        self.module_tree.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        scrollbar.pack(side='right', fill='y', pady=20)

    def build_details_tab(self) -> None:
        """Detaylar sekmesi"""
        # Eksik veriler
        missing_frame = tk.LabelFrame(self.details_frame, text="️ Eksik Veriler",
                                     bg='white', font=('Segoe UI', 11, 'bold'))
        missing_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('Modül', 'Alan', 'Eksik Kayıt Sayısı', 'Öncelik')
        self.missing_tree = ttk.Treeview(missing_frame, columns=columns, show='headings', height=8)

        for col in columns:
            self.missing_tree.heading(col, text=col)
            self.missing_tree.column(col, width=150)

        scrollbar1 = ttk.Scrollbar(missing_frame, orient='vertical', command=self.missing_tree.yview)
        self.missing_tree.configure(yscrollcommand=scrollbar1.set)

        self.missing_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar1.pack(side='right', fill='y', pady=10)

        # Tutarsız veriler
        inconsistent_frame = tk.LabelFrame(self.details_frame, text=" Tutarsız Veriler",
                                          bg='white', font=('Segoe UI', 11, 'bold'))
        inconsistent_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns2 = ('Modül', 'Tutarsızlık Türü', 'Etkilenen Kayıt', 'Önem')
        self.inconsistent_tree = ttk.Treeview(inconsistent_frame, columns=columns2, show='headings', height=8)

        for col in columns2:
            self.inconsistent_tree.heading(col, text=col)
            self.inconsistent_tree.column(col, width=150)

        scrollbar2 = ttk.Scrollbar(inconsistent_frame, orient='vertical', command=self.inconsistent_tree.yview)
        self.inconsistent_tree.configure(yscrollcommand=scrollbar2.set)

        self.inconsistent_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar2.pack(side='right', fill='y', pady=10)

    def load_quality_data(self) -> None:
        """Kalite verilerini yükle"""
        try:
            # Toplam skoru hesapla
            overall_score = self.scorer.calculate_overall_score(self.company_id)

            # Ana skoru güncelle
            self.total_score_label.config(text=str(overall_score))

            # Renk kodlama
            if overall_score >= 80:
                color = '#27ae60'
                status = 'MÜKEMMELove'
            elif overall_score >= 60:
                color = '#f39c12'
                status = 'İYİ'
            elif overall_score >= 40:
                color = '#e67e22'
                status = 'ORTA'
            else:
                color = '#e74c3c'
                status = 'DÜŞÜK'

            self.total_score_label.config(bg=color)
            self.score_status_label.config(text=f"/ 100 - {status}", bg=color)

            # Alt skorları yükle
            dimensions = self.scorer.calculate_quality_dimensions(self.company_id)

            self.sub_score_labels['completeness'].config(text=str(dimensions.get('completeness', 0)))
            self.sub_score_labels['consistency'].config(text=str(dimensions.get('consistency', 0)))
            self.sub_score_labels['accuracy'].config(text=str(dimensions.get('accuracy', 0)))
            self.sub_score_labels['timeliness'].config(text=str(dimensions.get('timeliness', 0)))

            # İstatistikleri yükle
            self.load_statistics()

            # Modül skorlarını yükle
            self.load_module_scores()

            # Detayları yükle
            self.load_quality_details()

        except Exception as e:
            messagebox.showerror("Hata", f"Veri yükme hatası: {e}")

    def load_statistics(self) -> None:
        """İstatistikleri yükle"""
        # İstatistik ağacını temizle
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)

        stats = self.scorer.get_quality_statistics(self.company_id)

        for stat in stats:
            status = ' İyi' if stat['value'] >= 80 else ('️ Orta' if stat['value'] >= 60 else ' Düşük')
            self.stats_tree.insert('', 'end', values=(stat['name'], f"{stat['value']}%", status))

    def load_module_scores(self) -> None:
        """Modül skorlarını yükle"""
        # Modül ağacını temizle
        for item in self.module_tree.get_children():
            self.module_tree.delete(item)

        module_scores = self.scorer.calculate_module_scores(self.company_id)

        for module in module_scores:
            level = self.get_quality_level(module['total_score'])
            self.module_tree.insert('', 'end', values=(
                module['name'],
                f"{module['completeness']}%",
                f"{module['consistency']}%",
                f"{module['accuracy']}%",
                f"{module['timeliness']}%",
                f"{module['total_score']}%",
                level
            ))

    def load_quality_details(self) -> None:
        """Kalite detaylarını yükle"""
        # Eksik verileri yükle
        for item in self.missing_tree.get_children():
            self.missing_tree.delete(item)

        missing_data = self.scorer.get_missing_data(self.company_id)
        for item in missing_data:
            priority = ' Yüksek' if item['count'] > 10 else (' Orta' if item['count'] > 5 else ' Düşük')
            self.missing_tree.insert('', 'end', values=(
                item['module'],
                item['field'],
                item['count'],
                priority
            ))

        # Tutarsız verileri yükle
        for item in self.inconsistent_tree.get_children():
            self.inconsistent_tree.delete(item)

        inconsistent_data = self.scorer.get_inconsistent_data(self.company_id)
        for item in inconsistent_data:
            importance = ' Kritik' if item['severity'] == 'high' else (' Orta' if item['severity'] == 'medium' else ' Düşük')
            self.inconsistent_tree.insert('', 'end', values=(
                item['module'],
                item['type'],
                item['affected_records'],
                importance
            ))

    def get_quality_level(self, score: int) -> str:
        """Kalite seviyesini belirle"""
        if score >= 90:
            return ' Mükemmel'
        elif score >= 75:
            return ' İyi'
        elif score >= 60:
            return ' Orta'
        elif score >= 40:
            return ' Düşük'
        else:
            return ' Kritik'

    def recalculate_scores(self) -> None:
        """Skorları yeniden hesapla"""
        try:
            self.scorer.recalculate_all_scores(self.company_id)
            self.load_quality_data()
            messagebox.showinfo("Başarılı", "Kalite skorları yeniden hesaplandı")
        except Exception as e:
            messagebox.showerror("Hata", f"Hesaplama hatası: {e}")

    def generate_report(self) -> None:
        """Kalite raporu oluştur"""
        try:
            report = self.scorer.generate_quality_report(self.company_id)

            # Rapor penceresi
            report_window = tk.Toplevel(self.parent)
            report_window.title("Veri Kalite Raporu")
            report_window.geometry("800x600")

            from tkinter import scrolledtext
            report_text = scrolledtext.ScrolledText(report_window, font=('Courier', 10), wrap='word')
            report_text.pack(fill='both', expand=True, padx=10, pady=10)
            report_text.insert('1.0', report)
            report_text.config(state='disabled')

            # Kapat butonu
            tk.Button(report_window, text=self.lm.tr("btn_close", "Kapat"), font=('Segoe UI', 10, 'bold'),
                     bg='#95a5a6', fg='white', relief='flat', cursor='hand2',
                     padx=20, pady=8, command=report_window.destroy).pack(pady=(0, 10))

        except Exception as e:
            messagebox.showerror("Hata", f"Rapor oluşturma hatası: {e}")

    def export_to_excel(self) -> None:
        """Excel'e aktar"""
        try:
            from tkinter import filedialog
            try:
                import pandas as pd
            except ImportError:
                messagebox.showerror(
                    "Eksik Bağımlılık",
                    "Excel export için 'pandas' kütüphanesi gerekiyor. Lütfen kurun: pip install pandas openpyxl"
                )
                return

            filename = filedialog.asksaveasfilename(
                    defaultextension='.xlsx',
                    filetypes=[(self.lm.tr("file_excel", "Excel Dosyası"), '*.xlsx'), (self.lm.tr("all_files", "Tüm Dosyalar"), '*.*')],
                    initialfile=f'Veri_Kalite_Raporu_{datetime.now().strftime("%Y%m%d")}.xlsx',
                    title=self.lm.tr("export_excel", "Excel'e Aktar")
                )

            if filename:
                # Ölçümleri topla
                overall_score = self.scorer.calculate_overall_score(self.company_id)
                dimensions = self.scorer.calculate_quality_dimensions(self.company_id)
                stats = self.scorer.get_quality_statistics(self.company_id)
                module_scores = self.scorer.calculate_module_scores(self.company_id)
                missing_data = self.scorer.get_missing_data(self.company_id)
                inconsistent_data = self.scorer.get_inconsistent_data(self.company_id)

                # DataFrames hazırla
                df_overview = pd.DataFrame([
                    {"Metrik": "Toplam Skor", "Değer": overall_score}
                ] + [
                    {"Metrik": k, "Değer": v} for k, v in dimensions.items()
                ])

                df_stats = pd.DataFrame([
                    {"Metrik": s.get('name'), "Değer(%)": s.get('value')} for s in stats
                ])

                df_modules = pd.DataFrame([
                    {
                        "Modül": m.get('name'),
                        "Tamamlık(%)": m.get('completeness'),
                        "Tutarlılık(%)": m.get('consistency'),
                        "Doğruluk(%)": m.get('accuracy'),
                        "Güncellik(%)": m.get('timeliness'),
                        "Toplam Skor(%)": m.get('total_score')
                    } for m in module_scores
                ])

                df_missing = pd.DataFrame([
                    {
                        "Modül": d.get('module'),
                        "Alan": d.get('field'),
                        "Eksik Kayıt": d.get('count')
                    } for d in missing_data
                ])

                df_inconsistent = pd.DataFrame([
                    {
                        "Modül": d.get('module'),
                        "Tutarsızlık Türü": d.get('type'),
                        "Etkilenen Kayıt": d.get('affected_records'),
                        "Önem": d.get('severity')
                    } for d in inconsistent_data
                ])

                # Excel'e yaz
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    df_overview.to_excel(writer, sheet_name='Genel Bakış', index=False)
                    df_stats.to_excel(writer, sheet_name='İstatistikler', index=False)
                    df_modules.to_excel(writer, sheet_name='Modül Skorları', index=False)
                    df_missing.to_excel(writer, sheet_name='Eksik Veriler', index=False)
                    df_inconsistent.to_excel(writer, sheet_name='Tutarsız Veriler', index=False)

                messagebox.showinfo(self.lm.tr("success", "Başarılı"), f"{self.lm.tr('excel_export_success', 'Excel dosyası oluşturuldu')}:\n{filename}")

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('export_error', 'Export hatası')}: {e}")

