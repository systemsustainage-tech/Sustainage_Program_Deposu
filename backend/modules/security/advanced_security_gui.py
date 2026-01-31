#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Güvenlik Özellikleri GUI
Multi-factor authentication, IP whitelist, session recording, threat detection
"""

import logging
import tkinter as tk
from tkinter import messagebox, ttk
from config.icons import Icons

# İsteğe bağlı bağımlılıklar — eksikse modül yine yüklenir
try:
    import qrcode
except Exception:
    qrcode = None

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

try:
    import pyotp
except Exception:
    pyotp = None
import os
from datetime import datetime
from typing import Any, Dict, List

from .advanced_security_manager import AdvancedSecurityManager
from config.icons import Icons


class AdvancedSecurityGUI:
    """Gelişmiş Güvenlik Özellikleri GUI"""

    def __init__(self, parent, user_id: int) -> None:
        self.parent = parent
        self.user_id = user_id
        self.manager = AdvancedSecurityManager()
        # Bağımlılık durum bilgisi
        self._deps_info = {
            'pyotp': pyotp is not None,
            'qrcode': qrcode is not None,
            'Pillow': (Image is not None and ImageTk is not None)
        }

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Ana arayüzü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Başlık
        header_frame = tk.Frame(main_frame, bg='#e74c3c', height=70)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text=" Gelişmiş Güvenlik Özellikleri",
                              font=('Segoe UI', 18, 'bold'), fg='white', bg='#e74c3c')
        title_label.pack(side='left', padx=20, pady=15)

        subtitle_label = tk.Label(header_frame, text="Multi-Factor Authentication, IP Whitelist, Session Recording",
                                 font=('Segoe UI', 11), fg='#f4ecf7', bg='#e74c3c')
        subtitle_label.pack(side='left')

        # Eksik bağımlılık uyarısı
        if not all(self._deps_info.values()):
            missing = [name for name, ok in self._deps_info.items() if not ok]
            warn_text = (
                "Bazı güvenlik özellikleri için ek paketler gerekli: "
                + ", ".join(missing)
                + "\nKurulum: pip install pillow qrcode pyotp"
            )
            dep_warn = tk.Label(main_frame, text=warn_text,
                               font=('Segoe UI', 10), fg='#e67e22', bg='#f5f5f5', justify='left')
            dep_warn.pack(fill='x', padx=5, pady=(0, 10))

        # Ana notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Sekmeleri oluştur
        self.create_mfa_tab()
        self.create_ip_whitelist_tab()
        self.create_session_recording_tab()
        self.create_threat_detection_tab()
        self.create_penetration_testing_tab()
        self.create_security_dashboard_tab()

    def create_mfa_tab(self) -> None:
        """Multi-Factor Authentication sekmesi"""
        mfa_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(mfa_frame, text=" MFA")

        # Başlık
        title_frame = tk.Frame(mfa_frame, bg='#3498db', height=50)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="Multi-Factor Authentication (MFA)",
                font=('Segoe UI', 14, 'bold'), fg='white', bg='#3498db').pack(expand=True)

        # MFA durumu
        self.create_mfa_status(mfa_frame)

        # MFA kurulumu
        self.create_mfa_setup(mfa_frame)

        # Backup kodları
        self.create_backup_codes(mfa_frame)

    def create_mfa_status(self, parent) -> None:
        """MFA durumunu göster"""
        status_frame = tk.LabelFrame(parent, text="MFA Durumu",
                                    font=('Segoe UI', 12, 'bold'), bg='white')
        status_frame.pack(fill='x', padx=20, pady=20)

        # Durum bilgisi
        status_content = tk.Frame(status_frame, bg='white')
        status_content.pack(fill='x', padx=10, pady=10)

        # MFA durumu kontrolü
        # Burada gerçek MFA durumu kontrolü yapılacak

        self.mfa_status_label = tk.Label(status_content, text="MFA Durumu: Devre Dışı",
                                        font=('Segoe UI', 12), bg='white', fg='#e74c3c')
        self.mfa_status_label.pack(side='left')

        # MFA etkinleştir butonu
        self.enable_mfa_btn = tk.Button(status_content, text="MFA'yı Etkinleştir",
                                       font=('Segoe UI', 10, 'bold'), bg='#27ae60', fg='white',
                                       relief='flat', cursor='hand2', padx=20, pady=5,
                                       command=self.setup_mfa)
        self.enable_mfa_btn.pack(side='right')
        if not (self._deps_info['pyotp'] and self._deps_info['qrcode']):
            self.enable_mfa_btn.config(state='disabled')
            info = tk.Label(status_content,
                            text="MFA’yı etkinleştirmek için 'pyotp' ve 'qrcode' gereklidir.",
                            font=('Segoe UI', 9), fg='#7f8c8d', bg='white')
            info.pack(side='left')

    def create_mfa_setup(self, parent) -> None:
        """MFA kurulum bölümü"""
        setup_frame = tk.LabelFrame(parent, text="MFA Kurulumu",
                                   font=('Segoe UI', 12, 'bold'), bg='white')
        setup_frame.pack(fill='x', padx=20, pady=20)

        # Kurulum adımları
        steps_frame = tk.Frame(setup_frame, bg='white')
        steps_frame.pack(fill='x', padx=10, pady=10)

        steps_text = """
