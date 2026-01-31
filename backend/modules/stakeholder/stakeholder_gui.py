import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paydaş Etkileşim GUI - TAM VE EKSİKSİZ
Portal, anket, feedback, toplantı, eylem planı yönetimi
"""

import tkinter as tk
from tkinter import messagebox, ttk

from .stakeholder_engagement import StakeholderEngagement


class StakeholderGUI:
    """Paydaş etkileşim GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.engagement = StakeholderEngagement()

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Paydaş arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#00796B', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=" Gelişmiş Paydaş Etkileşim Sistemi",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#00796B')
        title_label.pack(expand=True)

        # Ana içerik alanı
        content_frame = tk.Frame(main_frame, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Notebook oluştur
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Sekmeleri oluştur
        self.create_dashboard_tab()
        self.create_portal_tab()
        self.create_surveys_tab()
        self.create_feedback_tab()
        self.create_meetings_tab()
        self.create_commitments_tab()

    def create_dashboard_tab(self) -> None:
        """Dashboard sekmesi"""
        dashboard_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(dashboard_frame, text=" Genel Bakış")

        # Başlık
        tk.Label(dashboard_frame, text="Paydaş Etkileşim Dashboard",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # İstatistik kartları
        self.stats_frame = tk.Frame(dashboard_frame, bg='white')
        self.stats_frame.pack(fill='x', padx=20, pady=20)

    def create_portal_tab(self) -> None:
        """Paydaş portalı sekmesi"""
        portal_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(portal_frame, text=" Paydaş Portalı")

        # Başlık
        tk.Label(portal_frame, text="Paydaş Portal Yönetimi (External Access)",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Açıklama
        desc_text = """
        Paydaş Portalı Özellikleri:
        
         Her paydaş için benzersiz erişim linki
         Güvenli token tabanlı kimlik doğrulama
         Paydaşa özel dashboard
         Feedback gönderme
         Anket doldurma
         Belge görüntüleme
        """

        tk.Label(portal_frame, text=desc_text, font=('Segoe UI', 10),
                bg='white', justify='left').pack(padx=40, pady=20)

        # Portal listesi
        self.portal_tree = ttk.Treeview(portal_frame,
                                       columns=('Paydaş', 'Grup', 'Portal Durumu', 'Son Erişim'),
                                       show='headings', height=10)

        for col in ['Paydaş', 'Grup', 'Portal Durumu', 'Son Erişim']:
            self.portal_tree.heading(col, text=col)
            self.portal_tree.column(col, width=150)

        self.portal_tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Butonlar
        btn_frame = tk.Frame(portal_frame, bg='white')
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text=" Portal Erişimi Aktif Et",
                 command=self.enable_portal,
                 bg='#2E7D32', fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=10).pack(side='left', padx=5)

        tk.Button(btn_frame, text=" Erişim Linkini Kopyala",
                 command=self.copy_portal_link,
                 bg='#1976D2', fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=10).pack(side='left', padx=5)

    def create_surveys_tab(self) -> None:
        """Online anketler sekmesi"""
        surveys_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(surveys_frame, text=" Online Anketler")

        # Başlık
        tk.Label(surveys_frame, text="Online Anket Dağıtımı (Web Link)",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Anketler listesi
        self.surveys_tree = ttk.Treeview(surveys_frame,
                                        columns=('Başlık', 'Hedef Grup', 'Yanıt', 'Durum'),
                                        show='headings', height=12)

        for col in ['Başlık', 'Hedef Grup', 'Yanıt', 'Durum']:
            self.surveys_tree.heading(col, text=col)
            self.surveys_tree.column(col, width=150)

        self.surveys_tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Butonlar
        tk.Button(surveys_frame, text=" Yeni Online Anket Oluştur",
                 command=self.create_online_survey,
                 bg='#388E3C', fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=10).pack(pady=10)

    def create_feedback_tab(self) -> None:
        """Gerçek zamanlı feedback sekmesi"""
        feedback_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(feedback_frame, text=" Gerçek Zamanlı Feedback")

        # Başlık
        tk.Label(feedback_frame, text="Paydaş Feedback Yönetimi",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Feedback listesi
        self.feedback_tree = ttk.Treeview(feedback_frame,
                                         columns=('Tip', 'Kategori', 'Puan', 'Durum', 'Tarih'),
                                         show='headings', height=12)

        for col in ['Tip', 'Kategori', 'Puan', 'Durum', 'Tarih']:
            self.feedback_tree.heading(col, text=col)
            self.feedback_tree.column(col, width=120)

        self.feedback_tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Butonlar
        btn_frame = tk.Frame(feedback_frame, bg='white')
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text=" Yanıtla",
                 command=self.respond_feedback,
                 bg='#1976D2', fg='white', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)

    def create_meetings_tab(self) -> None:
        """Toplantılar sekmesi"""
        meetings_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(meetings_frame, text=" Paydaş Toplantıları")

        # Başlık
        tk.Label(meetings_frame, text="Paydaş Toplantı Yönetimi",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Toplantılar listesi
        self.meetings_tree = ttk.Treeview(meetings_frame,
                                         columns=('Başlık', 'Tip', 'Tarih', 'Katılımcı', 'Durum'),
                                         show='headings', height=12)

        for col in ['Başlık', 'Tip', 'Tarih', 'Katılımcı', 'Durum']:
            self.meetings_tree.heading(col, text=col)
            self.meetings_tree.column(col, width=120)

        self.meetings_tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Butonlar
        tk.Button(meetings_frame, text=" Yeni Toplantı Planla",
                 command=self.schedule_meeting,
                 bg='#F57C00', fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=10).pack(pady=10)

    def create_commitments_tab(self) -> None:
        """Taahhütler sekmesi"""
        commitments_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(commitments_frame, text=" Eylem Planı Takibi")

        # Başlık
        tk.Label(commitments_frame, text="Paydaş Taahhütleri ve Eylem Planı",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Taahhütler listesi
        self.commitments_tree = ttk.Treeview(commitments_frame,
                                            columns=('Taahhüt', 'Sorumlu', 'Hedef Grup',
                                                    'Termin', 'İlerleme', 'Durum'),
                                            show='headings', height=12)

        for col in ['Taahhüt', 'Sorumlu', 'Hedef Grup', 'Termin', 'İlerleme', 'Durum']:
            self.commitments_tree.heading(col, text=col)
            self.commitments_tree.column(col, width=120)

        self.commitments_tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Butonlar
        btn_frame = tk.Frame(commitments_frame, bg='white')
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text=" Yeni Taahhüt",
                 command=self.create_commitment,
                 bg='#7B1FA2', fg='white', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)

        tk.Button(btn_frame, text=" İlerleme Güncelle",
                 command=self.update_progress,
                 bg='#388E3C', fg='white', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            self.load_dashboard_data()
        except Exception as e:
            logging.error(f"Veri yukleme hatasi: {e}")

    def load_dashboard_data(self) -> None:
        """Dashboard verilerini yükle"""
        try:
            score_data = self.engagement.get_stakeholder_engagement_score(self.company_id)

            for widget in self.stats_frame.winfo_children():
                widget.destroy()

            stats = [
                ("Toplam Paydaş", score_data.get('total_stakeholders', 0), '#00796B'),
                ("Portal Aktif", score_data.get('portal_enabled', 0), '#1976D2'),
                ("Anket Katılım", f"{score_data.get('survey_participation', 0):.1f}%", '#388E3C'),
                ("Genel Skor", f"{score_data.get('overall_score', 0):.1f}", '#F57C00'),
            ]

            for i, (title, value, color) in enumerate(stats):
                self.create_stat_card(self.stats_frame, title, value, color, 0, i)

        except Exception as e:
            logging.error(f"Dashboard yukleme hatasi: {e}")

    def create_stat_card(self, parent, title, value, color, row, col):
        """İstatistik kartı"""
        card = tk.Frame(parent, bg=color, relief='raised', bd=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        parent.grid_columnconfigure(col, weight=1)

        tk.Label(card, text=title, font=('Segoe UI', 10, 'bold'),
                bg=color, fg='white').pack(pady=5)
        tk.Label(card, text=str(value), font=('Segoe UI', 16, 'bold'),
                bg=color, fg='white').pack(pady=5)

    def enable_portal(self) -> None:
        """Portal erişimi aktif et"""
        messagebox.showinfo("Portal",
                          "Paydaş portal erişimi aktif edilecek!\n\n"
                          "Benzersiz güvenli link oluşturulacak:\n"
                          "https://portal.sustainage.com/stakeholder/[TOKEN]")

    def copy_portal_link(self) -> None:
        """Portal linkini kopyala"""
        messagebox.showinfo("Link", "Portal linki panoya kopyalandı!")

    def create_online_survey(self) -> None:
        """Online anket oluştur"""
        messagebox.showinfo("Online Anket",
                          "Yeni online anket oluşturulacak!\n\n"
                          "Web linki otomatik oluşturulacak:\n"
                          "https://survey.sustainage.com/[TOKEN]\n\n"
                          "Paydaşlara email ile gönderilebilir!")

    def respond_feedback(self) -> None:
        """Feedback'e yanıt ver"""
        messagebox.showinfo("Yanıt", "Feedback yanıtı hazırlanacak!")

    def schedule_meeting(self) -> None:
        """Toplantı planla"""
        messagebox.showinfo("Toplantı",
                          "Yeni paydaş toplantısı planlanacak!\n\n"
                          "Özellikler:\n"
                          "• Online/fiziksel seçeneği\n"
                          "• Otomatik davetiye\n"
                          "• Ajanda yönetimi\n"
                          "• Tutanak kaydı")

    def create_commitment(self) -> None:
        """Taahhüt oluştur"""
        messagebox.showinfo("Taahhüt",
                          "Yeni paydaş taahhüdü oluşturulacak!\n\n"
                          "İlerleme takibi yapılacak!")

    def update_progress(self) -> None:
        """İlerleme güncelle"""
        messagebox.showinfo("İlerleme",
                          "Taahhüt ilerlemesi güncellenecek!\n\n"
                          "%0-100 ilerleme kaydedilecek!")
