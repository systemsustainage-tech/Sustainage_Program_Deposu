#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TSRS/ESRS Çift Önemlendirme (Double Materiality) GUI
Impact ve Financial materiality değerlendirme arayüzü
"""

import logging
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

from utils.ui_theme import apply_theme

from .tsrs_esrs import TSRSESRSManager


class DoubleMaterialityGUI:
    """Çift Önemlendirme analiz arayüzü"""

    def __init__(self, parent, db_path: str, company_id: int, year: int = 2024) -> None:
        self.parent = parent
        self.db_path = db_path
        self.company_id = company_id
        self.year = year
        self.manager = TSRSESRSManager(db_path)
        self.lm = LanguageManager()

        self.setup_ui()
        self.load_topics()

    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        apply_theme(self.parent)
        # Başlık
        header = tk.Frame(self.parent, bg='#2c3e50', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(header, text=" Çift Önemlendirme Analizi (Double Materiality)",
                font=('Segoe UI', 16, 'bold'), fg='white', bg='#2c3e50').pack(side='left', padx=20, pady=20)

        tk.Label(header, text="TSRS/ESRS Uyumlu - İklim ve Sürdürülebilirlik Konuları",
                font=('Segoe UI', 10), fg='#bdc3c7', bg='#2c3e50').pack(side='left')

        toolbar = ttk.Frame(self.parent)
        toolbar.pack(fill='x', pady=(0, 10))
        ttk.Button(toolbar, text=" Rapor Merkezi", style='Primary.TButton', command=self.open_report_center_double_materiality).pack(side='left', padx=6)

        # İçerik alanı
        content_frame = tk.Frame(self.parent, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Sol panel - Konu listesi
        left_panel = tk.LabelFrame(content_frame, text=" Sürdürülebilirlik Konuları",
                                   bg='#ecf0f1', font=('Segoe UI', 12, 'bold'))
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # Sağ panel - Değerlendirme formu
        right_panel = tk.LabelFrame(content_frame, text=" Önemlendirme Değerlendirmesi",
                                    bg='white', font=('Segoe UI', 12, 'bold'))
        right_panel.pack(side='right', fill='both', expand=True)

        self.build_topic_list(left_panel)
        self.build_assessment_form(right_panel)

        # Alt panel - Materiyalite matrisi
        matrix_panel = tk.LabelFrame(self.parent, text=" Çift Önemlendirme Matrisi",
                                     bg='white', font=('Segoe UI', 12, 'bold'))
        matrix_panel.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        self.build_materiality_matrix(matrix_panel)

    def build_topic_list(self, parent) -> None:
        """Konu listesi oluştur"""
        # Yeni konu ekleme
        add_frame = tk.Frame(parent, bg='#ecf0f1')
        add_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(add_frame, text=self.lm.tr("add_new_topic_btn", " Yeni Konu Ekle"), style='Primary.TButton', command=self.add_new_topic).pack(fill='x')

        # Konu listesi
        list_frame = tk.Frame(parent, bg='#ecf0f1')
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        columns = ('Konu', 'Etki Skoru', 'Finansal Skoru', 'Düzey')
        self.topic_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        self.topic_tree.heading('Konu', text=self.lm.tr("topic_col", "Konu Adı"))
        self.topic_tree.heading('Etki Skoru', text=self.lm.tr("impact_score_col", "Etki"))
        self.topic_tree.heading('Finansal Skoru', text=self.lm.tr("financial_score_col", "Finansal"))
        self.topic_tree.heading('Düzey', text=self.lm.tr("level_col", "Önem Düzeyi"))

        self.topic_tree.column('Konu', width=200)
        self.topic_tree.column('Etki Skoru', width=60, anchor='center')
        self.topic_tree.column('Finansal Skoru', width=60, anchor='center')
        self.topic_tree.column('Düzey', width=100, anchor='center')

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.topic_tree.yview)
        self.topic_tree.configure(yscrollcommand=scrollbar.set)

        self.topic_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Tıklama eventi
        self.topic_tree.bind('<<TreeviewSelect>>', self.on_topic_select)

    def build_assessment_form(self, parent) -> None:
        """Değerlendirme formu oluştur"""
        form_frame = tk.Frame(parent, bg='white')
        form_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Konu adı
        tk.Label(form_frame, text=self.lm.tr("topic_name_label", "Konu Adı:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(0, 5))
        self.topic_name_var = tk.StringVar()
        self.topic_name_entry = tk.Entry(form_frame, textvariable=self.topic_name_var, font=('Segoe UI', 10), width=40)
        self.topic_name_entry.pack(fill='x', pady=(0, 15))

        # Etki Önemlendirmesi (Impact Materiality)
        impact_frame = tk.LabelFrame(form_frame, text=self.lm.tr("impact_materiality_title", " Etki Önemlendirmesi (Impact Materiality)"),
                                     bg='#e8f5e9', font=('Segoe UI', 11, 'bold'))
        impact_frame.pack(fill='x', pady=(0, 15))

        tk.Label(impact_frame, text=self.lm.tr("impact_score_label", "İşletmenin çevre/toplum üzerindeki etkisi (1-5):"),
                font=('Segoe UI', 9), bg='#e8f5e9').pack(anchor='w', padx=10, pady=(10, 5))

        self.impact_score_var = tk.DoubleVar(value=3.0)
        impact_scale = ttk.Scale(impact_frame, from_=1, to=5, orient='horizontal',
                                variable=self.impact_score_var, length=300,
                                command=self.update_materiality_level)
        impact_scale.pack(padx=10, pady=(0, 5))

        self.impact_score_label = tk.Label(impact_frame, text="3.0", font=('Segoe UI', 12, 'bold'),
                                           bg='#e8f5e9', fg='#27ae60')
        self.impact_score_label.pack(pady=(0, 5))

        tk.Label(impact_frame, text=self.lm.tr("stakeholder_impact_label", "Paydaş Etkisi:"), font=('Segoe UI', 9), bg='#e8f5e9').pack(anchor='w', padx=10, pady=(5, 0))
        self.stakeholder_impact_text = tk.Text(impact_frame, height=3, font=('Segoe UI', 9), wrap='word')
        self.stakeholder_impact_text.pack(padx=10, pady=(0, 10), fill='x')

        # Finansal Önemlendirme (Financial Materiality)
        financial_frame = tk.LabelFrame(form_frame, text=self.lm.tr("financial_materiality_title", " Finansal Önemlendirme (Financial Materiality)"),
                                       bg='#e3f2fd', font=('Segoe UI', 11, 'bold'))
        financial_frame.pack(fill='x', pady=(0, 15))

        tk.Label(financial_frame, text=self.lm.tr("financial_score_label", "Konunun işletmeye finansal etkisi (1-5):"),
                font=('Segoe UI', 9), bg='#e3f2fd').pack(anchor='w', padx=10, pady=(10, 5))

        self.financial_score_var = tk.DoubleVar(value=3.0)
        financial_scale = ttk.Scale(financial_frame, from_=1, to=5, orient='horizontal',
                                   variable=self.financial_score_var, length=300,
                                   command=self.update_materiality_level)
        financial_scale.pack(padx=10, pady=(0, 5))

        self.financial_score_label = tk.Label(financial_frame, text="3.0", font=('Segoe UI', 12, 'bold'),
                                             bg='#e3f2fd', fg='#3498db')
        self.financial_score_label.pack(pady=(0, 5))

        tk.Label(financial_frame, text=self.lm.tr("business_impact_label", "İşletme Etkisi:"), font=('Segoe UI', 9), bg='#e3f2fd').pack(anchor='w', padx=10, pady=(5, 0))
        self.business_impact_text = tk.Text(financial_frame, height=3, font=('Segoe UI', 9), wrap='word')
        self.business_impact_text.pack(padx=10, pady=(0, 10), fill='x')

        # Önem düzeyi göstergesi
        level_frame = tk.Frame(form_frame, bg='white')
        level_frame.pack(fill='x', pady=(0, 15))

        tk.Label(level_frame, text=self.lm.tr("materiality_level_label", "Çift Önemlendirme Düzeyi:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(side='left')
        self.materiality_level_label = tk.Label(level_frame, text=self.lm.tr("level_medium", "ORTA"), font=('Segoe UI', 14, 'bold'),
                                               bg='#f39c12', fg='white', padx=20, pady=5)
        self.materiality_level_label.pack(side='left', padx=10)

        # ESRS İlişkisi
        tk.Label(form_frame, text=self.lm.tr("related_esrs_standard", "İlgili ESRS Standardı:"), font=('Segoe UI', 9, 'bold'), bg='white').pack(anchor='w', pady=(5, 0))
        self.esrs_var = tk.StringVar()
        esrs_combo = ttk.Combobox(form_frame, textvariable=self.esrs_var, state='readonly', width=37)
        esrs_combo['values'] = ['E1 - İklim Değişikliği', 'E2 - Kirlilik', 'E3 - Su ve Deniz Kaynakları',
                                'E4 - Biyoçeşitlilik', 'E5 - Döngüsel Ekonomi',
                                'S1 - İşgücü', 'S2 - Değer Zinciri Çalışanları',
                                'S3 - Etkilenen Topluluklar', 'S4 - Tüketiciler',
                                'G1 - İş Etiği']
        esrs_combo.pack(fill='x', pady=(0, 15))

        # Butonlar
        button_frame = tk.Frame(form_frame, bg='white')
        button_frame.pack(fill='x')

        ttk.Button(button_frame, text=self.lm.tr("btn_save", " Kaydet"), style='Primary.TButton', command=self.save_assessment).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text=self.lm.tr("btn_delete", "️ Sil"), style='Accent.TButton', command=self.delete_assessment).pack(side='left')

    def build_materiality_matrix(self, parent) -> None:
        """Materiyalite matrisi oluştur"""
        try:
            import matplotlib
            matplotlib.use('TkAgg')

            # Kontrol paneli
            control_frame = tk.Frame(parent, bg='white')
            control_frame.pack(fill='x', padx=10, pady=10)

            ttk.Button(control_frame, text=self.lm.tr("refresh_matrix", " Matrisi Yenile"), style='Primary.TButton', command=self.refresh_matrix).pack(side='left', padx=5)
            ttk.Button(control_frame, text=self.lm.tr("save_as_png", " PNG Olarak Kaydet"), style='Primary.TButton', command=self.export_matrix).pack(side='left', padx=5)


            # Grafik alanı
            self.matrix_frame = tk.Frame(parent, bg='white')
            self.matrix_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

            self.refresh_matrix()

        except Exception as e:
            tk.Label(parent, text=f"{self.lm.tr('chart_create_error', 'Grafik oluşturulamadı')}: {e}",
                    font=('Segoe UI', 10), fg='red', bg='white').pack(pady=20)

    def open_report_center_double_materiality(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('tsrs')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for tsrs: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('report_center_error', 'Rapor Merkezi açılamadı')}:\n{e}")
            logging.error(f"Error opening report center: {e}")

    def load_topics(self) -> None:
        """Konuları yükle"""
        try:
            # Veritabanından konuları al
            topics = self.manager.get_double_materiality_assessments(self.company_id, self.year)

            # Ağacı temizle
            for item in self.topic_tree.get_children():
                self.topic_tree.delete(item)

            # Konuları ekle
            for topic in topics:
                level = self.calculate_materiality_level(
                    topic.get('impact_materiality_score', 0),
                    topic.get('financial_materiality_score', 0)
                )

                self.topic_tree.insert('', 'end', values=(
                    topic['topic_name'],
                    f"{topic.get('impact_materiality_score', 0):.1f}",
                    f"{topic.get('financial_materiality_score', 0):.1f}",
                    level
                ))

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('topics_load_error', 'Konular yüklenemedi')}: {e}")

    def on_topic_select(self, event) -> None:
        """Konu seçildiğinde formu doldur"""
        selection = self.topic_tree.selection()
        if not selection:
            return

        values = self.topic_tree.item(selection[0], 'values')
        if not values:
            return

        # Formları doldur
        self.topic_name_var.set(values[0])
        self.impact_score_var.set(float(values[1]))
        self.financial_score_var.set(float(values[2]))

        self.update_materiality_level(None)

    def update_materiality_level(self, event) -> None:
        """Önem düzeyini güncelle"""
        impact = self.impact_score_var.get()
        financial = self.financial_score_var.get()

        self.impact_score_label.config(text=f"{impact:.1f}")
        self.financial_score_label.config(text=f"{financial:.1f}")

        level = self.calculate_materiality_level(impact, financial)

        # Renk ve metin güncelleme
        colors = {
            self.lm.tr("level_low", "DÜŞÜK"): '#95a5a6',
            self.lm.tr("level_medium", "ORTA"): '#f39c12',
            self.lm.tr("level_high", "YÜKSEK"): '#e67e22',
            self.lm.tr("level_very_high", "ÇOK YÜKSEK"): '#e74c3c'
        }

        self.materiality_level_label.config(text=level, bg=colors.get(level, '#95a5a6'))

    def calculate_materiality_level(self, impact: float, financial: float) -> str:
        """Önem düzeyini hesapla"""
        avg = (impact + financial) / 2

        if avg >= 4.5:
            return self.lm.tr("level_very_high", "ÇOK YÜKSEK")
        elif avg >= 3.5:
            return self.lm.tr("level_high", "YÜKSEK")
        elif avg >= 2.5:
            return self.lm.tr("level_medium", "ORTA")
        else:
            return self.lm.tr("level_low", "DÜŞÜK")

    def add_new_topic(self) -> None:
        """Yeni konu ekle"""
        self.topic_name_var.set("")
        self.impact_score_var.set(3.0)
        self.financial_score_var.set(3.0)
        self.stakeholder_impact_text.delete('1.0', 'end')
        self.business_impact_text.delete('1.0', 'end')
        self.esrs_var.set("")
        self.update_materiality_level(None)

    def save_assessment(self) -> None:
        """Değerlendirmeyi kaydet"""
        try:
            topic_name = self.topic_name_var.get().strip()
            if not topic_name:
                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("topic_name_empty", "Konu adı boş olamaz"))
                return

            impact_score = self.impact_score_var.get()
            financial_score = self.financial_score_var.get()

            level = self.calculate_materiality_level(impact_score, financial_score)

            # Kaydet
            success = self.manager.add_double_materiality_assessment(
                company_id=self.company_id,
                assessment_year=self.year,
                topic_name=topic_name,
                impact_materiality_score=impact_score,
                financial_materiality_score=financial_score,
                double_materiality_level=level,
                esrs_relevance=self.esrs_var.get(),
                stakeholder_impact=self.stakeholder_impact_text.get('1.0', 'end').strip(),
                business_impact=self.business_impact_text.get('1.0', 'end').strip()
            )

            if success:
                messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("assessment_saved", "Değerlendirme kaydedildi"))
                self.load_topics()
                self.refresh_matrix()
            else:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("save_failed", "Kaydetme başarısız"))

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('save_error', 'Kaydetme hatası')}: {e}")

    def delete_assessment(self) -> None:
        """Değerlendirmeyi sil"""
        selection = self.topic_tree.selection()
        if not selection:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("select_topic_to_delete", "Lütfen silinecek konuyu seçin"))
            return

        # Seçili item'ı al
        item = self.topic_tree.item(selection[0])
        values = item['values']
        topic_name = values[0] if values else None

        if not topic_name:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("topic_info_not_found", "Konu bilgisi bulunamadı!"))
            return

        if messagebox.askyesno(self.lm.tr("confirmation", "Onay"), self.lm.tr("delete_confirmation", "'{topic_name}' değerlendirmesini silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz!").format(topic_name=topic_name)):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM materiality_assessments WHERE topic_name = ? AND company_id = ?",
                             (topic_name, self.company_id))
                conn.commit()
                conn.close()

                # Listeden kaldır
                self.topic_tree.delete(selection[0])
                messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("assessment_deleted", "Değerlendirme silindi!"))
                self.refresh_matrix()  # Matrisi yenile

            except Exception as e:
                messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('delete_error', 'Silme hatası')}: {e}")

    def refresh_matrix(self) -> None:
        """Matrisi yenile"""
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure

            # Eski grafiği temizle
            for widget in self.matrix_frame.winfo_children():
                widget.destroy()

            # Veri topla
            topics = []
            for item in self.topic_tree.get_children():
                values = self.topic_tree.item(item, 'values')
                topics.append({
                    'name': values[0],
                    'impact': float(values[1]),
                    'financial': float(values[2])
                })

            if not topics:
                tk.Label(self.matrix_frame, text=self.lm.tr("no_assessment_yet", "Henüz değerlendirme yok. Lütfen konu ekleyin."),
                        font=('Segoe UI', 11), fg='#666', bg='white').pack(pady=50)
                return

            # Grafik oluştur
            fig = Figure(figsize=(10, 6), dpi=100)
            ax = fig.add_subplot(111)

            # Scatter plot
            for topic in topics:
                ax.scatter(topic['financial'], topic['impact'], s=200, alpha=0.6)
                ax.annotate(topic['name'], (topic['financial'], topic['impact']),
                           xytext=(5, 5), textcoords='offset points', fontsize=8)

            # Bölge çizgileri
            ax.axhline(y=3.5, color='gray', linestyle='--', alpha=0.5)
            ax.axvline(x=3.5, color='gray', linestyle='--', alpha=0.5)

            # Bölge etiketleri
            ax.text(1.5, 4.5, self.lm.tr("high_impact_low_financial", 'Yüksek Etki\nDüşük Finansal'), ha='center', va='center', fontsize=9, alpha=0.5)
            ax.text(4.5, 4.5, self.lm.tr("very_high_important", 'ÇOK YÜKSEK\nÖNEMLİ'), ha='center', va='center', fontsize=10, weight='bold', alpha=0.7)
            ax.text(1.5, 1.5, self.lm.tr("level_low", 'DÜŞÜK'), ha='center', va='center', fontsize=9, alpha=0.5)
            ax.text(4.5, 1.5, self.lm.tr("low_impact_high_financial", 'Düşük Etki\nYüksek Finansal'), ha='center', va='center', fontsize=9, alpha=0.5)

            ax.set_xlabel('Finansal Önemlendirme →', fontsize=11, weight='bold')
            ax.set_ylabel('Etki Önemlendirmesi →', fontsize=11, weight='bold')
            ax.set_title(self.lm.tr("double_materiality_matrix_title", 'Çift Önemlendirme Matrisi (Double Materiality Matrix)'), fontsize=13, weight='bold')
            ax.set_xlim(0.5, 5.5)
            ax.set_ylim(0.5, 5.5)
            ax.grid(True, alpha=0.3)

            # Canvas
            canvas = FigureCanvasTkAgg(fig, master=self.matrix_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)

        except Exception as e:
            tk.Label(self.matrix_frame, text=f"{self.lm.tr('matrix_create_error', 'Matris oluşturulamadı')}: {e}",
                    font=('Segoe UI', 10), fg='red', bg='white').pack(pady=20)

    def export_matrix(self) -> None:
        """Matrisi PNG olarak kaydet"""
        try:
            from tkinter import filedialog

            import matplotlib.pyplot as plt
            from matplotlib.figure import Figure

            # Veriyi topla
            topics = []
            for item in self.topic_tree.get_children():
                values = self.topic_tree.item(item, 'values')
                topics.append({
                    'name': values[0],
                    'impact': float(values[1]),
                    'financial': float(values[2])
                })

            if not topics:
                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("save_data_warning", "Kaydedilecek veri yok!"))
                return

            # Dosya adı sor
            filename = filedialog.asksaveasfilename(
                defaultextension='.png',
                filetypes=[
                    (self.lm.tr("file_png", 'PNG Dosyaları'), '*.png'),
                    (self.lm.tr("file_pdf", 'PDF Dosyaları'), '*.pdf'),
                    (self.lm.tr("all_files", 'Tüm Dosyalar'), '*.*')
                ],
                initialfile=f'Cift_Onemlendirme_Matrisi_{self.year}.png',
                title=self.lm.tr('save_matrix', "Matrisi Kaydet")
            )

            if not filename:
                return

            # Yeni figure oluştur (yüksek çözünürlük)
            fig = Figure(figsize=(12, 10), dpi=150)
            ax = fig.add_subplot(111)

            # Arka plan renkleri
            ax.axhspan(0.5, 3, 0, 0.6, facecolor='lightgreen', alpha=0.2)
            ax.axhspan(3, 5.5, 0, 0.6, facecolor='yellow', alpha=0.2)
            ax.axhspan(0.5, 3, 0.6, 1, facecolor='yellow', alpha=0.2)
            ax.axhspan(3, 5.5, 0.6, 1, facecolor='red', alpha=0.2)

            # Noktaları çiz
            for topic in topics:
                ax.scatter(topic['financial'], topic['impact'], s=200, alpha=0.6, edgecolors='black', linewidths=2)
                ax.annotate(topic['name'], (topic['financial'], topic['impact']),
                          fontsize=9, ha='center', va='bottom')

            # Bölge etiketleri
            ax.text(1.5, 4.5, self.lm.tr("high_impact_low_financial", 'Yüksek Etki\nDüşük Finansal'), ha='center', va='center', fontsize=11, alpha=0.5)
            ax.text(4.5, 4.5, self.lm.tr("very_high_important", 'ÇOK YÜKSEK\nÖNEMLİ'), ha='center', va='center', fontsize=12, weight='bold', alpha=0.7)
            ax.text(1.5, 1.5, self.lm.tr("level_low", 'DÜŞÜK'), ha='center', va='center', fontsize=11, alpha=0.5)
            ax.text(4.5, 1.5, self.lm.tr("low_impact_high_financial", 'Düşük Etki\nYüksek Finansal'), ha='center', va='center', fontsize=11, alpha=0.5)

            ax.set_xlabel('Finansal Önemlendirme →', fontsize=13, weight='bold')
            ax.set_ylabel('Etki Önemlendirmesi →', fontsize=13, weight='bold')
            ax.set_title(f"{self.lm.tr('double_materiality_matrix_title', 'Çift Önemlendirme Matrisi (Double Materiality Matrix)')} - {self.year}", fontsize=15, weight='bold', pad=20)
            ax.set_xlim(0.5, 5.5)
            ax.set_ylim(0.5, 5.5)
            ax.grid(True, alpha=0.3)

            # Kaydet
            fig.tight_layout()
            fig.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close(fig)

            messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("matrix_saved", "Matris kaydedildi:\n\n{path}").format(path=filename))

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('export_error', 'Export hatası')}: {e}")

