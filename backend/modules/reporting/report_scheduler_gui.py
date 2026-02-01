#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Otomatik Rapor Scheduling GUI - TÜRKÇE
Zamanlanmış raporlar, dağıtım, onay, versiyon yönetimi
"""

import logging
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict

from modules.multilingual.language_manager import LanguageManager

from .report_scheduler import ReportScheduler
from config.icons import Icons
from config.database import DB_PATH


class ReportSchedulerGUI:
    """Rapor scheduling GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()
        self.scheduler = ReportScheduler()

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Zoom state error: {e}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Scheduling arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#6A1B9A', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=" " + self.lm.tr('report_scheduler_title', 'Otomatik Rapor Scheduling ve Dağıtım'),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#6A1B9A')
        title_label.pack(expand=True)

        # Ana içerik alanı
        content_frame = tk.Frame(main_frame, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Notebook oluştur
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Sekmeleri oluştur
        self.create_dashboard_tab()
        self.create_scheduled_reports_tab()
        self.create_distribution_lists_tab()
        self.create_approval_workflow_tab()
        self.create_version_management_tab()

    def create_dashboard_tab(self) -> None:
        """Dashboard sekmesi"""
        dashboard_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(dashboard_frame, text=" " + self.lm.tr('overview', 'Genel Bakış'))

        # Başlık
        tk.Label(dashboard_frame, text=self.lm.tr('report_scheduler_dashboard', 'Rapor Scheduling Dashboard'),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Açıklama
        desc_text = self.lm.tr('scheduler_features_desc', """
         Otomatik Rapor Scheduling Özellikleri:
        
         Zamanlanmış Rapor Oluşturma (Günlük, Haftalık, Aylık, Çeyreklik, Yıllık)
         Email ile Otomatik Gönderim
         Rapor Distribution Listesi
         Rapor Onay Workflow'u (Taslak → Onay → Yayın)
         Rapor Versiyon Yönetimi (v1, v2, v3...)
        """)

        tk.Label(dashboard_frame, text=desc_text, font=('Segoe UI', 11),
                bg='white', justify='left').pack(padx=40, pady=20)

        # İstatistik kartları
        self.stats_frame = tk.Frame(dashboard_frame, bg='white')
        self.stats_frame.pack(fill='x', padx=20, pady=20)

    def create_scheduled_reports_tab(self) -> None:
        """Zamanlanmış raporlar sekmesi"""
        scheduled_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(scheduled_frame, text=" " + self.lm.tr('scheduled_reports', 'Zamanlanmış Raporlar'))

        # Başlık
        tk.Label(scheduled_frame, text=self.lm.tr('scheduled_report_management', 'Zamanlanmış Rapor Yönetimi'),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Periyot açıklaması
        period_text = self.lm.tr('report_periods_desc', """
         Rapor Periyotları:
        
        • Günlük: Her gün otomatik oluşturulur
        • Haftalık: Her hafta Pazartesi
        • Aylık: Her ayın 1'i
        • Çeyreklik: Mart, Haziran, Eylül, Aralık aylarının 1'i
        • Yıllık: Her yılın 1 Ocak'ı
        
         Rapor Formatları: PDF, Excel, JSON, XBRL
        """)

        tk.Label(scheduled_frame, text=period_text, font=('Segoe UI', 10),
                bg='white', justify='left').pack(padx=30, pady=10)

        # Rapor listesi
        columns = (self.lm.tr("report_label", "Rapor"), self.lm.tr('type', 'Tip'), self.lm.tr('period', 'Periyot'), self.lm.tr('last_run', 'Son Çalışma'), self.lm.tr('btn_next', 'Sonraki'), self.lm.tr('status', 'Durum'))
        self.scheduled_tree = ttk.Treeview(scheduled_frame,
                                          columns=columns,
                                          show='headings', height=10)

        for col in columns:
            self.scheduled_tree.heading(col, text=col)
            self.scheduled_tree.column(col, width=120)

        self.scheduled_tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Butonlar
        btn_frame = tk.Frame(scheduled_frame, bg='white')
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text=" " + self.lm.tr('new_scheduled_report', 'Yeni Zamanlanmış Rapor'),
                 command=self.create_new_schedule,
                 bg='#6A1B9A', fg='white', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)

        tk.Button(btn_frame, text=f"{Icons.PLAY} " + self.lm.tr('run_manual', 'Manuel Çalıştır'),
                  command=self.run_manual_report,
                  bg='#2ecc71', fg='white', font=('Segoe UI', 10, 'bold'),
                  padx=15, pady=5).pack(side='left', padx=5)

    def create_distribution_lists_tab(self) -> None:
        """Distribution listesi sekmesi"""
        dist_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(dist_frame, text=" " + self.lm.tr('distribution_list', 'Distribution Listesi'))

        # Başlık
        tk.Label(dist_frame, text=self.lm.tr('email_distribution_lists', 'Email Dağıtım Listeleri'),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        dist_text = self.lm.tr('distribution_list_features_desc', """
         Distribution List Özellikleri:
        
        • To (Ana Alıcılar): Doğrudan alıcılar
        • CC (Kopya): Kopya alıcılar
        • BCC (Gizli Kopya): Gizli kopya alıcılar
        
         Örnek Listeler:
        • Yönetim Kurulu
        • Denetim Komitesi
        • Sürdürülebilirlik Ekibi
        • Paydaşlar
        • Yatırımcılar
        """)

        tk.Label(dist_frame, text=dist_text, font=('Segoe UI', 10),
                bg='white', justify='left').pack(padx=30, pady=10)

        # Liste
        columns = (self.lm.tr('list_name', 'Liste Adı'), self.lm.tr('description', 'Açıklama'), self.lm.tr('recipient_count', 'Alıcı Sayısı'))
        self.dist_tree = ttk.Treeview(dist_frame,
                                     columns=columns,
                                     show='headings', height=10)

        for col in columns:
            self.dist_tree.heading(col, text=col)
            self.dist_tree.column(col, width=200)

        self.dist_tree.pack(fill='both', expand=True, padx=20, pady=10)

        tk.Button(dist_frame, text=" " + self.lm.tr('new_distribution_list', 'Yeni Distribution Listesi'),
                 command=self.create_distribution_list,
                 bg='#388E3C', fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=10).pack(pady=10)

    def create_approval_workflow_tab(self) -> None:
        """Onay workflow sekmesi"""
        approval_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(approval_frame, text=" " + self.lm.tr('approval_workflow', 'Onay Workflow'))

        # Başlık
        tk.Label(approval_frame, text=self.lm.tr('report_approval_workflow', "Rapor Onay Workflow'u"),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        workflow_text = self.lm.tr('approval_workflow_desc', """
         Onay Aşamaları:
        
        1️⃣ Taslak: Rapor hazırlanıyor
        2️⃣ Onay Bekliyor: Yöneticiye gönderildi
        3️⃣ Revizyon: Düzeltme gerekli
        4️⃣ Onaylandı: Onay verildi
        5️⃣ Yayınlandı: Dağıtıma gönderildi
        6️⃣ İptal: İptal edildi
        
         Onaylayıcılar:
        • Sürdürülebilirlik Müdürü
        • CFO / Mali İşler Direktörü
        • CEO / Genel Müdür
        """)

        tk.Label(approval_frame, text=workflow_text, font=('Segoe UI', 10),
                bg='white', justify='left').pack(padx=30, pady=10)

        # Workflow listesi
        columns = (self.lm.tr("report_label", "Rapor"), self.lm.tr('version', 'Versiyon'), self.lm.tr('status', 'Durum'), self.lm.tr('sender', 'Gönderen'), self.lm.tr('approver', 'Onaylayan'), self.lm.tr('date', 'Tarih'))
        self.approval_tree = ttk.Treeview(approval_frame,
                                         columns=columns,
                                         show='headings', height=10)

        for col in columns:
            self.approval_tree.heading(col, text=col)
            self.approval_tree.column(col, width=100)

        self.approval_tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Butonlar
        btn_frame = tk.Frame(approval_frame, bg='white')
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text=" " + self.lm.tr('approve', 'Onayla'),
                 command=self.approve_report,
                 bg='#2E7D32', fg='white', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)

        tk.Button(btn_frame, text=" " + self.lm.tr('reject', 'Reddet'),
                 command=self.reject_report,
                 bg='#C62828', fg='white', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)

    def create_version_management_tab(self) -> None:
        """Versiyon yönetimi sekmesi"""
        version_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(version_frame, text=" " + self.lm.tr('version_management', 'Versiyon Yönetimi'))

        # Başlık
        tk.Label(version_frame, text=self.lm.tr('report_version_management', 'Rapor Versiyon Yönetimi'),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        version_text = self.lm.tr('version_control_desc', """
         Versiyon Kontrol:
        
        • Her rapor değişikliğinde yeni versiyon (v1, v2, v3...)
        • Değişiklik notları (change log)
        • Dosya boyutu ve checksum
        • Mevcut versiyon işaretleme
        • Önceki versiyonlara erişim
        
         Örnek:
        CSRD Raporu 2024
        ├─ v1 (15.03.2024) - İlk taslak
        ├─ v2 (18.03.2024) - Revizyon sonrası
        └─ v3 (20.03.2024) - Onaylanmış (Mevcut)
        """)

        tk.Label(version_frame, text=version_text, font=('Segoe UI', 10),
                bg='white', justify='left').pack(padx=30, pady=10)

        # Versiyon listesi
        columns = (self.lm.tr('report_type', 'Rapor Tipi'), self.lm.tr('version', 'Versiyon'), self.lm.tr('period', 'Dönem'), self.lm.tr('date', 'Tarih'), self.lm.tr('current', 'Mevcut'), self.lm.tr('notes', 'Notlar'))
        self.version_tree = ttk.Treeview(version_frame,
                                        columns=columns,
                                        show='headings', height=10)

        for col in columns:
            self.version_tree.heading(col, text=col)
            self.version_tree.column(col, width=100)

        self.version_tree.pack(fill='both', expand=True, padx=20, pady=10)

        tk.Button(version_frame, text=" " + self.lm.tr('show_version_history', 'Versiyon Geçmişini Göster'),
                 command=self.show_version_history,
                 bg='#F57C00', fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=10).pack(pady=10)

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            self.load_dashboard_data()
        except Exception as e:
            logging.error(f"Veri yukleme hatasi: {e}")

    def load_dashboard_data(self) -> None:
        """Dashboard verilerini yükle - Gerçek verilerle"""
        try:
            for widget in self.stats_frame.winfo_children():
                widget.destroy()

            # Gerçek istatistikleri al
            real_stats = self._get_real_statistics()

            stats = [
                (self.lm.tr('scheduled_reports', "Zamanlanmış Raporlar"), str(real_stats['scheduled_reports']), '#6A1B9A'),
                (self.lm.tr('distribution_lists', "Distribution Listeleri"), str(real_stats['distribution_lists']), '#388E3C'),
                (self.lm.tr('pending_approval', "Onay Bekleyen"), str(real_stats['pending_approval']), '#E65100'),
                (self.lm.tr('total_versions', "Toplam Versiyon"), str(real_stats['total_versions']), '#1976D2'),
            ]

            for i, (title, value, color) in enumerate(stats):
                self.create_stat_card(self.stats_frame, title, value, color, 0, i)

        except Exception as e:
            logging.error(f"Dashboard yukleme hatasi: {e}")

    def _get_real_statistics(self) -> Dict[str, int]:
        """Gerçek rapor istatistiklerini al"""
        try:
            import os
            import sqlite3

            # Database yolunu bul
            db_path = DB_PATH
            if not os.path.isabs(db_path):
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
                db_path = os.path.join(base_dir, db_path)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Zamanlanmış raporlar sayısı
            try:
                cursor.execute("SELECT COUNT(*) FROM scheduled_reports WHERE is_active = 1")
                scheduled_reports = cursor.fetchone()[0]
            except Exception:
                scheduled_reports = 0

            # Distribution listeleri sayısı
            try:
                cursor.execute("SELECT COUNT(DISTINCT list_name) FROM distribution_lists WHERE is_active = 1")
                distribution_lists = cursor.fetchone()[0]
            except Exception:
                distribution_lists = 0

            # Onay bekleyen raporlar
            try:
                cursor.execute("SELECT COUNT(*) FROM report_versions WHERE approval_status = 'pending'")
                pending_approval = cursor.fetchone()[0]
            except Exception:
                pending_approval = 0

            # Toplam versiyon sayısı
            try:
                cursor.execute("SELECT COUNT(*) FROM report_versions")
                total_versions = cursor.fetchone()[0]
            except Exception:
                total_versions = 0

            conn.close()

            return {
                'scheduled_reports': scheduled_reports,
                'distribution_lists': distribution_lists,
                'pending_approval': pending_approval,
                'total_versions': total_versions
            }

        except Exception as e:
            logging.error(f"Istatistik alma hatasi: {e}")
            # Hata durumunda 0 döndür
            return {
                'scheduled_reports': 0,
                'distribution_lists': 0,
                'pending_approval': 0,
                'total_versions': 0
            }

    def create_stat_card(self, parent, title, value, color, row, col):
        """İstatistik kartı"""
        card = tk.Frame(parent, bg=color, relief='raised', bd=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        parent.grid_columnconfigure(col, weight=1)

        tk.Label(card, text=title, font=('Segoe UI', 10, 'bold'),
                bg=color, fg='white').pack(pady=5)
        tk.Label(card, text=str(value), font=('Segoe UI', 16, 'bold'),
                bg=color, fg='white').pack(pady=5)

    def create_new_schedule(self) -> None:
        """Yeni zamanlanmış rapor oluşturma diyaloğu"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('new_scheduled_report', "Yeni Zamanlanmış Rapor"))
        dialog.geometry("450x550")
        dialog.transient(self.parent)
        dialog.grab_set()

        # Form variables
        name_var = tk.StringVar()
        type_var = tk.StringVar(value="CSRD")
        freq_var = tk.StringVar(value="monthly")
        start_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        auto_send_var = tk.BooleanVar(value=False)
        format_var = tk.StringVar(value="PDF")

        # UI Layout
        pad_opts = {'padx': 10, 'pady': 5, 'sticky': 'w'}
        
        tk.Label(dialog, text=self.lm.tr('report_name', "Rapor Adı") + ":").pack(**pad_opts)
        tk.Entry(dialog, textvariable=name_var, width=40).pack(**pad_opts)

        tk.Label(dialog, text=self.lm.tr('report_type', "Rapor Tipi") + ":").pack(**pad_opts)
        type_combo = ttk.Combobox(dialog, textvariable=type_var, width=37)
        type_combo['values'] = ('CSRD', 'GRI', 'TCFD', 'Carbon', 'Executive Summary', 'Energy', 'Waste', 'Water')
        type_combo.pack(**pad_opts)

        tk.Label(dialog, text=self.lm.tr('frequency', "Sıklık") + ":").pack(**pad_opts)
        freq_combo = ttk.Combobox(dialog, textvariable=freq_var, width=37)
        freq_combo['values'] = ('daily', 'weekly', 'monthly', 'quarterly', 'yearly')
        freq_combo.pack(**pad_opts)

        tk.Label(dialog, text=self.lm.tr('start_date', "Başlangıç Tarihi (YYYY-MM-DD)") + ":").pack(**pad_opts)
        tk.Entry(dialog, textvariable=start_date_var, width=40).pack(**pad_opts)

        tk.Label(dialog, text=self.lm.tr('format', "Format") + ":").pack(**pad_opts)
        format_combo = ttk.Combobox(dialog, textvariable=format_var, width=37)
        format_combo['values'] = ('PDF', 'Excel', 'JSON', 'XBRL')
        format_combo.pack(**pad_opts)

        tk.Checkbutton(dialog, text=self.lm.tr('auto_send', "Otomatik Gönder"), variable=auto_send_var).pack(**pad_opts)

        def save():
            if not name_var.get():
                messagebox.showerror("Hata", "Rapor adı zorunludur!")
                return
                
            try:
                start_date = datetime.strptime(start_date_var.get(), "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Hata", "Geçersiz tarih formatı! YYYY-MM-DD olmalı.")
                return

            try:
                report_id = self.scheduler.create_scheduled_report(
                    company_id=self.company_id,
                    report_name=name_var.get(),
                    report_type=type_var.get(),
                    frequency=freq_var.get(),
                    start_date=start_date,
                    report_format=format_var.get(),
                    auto_send=auto_send_var.get()
                )
                
                if report_id:
                    messagebox.showinfo("Başarılı", "Zamanlanmış rapor oluşturuldu!")
                    dialog.destroy()
                    self.load_data() # Refresh UI
                else:
                    messagebox.showerror("Hata", "Rapor oluşturulamadı.")
            except Exception as e:
                logging.error(f"Save schedule error: {e}")
                messagebox.showerror("Hata", f"Bir hata oluştu: {e}")

        tk.Button(dialog, text=self.lm.tr('save', "Kaydet"), command=save, 
                 bg='#4CAF50', fg='white', font=('Segoe UI', 10, 'bold'), width=20).pack(pady=20)

    def run_manual_report(self) -> None:
        """Manuel çalıştır"""
        # Seçili raporu al
        selection = self.scheduled_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen listeden bir rapor seçin.")
            return

        report_id = selection[0]
        
        # Onay al
        if not messagebox.askyesno(self.lm.tr('confirm', "Onay"), 
                                 self.lm.tr('confirm_run_report', "Bu raporu şimdi çalıştırmak istiyor musunuz?")):
            return

        try:
            success = self.scheduler.run_scheduled_report(int(report_id))
            
            if success:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), 
                                  self.lm.tr('report_run_success', "Rapor başarıyla oluşturuldu."))
                self.load_data() # Refresh UI
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), 
                                   self.lm.tr('report_run_error', "Rapor oluşturulamadı."))
        except Exception as e:
            logging.error(f"Manual run error: {e}")
            messagebox.showerror(self.lm.tr('error', "Hata"), f"Hata: {e}")

    def create_distribution_list(self) -> None:
        """Distribution listesi oluştur"""
        messagebox.showinfo(self.lm.tr('distribution_list', "Distribution Listesi"),
                          self.lm.tr('new_distribution_list_msg', "Yeni Email Dağıtım Listesi\n\n"
                          "Alıcı Tipleri:\n"
                          "• To (Ana Alıcılar)\n"
                          "• CC (Kopya)\n"
                          "• BCC (Gizli Kopya)\n\n"
                          "Örnek Listeler:\n"
                          " Yönetim Kurulu\n"
                          " Denetim Komitesi\n"
                          " Paydaşlar"))

    def approve_report(self) -> None:
        """Raporu onayla"""
        messagebox.showinfo(self.lm.tr('report_approval', "Rapor Onay"),
                          self.lm.tr('report_approval_msg', "Rapor Onaylanacak!\n\n"
                          " Onay durumu güncellenecek\n"
                          " Onay notu eklenecek\n"
                          " Onaylayan bilgisi kaydedilecek\n"
                          " Dağıtıma hazır hale gelecek"))

    def reject_report(self) -> None:
        """Raporu reddet"""
        messagebox.showinfo(self.lm.tr('report_rejection', "Rapor Reddet"),
                          self.lm.tr('report_rejection_msg', "Rapor Reddedilecek!\n\n"
                          " Revizyon gerekli durumuna alınacak\n"
                          " Ret gerekçesi eklenecek\n"
                          " Hazırlayan bilgilendirilecek"))

    def show_version_history(self) -> None:
        """Versiyon geçmişi"""
        messagebox.showinfo(self.lm.tr('version_history', "Versiyon Geçmişi"),
                          self.lm.tr('version_history_msg', "Rapor Versiyon Geçmişi\n\n"
                          "Gösterilecek Bilgiler:\n"
                          " Tüm versiyonlar (v1, v2, v3...)\n"
                          " Değişiklik notları\n"
                          " Oluşturma tarihleri\n"
                          " Dosya boyutları\n"
                          " Mevcut versiyon işareti"))
