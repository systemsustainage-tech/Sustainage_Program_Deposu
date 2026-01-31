#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
"""
Güvenlik Yönetimi GUI
SUSTAINAGE-SDG'den adapte edilmiş güvenlik yönetim arayüzü
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

import qrcode
from PIL import Image, ImageTk

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

import sqlite3

from yonetim.security.core.auth import generate_totp_secret, get_otpauth_uri
from yonetim.security.core.support_session import (get_support_session_state,
                                                   start_support_session,
                                                   stop_support_session)
from utils.language_manager import LanguageManager
from config.database import DB_PATH


class SecurityManagementGUI:
    """Güvenlik Yönetimi GUI"""

    def __init__(self, parent, current_user_id: int = 1) -> None:
        self.parent = parent
        self.current_user_id = current_user_id
        self.lm = LanguageManager()

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Güvenlik yönetimi arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=f" {self.lm.tr('security_management_title', 'Güvenlik Yönetimi')}",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)

        # Ana içerik - Notebook (Sekmeler)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # 2FA Yönetimi sekmesi
        self.twofa_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.twofa_frame, text=f" {self.lm.tr('tab_2fa_management', '2FA Yönetimi')}")

        # Güvenlik Ayarları sekmesi
        self.security_settings_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.security_settings_frame, text=f"️ {self.lm.tr('tab_security_settings', 'Güvenlik Ayarları')}")

        # Güvenlik İstatistikleri sekmesi
        self.security_stats_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.security_stats_frame, text=f" {self.lm.tr('tab_security_stats', 'Güvenlik İstatistikleri')}")

        # Güvenlik Logları sekmesi
        self.security_logs_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.security_logs_frame, text=f" {self.lm.tr('tab_security_logs', 'Güvenlik Logları')}")

        # Sekmeleri oluştur
        self.create_twofa_tab()
        self.create_security_settings_tab()
        self.create_security_stats_tab()
        self.create_security_logs_tab()

    def create_twofa_tab(self) -> None:
        """2FA Yönetimi sekmesi"""
        content_frame = tk.Frame(self.twofa_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        tk.Label(content_frame, text=self.lm.tr('2fa_title', "İki Faktörlü Doğrulama (2FA) Yönetimi"),
                font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='white').pack(pady=(0, 20))

        # 2FA Durumu
        status_frame = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        status_frame.pack(fill='x', pady=10)

        status_content = tk.Frame(status_frame, bg='#f8f9fa')
        status_content.pack(fill='x', padx=20, pady=15)

        tk.Label(status_content, text=self.lm.tr('2fa_status_title', "2FA Durumu"), font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w')

        self.twofa_status_label = tk.Label(status_content, text=self.lm.tr('2fa_status_loading', "Yükleniyor..."),
                                          font=('Segoe UI', 12), fg='#7f8c8d', bg='#f8f9fa')
        self.twofa_status_label.pack(anchor='w', pady=5)

        # 2FA Kontrolü
        check_frame = tk.Frame(content_frame, bg='white')
        check_frame.pack(fill='x', pady=10)

        tk.Button(check_frame, text=self.lm.tr('2fa_check_btn', "2FA Durumunu Kontrol Et"),
                 font=('Segoe UI', 10), bg='#3498db', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=self.check_twofa_status).pack(side='left', padx=5)

        # 2FA Kurulumu
        setup_frame = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        setup_frame.pack(fill='x', pady=10)

        setup_content = tk.Frame(setup_frame, bg='#f8f9fa')
        setup_content.pack(fill='x', padx=20, pady=15)

        tk.Label(setup_content, text=self.lm.tr('2fa_setup_title', "2FA Kurulumu"), font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w')

        self.setup_2fa_button = tk.Button(setup_content, text=self.lm.tr('2fa_enable_btn', "2FA'yı Etkinleştir"),
                                         font=('Segoe UI', 10), bg='#27ae60', fg='white',
                                         relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                                         command=self.setup_twofa)
        self.setup_2fa_button.pack(anchor='w', pady=10)

        # QR Code Alanı
        self.qr_frame = tk.Frame(content_frame, bg='white')
        self.qr_frame.pack(fill='both', expand=True, pady=10)

        # 2FA Doğrulama
        verify_frame = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        verify_frame.pack(fill='x', pady=10)

        verify_content = tk.Frame(verify_frame, bg='#f8f9fa')
        verify_content.pack(fill='x', padx=20, pady=15)

        tk.Label(verify_content, text=self.lm.tr('2fa_verify_title', "2FA Doğrulama"), font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w')

        code_frame = tk.Frame(verify_content, bg='#f8f9fa')
        code_frame.pack(fill='x', pady=10)

        tk.Label(code_frame, text=self.lm.tr('2fa_verify_code_label', "Doğrulama Kodu:"), bg='#f8f9fa').pack(side='left')
        self.verify_code_var = tk.StringVar()
        verify_entry = tk.Entry(code_frame, textvariable=self.verify_code_var, width=15)
        verify_entry.pack(side='left', padx=(5, 10))

        verify_btn = ttk.Button(code_frame, text=f" {self.lm.tr('2fa_verify_btn', 'Doğrula')}", style='Menu.TButton',
                                command=self.verify_twofa_code)
        verify_btn.pack(side='left')
        try:
            from utils.tooltip import add_tooltip
            add_tooltip(verify_btn, self.lm.tr('2fa_verify_tooltip', '2FA doğrulama kodunu onayla'))
        except Exception as e:
            logging.error(f'Silent error in security_management_gui.py: {str(e)}')

    def create_security_settings_tab(self) -> None:
        """Güvenlik Ayarları sekmesi"""
        content_frame = tk.Frame(self.security_settings_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        tk.Label(content_frame, text=self.lm.tr('settings_title', "Güvenlik Ayarları"),
                font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='white').pack(pady=(0, 20))

        # Şifre Politikaları
        password_frame = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        password_frame.pack(fill='x', pady=10)

        password_content = tk.Frame(password_frame, bg='#f8f9fa')
        password_content.pack(fill='x', padx=20, pady=15)

        tk.Label(password_content, text=self.lm.tr('password_policies_title', "Şifre Politikaları"), font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w')

        # Şifre değiştirme
        change_pass_frame = tk.Frame(password_content, bg='#f8f9fa')
        change_pass_frame.pack(fill='x', pady=10)

        tk.Label(change_pass_frame, text=self.lm.tr('current_password', "Mevcut Şifre:"), bg='#f8f9fa').pack(anchor='w')
        self.current_pass_var = tk.StringVar()
        tk.Entry(change_pass_frame, textvariable=self.current_pass_var, show='*', width=30).pack(anchor='w', pady=2)

        tk.Label(change_pass_frame, text=self.lm.tr('new_password', "Yeni Şifre:"), bg='#f8f9fa').pack(anchor='w')
        self.new_pass_var = tk.StringVar()
        tk.Entry(change_pass_frame, textvariable=self.new_pass_var, show='*', width=30).pack(anchor='w', pady=2)

        tk.Label(change_pass_frame, text=self.lm.tr('confirm_password', "Şifre Tekrar:"), bg='#f8f9fa').pack(anchor='w')
        self.confirm_pass_var = tk.StringVar()
        tk.Entry(change_pass_frame, textvariable=self.confirm_pass_var, show='*', width=30).pack(anchor='w', pady=2)

        tk.Button(change_pass_frame, text=self.lm.tr('change_password_btn', "Şifreyi Değiştir"),
                 font=('Segoe UI', 10), bg='#e74c3c', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=self.change_password).pack(anchor='w', pady=10)

        # Rate Limiting
        rate_frame = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        rate_frame.pack(fill='x', pady=10)

        rate_content = tk.Frame(rate_frame, bg='#f8f9fa')
        rate_content.pack(fill='x', padx=20, pady=15)

        tk.Label(rate_content, text=self.lm.tr('rate_limiting_title', "Rate Limiting"), font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w')

        # Rate limiting ayarları
        rate_settings_frame = tk.Frame(rate_content, bg='#f8f9fa')
        rate_settings_frame.pack(fill='x', pady=10)

        tk.Label(rate_settings_frame, text=self.lm.tr('max_login_attempts', "Maksimum Login Denemesi:"), bg='#f8f9fa').pack(anchor='w')
        self.max_attempts_var = tk.StringVar(value="5")
        tk.Entry(rate_settings_frame, textvariable=self.max_attempts_var, width=10).pack(anchor='w', pady=2)

        tk.Label(rate_settings_frame, text=self.lm.tr('lockout_duration', "Kilitleme Süresi (saniye):"), bg='#f8f9fa').pack(anchor='w')
        self.lockout_duration_var = tk.StringVar(value="600")
        tk.Entry(rate_settings_frame, textvariable=self.lockout_duration_var, width=10).pack(anchor='w', pady=2)

        tk.Button(rate_settings_frame, text=self.lm.tr('save_settings_btn', "Ayarları Kaydet"),
                 font=('Segoe UI', 10), bg='#3498db', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=self.save_rate_limiting_settings).pack(anchor='w', pady=10)

        # Destek Oturumu (Break-glass)
        support_frame = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        support_frame.pack(fill='x', pady=10)

        support_content = tk.Frame(support_frame, bg='#f8f9fa')
        support_content.pack(fill='x', padx=20, pady=15)

        tk.Label(support_content, text=self.lm.tr('support_session_title', "Destek Oturumu (Break-glass)"), font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w')

        self.support_status_label = tk.Label(support_content, text=self.lm.tr('support_status_unknown', "Durum: Bilinmiyor"),
                                            font=('Segoe UI', 12), fg='#7f8c8d', bg='#f8f9fa')
        self.support_status_label.pack(anchor='w', pady=5)

        btn_frame = tk.Frame(support_content, bg='#f8f9fa')
        btn_frame.pack(fill='x', pady=10)

        tk.Button(btn_frame, text=self.lm.tr('start_support_btn', "Destek Oturumunu Başlat"),
                 font=('Segoe UI', 10), bg='#8e44ad', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=self._ui_start_support_session).pack(side='left', padx=5)

        tk.Button(btn_frame, text=self.lm.tr('stop_support_btn', "Oturumu Sonlandır"),
                 font=('Segoe UI', 10), bg='#c0392b', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=self._ui_stop_support_session).pack(side='left', padx=5)

    def create_security_stats_tab(self) -> None:
        """Güvenlik İstatistikleri sekmesi"""
        content_frame = tk.Frame(self.security_stats_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        tk.Label(content_frame, text=self.lm.tr('stats_title', "Güvenlik İstatistikleri"),
                font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='white').pack(pady=(0, 20))

        # İstatistik kartları
        stats_frame = tk.Frame(content_frame, bg='white')
        stats_frame.pack(fill='x', pady=20)

        self.stats_labels = {}

        stats_data = [
            (self.lm.tr('stat_successful_logins', "Başarılı Girişler"), "successful_logins", "#2ecc71"),
            (self.lm.tr('stat_failed_logins', "Başarısız Girişler"), "failed_logins", "#e74c3c"),
            (self.lm.tr('stat_active_users', "Aktif Kullanıcılar"), "active_users", "#3498db"),
            (self.lm.tr('stat_2fa_active', "2FA Aktif"), "totp_users", "#f39c12")
        ]

        for i, (title, key, color) in enumerate(stats_data):
            card = tk.Frame(stats_frame, bg=color, relief='raised', bd=1)
            card.pack(side='left', fill='x', expand=True, padx=(0, 5) if i < len(stats_data)-1 else 0)

            card_content = tk.Frame(card, bg=color)
            card_content.pack(fill='both', expand=True, padx=15, pady=10)

            title_label = tk.Label(card_content, text=title, font=('Segoe UI', 9, 'bold'),
                                  fg='white', bg=color)
            title_label.pack()

            value_label = tk.Label(card_content, text="0", font=('Segoe UI', 12, 'bold'),
                                  fg='white', bg=color)
            value_label.pack()

            self.stats_labels[key] = value_label

        # Yenile butonu
        refresh_frame = tk.Frame(content_frame, bg='white')
        refresh_frame.pack(fill='x', pady=10)

        ref_btn = ttk.Button(refresh_frame, text=f" {self.lm.tr('refresh_stats_btn', 'İstatistikleri Yenile')}", style='Menu.TButton',
                             command=self.refresh_security_stats)
        ref_btn.pack()
        try:
            from utils.tooltip import add_tooltip
            add_tooltip(ref_btn, self.lm.tr('refresh_stats_tooltip', 'Güvenlik istatistiklerini yenile'))
        except Exception as e:
            logging.error(f'Silent error in security_management_gui.py: {str(e)}')

    def create_security_logs_tab(self) -> None:
        """Güvenlik Logları sekmesi"""
        content_frame = tk.Frame(self.security_logs_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        tk.Label(content_frame, text=self.lm.tr('logs_title', "Güvenlik Logları"),
                font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='white').pack(pady=(0, 20))

        # Log listesi
        log_frame = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
        log_frame.pack(fill='both', expand=True)

        # Log ağacı
        columns = ('timestamp', 'actor', 'action', 'success')
        self.log_tree = ttk.Treeview(log_frame, columns=columns, show='headings', height=15)

        self.log_tree.heading('timestamp', text=self.lm.tr('col_timestamp', 'Tarih/Saat'))
        self.log_tree.heading('actor', text=self.lm.tr('col_actor', 'Kullanıcı'))
        self.log_tree.heading('action', text=self.lm.tr('col_action', 'İşlem'))
        self.log_tree.heading('success', text=self.lm.tr('col_success', 'Durum'))

        self.log_tree.column('timestamp', width=120)
        self.log_tree.column('actor', width=100)
        self.log_tree.column('action', width=150)
        self.log_tree.column('success', width=80)

        # Scrollbar
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=log_scrollbar.set)

        self.log_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        log_scrollbar.pack(side='right', fill='y', pady=10)

        # Yenile butonu
        refresh_frame = tk.Frame(content_frame, bg='white')
        refresh_frame.pack(fill='x', pady=10)

        tk.Button(refresh_frame, text=self.lm.tr('refresh_logs_btn', "Logları Yenile"),
                 font=('Segoe UI', 10), bg='#3498db', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=self.refresh_security_logs).pack()

    def load_data(self) -> None:
        """Verileri yükle"""
        self.check_twofa_status()
        self.refresh_security_stats()
        self.refresh_security_logs()
        try:
            self._refresh_support_status()
        except Exception as e:
            logging.error(f'Silent error in security_management_gui.py: {str(e)}')

    def _open_db(self) -> None:
        """Varsayılan veritabanını aç (sqlite)."""
        path = DB_PATH
        try:
            return sqlite3.connect(path)
        except Exception as e:
            raise RuntimeError(self.lm.tr('error_db_open', f"Veritabanı açılamadı: {e}").format(e=e))

    def _refresh_support_status(self) -> None:
        try:
            conn = self._open_db()
            state = get_support_session_state(conn)
            conn.close()
            if state.get('active'):
                exp = state.get('exp') or 0
                scope = state.get('scope') or '-'
                actor = state.get('actor') or '-'
                text = self.lm.tr('support_status_active', "Durum: Aktif | Kapsam: {scope} | Başlatan: {actor} | Bitiş: {exp}").format(scope=scope, actor=actor, exp=exp)
                self.support_status_label.config(text=text, fg='#27ae60')
            else:
                self.support_status_label.config(text=self.lm.tr('support_status_passive', "Durum: Pasif"), fg='#7f8c8d')
        except Exception as e:
            self.support_status_label.config(text=self.lm.tr('support_status_error', f"Durum okunamadı: {e}").format(e=e), fg='#e74c3c')

    def _ui_start_support_session(self) -> None:
        try:
            token = simpledialog.askstring("Destek Token", self.lm.tr('support_token_prompt', "Vendor destek tokenını girin:"), parent=self.parent)
            if not token:
                return
            totp = simpledialog.askstring("2FA Doğrulama", self.lm.tr('support_totp_prompt', "TOTP kodunuzu girin:"), show='*', parent=self.parent)
            if not totp:
                return
            # Not: current actor kullanıcı adı, gerçek uygulamada oturumdan gelmeli
            actor = simpledialog.askstring("Aktör", self.lm.tr('support_actor_prompt', "Kullanıcı adınızı doğrulayın:"), parent=self.parent)
            if not actor:
                return
            conn = self._open_db()
            res = start_support_session(conn, actor, token, totp)
            conn.close()
            if res.get('ok'):
                messagebox.showinfo(self.lm.tr('success_title', "Başarılı"), self.lm.tr('support_start_success', "Destek oturumu başlatıldı."))
                self._refresh_support_status()
            else:
                messagebox.showerror(self.lm.tr('error_title', "Hata"), self.lm.tr('support_start_error', f"Başlatılamadı: {res.get('reason')}").format(reason=res.get('reason')))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error_title', "Hata"), self.lm.tr('support_session_error', f"Destek oturumu başlatılırken hata: {e}").format(e=e))

    def _ui_stop_support_session(self) -> None:
        try:
            actor = simpledialog.askstring("Aktör", self.lm.tr('support_actor_prompt', "Kullanıcı adınızı doğrulayın:"), parent=self.parent)
            if not actor:
                return
            conn = self._open_db()
            res = stop_support_session(conn, actor)
            conn.close()
            if res.get('ok'):
                messagebox.showinfo(self.lm.tr('info_title', "Bilgi"), self.lm.tr('support_stop_success', "Destek oturumu sonlandırıldı."))
                self._refresh_support_status()
            else:
                messagebox.showerror(self.lm.tr('error_title', "Hata"), self.lm.tr('support_stop_error', "Oturum sonlandırılamadı."))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error_title', "Hata"), self.lm.tr('support_stop_exception', f"Oturum sonlandırılırken hata: {e}").format(e=e))

    def check_twofa_status(self) -> None:
        """2FA durumunu kontrol et"""
        try:
            # Bu fonksiyon gerçek implementasyonda veritabanından 2FA durumunu kontrol edecek
            # Şimdilik örnek veri gösteriyoruz
            self.twofa_status_label.config(text=self.lm.tr('2fa_status_disabled', "2FA Devre Dışı"), fg='#e74c3c')
            self.setup_2fa_button.config(text=self.lm.tr('2fa_enable_btn', "2FA'yı Etkinleştir"), bg='#27ae60')
        except Exception as e:
            messagebox.showerror(self.lm.tr('error_title', "Hata"), self.lm.tr('error_2fa_check', f"2FA durumu kontrol edilirken hata: {e}").format(e=e))

    def setup_twofa(self) -> None:
        """2FA kurulumu"""
        try:
            # 2FA secret oluştur
            secret = generate_totp_secret()

            # QR code oluştur
            otpauth_uri = get_otpauth_uri("current_user", secret)

            # QR code göster
            self.show_qr_code(otpauth_uri)

            messagebox.showinfo(self.lm.tr('info_title', "Bilgi"), self.lm.tr('2fa_qr_info', "QR kodu telefonunuzla tarayın ve doğrulama kodunu girin."))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error_title', "Hata"), self.lm.tr('error_2fa_setup', f"2FA kurulumu sırasında hata: {e}").format(e=e))

    def show_qr_code(self, otpauth_uri) -> None:
        """QR kodunu göster"""
        try:
            # QR code oluştur
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(otpauth_uri)
            qr.make(fit=True)

            # QR code resmini oluştur
            img = qr.make_image(fill_color="black", back_color="white")

            # Tkinter için uygun formata çevir
            img = img.resize((200, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            # QR code frame'ini temizle
            for widget in self.qr_frame.winfo_children():
                widget.destroy()

            # QR code label'ı oluştur
            qr_label = tk.Label(self.qr_frame, image=photo)
            qr_label.image = photo  # Referansı koru
            qr_label.pack(pady=20)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error_title', "Hata"), self.lm.tr('error_qr_create', f"QR kod oluşturulurken hata: {e}").format(e=e))

    def verify_twofa_code(self) -> None:
        """2FA kodunu doğrula"""
        code = self.verify_code_var.get()
        if not code:
            messagebox.showerror(self.lm.tr('error_title', "Hata"), self.lm.tr('2fa_verify_empty_error', "Doğrulama kodunu girin."))
            return

        try:
            # Bu fonksiyon gerçek implementasyonda TOTP kodunu doğrulayacak
            # Şimdilik örnek doğrulama
            if len(code) == 6 and code.isdigit():
                messagebox.showinfo(self.lm.tr('success_title', "Başarılı"), "2FA başarıyla etkinleştirildi!")
                self.check_twofa_status()
            else:
                messagebox.showerror(self.lm.tr('error_title', "Hata"), "Geçersiz doğrulama kodu.")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error_title', "Hata"), f"2FA doğrulama hatası: {e}")

    def change_password(self) -> None:
        """Şifre değiştir"""
        current_pass = self.current_pass_var.get()
        new_pass = self.new_pass_var.get()
        confirm_pass = self.confirm_pass_var.get()

        if not all([current_pass, new_pass, confirm_pass]):
            messagebox.showerror(self.lm.tr('error_title', "Hata"), "Tüm alanları doldurun.")
            return

        if new_pass != confirm_pass:
            messagebox.showerror(self.lm.tr('error_title', "Hata"), "Yeni şifreler eşleşmiyor.")
            return

        if len(new_pass) < 8:
            messagebox.showerror(self.lm.tr('error_title', "Hata"), "Şifre en az 8 karakter olmalıdır.")
            return

        try:
            # Bu fonksiyon gerçek implementasyonda şifre değişikliğini yapacak
            messagebox.showinfo(self.lm.tr('success_title', "Başarılı"), "Şifre başarıyla değiştirildi!")

            # Alanları temizle
            self.current_pass_var.set("")
            self.new_pass_var.set("")
            self.confirm_pass_var.set("")

        except Exception as e:
            messagebox.showerror(self.lm.tr('error_title', "Hata"), f"Şifre değiştirme hatası: {e}")

    def save_rate_limiting_settings(self) -> None:
        """Rate limiting ayarlarını kaydet"""
        try:
            max_attempts = int(self.max_attempts_var.get())
            lockout_duration = int(self.lockout_duration_var.get())

            if max_attempts < 1 or lockout_duration < 1:
                messagebox.showerror(self.lm.tr('error_title', "Hata"), "Geçerli değerler girin.")
                return

            # Bu fonksiyon gerçek implementasyonda ayarları kaydedecek
            messagebox.showinfo(self.lm.tr('success_title', "Başarılı"), "Rate limiting ayarları kaydedildi!")

        except ValueError:
            messagebox.showerror(self.lm.tr('error_title', "Hata"), "Geçerli sayısal değerler girin.")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error_title', "Hata"), f"Ayarlar kaydedilirken hata: {e}")

    def refresh_security_stats(self) -> None:
        """Güvenlik istatistiklerini yenile"""
        try:
            # Bu fonksiyon gerçek implementasyonda veritabanından istatistikleri çekecek
            # Şimdilik örnek veri gösteriyoruz
            stats = {
                'successful_logins': 150,
                'failed_logins': 12,
                'active_users': 25,
                'totp_users': 8
            }

            self.stats_labels['successful_logins'].config(text=str(stats['successful_logins']))
            self.stats_labels['failed_logins'].config(text=str(stats['failed_logins']))
            self.stats_labels['active_users'].config(text=str(stats['active_users']))
            self.stats_labels['totp_users'].config(text=str(stats['totp_users']))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error_title', "Hata"), f"İstatistikler yüklenirken hata: {e}")

    def refresh_security_logs(self) -> None:
        """Güvenlik loglarını yenile"""
        try:
            # Log ağacını temizle
            for item in self.log_tree.get_children():
                self.log_tree.delete(item)

            # Bu fonksiyon gerçek implementasyonda veritabanından logları çekecek
            # Şimdilik örnek veri gösteriyoruz
            sample_logs = [
                ("2024-01-15 10:30", "admin", "login_success", self.lm.tr("success_title", "Başarılı")),
                ("2024-01-15 10:25", "user1", "login_fail", self.lm.tr("status_failed", "Başarısız")),
                ("2024-01-15 10:20", "admin", "password_change", self.lm.tr("success_title", "Başarılı")),
                ("2024-01-15 10:15", "user2", "2fa_enable", self.lm.tr("success_title", "Başarılı")),
            ]

            for log in sample_logs:
                self.log_tree.insert('', 'end', values=log)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error_title', "Hata"), f"Loglar yüklenirken hata: {e}")