1. MFA'yı etkinleştir butonuna tıklayın
2. QR kodu telefonunuzdaki authenticator uygulaması ile tarayın
3. Uygulama tarafından verilen 6 haneli kodu girin
4. Backup kodlarınızı güvenli bir yerde saklayın
        """

        tk.Label(steps_frame, text=steps_text, font=('Segoe UI', 10),
                bg='white', justify='left').pack(anchor='w')

        # QR kod alanı
        self.qr_frame = tk.Frame(setup_frame, bg='white')
        self.qr_frame.pack(fill='x', padx=10, pady=10)

        # MFA kodu girişi
        code_frame = tk.Frame(setup_frame, bg='white')
        code_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(code_frame, text="MFA Kodu:", font=('Segoe UI', 10, 'bold'), bg='white').pack(side='left')

        self.mfa_code_var = tk.StringVar()
        self.mfa_code_entry = tk.Entry(code_frame, textvariable=self.mfa_code_var,
                                     font=('Segoe UI', 12), width=10)
        self.mfa_code_entry.pack(side='left', padx=(10, 0))

        verify_btn = tk.Button(code_frame, text="Doğrula",
                              font=('Segoe UI', 10, 'bold'), bg='#3498db', fg='white',
                              relief='flat', cursor='hand2', padx=15, pady=5,
                              command=self.verify_mfa_code)
        verify_btn.pack(side='left', padx=(10, 0))

    def create_backup_codes(self, parent) -> None:
        """Backup kodları bölümü"""
        backup_frame = tk.LabelFrame(parent, text="Backup Kodları",
                                    font=('Segoe UI', 12, 'bold'), bg='white')
        backup_frame.pack(fill='x', padx=20, pady=20)

        # Backup kodları listesi
        self.backup_codes_listbox = tk.Listbox(backup_frame, font=('Courier', 10), height=6)
        self.backup_codes_listbox.pack(fill='x', padx=10, pady=10)

        # Backup kodları yenile butonu
        refresh_btn = tk.Button(backup_frame, text="Backup Kodlarını Yenile",
                               font=('Segoe UI', 10, 'bold'), bg='#f39c12', fg='white',
                               relief='flat', cursor='hand2', padx=15, pady=5,
                               command=self.refresh_backup_codes)
        refresh_btn.pack(side='right', padx=10, pady=10)

    def create_ip_whitelist_tab(self) -> None:
        """IP Whitelist sekmesi"""
        ip_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(ip_frame, text=" IP Whitelist")

        # Başlık
        title_frame = tk.Frame(ip_frame, bg='#9b59b6', height=50)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="IP Whitelist Yönetimi",
                font=('Segoe UI', 14, 'bold'), fg='white', bg='#9b59b6').pack(expand=True)

        # IP ekleme formu
        self.create_ip_add_form(ip_frame)

        # IP listesi
        self.create_ip_list(ip_frame)

    def create_ip_add_form(self, parent) -> None:
        """IP ekleme formu"""
        form_frame = tk.LabelFrame(parent, text="Yeni IP Ekle",
                                  font=('Segoe UI', 12, 'bold'), bg='white')
        form_frame.pack(fill='x', padx=20, pady=20)

        # Form alanları
        form_content = tk.Frame(form_frame, bg='white')
        form_content.pack(fill='x', padx=10, pady=10)

        # IP adresi
        tk.Label(form_content, text="IP Adresi:", font=('Segoe UI', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.ip_address_var = tk.StringVar()
        ip_entry = tk.Entry(form_content, textvariable=self.ip_address_var, font=('Segoe UI', 10), width=20)
        ip_entry.grid(row=0, column=1, padx=(10, 0), pady=5)

        # Açıklama
        tk.Label(form_content, text="Açıklama:", font=('Segoe UI', 10, 'bold'), bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.ip_description_var = tk.StringVar()
        desc_entry = tk.Entry(form_content, textvariable=self.ip_description_var, font=('Segoe UI', 10), width=30)
        desc_entry.grid(row=1, column=1, padx=(10, 0), pady=5)

        # Ekle butonu
        add_btn = tk.Button(form_content, text="IP Ekle",
                           font=('Segoe UI', 10, 'bold'), bg='#27ae60', fg='white',
                           relief='flat', cursor='hand2', padx=20, pady=5,
                           command=self.add_ip_to_whitelist)
        add_btn.grid(row=2, column=1, sticky='e', pady=10)

    def create_ip_list(self, parent) -> None:
        """IP listesi"""
        list_frame = tk.LabelFrame(parent, text="Whitelist'teki IP'ler",
                                  font=('Segoe UI', 12, 'bold'), bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # IP tablosu
        columns = ('IP Adresi', 'Açıklama', 'Durum', 'Eklenme Tarihi', 'İşlemler')

        self.ip_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)

        for col in columns:
            self.ip_tree.heading(col, text=col)
            self.ip_tree.column(col, width=120, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.ip_tree.yview)
        self.ip_tree.configure(yscrollcommand=scrollbar.set)

        self.ip_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')

    def create_session_recording_tab(self) -> None:
        """Session Recording sekmesi"""
        session_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(session_frame, text=" Session Recording")

        # Başlık
        title_frame = tk.Frame(session_frame, bg='#2c3e50', height=50)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="Session Recording ve İzleme",
                font=('Segoe UI', 14, 'bold'), fg='white', bg='#2c3e50').pack(expand=True)

        # Session istatistikleri
        self.create_session_stats(session_frame)

        # Session listesi
        self.create_session_list(session_frame)

    def create_session_stats(self, parent) -> None:
        """Session istatistikleri - Gerçek verilerle"""
        stats_frame = tk.LabelFrame(parent, text="Session İstatistikleri",
                                   font=('Segoe UI', 12, 'bold'), bg='white')
        stats_frame.pack(fill='x', padx=20, pady=20)

        # İstatistik kartları
        stats_content = tk.Frame(stats_frame, bg='white')
        stats_content.pack(fill='x', padx=10, pady=10)

        # Gerçek verileri al
        session_stats = self._get_real_session_stats()

        stats = [
            ("Aktif Session", str(session_stats['active_sessions']), "#27ae60", Icons.UNLOCK),
            ("Toplam Session", str(session_stats['total_sessions']), "#3498db", Icons.REPORT),
            ("Bugünkü Giriş", str(session_stats['today_logins']), "#f39c12", Icons.CALENDAR),
            ("Ortalama Süre", session_stats['avg_duration'], "#9b59b6", "⏱️")
        ]

        for i, (title, value, color, icon) in enumerate(stats):
            card = tk.Frame(stats_content, bg=color, relief='raised', bd=2)
            card.pack(side='left', fill='x', expand=True, padx=5)

            # İkon ve başlık
            header_frame = tk.Frame(card, bg=color)
            header_frame.pack(fill='x', padx=10, pady=(10, 5))

            tk.Label(header_frame, text=icon, font=('Segoe UI', 16),
                    bg=color, fg='white').pack(side='left')
            tk.Label(header_frame, text=title, font=('Segoe UI', 10, 'bold'),
                    bg=color, fg='white').pack(side='left', padx=(5, 0))

            # Değer
            tk.Label(card, text=value, font=('Segoe UI', 18, 'bold'),
                    bg=color, fg='white').pack(pady=(0, 10))

    def create_session_list(self, parent) -> None:
        """Session listesi"""
        list_frame = tk.LabelFrame(parent, text="Session Kayıtları",
                                  font=('Segoe UI', 12, 'bold'), bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Session tablosu
        columns = ('Session ID', 'IP Adresi', 'Giriş Zamanı', 'Çıkış Zamanı', 'Aksiyon Sayısı', 'Durum')

        self.session_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)

        for col in columns:
            self.session_tree.heading(col, text=col)
            self.session_tree.column(col, width=120, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.session_tree.yview)
        self.session_tree.configure(yscrollcommand=scrollbar.set)

        self.session_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')

    def create_threat_detection_tab(self) -> None:
        """Threat Detection sekmesi"""
        threat_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(threat_frame, text="️ Threat Detection")

        # Başlık
        title_frame = tk.Frame(threat_frame, bg='#e67e22', height=50)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="Tehdit Tespiti ve Analizi",
                font=('Segoe UI', 14, 'bold'), fg='white', bg='#e67e22').pack(expand=True)

        # Tehdit istatistikleri
        self.create_threat_stats(threat_frame)

        # Tehdit listesi
        self.create_threat_list(threat_frame)

    def create_threat_stats(self, parent) -> None:
        """Tehdit istatistikleri - Gerçek verilerle"""
        stats_frame = tk.LabelFrame(parent, text="Tehdit İstatistikleri",
                                   font=('Segoe UI', 12, 'bold'), bg='white')
        stats_frame.pack(fill='x', padx=20, pady=20)

        # İstatistik kartları
        stats_content = tk.Frame(stats_frame, bg='white')
        stats_content.pack(fill='x', padx=10, pady=10)

        # Gerçek verileri al
        threat_stats = self._get_real_threat_stats()

        stats = [
            ("Aktif Tehdit", str(threat_stats['active_threats']), "#e74c3c", "🔴"),
            ("Kritik Tehdit", str(threat_stats['critical_threats']), "#8e44ad", Icons.WARNING),
            ("Yüksek Tehdit", str(threat_stats['high_threats']), "#e67e22", "🟠"),
            ("Orta Tehdit", str(threat_stats['medium_threats']), "#f39c12", "🟡")
        ]

        # Kartları oluştur
        self.threat_stat_cards = {}
        for i, (title, value, color, icon) in enumerate(stats):
            card = tk.Frame(stats_content, bg=color, relief='raised', bd=2)
            card.pack(side='left', fill='x', expand=True, padx=5)

            # İkon ve başlık
            header_frame = tk.Frame(card, bg=color)
            header_frame.pack(fill='x', padx=10, pady=(10, 5))

            tk.Label(header_frame, text=icon, font=('Segoe UI', 16),
                    bg=color, fg='white').pack(side='left')
            tk.Label(header_frame, text=title, font=('Segoe UI', 10, 'bold'),
                    bg=color, fg='white').pack(side='left', padx=(5, 0))

            # Değer (dinamik olarak güncellenebilir)
            value_label = tk.Label(card, text=value, font=('Segoe UI', 18, 'bold'),
                    bg=color, fg='white')
            value_label.pack(pady=(0, 10))

            # Referansı sakla
            self.threat_stat_cards[title] = value_label

    def create_threat_list(self, parent) -> None:
        """Tehdit listesi"""
        list_frame = tk.LabelFrame(parent, text="Tespit Edilen Tehditler",
                                  font=('Segoe UI', 12, 'bold'), bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Toolbar
        toolbar = tk.Frame(list_frame, bg='white')
        toolbar.pack(fill='x', padx=10, pady=(10, 0))

        scan_btn = tk.Button(toolbar, text=f"{Icons.SEARCH} Tehdit Taraması Yap",
                            font=('Segoe UI', 10, 'bold'), bg='#e74c3c', fg='white',
                            relief='flat', cursor='hand2', padx=15, pady=5,
                            command=self.scan_threats)
        scan_btn.pack(side='left', padx=5)

        refresh_btn = tk.Button(toolbar, text=f"{Icons.LOADING} Yenile",
                               font=('Segoe UI', 10, 'bold'), bg='#3498db', fg='white',
                               relief='flat', cursor='hand2', padx=15, pady=5,
                               command=self.refresh_threat_data)
        refresh_btn.pack(side='left', padx=5)

        resolve_btn = tk.Button(toolbar, text=f"{Icons.PASS} Seçileni Çöz",
                               font=('Segoe UI', 10, 'bold'), bg='#27ae60', fg='white',
                               relief='flat', cursor='hand2', padx=15, pady=5,
                               command=self.resolve_selected_threat)
        resolve_btn.pack(side='left', padx=5)

        # Tehdit tablosu
        columns = ('Tehdit Tipi', 'Seviye', 'Açıklama', 'IP Adresi', 'Tespit Zamanı', 'Durum')

        self.threat_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)

        for col in columns:
            self.threat_tree.heading(col, text=col)
            self.threat_tree.column(col, width=120, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.threat_tree.yview)
        self.threat_tree.configure(yscrollcommand=scrollbar.set)

        self.threat_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')

    def create_penetration_testing_tab(self) -> None:
        """Penetration Testing sekmesi"""
        pen_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(pen_frame, text=" Penetration Testing")

        # Başlık
        title_frame = tk.Frame(pen_frame, bg='#8e44ad', height=50)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="Penetration Testing ve Vulnerability Yönetimi",
                font=('Segoe UI', 14, 'bold'), fg='white', bg='#8e44ad').pack(expand=True)

        # Test oluşturma formu
        self.create_pen_test_form(pen_frame)

        # Test listesi
        self.create_pen_test_list(pen_frame)

    def create_pen_test_form(self, parent) -> None:
        """Penetration test oluşturma formu"""
        form_frame = tk.LabelFrame(parent, text="Yeni Penetration Test",
                                  font=('Segoe UI', 12, 'bold'), bg='white')
        form_frame.pack(fill='x', padx=20, pady=20)

        # Form alanları
        form_content = tk.Frame(form_frame, bg='white')
        form_content.pack(fill='x', padx=10, pady=10)

        # Test adı
        tk.Label(form_content, text="Test Adı:", font=('Segoe UI', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.test_name_var = tk.StringVar()
        test_name_entry = tk.Entry(form_content, textvariable=self.test_name_var, font=('Segoe UI', 10), width=30)
        test_name_entry.grid(row=0, column=1, padx=(10, 0), pady=5)

        # Test tipi
        tk.Label(form_content, text="Test Tipi:", font=('Segoe UI', 10, 'bold'), bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.test_type_var = tk.StringVar()
        test_type_combo = ttk.Combobox(form_content, textvariable=self.test_type_var,
                                      values=["Web Application", "Network", "Mobile", "API", "Infrastructure"], width=27)
        test_type_combo.grid(row=1, column=1, padx=(10, 0), pady=5)

        # Test eden
        tk.Label(form_content, text="Test Eden:", font=('Segoe UI', 10, 'bold'), bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.tester_name_var = tk.StringVar()
        tester_entry = tk.Entry(form_content, textvariable=self.tester_name_var, font=('Segoe UI', 10), width=30)
        tester_entry.grid(row=2, column=1, padx=(10, 0), pady=5)

        # Test oluştur butonu
        create_btn = tk.Button(form_content, text="Test Oluştur",
                              font=('Segoe UI', 10, 'bold'), bg='#27ae60', fg='white',
                              relief='flat', cursor='hand2', padx=20, pady=5,
                              command=self.create_penetration_test)
        create_btn.grid(row=3, column=1, sticky='e', pady=10)

    def create_pen_test_list(self, parent) -> None:
        """Penetration test listesi"""
        list_frame = tk.LabelFrame(parent, text="Penetration Testleri",
                                  font=('Segoe UI', 12, 'bold'), bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Test tablosu
        columns = ('Test Adı', 'Tip', 'Test Eden', 'Tarih', 'Vulnerability', 'Durum', 'İşlemler')

        self.pen_test_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)

        for col in columns:
            self.pen_test_tree.heading(col, text=col)
            self.pen_test_tree.column(col, width=120, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.pen_test_tree.yview)
        self.pen_test_tree.configure(yscrollcommand=scrollbar.set)

        self.pen_test_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')

    def create_security_dashboard_tab(self) -> None:
        """Güvenlik Dashboard sekmesi"""
        dashboard_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(dashboard_frame, text=" Dashboard")

        # Başlık
        title_frame = tk.Frame(dashboard_frame, bg='#34495e', height=50)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="Güvenlik Dashboard",
                font=('Segoe UI', 14, 'bold'), fg='white', bg='#34495e').pack(expand=True)

        # Dashboard kartları
        self.create_dashboard_cards(dashboard_frame)

        # Güvenlik raporu
        self.create_security_report(dashboard_frame)

    def create_dashboard_cards(self, parent) -> None:
        """Dashboard kartları"""
        cards_frame = tk.Frame(parent, bg='white')
        cards_frame.pack(fill='x', padx=20, pady=20)

        # Güvenlik metrikleri
        metrics = [
            ("MFA Etkin", "15", "#27ae60", ""),
            ("Whitelist IP", "8", "#3498db", ""),
            ("Aktif Session", "3", "#f39c12", ""),
            ("Tespit Tehdit", "2", "#e74c3c", "️"),
            ("Penetration Test", "5", "#9b59b6", ""),
            ("Güvenlik Skoru", "85/100", "#2ecc71", "️")
        ]

        for i, (title, value, color, icon) in enumerate(metrics):
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
            tk.Label(card, text=value, font=('Segoe UI', 18, 'bold'),
                    bg=color, fg='white').pack(pady=(0, 10))

    def create_security_report(self, parent) -> None:
        """Güvenlik raporu"""
        report_frame = tk.LabelFrame(parent, text="Güvenlik Raporu",
                                    font=('Segoe UI', 12, 'bold'), bg='white')
        report_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Rapor butonları
        buttons_frame = tk.Frame(report_frame, bg='white')
        buttons_frame.pack(fill='x', padx=10, pady=10)

        # Rapor oluştur butonu
        create_report_btn = tk.Button(buttons_frame, text="Güvenlik Raporu Oluştur",
                                    font=('Segoe UI', 12, 'bold'), bg='#e74c3c', fg='white',
                                    relief='flat', cursor='hand2', padx=30, pady=10,
                                    command=self.generate_security_report)
        create_report_btn.pack(side='left', padx=10)

        # Excel export butonu
        export_btn = tk.Button(buttons_frame, text="Excel'e Aktar",
                              font=('Segoe UI', 12, 'bold'), bg='#27ae60', fg='white',
                              relief='flat', cursor='hand2', padx=30, pady=10,
                              command=self.export_security_report)
        export_btn.pack(side='left', padx=10)

    # ==================== EVENT HANDLERS ====================

    def setup_mfa(self) -> None:
        """MFA kurulumu yap"""
        try:
            if not (self._deps_info['pyotp'] and self._deps_info['qrcode']):
                messagebox.showwarning(
                    "Eksik Paket",
                    "MFA kurulumu için 'pyotp' ve 'qrcode' paketleri gerekir.\n"
                    "Kurulum: pip install pyotp qrcode"
                )
                return
            result = self.manager.setup_mfa(self.user_id)

            if result['success']:
                # QR kodu göster
                self.show_qr_code(result['qr_path'])

                # Backup kodları göster
                self.show_backup_codes(result['backup_codes'])

                messagebox.showinfo("Başarılı", "MFA kurulumu tamamlandı! QR kodu tarayın ve kodu doğrulayın.")
            else:
                messagebox.showerror("Hata", f"MFA kurulum hatası: {result['error']}")

        except Exception as e:
            messagebox.showerror("Hata", f"MFA kurulum hatası: {e}")

    def show_qr_code(self, qr_path: str) -> None:
        """QR kodunu göster"""
        try:
            if Image is None or ImageTk is None:
                # Pillow yoksa dosya yolunu metin olarak göster
                tk.Label(self.qr_frame, text=f"QR kod: {qr_path}",
                         font=('Segoe UI', 10), fg='#2c3e50', bg='white').pack(pady=10)
            else:
                # QR kod resmini yükle
                qr_image = Image.open(qr_path)
                qr_image = qr_image.resize((200, 200), Image.Resampling.LANCZOS)
                qr_photo = ImageTk.PhotoImage(qr_image)

                # QR kod etiketi
                qr_label = tk.Label(self.qr_frame, image=qr_photo, bg='white')
                qr_label.image = qr_photo  # Referansı sakla
                qr_label.pack(pady=10)

        except Exception as e:
            logging.error(f"QR kod gösterim hatası: {e}")

    def show_backup_codes(self, backup_codes: List[str]) -> None:
        """Backup kodlarını göster"""
        # Mevcut kodları temizle
        self.backup_codes_listbox.delete(0, tk.END)

        # Yeni kodları ekle
        for code in backup_codes:
            self.backup_codes_listbox.insert(tk.END, code)

    def verify_mfa_code(self) -> None:
        """MFA kodunu doğrula"""
        try:
            code = self.mfa_code_var.get().strip()
            if pyotp is None:
                messagebox.showwarning(
                    "Eksik Paket",
                    "Kod doğrulama için 'pyotp' gereklidir. Kurulum: pip install pyotp"
                )
                return

            if not code:
                messagebox.showerror("Hata", "Lütfen MFA kodunu girin!")
                return

            if self.manager.verify_mfa_code(self.user_id, code):
                # MFA'yı etkinleştir
                if self.manager.enable_mfa(self.user_id):
                    self.mfa_status_label.config(text="MFA Durumu: Etkin", fg='#27ae60')
                    self.enable_mfa_btn.config(state='disabled')
                    messagebox.showinfo("Başarılı", "MFA başarıyla etkinleştirildi!")
                else:
                    messagebox.showerror("Hata", "MFA etkinleştirilemedi!")
            else:
                messagebox.showerror("Hata", "Geçersiz MFA kodu!")

        except Exception as e:
            messagebox.showerror("Hata", f"MFA doğrulama hatası: {e}")

    def refresh_backup_codes(self) -> None:
        """Backup kodlarını yenile"""
        try:
            import json
            import secrets
            import sqlite3
            conn = sqlite3.connect(self.manager.db_path)
            cur = conn.cursor()
            codes = [secrets.token_hex(4).upper() for _ in range(10)]
            cur.execute(
                """
                UPDATE mfa_settings SET backup_codes = ? WHERE user_id = ?
                """,
                (json.dumps(codes), self.user_id),
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", f"Backup kodları yenilendi. Toplam: {len(codes)} kod")
        except Exception as e:
            messagebox.showerror("Hata", f"Backup kodları yenilenemedi: {e}")

    def add_ip_to_whitelist(self) -> None:
        """IP'yi whitelist'e ekle"""
        try:
            ip_address = self.ip_address_var.get().strip()
            description = self.ip_description_var.get().strip()

            if not ip_address:
                messagebox.showerror("Hata", "Lütfen IP adresini girin!")
                return

            if self.manager.add_ip_to_whitelist(self.user_id, ip_address, description):
                messagebox.showinfo("Başarılı", "IP adresi whitelist'e eklendi!")
                self.load_ip_list()
                self.ip_address_var.set("")
                self.ip_description_var.set("")
            else:
                messagebox.showerror("Hata", "IP adresi eklenemedi!")

        except Exception as e:
            messagebox.showerror("Hata", f"IP ekleme hatası: {e}")

    def load_ip_list(self) -> None:
        """IP listesini yükle"""
        try:
            # Mevcut verileri temizle
            for item in self.ip_tree.get_children():
                self.ip_tree.delete(item)

            # IP'leri getir
            ips = self.manager.get_user_whitelisted_ips(self.user_id)

            for ip in ips:
                status = "Aktif" if ip['is_active'] else "Pasif"
                self.ip_tree.insert('', 'end', values=(
                    ip['ip_address'],
                    ip['description'] or "",
                    status,
                    ip['created_at'],
                    "Düzenle | Sil"
                ))

        except Exception as e:
            logging.error(f"IP listesi yükleme hatası: {e}")

    def create_penetration_test(self) -> None:
        """Penetration test oluştur"""
        try:
            test_name = self.test_name_var.get().strip()
            test_type = self.test_type_var.get().strip()
            tester_name = self.tester_name_var.get().strip()

            if not all([test_name, test_type, tester_name]):
                messagebox.showerror("Hata", "Lütfen tüm alanları doldurun!")
                return

            test_id = self.manager.create_penetration_test(
                test_name, test_type, datetime.now(), tester_name
            )

            if test_id:
                messagebox.showinfo("Başarılı", f"Penetration test oluşturuldu! Test ID: {test_id}")
                self.load_pen_test_list()
                self.test_name_var.set("")
                self.test_type_var.set("")
                self.tester_name_var.set("")
            else:
                messagebox.showerror("Hata", "Penetration test oluşturulamadı!")

        except Exception as e:
            messagebox.showerror("Hata", f"Penetration test oluşturma hatası: {e}")

    def load_pen_test_list(self) -> None:
        """Penetration test listesini yükle"""
        try:
            # Mevcut verileri temizle
            for item in self.pen_test_tree.get_children():
                self.pen_test_tree.delete(item)

            # Testleri getir
            tests = self.manager.get_penetration_tests()

            for test in tests:
                self.pen_test_tree.insert('', 'end', values=(
                    test['test_name'],
                    test['test_type'],
                    test['tester_name'],
                    test['test_date'],
                    test['vulnerabilities_found'],
                    test['status'],
                    "Detay | Rapor"
                ))

        except Exception as e:
            logging.error(f"Penetration test listesi yükleme hatası: {e}")

    def generate_security_report(self) -> None:
        """Güvenlik raporu oluştur"""
        try:
            report_data = self.manager.generate_security_report(self.user_id)

            # Rapor dosyası oluştur
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = f"reports/security_report_{timestamp}.txt"

            os.makedirs("reports", exist_ok=True)

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("GELİŞMİŞ GÜVENLİK RAPORU\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
                f.write(f"Kullanıcı ID: {self.user_id}\n\n")

                f.write("GÜVENLİK METRİKLERİ\n")
                f.write("-" * 20 + "\n")
                f.write(f"MFA Etkin Kullanıcı: {report_data.get('mfa_enabled_count', 0)}\n")
                f.write(f"Whitelist IP Sayısı: {report_data.get('whitelisted_ips_count', 0)}\n")
                f.write(f"Aktif Session: {report_data.get('active_sessions_count', 0)}\n")
                f.write(f"Aktif Tehdit: {report_data.get('active_threats_count', 0)}\n\n")

                f.write("GÜVENLİK OLAYLARI (Son 30 Gün)\n")
                f.write("-" * 30 + "\n")
                for severity, count in report_data.get('security_events', {}).items():
                    f.write(f"{severity}: {count}\n")
                f.write("\n")

                f.write("PENETRATION TEST İSTATİSTİKLERİ\n")
                f.write("-" * 30 + "\n")
                f.write(f"Test Sayısı: {report_data.get('penetration_tests_count', 0)}\n")
                f.write(f"Toplam Vulnerability: {report_data.get('total_vulnerabilities', 0)}\n")
                f.write(f"Kritik Vulnerability: {report_data.get('critical_vulnerabilities', 0)}\n")
                f.write(f"Yüksek Vulnerability: {report_data.get('high_vulnerabilities', 0)}\n")

            messagebox.showinfo("Başarılı", f"Güvenlik raporu oluşturuldu:\n{report_path}")

        except Exception as e:
            messagebox.showerror("Hata", f"Güvenlik raporu oluşturma hatası: {e}")

    def export_security_report(self) -> None:
        """Güvenlik raporunu CSV'ye aktar"""
        try:
            report_data = self.manager.generate_security_report(self.user_id)
            from datetime import datetime
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs("reports", exist_ok=True)
            path = f"reports/security_report_{ts}.csv"
            import csv
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Metric", "Value"])
                w.writerow(["mfa_enabled_count", report_data.get("mfa_enabled_count", 0)])
                w.writerow(["whitelisted_ips_count", report_data.get("whitelisted_ips_count", 0)])
                w.writerow(["active_sessions_count", report_data.get("active_sessions_count", 0)])
                w.writerow(["active_threats_count", report_data.get("active_threats_count", 0)])
                w.writerow(["penetration_tests_count", report_data.get("penetration_tests_count", 0)])
                w.writerow(["total_vulnerabilities", report_data.get("total_vulnerabilities", 0)])
                w.writerow(["critical_vulnerabilities", report_data.get("critical_vulnerabilities", 0)])
                w.writerow(["high_vulnerabilities", report_data.get("high_vulnerabilities", 0)])
            messagebox.showinfo("Başarılı", f"Güvenlik raporu CSV olarak dışa aktarıldı:\n{path}")
        except Exception as e:
            messagebox.showerror("Hata", f"CSV dışa aktarım hatası: {e}")

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            self.load_ip_list()
            self.load_pen_test_list()
            self.load_threat_list()
            self.load_session_list()
        except Exception as e:
            logging.error(f"Veri yükleme hatası: {e}")

    def _get_real_threat_stats(self) -> Dict[str, int]:
        """Gerçek tehdit istatistiklerini al"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.manager.db_path)
            cursor = conn.cursor()

            # Aktif tehditler (çözülmemiş)
            cursor.execute("""
                SELECT COUNT(*) FROM threat_detection 
                WHERE is_resolved = FALSE
            """)
            active_threats = cursor.fetchone()[0]

            # Kritik tehditler
            cursor.execute("""
                SELECT COUNT(*) FROM threat_detection 
                WHERE is_resolved = FALSE AND threat_level = 'CRITICAL'
            """)
            critical_threats = cursor.fetchone()[0]

            # Yüksek tehditler
            cursor.execute("""
                SELECT COUNT(*) FROM threat_detection 
                WHERE is_resolved = FALSE AND threat_level = 'HIGH'
            """)
            high_threats = cursor.fetchone()[0]

            # Orta tehditler
            cursor.execute("""
                SELECT COUNT(*) FROM threat_detection 
                WHERE is_resolved = FALSE AND threat_level = 'MEDIUM'
            """)
            medium_threats = cursor.fetchone()[0]

            conn.close()

            return {
                'active_threats': active_threats,
                'critical_threats': critical_threats,
                'high_threats': high_threats,
                'medium_threats': medium_threats
            }
        except Exception as e:
            logging.error(f"Tehdit istatistik hatası: {e}")
            return {
                'active_threats': 0,
                'critical_threats': 0,
                'high_threats': 0,
                'medium_threats': 0
            }

    def _get_real_session_stats(self) -> Dict[str, Any]:
        """Gerçek session istatistiklerini al"""
        try:
            import sqlite3
            from datetime import datetime

            conn = sqlite3.connect(self.manager.db_path)
            cursor = conn.cursor()

            # Aktif sessionlar
            cursor.execute("""
                SELECT COUNT(*) FROM session_recordings 
                WHERE is_active = TRUE
            """)
            active_sessions = cursor.fetchone()[0]

            # Toplam sessionlar
            cursor.execute("SELECT COUNT(*) FROM session_recordings")
            total_sessions = cursor.fetchone()[0]

            # Bugünkü girişler
            today = datetime.now().date().isoformat()
            cursor.execute("""
                SELECT COUNT(*) FROM session_recordings 
                WHERE DATE(login_time) = ?
            """, (today,))
            today_logins = cursor.fetchone()[0]

            # Ortalama süre hesapla
            cursor.execute("""
                SELECT AVG(
                    CAST((julianday(logout_time) - julianday(login_time)) * 24 AS INTEGER)
                ) FROM session_recordings 
                WHERE logout_time IS NOT NULL
            """)
            avg_hours = cursor.fetchone()[0]
            avg_duration = f"{avg_hours or 0:.1f} saat" if avg_hours else "N/A"

            conn.close()

            return {
                'active_sessions': active_sessions,
                'total_sessions': total_sessions,
                'today_logins': today_logins,
                'avg_duration': avg_duration
            }
        except Exception as e:
            logging.error(f"Session istatistik hatası: {e}")
            return {
                'active_sessions': 0,
                'total_sessions': 0,
                'today_logins': 0,
                'avg_duration': 'N/A'
            }

    def load_threat_list(self) -> None:
        """Tehdit listesini yükle"""
        try:
            import sqlite3

            # Mevcut verileri temizle
            for item in self.threat_tree.get_children():
                self.threat_tree.delete(item)

            conn = sqlite3.connect(self.manager.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT threat_type, threat_level, description, 
                       ip_address, detection_time, is_resolved
                FROM threat_detection 
                ORDER BY detection_time DESC
                LIMIT 100
            """)

            threats = cursor.fetchall()
            conn.close()

            for threat in threats:
                threat_type, level, desc, ip, time, resolved = threat
                status = "Çözüldü" if resolved else "Aktif"

                # Renk kodlaması
                tag = 'critical' if level == 'CRITICAL' else 'high' if level == 'HIGH' else 'normal'

                self.threat_tree.insert('', 'end', values=(
                    threat_type, level, desc or 'N/A',
                    ip or 'N/A', time, status
                ), tags=(tag,))

            # Renk taglerini ayarla
            self.threat_tree.tag_configure('critical', background='#ffcccc')
            self.threat_tree.tag_configure('high', background='#ffe6cc')

            logging.info(f"{Icons.PASS} {len(threats)} tehdit yüklendi")

        except Exception as e:
            logging.error(f"Tehdit listesi yükleme hatası: {e}")
            import traceback
            traceback.print_exc()

    def load_session_list(self) -> None:
        """Session listesini yükle"""
        try:

            # Mevcut verileri temizle
            for item in self.session_tree.get_children():
                self.session_tree.delete(item)

            sessions = self.manager.get_session_recordings(limit=100)

            for session in sessions:
                session_id = session['session_id'][:12] + '...'  # Kısa göster
                ip = session['ip_address'] or 'N/A'
                login = session['login_time'] or 'N/A'
                logout = session['logout_time'] or 'Aktif'
                actions = session['actions_count']
                status = "Aktif" if session['is_active'] else "Sonlandı"

                self.session_tree.insert('', 'end', values=(
                    session_id, ip, login, logout, actions, status
                ))

            logging.info(f"{Icons.PASS} {len(sessions)} session yüklendi")

        except Exception as e:
            logging.error(f"Session listesi yükleme hatası: {e}")
            import traceback
            traceback.print_exc()

    def scan_threats(self) -> None:
        """Tehdit taraması yap"""
        try:
            messagebox.showinfo("Tarama Başlatıldı",
                              "Tehdit taraması başlatıldı...\nAudit logları analiz ediliyor...")

            # Gerçek zamanlı tarama yap
            result = self.manager.scan_for_threats_realtime()

            if result['success']:
                threats_count = result['threats_found']

                # İstatistikleri güncelle
                self.refresh_threat_data()

                if threats_count > 0:
                    messagebox.showwarning("Tehdit Tespit Edildi!",
                                         f"{Icons.WARNING} {threats_count} yeni tehdit tespit edildi!\n\n"
                                         "Detaylar için aşağıdaki listeyi kontrol edin.")
                else:
                    messagebox.showinfo("Tarama Tamamlandı",
                                      f"{Icons.SUCCESS} Tarama tamamlandı!\n\n"
                                      "Herhangi bir tehdit tespit edilmedi.")
            else:
                messagebox.showerror("Tarama Hatası",
                                   f"Tarama sırasında hata oluştu:\n{result.get('error', 'Bilinmeyen hata')}")
        except Exception as e:
            logging.error(f"Tehdit tarama hatası: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Hata", f"Tarama hatası: {str(e)}")

    def refresh_threat_data(self) -> None:
        """Tehdit verilerini yenile"""
        try:
            # İstatistikleri güncelle
            threat_stats = self._get_real_threat_stats()

            if hasattr(self, 'threat_stat_cards'):
                self.threat_stat_cards["Aktif Tehdit"].config(text=str(threat_stats['active_threats']))
                self.threat_stat_cards["Kritik Tehdit"].config(text=str(threat_stats['critical_threats']))
                self.threat_stat_cards["Yüksek Tehdit"].config(text=str(threat_stats['high_threats']))
                self.threat_stat_cards["Orta Tehdit"].config(text=str(threat_stats['medium_threats']))

            # Listeyi yenile
            self.load_threat_list()

            messagebox.showinfo("Yenilendi", "Tehdit verileri güncellendi!")
        except Exception as e:
            logging.error(f"Yenileme hatası: {e}")
            messagebox.showerror("Hata", f"Yenileme hatası: {str(e)}")

    def resolve_selected_threat(self) -> None:
        """Seçili tehdidi çöz"""
        try:
            import sqlite3

            selected = self.threat_tree.selection()
            if not selected:
                messagebox.showwarning("Uyarı", "Lütfen çözmek istediğiniz tehdidi seçin!")
                return

            # Kullanıcıdan onay al
            confirm = messagebox.askyesno("Onay",
                                         "Seçili tehdit çözüldü olarak işaretlenecek.\n\n"
                                         "Devam etmek istiyor musunuz?")
            if not confirm:
                return

            # Threat bilgilerini al
            item = self.threat_tree.item(selected[0])
            values = item['values']
            threat_type = values[0]
            level = values[1]
            detection_time = values[4]

            # Database'de güncelle
            conn = sqlite3.connect(self.manager.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE threat_detection 
                SET is_resolved = TRUE,
                resolution_notes = 'Manuel olarak çözüldü'
                WHERE threat_type = ? AND threat_level = ? AND detection_time = ?
            """, (threat_type, level, detection_time))

            conn.commit()
            conn.close()

            # Verileri yenile
            self.refresh_threat_data()

            messagebox.showinfo("Başarılı", "Tehdit çözüldü olarak işaretlendi!")

        except Exception as e:
            logging.error(f"Tehdit çözme hatası: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Hata", f"Tehdit çözme hatası: {str(e)}")
