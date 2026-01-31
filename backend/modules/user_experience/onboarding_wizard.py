#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
İlk Kullanım Turu (Onboarding Wizard)
Yeni kullanıcılar için interaktif sistem tanıtımı
"""

import logging
import sqlite3
import tkinter as tk
from typing import Callable, Optional

from utils.language_manager import LanguageManager
from utils.ui_theme import apply_theme
from config.icons import Icons


class OnboardingWizard:
    """İlk kullanım turu yöneticisi"""

    def __init__(self, parent, db_path: str, user_id: int, on_complete: Optional[Callable] = None) -> None:
        self.parent = parent
        self.db_path = db_path
        self.user_id = user_id
        self.on_complete = on_complete
        self.current_step = 0
        self.total_steps = 6
        self.lm = LanguageManager()

        # Kullanıcının turu görmüş olup olmadığını kontrol et
        if self.has_seen_tour():
            if on_complete:
                on_complete()
            return

        self.create_wizard()

    def has_seen_tour(self) -> bool:
        """Kullanıcı turu daha önce görmüş mü?"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # User settings tablosunu kontrol et
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY,
                    onboarding_completed INTEGER DEFAULT 0,
                    show_onboarding INTEGER DEFAULT 1,
                    show_welcome_banner INTEGER DEFAULT 1,
                    theme TEXT DEFAULT 'default',
                    language TEXT DEFAULT 'tr',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("SELECT onboarding_completed, show_onboarding FROM user_settings WHERE user_id = ?", (self.user_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                onboarding_completed, show_onboarding = result
                # Eğer onboarding tamamlandıysa ve "bir daha gösterme" seçildiyse (show_onboarding = 0)
                if onboarding_completed == 1 and show_onboarding == 0:
                    return True
                # Eğer onboarding tamamlandıysa ama "bir daha gösterme" seçilmediyse (show_onboarding = 1)
                elif onboarding_completed == 1 and show_onboarding == 1:
                    return False
                # Eğer onboarding tamamlanmadıysa, turu göster
                else:
                    return False

            # Eğer hiç kayıt yoksa, turu göster
            return False
        except Exception as e:
            logging.error(f"Onboarding kontrol hatası: {e}")
            return False

    def mark_tour_completed(self) -> None:
        """Turu tamamlandı olarak işaretle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Mevcut satır varsa show_onboarding değerini koru; yoksa 1 olarak başlat
            cursor.execute("""
                INSERT OR REPLACE INTO user_settings (user_id, onboarding_completed, show_onboarding)
                VALUES (?, 1, COALESCE((SELECT show_onboarding FROM user_settings WHERE user_id = ?), 1))
            """, (self.user_id, self.user_id))

            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Onboarding tamamlama hatası: {e}")

    def create_wizard(self) -> None:
        """Wizard penceresini oluştur"""
        # Ana overlay pencere
        self.wizard_window = tk.Toplevel(self.parent)
        self.wizard_window.title(self.lm.tr('onboarding_welcome_title', "Sustainage - Hoş Geldiniz"))

        # Tam ekran overlay
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        self.wizard_window.geometry(f"{screen_width}x{screen_height}+0+0")

        # Modal yap
        self.wizard_window.transient(self.parent)
        self.wizard_window.grab_set()

        # Yarı saydam arka plan
        self.wizard_window.configure(bg='#000000')
        self.wizard_window.attributes('-alpha', 0.95)
        apply_theme(self.wizard_window)

        # ESC tuşu ile kapatma
        self.wizard_window.bind('<Escape>', lambda e: self.close_wizard())

        # Ana container - merkeze yerleştir
        container_width = 900
        container_height = 700

        self.main_container = tk.Frame(self.wizard_window, bg='white',
                                       relief='raised', bd=5, width=container_width,
                                       height=container_height)
        self.main_container.pack(expand=True)
        self.main_container.pack_propagate(False)

        # Header
        header = tk.Frame(self.main_container, bg='#1e40af', height=100)
        header.pack(fill='x')
        header.pack_propagate(False)

        # Kapatma butonu (X) - header içinde sağ üst köşe
        close_btn = tk.Button(header, text="", font=('Segoe UI', 14, 'bold'),
                             bg='#e74c3c', fg='white', relief='flat', cursor='hand2',
                             command=self.close_wizard, width=3, height=1)
        close_btn.pack(side='right', padx=12, pady=12)

        tk.Label(header, text=" " + self.lm.tr('onboarding_welcome_header', "Sustainage'ye Hoş Geldiniz!"),
                font=('Segoe UI', 20, 'bold'), fg='white', bg='#1e40af').pack(pady=30)

        # Content area with scrollbar
        content_container = tk.Frame(self.main_container, bg='white')
        content_container.pack(fill='both', expand=True, padx=30, pady=20)

        # Scrollable frame
        self.canvas = tk.Canvas(content_container, bg='white', highlightthickness=0)
        self.scrollbar = tk.Scrollbar(content_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Content area referansı
        self.content_area = self.scrollable_frame

        # Mouse wheel binding
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

        # Footer - Navigation
        footer = tk.Frame(self.main_container, bg='#f5f5f5', height=80)
        footer.pack(fill='x', side='bottom')
        footer.pack_propagate(False)

        # Progress indicator
        self.progress_label = tk.Label(footer, text=f"{self.lm.tr('step', 'Adım')} 1 / {self.total_steps}",
                                       font=('Segoe UI', 10), bg='#f5f5f5', fg='#666')
        self.progress_label.pack(pady=10)

        # "Bir daha gösterme" checkbox - daha belirgin
        self.dont_show_var = tk.BooleanVar()
        dont_show_check = tk.Checkbutton(footer, text=f"️ {self.lm.tr('dont_show_again', 'Bir daha gösterme')}",
                                        variable=self.dont_show_var,
                                        font=('Segoe UI', 10, 'bold'), bg='#f5f5f5', fg='#e74c3c',
                                        selectcolor='#3498db', activebackground='#f5f5f5',
                                        activeforeground='#e74c3c')
        dont_show_check.pack(side='left', padx=30, pady=10)

        # Butonlar
        button_frame = tk.Frame(footer, bg='#f5f5f5')
        button_frame.pack(fill='x', padx=30, pady=(0, 10))

        # Atla butonu
        self.skip_btn = tk.Button(button_frame, text=f"{Icons.NEXT} {self.lm.tr('skip', 'Atla')}",
                                  font=('Segoe UI', 10), bg='#95a5a6', fg='white',
                                  relief='flat', cursor='hand2', padx=20, pady=8,
                                  command=self.skip_tour)
        self.skip_btn.pack(side='left')

        # Geri butonu
        self.back_btn = tk.Button(button_frame, text=f"{Icons.LEFT} {self.lm.tr('btn_back', 'Geri')}",
                                  font=('Segoe UI', 10), bg='#7f8c8d', fg='white',
                                  relief='flat', cursor='hand2', padx=20, pady=8,
                                  command=self.previous_step, state='disabled')
        self.back_btn.pack(side='left', padx=10)

        # İleri/Bitir butonu
        self.next_btn = tk.Button(button_frame, text=f"{self.lm.tr('btn_next', 'İleri')} ️",
                                  font=('Segoe UI', 10, 'bold'), bg='#3498db', fg='white',
                                  relief='flat', cursor='hand2', padx=20, pady=8,
                                  command=self.next_step)
        self.next_btn.pack(side='right')

        # İlk adımı göster
        self.show_current_step()

    def _on_mousewheel(self, event) -> None:
        """Mouse wheel ile scroll"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _update_scroll_region(self) -> None:
        """Scroll region'ı güncelle"""
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def close_wizard(self) -> None:
        """Wizard'ı kapat"""
        from tkinter import messagebox

        # "Bir daha gösterme" kutucuğu işaretli mi kontrol et
        dont_show_again = getattr(self, 'dont_show_var', None) and self.dont_show_var.get()

        if dont_show_again:
            # Kutucuk işaretliyse direkt kapat
            self.complete_tour()
        else:
            # Kutucuk işaretli değilse onay iste
            if messagebox.askyesno(self.lm.tr('btn_close', "Kapat"),
                                  self.lm.tr('onboarding_close_confirm', "İlk kullanım turunu kapatmak istediğinizden emin misiniz?\n\nTuru tekrar görmek istemiyorsanız 'Bir daha gösterme' kutucuğunu işaretleyin.")):
                self.complete_tour()

    def show_current_step(self) -> None:
        """Mevcut adımı göster"""
        # Content area'yı temizle
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # Progress güncel
        self.progress_label.config(text=f"{self.lm.tr('step', 'Adım')} {self.current_step + 1} / {self.total_steps}")

        # Geri butonunu kontrol et
        self.back_btn.config(state='normal' if self.current_step > 0 else 'disabled')

        # İleri butonu metni
        if self.current_step == self.total_steps - 1:
            self.next_btn.config(text=f" {self.lm.tr('lets_start', 'Başlayalım!')}", bg='#27ae60')
        else:
            self.next_btn.config(text=f"{self.lm.tr('btn_next', 'İleri')} ️", bg='#3498db')

        # Adım içeriğini göster
        steps = [
            self.step_welcome,
            self.step_dashboard,
            self.step_modules,
            self.step_data_entry,
            self.step_reporting,
            self.step_help
        ]

        if self.current_step < len(steps):
            steps[self.current_step]()

        # Scroll region'ı güncelle
        self._update_scroll_region()

    def step_welcome(self) -> None:
        """Adım 1: Hoş geldiniz"""
        tk.Label(self.content_area, text=f" {self.lm.tr('onboarding_title', 'Sürdürülebilirlik Yönetimi Platformu')}",
                font=('Segoe UI', 18, 'bold'), bg='white', fg='#2c3e50').pack(pady=(20, 10))

        tk.Label(self.content_area,
                text=self.lm.tr('onboarding_desc', "SUSTAINAGE, sürdürülebilirlik verilerinizi toplamak, analiz etmek\nve raporlamak için tasarlanmış kapsamlı bir platformdur."),
                font=('Segoe UI', 11), bg='white', fg='#555', justify='center').pack(pady=10)

        # Özellikler listesi
        features_frame = tk.Frame(self.content_area, bg='white')
        features_frame.pack(pady=20)

        features = [
            ("", self.lm.tr('feature_1_title', "SDG, GRI ve TSRS Standartları"), self.lm.tr('feature_1_desc', "Uluslararası raporlama standartlarına tam uyum")),
            ("", self.lm.tr('feature_2_title', "Otomatik Görev Yönetimi"), self.lm.tr('feature_2_desc', "Veri toplama süreçlerini kolaylaştırın")),
            ("", self.lm.tr('feature_3_title', "Gelişmiş Analizler"), self.lm.tr('feature_3_desc', "Verilerinizi görselleştirin ve analiz edin")),
            ("", self.lm.tr('feature_4_title', "Profesyonel Raporlar"), self.lm.tr('feature_4_desc', "Tek tıkla raporlarınızı oluşturun")),
            ("", self.lm.tr('feature_5_title', "Güvenli ve Uyumlu"), self.lm.tr('feature_5_desc', "GDPR/KVKK uyumlu, güvenli veri yönetimi"))
        ]

        for icon, title, desc in features:
            feature_row = tk.Frame(features_frame, bg='white')
            feature_row.pack(fill='x', pady=8)

            tk.Label(feature_row, text=icon, font=('Segoe UI', 16), bg='white').pack(side='left', padx=10)

            text_frame = tk.Frame(feature_row, bg='white')
            text_frame.pack(side='left', fill='x')

            tk.Label(text_frame, text=title, font=('Segoe UI', 11, 'bold'),
                    bg='white', fg='#2c3e50', anchor='w').pack(fill='x')
            tk.Label(text_frame, text=desc, font=('Segoe UI', 9),
                    bg='white', fg='#7f8c8d', anchor='w').pack(fill='x')

    def step_dashboard(self) -> None:
        """Adım 2: Dashboard tanıtımı"""
        tk.Label(self.content_area, text=f" {self.lm.tr('dashboard_title', 'Dashboard - Merkezi Kontrol Paneli')}",
                font=('Segoe UI', 16, 'bold'), bg='white', fg='#2c3e50').pack(pady=(20, 10))

        tk.Label(self.content_area,
                text=self.lm.tr('dashboard_desc', "Dashboard, tüm sürdürülebilirlik verilerinizin özet görünümüdür.\nBurada hızlı metriklere, grafikleresve önemli bildirimlere erişebilirsiniz."),
                font=('Segoe UI', 10), bg='white', fg='#555', justify='center').pack(pady=10)

        # Dashboard özellikleri
        info_frame = tk.LabelFrame(self.content_area, text=self.lm.tr('dashboard_features', "Dashboard Özellikleri"),
                                   bg='white', font=('Segoe UI', 11, 'bold'), fg='#3498db')
        info_frame.pack(fill='both', expand=True, padx=20, pady=20)

        features = [
            f" {self.lm.tr('dashboard_feature_1', 'Gerçek zamanlı KPI kartları (Toplam görev, tamamlanma oranı, vb.)')}",
            f" {self.lm.tr('dashboard_feature_2', 'İlerleme grafikleri ve trend analizleri')}",
            f" {self.lm.tr('dashboard_feature_3', 'Görev durumu ve deadline takibi')}",
            f" {self.lm.tr('dashboard_feature_4', 'Hızlı erişim kısayolları')}",
            f" {self.lm.tr('dashboard_feature_5', 'Sistem bildirimleri ve uyarılar')}",
            f" {self.lm.tr('dashboard_feature_6', 'Gelişmiş Dashboard: Departman ve kullanıcı bazlı detaylı analiz (Ctrl+Shift+D)')}"
        ]

        for feature in features:
            tk.Label(info_frame, text=feature, font=('Segoe UI', 10),
                    bg='white', fg='#2c3e50', anchor='w', padx=20, pady=5).pack(fill='x')

        # İpucu
        tip_frame = tk.Frame(self.content_area, bg='#fff3cd', relief='solid', bd=1)
        tip_frame.pack(fill='x', padx=20, pady=(10, 0))

        tk.Label(tip_frame, text=f" {self.lm.tr('tip', 'İpucu')}:", font=('Segoe UI', 10, 'bold'),
                bg='#fff3cd', fg='#856404').pack(side='left', padx=10, pady=8)
        tk.Label(tip_frame, text=self.lm.tr('dashboard_tip_text', "F5 tuşu ile herhangi bir sayfayı yenileyebilirsiniz."),
                font=('Segoe UI', 9), bg='#fff3cd', fg='#856404').pack(side='left', pady=8)

    def step_modules(self) -> None:
        """Adım 3: Modüller tanıtımı"""
        tk.Label(self.content_area, text=f" {self.lm.tr('main_modules', 'Ana Modüller')}",
                font=('Segoe UI', 16, 'bold'), bg='white', fg='#2c3e50').pack(pady=(20, 10))

        tk.Label(self.content_area,
                text=self.lm.tr('modules_desc', "Sol menüden tüm modüllere erişebilirsiniz.\nHer modül belirli bir sürdürülebilirlik alanını yönetir."),
                font=('Segoe UI', 10), bg='white', fg='#555', justify='center').pack(pady=10)

        # Modül listesi
        modules_frame = tk.Frame(self.content_area, bg='white')
        modules_frame.pack(fill='both', expand=True, pady=10)

        # Sol kolon
        left_col = tk.Frame(modules_frame, bg='white')
        left_col.pack(side='left', fill='both', expand=True, padx=10)

        left_modules = [
            (f" {self.lm.tr('module_sdg', 'SDG Modülü')}", self.lm.tr('module_sdg_desc', "17 Sürdürülebilir Kalkınma Amacı")),
            (f" {self.lm.tr('module_gri', 'GRI Standartları')}", self.lm.tr('module_gri_desc', "Global Reporting Initiative")),
            (f" {self.lm.tr('module_tsrs', 'TSRS Standartları')}", self.lm.tr('module_tsrs_desc', "Türkiye Sürdürülebilirlik Raporlama")),
            (f" {self.lm.tr('module_esg', 'ESG Modülü')}", self.lm.tr('module_esg_desc', "Çevre, Sosyal, Yönetişim")),
            (f" {self.lm.tr('module_skdm', 'SKDM Modülü')}", self.lm.tr('module_skdm_desc', "Sınır Ötesi Karbon Düzenleme"))
        ]

        for title, desc in left_modules:
            module_frame = tk.Frame(left_col, bg='#ecf0f1', relief='groove', bd=1)
            module_frame.pack(fill='x', pady=5)

            tk.Label(module_frame, text=title, font=('Segoe UI', 10, 'bold'),
                    bg='#ecf0f1', fg='#2c3e50', anchor='w').pack(fill='x', padx=10, pady=(8, 2))
            tk.Label(module_frame, text=desc, font=('Segoe UI', 9),
                    bg='#ecf0f1', fg='#7f8c8d', anchor='w').pack(fill='x', padx=10, pady=(0, 8))

        # Sağ kolon
        right_col = tk.Frame(modules_frame, bg='white')
        right_col.pack(side='right', fill='both', expand=True, padx=10)

        right_modules = [
            (f" {self.lm.tr('strategic_management', 'Stratejik Yönetim')}", self.lm.tr('strategic_management_desc', "CEO Mesajı, Riskler, Hedefler")),
            (f" {self.lm.tr('my_tasks', 'Görevlerim')}", self.lm.tr('my_tasks_desc', "Kişisel görev yönetimi")),
            (f" {self.lm.tr('my_surveys', 'Anketlerim')}", self.lm.tr('my_surveys_desc', "Paydaş anketleri ve değerlendirme")),
            (f" {self.lm.tr('reports', 'Raporlar')}", self.lm.tr('reports_desc', "Kapsamlı raporlama merkezi")),
            (f"️ {self.lm.tr('management', 'Yönetim')}", self.lm.tr('management_desc', "Sistem ayarları ve kullanıcı yönetimi"))
        ]

        for title, desc in right_modules:
            module_frame = tk.Frame(right_col, bg='#e8f5e9', relief='groove', bd=1)
            module_frame.pack(fill='x', pady=5)

            tk.Label(module_frame, text=title, font=('Segoe UI', 10, 'bold'),
                    bg='#e8f5e9', fg='#2c3e50', anchor='w').pack(fill='x', padx=10, pady=(8, 2))
            tk.Label(module_frame, text=desc, font=('Segoe UI', 9),
                    bg='#e8f5e9', fg='#558b2f', anchor='w').pack(fill='x', padx=10, pady=(0, 8))

    def step_data_entry(self) -> None:
        """Adım 4: Veri girişi"""
        tk.Label(self.content_area, text=f" {self.lm.tr('data_entry_title', 'Veri Toplama ve Girişi')}",
                font=('Segoe UI', 16, 'bold'), bg='white', fg='#2c3e50').pack(pady=(20, 10))

        tk.Label(self.content_area,
                text=self.lm.tr('data_entry_desc', "Sürdürülebilirlik verilerinizi sisteme girmenin birkaç yolu vardır."),
                font=('Segoe UI', 10), bg='white', fg='#555', justify='center').pack(pady=10)

        # Veri giriş yöntemleri
        methods_frame = tk.Frame(self.content_area, bg='white')
        methods_frame.pack(fill='both', expand=True, pady=10)

        methods = [
            {
                'icon': '',
                'title': self.lm.tr('manual_data_entry', 'Manuel Veri Girişi'),
                'desc': self.lm.tr('manual_data_entry_desc', 'Her modülde form tabanlı veri girişi yapabilirsiniz.'),
                'steps': [f"• {self.lm.tr('open_module', 'Modülü açın')}", f"• {self.lm.tr('click_data_entry', 'Veri Girişi butonuna tıklayın')}", f"• {self.lm.tr('fill_form', 'Formu doldurun ve kaydedin')}"]
            },
            {
                'icon': '',
                'title': self.lm.tr('bulk_data_import', 'Toplu Veri İçe Aktarımı'),
                'desc': self.lm.tr('bulk_data_import_desc', 'Excel veya CSV dosyalarından toplu veri yükleyin.'),
                'steps': [f"• {self.lm.tr('bulk_import_step_1', 'Görevlerim sayfasında Veri İçe Aktarım butonuna tıklayın')}",
                          f"• {self.lm.tr('bulk_import_step_2', 'Dosyanızı seçin ve yükleyin')}", f"• {self.lm.tr('bulk_import_step_3', 'Sütunları eşleştirin ve onaylayın')}"]
            },
            {
                'icon': '',
                'title': self.lm.tr('auto_task_system', 'Otomatik Görev Sistemi'),
                'desc': self.lm.tr('auto_task_system_desc', 'Sistem otomatik olarak veri toplama görevleri oluşturur.'),
                'steps': [f"• {self.lm.tr('auto_task_step_1', 'Görevlerim sayfasında Otomatik Görevler kısayolunu kullanın')}",
                          f"• {self.lm.tr('auto_task_step_2', 'SDG/GRI/TSRS seçimlerinize göre görevler oluşturulur')}",
                          f"• {self.lm.tr('auto_task_step_3', 'Görevleri tamamlayın')}"]
            }
        ]

        for method in methods:
            method_frame = tk.LabelFrame(methods_frame, text=f"{method['icon']} {method['title']}",
                                        bg='white', font=('Segoe UI', 10, 'bold'), fg='#3498db')
            method_frame.pack(fill='x', padx=20, pady=8)

            tk.Label(method_frame, text=method['desc'], font=('Segoe UI', 9),
                    bg='white', fg='#555', wraplength=700, justify='left').pack(fill='x', padx=10, pady=(5, 2))

            for step in method['steps']:
                tk.Label(method_frame, text=step, font=('Segoe UI', 9),
                        bg='white', fg='#7f8c8d', anchor='w').pack(fill='x', padx=20, pady=1)

    def step_reporting(self) -> None:
        """Adım 5: Raporlama"""
        tk.Label(self.content_area, text=f" {self.lm.tr('reporting_analysis', 'Raporlama ve Analiz')}",
                font=('Segoe UI', 16, 'bold'), bg='white', fg='#2c3e50').pack(pady=(20, 10))

        tk.Label(self.content_area,
                text=self.lm.tr('reporting_analysis_desc', "Verilerinizi profesyonel raporlara dönüştürün."),
                font=('Segoe UI', 10), bg='white', fg='#555', justify='center').pack(pady=10)

        # Rapor türleri
        reports_frame = tk.Frame(self.content_area, bg='white')
        reports_frame.pack(fill='both', expand=True, pady=10)

        reports = [
            (f" {self.lm.tr('sdg_report_title', 'SDG Raporu')}", self.lm.tr('sdg_report_desc', "Sürdürülebilir Kalkınma Amaçları raporu"), "#3498db"),
            (f" {self.lm.tr('gri_report_title', 'GRI Raporu')}", self.lm.tr('gri_report_desc', "Global Reporting Initiative standardı"), "#27ae60"),
            (f" {self.lm.tr('tsrs_report_title', 'TSRS Raporu')}", self.lm.tr('tsrs_report_desc', "Türkiye Sürdürülebilirlik Raporu"), "#e67e22"),
            (f" {self.lm.tr('esg_report_title', 'ESG Raporu')}", self.lm.tr('esg_report_desc', "Çevre, Sosyal, Yönetişim raporu"), "#9b59b6"),
            (f" {self.lm.tr('advanced_analysis_title', 'Gelişmiş Analiz')}", self.lm.tr('advanced_analysis_desc', "Özel metrikler ve karşılaştırmalar"), "#f39c12")
        ]

        for title, desc, color in reports:
            report_card = tk.Frame(reports_frame, bg=color, relief='groove', bd=2)
            report_card.pack(fill='x', padx=20, pady=5)

            tk.Label(report_card, text=title, font=('Segoe UI', 11, 'bold'),
                    bg=color, fg='white', anchor='w').pack(fill='x', padx=15, pady=(10, 2))
            tk.Label(report_card, text=desc, font=('Segoe UI', 9),
                    bg=color, fg='#ecf0f1', anchor='w').pack(fill='x', padx=15, pady=(0, 10))

        # Rapor oluşturma adımları
        steps_frame = tk.LabelFrame(self.content_area, text=self.lm.tr('report_creation_steps', "Rapor Oluşturma Adımları"),
                                    bg='white', font=('Segoe UI', 10, 'bold'))
        steps_frame.pack(fill='x', padx=20, pady=(15, 0))

        steps = [
            f"1. {self.lm.tr('report_step_1', 'Sol menüden Raporlar modülünü açın')}",
            f"2. {self.lm.tr('report_step_2', 'Rapor türünü seçin')}",
            f"3. {self.lm.tr('report_step_3', 'Dönem ve filtre seçeneklerini ayarlayın')}",
            f"4. {self.lm.tr('report_step_4', 'Rapor Oluştur butonuna tıklayın')}",
            f"5. {self.lm.tr('report_step_5', 'Raporu PDF olarak indirin veya yazdırın')}"
        ]

        for step in steps:
            tk.Label(steps_frame, text=step, font=('Segoe UI', 9),
                    bg='white', fg='#2c3e50', anchor='w').pack(fill='x', padx=15, pady=3)

    def step_help(self) -> None:
        """Adım 6: Yardım ve destek"""
        tk.Label(self.content_area, text=f" {self.lm.tr('help_support', 'Yardım ve Destek')}",
                font=('Segoe UI', 16, 'bold'), bg='white', fg='#2c3e50').pack(pady=(20, 10))

        tk.Label(self.content_area,
                text=self.lm.tr('help_support_desc', "İhtiyacınız olduğunda her zaman yardım alabileceğiniz kaynaklar."),
                font=('Segoe UI', 10), bg='white', fg='#555', justify='center').pack(pady=10)

        # Yardım kaynakları
        help_frame = tk.Frame(self.content_area, bg='white')
        help_frame.pack(fill='both', expand=True, pady=10)

        resources = [
            {
                'icon': '',
                'title': self.lm.tr('help_button', 'Yardım Butonu'),
                'desc': self.lm.tr('help_button_desc', 'Sol alt köşede bulunan "YARDIM" butonuna tıklayarak detaylı kullanım kılavuzuna erişebilirsiniz.'),
                'shortcut': self.lm.tr('help_shortcut', 'F1 veya Ctrl+H')
            },
            {
                'icon': '',
                'title': self.lm.tr('refresh_page', 'Sayfa Yenileme'),
                'desc': self.lm.tr('refresh_page_desc', 'Herhangi bir sayfayı yenilemek için F5 tuşunu kullanabilirsiniz.'),
                'shortcut': 'F5'
            },
            {
                'icon': Icons.LEFT,
                'title': self.lm.tr('go_back', 'Geri Gitme'),
                'desc': self.lm.tr('go_back_desc', 'Bir önceki sayfaya dönmek için "Geri" butonunu veya Escape tuşunu kullanın.'),
                'shortcut': self.lm.tr('back_shortcut', 'ESC veya Ctrl+B')
            },
            {
                'icon': '',
                'title': self.lm.tr('admin_panel', 'Super Admin Paneli'),
                'desc': self.lm.tr('admin_panel_desc', 'Sistem yöneticileri için gelişmiş ayarlar ve kullanıcı yönetimi.'),
                'shortcut': self.lm.tr('admin_shortcut', 'Sol alt köşede kırmızı buton')
            }
        ]

        for resource in resources:
            res_frame = tk.Frame(help_frame, bg='#f8f9fa', relief='solid', bd=1)
            res_frame.pack(fill='x', padx=20, pady=5)

            # Başlık
            title_frame = tk.Frame(res_frame, bg='#f8f9fa')
            title_frame.pack(fill='x', padx=15, pady=(10, 5))

            tk.Label(title_frame, text=resource['icon'], font=('Segoe UI', 14),
                    bg='#f8f9fa').pack(side='left', padx=(0, 10))
            tk.Label(title_frame, text=resource['title'], font=('Segoe UI', 11, 'bold'),
                    bg='#f8f9fa', fg='#2c3e50').pack(side='left')

            # Açıklama
            tk.Label(res_frame, text=resource['desc'], font=('Segoe UI', 9),
                    bg='#f8f9fa', fg='#555', wraplength=700, justify='left').pack(
                        fill='x', padx=15, pady=(0, 5))

            # Kısayol
            shortcut_frame = tk.Frame(res_frame, bg='#3498db', relief='flat')
            shortcut_frame.pack(fill='x', padx=15, pady=(0, 10))

            tk.Label(shortcut_frame, text=f"⌨️ {resource['shortcut']}", font=('Segoe UI', 9, 'bold'),
                    bg='#3498db', fg='white').pack(padx=10, pady=5)

        # Final mesaj
        final_frame = tk.Frame(self.content_area, bg='#d4edda', relief='solid', bd=2)
        final_frame.pack(fill='x', padx=20, pady=(15, 0))

        tk.Label(final_frame, text=f" {self.lm.tr('ready_to_start', 'Artık hazırsınız!')}",
                font=('Segoe UI', 12, 'bold'), bg='#d4edda', fg='#155724').pack(pady=(15, 5))
        tk.Label(final_frame,
                text=self.lm.tr('onboarding_final_desc', "Sürdürülebilirlik yolculuğunuzda başarılar dileriz.\nHerhangi bir sorunuz olduğunda yardım butonunu kullanmaktan çekinmeyin!"),
                font=('Segoe UI', 10), bg='#d4edda', fg='#155724', justify='center').pack(pady=(0, 15))

    def next_step(self) -> None:
        """Sonraki adıma geç"""
        if self.current_step < self.total_steps - 1:
            self.current_step += 1
            self.show_current_step()
        else:
            # Tour bitti
            self.complete_tour()

    def previous_step(self) -> None:
        """Önceki adıma dön"""
        if self.current_step > 0:
            self.current_step -= 1
            self.show_current_step()

    def skip_tour(self) -> None:
        """Turu atla"""
        from tkinter import messagebox
        if messagebox.askyesno(self.lm.tr('skip_tour_title', "Turu Atla"),
                              self.lm.tr('skip_tour_confirm', "İlk kullanım turunu atlamak istediğinizden emin misiniz?\n\nTuru dilediğiniz zaman Yardım menüsünden tekrar başlatabilirsiniz.")):
            self.complete_tour()

    def complete_tour(self) -> None:
        """Turu tamamla"""
        # "Bir daha gösterme" seçeneğini kontrol et
        if hasattr(self, 'dont_show_var') and self.dont_show_var.get():
            self.mark_dont_show_again()

        self.mark_tour_completed()
        self.wizard_window.destroy()

        if self.on_complete:
            self.on_complete()

    def mark_dont_show_again(self) -> None:
        """Bir daha gösterme seçeneğini kaydet - hem onboarding hem welcome banner için"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # User settings tablosunu oluştur
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY,
                    onboarding_completed INTEGER DEFAULT 0,
                    show_onboarding INTEGER DEFAULT 1,
                    show_welcome_banner INTEGER DEFAULT 1,
                    theme TEXT DEFAULT 'default',
                    language TEXT DEFAULT 'tr',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Hem onboarding hem de welcome banner ayarlarını güncelle
            cursor.execute("""
                INSERT OR REPLACE INTO user_settings (user_id, onboarding_completed, show_onboarding, show_welcome_banner)
                VALUES (?, 1, 0, 0)
            """, (self.user_id,))

            conn.commit()
            conn.close()
        except Exception as e:
            logging.info(f"Bir daha gösterme ayarı kaydedilemedi: {e}")


def show_onboarding(parent, db_path: str, user_id: int, on_complete: Optional[Callable] = None) -> None:
    """Onboarding wizard'ı göster"""
    OnboardingWizard(parent, db_path, user_id, on_complete)

