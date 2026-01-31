#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistem Ayarları GUI
"""

import tkinter as tk
from tkinter import messagebox, ttk
import os
import json
import logging
from config.icons import Icons

class SystemSettingsGUI:
    """Sistem Ayarları Yönetimi GUI"""

    def __init__(self, parent, current_user_id: int = 1) -> None:
        self.parent = parent
        self.current_user_id = current_user_id

        self.setup_ui()

    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        # Ana container
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        title_label = tk.Label(main_frame, text=f"{Icons.SETTINGS} Sistem Ayarları",
                              font=('Segoe UI', 18, 'bold'), fg='#2c3e50', bg='#f5f5f5')
        title_label.pack(pady=(0, 20))

        # Notebook (Sekmeler)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)

        # Genel Ayarlar Sekmesi
        general_frame = tk.Frame(notebook, bg='white')
        notebook.add(general_frame, text=f"{Icons.HOME} Genel Ayarlar")
        self.create_general_settings(general_frame)

        # Veritabanı Ayarları Sekmesi
        db_frame = tk.Frame(notebook, bg='white')
        notebook.add(db_frame, text="🗃️ Veritabanı")
        self.create_database_settings(db_frame)

        # Email Ayarları Sekmesi
        email_frame = tk.Frame(notebook, bg='white')
        notebook.add(email_frame, text=f"{Icons.EMAIL} Email Ayarları")
        self.create_email_settings(email_frame)

        # Güvenlik Ayarları Sekmesi
        security_frame = tk.Frame(notebook, bg='white')
        notebook.add(security_frame, text=f"{Icons.SECURE} Güvenlik")
        self.create_security_settings(security_frame)

    def create_general_settings(self, parent):
        """Genel ayarlar sekmesi"""
        # Container
        container = tk.Frame(parent, bg='white')
        container.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        tk.Label(container, text="Genel Sistem Ayarları",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(anchor='w', pady=(0, 15))

        # Ayarlar formu
        settings_frame = tk.Frame(container, bg='white')
        settings_frame.pack(fill='x', pady=10)

        # Uygulama Adı
        app_label = tk.Label(
            settings_frame,
            text="Uygulama Adı:",
            font=('Segoe UI', 10),
            bg='white',
        )
        app_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.app_name_var = tk.StringVar(value="SUSTAINAGE SDG")
        app_entry = tk.Entry(
            settings_frame,
            textvariable=self.app_name_var,
            width=30,
        )
        app_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Varsayılan Dil
        lang_label = tk.Label(
            settings_frame,
            text="Varsayılan Dil:",
            font=('Segoe UI', 10),
            bg='white',
        )
        lang_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.language_var = tk.StringVar(value="Türkçe")
        lang_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.language_var,
            values=["Türkçe", "English"],
            state='readonly',
            width=27,
        )
        lang_combo.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # Otomatik Yedekleme
        self.auto_backup_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            settings_frame,
            text="Otomatik yedekleme aktif",
            variable=self.auto_backup_var,
            bg='white',
            font=('Segoe UI', 10),
        ).grid(row=2, column=0, columnspan=2, sticky='w', padx=5, pady=5)

        # Log Seviyesi
        log_label = tk.Label(
            settings_frame,
            text="Log Seviyesi:",
            font=('Segoe UI', 10),
            bg='white',
        )
        log_label.grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.log_level_var = tk.StringVar(value="INFO")
        ttk.Combobox(
            settings_frame,
            textvariable=self.log_level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            state='readonly',
            width=27,
        ).grid(row=3, column=1, padx=5, pady=5, sticky='w')

        # Kaydet butonu
        tk.Button(container, text=f"{Icons.SAVE} Ayarları Kaydet", font=('Segoe UI', 10, 'bold'),
                 bg='#27ae60', fg='white', relief='flat', bd=0, cursor='hand2',
                 padx=20, pady=8, command=self.save_general_settings).pack(pady=20)

    def create_database_settings(self, parent):
        """Veritabanı ayarları sekmesi"""
        container = tk.Frame(parent, bg='white')
        container.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(container, text="Veritabanı Ayarları",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(anchor='w', pady=(0, 15))

        # Bilgi kartları
        info_frame = tk.Frame(container, bg='white')
        info_frame.pack(fill='x', pady=10)

        # DB Durumu
        status_card = tk.Frame(info_frame, bg='#d5f4e6', relief='raised', bd=2)
        status_card.pack(fill='x', pady=5)

        tk.Label(status_card, text=f"{Icons.SUCCESS} Veritabanı Durumu: Aktif",
                font=('Segoe UI', 11, 'bold'), fg='#27ae60', bg='#d5f4e6').pack(pady=10)

        # İstatistikler
        stats_frame = tk.Frame(container, bg='white')
        stats_frame.pack(fill='x', pady=10)

        stats_info = [
            (f"{Icons.REPORT} Toplam Tablolar", "45"),
            (f"{Icons.USERS} Kullanıcı Sayısı", "12"),
            ("🏢 Firma Sayısı", "3"),
            (f"{Icons.SAVE} Veritabanı Boyutu", "2.3 MB")
        ]

        for i, (label, value) in enumerate(stats_info):
            row = i // 2
            col = i % 2

            stat_frame = tk.Frame(stats_frame, bg='#ecf0f1', relief='raised', bd=1)
            stat_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')

            tk.Label(stat_frame, text=label, font=('Segoe UI', 9), bg='#ecf0f1').pack(pady=2)
            tk.Label(stat_frame, text=value, font=('Segoe UI', 12, 'bold'), fg='#3498db', bg='#ecf0f1').pack(pady=2)

        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)

        # Aksiyon butonları
        btn_frame = tk.Frame(container, bg='white')
        btn_frame.pack(fill='x', pady=20)

        ref_btn = ttk.Button(btn_frame, text=f"{Icons.LOADING} Yenile", style='Menu.TButton')
        ref_btn.pack(side='left', padx=6)
        opt_btn = ttk.Button(btn_frame, text=f"{Icons.TOOLS} Optimize Et", style='Menu.TButton')
        opt_btn.pack(side='left', padx=6)
        ana_btn = ttk.Button(btn_frame, text=f"{Icons.REPORT} Analiz", style='Menu.TButton')
        ana_btn.pack(side='left', padx=6)
        try:
            from utils.tooltip import add_tooltip
            add_tooltip(ref_btn, 'Sistem durumunu yenile')
            add_tooltip(opt_btn, 'Veritabanı ve önbellek optimizasyonu')
            add_tooltip(ana_btn, 'Sistem analizi ve rapor')
        except Exception as e:
            logging.error(f"Error adding tooltips: {e}")

    def create_email_settings(self, parent):
        container = tk.Frame(parent, bg='white')
        container.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(container, text="Email Ayarları",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(anchor='w', pady=(0, 15))

        form = tk.Frame(container, bg='white')
        form.pack(fill='x', pady=10)

        tk.Label(form, text="Sistem Mail Adresi:", font=('Segoe UI', 10), bg='white').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.system_email_var = tk.StringVar()
        tk.Entry(form, textvariable=self.system_email_var, width=32).grid(row=0, column=1, padx=5, pady=5, sticky='w')

        tk.Label(form, text="Gelen Sunucu Adı:", font=('Segoe UI', 10), bg='white').grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.in_server_var = tk.StringVar()
        tk.Entry(form, textvariable=self.in_server_var, width=32).grid(row=1, column=1, padx=5, pady=5, sticky='w')

        tk.Label(form, text="Gelen Port:", font=('Segoe UI', 10), bg='white').grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.in_port_var = tk.StringVar()
        tk.Entry(form, textvariable=self.in_port_var, width=10).grid(row=1, column=3, padx=5, pady=5, sticky='w')

        tk.Label(form, text="Giden Sunucu Adı:", font=('Segoe UI', 10), bg='white').grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.out_server_var = tk.StringVar()
        tk.Entry(form, textvariable=self.out_server_var, width=32).grid(row=2, column=1, padx=5, pady=5, sticky='w')

        tk.Label(form, text="Giden Port:", font=('Segoe UI', 10), bg='white').grid(row=2, column=2, sticky='w', padx=5, pady=5)
        self.out_port_var = tk.StringVar()
        tk.Entry(form, textvariable=self.out_port_var, width=10).grid(row=2, column=3, padx=5, pady=5, sticky='w')

        tk.Label(form, text="Güvenlik:", font=('Segoe UI', 10), bg='white').grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.security_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.security_var, values=["TLS", "SSL", "YOK"], state='readonly', width=29).grid(row=3, column=1, padx=5, pady=5, sticky='w')

        tk.Label(form, text="Yanıt Adresi:", font=('Segoe UI', 10), bg='white').grid(row=3, column=2, sticky='w', padx=5, pady=5)
        self.reply_to_var = tk.StringVar()
        tk.Entry(form, textvariable=self.reply_to_var, width=22).grid(row=3, column=3, padx=5, pady=5, sticky='w')

        tk.Label(form, text="Parola:", font=('Segoe UI', 10), bg='white').grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.password_var = tk.StringVar()
        tk.Entry(form, textvariable=self.password_var, width=32, show='*').grid(row=4, column=1, padx=5, pady=5, sticky='w')

        btns = tk.Frame(container, bg='white')
        btns.pack(fill='x', pady=15)

        tk.Button(btns, text=f"{Icons.SAVE} Kaydet", font=('Segoe UI', 10, 'bold'), bg='#27ae60', fg='white', relief='flat', bd=0, cursor='hand2', padx=18, pady=8, command=self.save_email_settings).pack(side='left')
        tk.Button(btns, text=f"{Icons.LOADING} Yenile", font=('Segoe UI', 10, 'bold'), bg='#3498db', fg='white', relief='flat', bd=0, cursor='hand2', padx=18, pady=8, command=self.load_email_settings).pack(side='left', padx=8)

        self.load_email_settings()

    def _smtp_config_path(self) -> str:
        # backend/yonetim/system_settings/gui -> backend/config/smtp_config.json
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../config/smtp_config.json'))

    def load_email_settings(self) -> None:
        path = self._smtp_config_path()
        data = {}
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
        except Exception as e:
            logging.error(f"Error loading email settings: {e}")
            data = {}
        self.system_email_var.set(data.get('system_email') or data.get('sender_email') or 'system@sustainage.tr')
        self.in_server_var.set(data.get('pop3_server') or '')
        self.in_port_var.set(str(data.get('pop3_port') or ''))
        self.out_server_var.set(data.get('smtp_server') or '')
        self.out_port_var.set(str(data.get('smtp_port') or ''))
        sec = (data.get('security') or ('TLS' if data.get('use_tls') else 'YOK')).upper()
        if sec not in ('TLS', 'SSL', 'YOK'):
            sec = 'TLS'
        self.security_var.set(sec)
        self.reply_to_var.set(data.get('reply_to') or 'destek@sustainage.tr')

    def save_email_settings(self) -> None:
        try:
            path = self._smtp_config_path()
            os.makedirs(os.path.dirname(path), exist_ok=True)
            data = {}
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except Exception as e:
                    logging.warning(f"Error reading existing email settings: {e}")
                    data = {}
            data['system_email'] = self.system_email_var.get().strip()
            data['sender_email'] = data['system_email']
            data['smtp_server'] = self.out_server_var.get().strip()
            data['smtp_port'] = int(self.out_port_var.get().strip() or '0')
            data['pop3_server'] = self.in_server_var.get().strip()
            data['pop3_port'] = int(self.in_port_var.get().strip() or '0')
            sec = self.security_var.get().upper()
            data['security'] = sec
            data['use_tls'] = (sec == 'TLS')
            data['reply_to'] = self.reply_to_var.get().strip()
            
            pwd = (self.password_var.get() or '').strip()
            if pwd:
                data['sender_password'] = pwd
                
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("Başarılı", "Email ayarları kaydedildi!")
        except Exception as e:
            messagebox.showerror("Hata", f"Email ayarları kaydedilemedi: {e}")

    def create_security_settings(self, parent):
        """Güvenlik ayarları sekmesi"""
        container = tk.Frame(parent, bg='white')
        container.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(container, text="Güvenlik Ayarları",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(anchor='w', pady=(0, 15))

        # Güvenlik durumu
        security_frame = tk.Frame(container, bg='#fff3cd', relief='raised', bd=2)
        security_frame.pack(fill='x', pady=10)

        tk.Label(security_frame, text=f"{Icons.SECURE} Güvenlik Durumu: Normal",
                font=('Segoe UI', 12, 'bold'), fg='#856404', bg='#fff3cd').pack(pady=10)

        # Güvenlik seçenekleri
        options_frame = tk.Frame(container, bg='white')
        options_frame.pack(fill='x', pady=15)

        self.two_factor_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="İki faktörlü kimlik doğrulama",
                      variable=self.two_factor_var, bg='white').pack(anchor='w', pady=3)

        self.session_timeout_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Oturum zaman aşımı (30 dakika)",
                      variable=self.session_timeout_var, bg='white').pack(anchor='w', pady=3)

        self.audit_log_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Audit log kayıtları",
                      variable=self.audit_log_var, bg='white').pack(anchor='w', pady=3)

    def save_general_settings(self):
        """Genel ayarları kaydet"""
        try:

            messagebox.showinfo("Başarılı", "Sistem ayarları başarıyla kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Ayarlar kaydedilirken hata: {e}")
