#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUSTAINAGE SDG - Kullanıcı Profil Yönetimi GUI
- Kullanıcı bilgilerini görüntüleme
- Şifre değiştirme
- Email değiştirme
- Profil güncelleme
"""

import logging
import os
import sqlite3
import sys
import tkinter as tk
from tkinter import messagebox, ttk

from utils.language_manager import LanguageManager

# Email servisi import
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from yonetim.security.core.crypto import hash_password
from yonetim.security.core.crypto import verify_password_compat as verify_password


class UserProfileGUI:
    def __init__(self, parent, db_path, user_id, username):
        self.parent = parent
        self.db_path = db_path
        self.user_id = user_id
        self.username = username
        self.lm = LanguageManager()

        # Tema
        self.theme = {
            'primary': '#2E8B57',
            'primary_hover': '#3CB371',
            'danger': '#DC143C',
            'success': '#28a745',
            'bg_light': '#f0f0f0',
            'white': '#ffffff',
            'text_dark': '#333333',
            'text_muted': '#666666'
        }

        self.setup_window()
        self.load_user_data()

    def setup_window(self):
        """Kullanıcı profil penceresini oluştur"""
        self.window = tk.Toplevel(self.parent)
        self.window.title(self.lm.tr("user_profile_title", "Kullanıcı Profili") + f" - {self.username}")
        self.window.geometry("600x500")
        self.window.configure(bg=self.theme['white'])
        self.window.resizable(False, False)

        # Pencereyi ortala
        self.window.transient(self.parent)
        self.window.grab_set()

        # Ana frame
        main_frame = tk.Frame(self.window, bg=self.theme['white'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        title_label = tk.Label(main_frame, text=self.lm.tr("user_profile_header", "Kullanıcı Profili"),
                              font=('Segoe UI', 18, 'bold'),
                              fg=self.theme['primary'],
                              bg=self.theme['white'])
        title_label.pack(pady=(0, 20))

        # Notebook (Tab sistemi)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Profil Bilgileri Tab
        self.profile_frame = tk.Frame(self.notebook, bg=self.theme['white'])
        self.notebook.add(self.profile_frame, text=self.lm.tr("profile_info_tab", "Profil Bilgileri"))
        self.setup_profile_tab()

        # Şifre Değiştir Tab
        self.password_frame = tk.Frame(self.notebook, bg=self.theme['white'])
        self.notebook.add(self.password_frame, text=self.lm.tr("change_password_tab", "Şifre Değiştir"))
        self.setup_password_tab()

        # Email Değiştir Tab
        self.email_frame = tk.Frame(self.notebook, bg=self.theme['white'])
        self.notebook.add(self.email_frame, text=self.lm.tr("change_email_tab", "Email Değiştir"))
        self.setup_email_tab()

    def setup_profile_tab(self):
        """Profil bilgileri tabını oluştur"""
        # Kullanıcı bilgileri frame
        info_frame = tk.Frame(self.profile_frame, bg=self.theme['white'])
        info_frame.pack(fill='x', padx=20, pady=20)

        # Kullanıcı adı
        username_label = tk.Label(info_frame, text=self.lm.tr("username_label", "Kullanıcı Adı:"),
                                 font=('Segoe UI', 12, 'bold'),
                                 fg=self.theme['text_dark'],
                                 bg=self.theme['white'])
        username_label.pack(anchor='w', pady=(0, 5))

        self.username_display = tk.Label(info_frame, text=self.username,
                                        font=('Segoe UI', 12),
                                        fg=self.theme['text_muted'],
                                        bg=self.theme['white'])
        self.username_display.pack(anchor='w', pady=(0, 15))

        # Email
        email_label = tk.Label(info_frame, text=self.lm.tr("email_label", "Email Adresi:"),
                               font=('Segoe UI', 12, 'bold'),
                               fg=self.theme['text_dark'],
                               bg=self.theme['white'])
        email_label.pack(anchor='w', pady=(0, 5))

        self.email_display = tk.Label(info_frame, text="",
                                     font=('Segoe UI', 12),
                                     fg=self.theme['text_muted'],
                                     bg=self.theme['white'])
        self.email_display.pack(anchor='w', pady=(0, 15))

        # Kayıt tarihi
        reg_date_label = tk.Label(info_frame, text=self.lm.tr("reg_date_label", "Kayıt Tarihi:"),
                                 font=('Segoe UI', 12, 'bold'),
                                 fg=self.theme['text_dark'],
                                 bg=self.theme['white'])
        reg_date_label.pack(anchor='w', pady=(0, 5))

        self.reg_date_display = tk.Label(info_frame, text="",
                                        font=('Segoe UI', 12),
                                        fg=self.theme['text_muted'],
                                        bg=self.theme['white'])
        self.reg_date_display.pack(anchor='w', pady=(0, 15))

        # Son giriş
        last_login_label = tk.Label(info_frame, text=self.lm.tr("last_login_label", "Son Giriş:"),
                                   font=('Segoe UI', 12, 'bold'),
                                   fg=self.theme['text_dark'],
                                   bg=self.theme['white'])
        last_login_label.pack(anchor='w', pady=(0, 5))

        self.last_login_display = tk.Label(info_frame, text="",
                                          font=('Segoe UI', 12),
                                          fg=self.theme['text_muted'],
                                          bg=self.theme['white'])
        self.last_login_display.pack(anchor='w')

    def setup_password_tab(self):
        """Şifre değiştir tabını oluştur"""
        # Şifre değiştir frame
        password_frame = tk.Frame(self.password_frame, bg=self.theme['white'])
        password_frame.pack(fill='x', padx=20, pady=20)

        # Mevcut şifre
        current_pass_label = tk.Label(password_frame, text=self.lm.tr("current_pass_label", "Mevcut Şifre:"),
                                     font=('Segoe UI', 12, 'bold'),
                                     fg=self.theme['text_dark'],
                                     bg=self.theme['white'])
        current_pass_label.pack(anchor='w', pady=(0, 5))

        self.current_pass_entry = tk.Entry(password_frame, font=('Segoe UI', 12),
                                          relief='solid', bd=1, show='*',
                                          highlightthickness=1,
                                          highlightcolor=self.theme['primary'])
        self.current_pass_entry.pack(fill='x', pady=(0, 15))

        # Yeni şifre
        new_pass_label = tk.Label(password_frame, text=self.lm.tr("new_pass_label", "Yeni Şifre:"),
                                 font=('Segoe UI', 12, 'bold'),
                                 fg=self.theme['text_dark'],
                                 bg=self.theme['white'])
        new_pass_label.pack(anchor='w', pady=(0, 5))

        self.new_pass_entry = tk.Entry(password_frame, font=('Segoe UI', 12),
                                       relief='solid', bd=1, show='*',
                                       highlightthickness=1,
                                       highlightcolor=self.theme['primary'])
        self.new_pass_entry.pack(fill='x', pady=(0, 15))

        # Şifre tekrar
        confirm_pass_label = tk.Label(password_frame, text=self.lm.tr("confirm_pass_label", "Şifre Tekrar:"),
                                     font=('Segoe UI', 12, 'bold'),
                                     fg=self.theme['text_dark'],
                                     bg=self.theme['white'])
        confirm_pass_label.pack(anchor='w', pady=(0, 5))

        self.confirm_pass_entry = tk.Entry(password_frame, font=('Segoe UI', 12),
                                          relief='solid', bd=1, show='*',
                                          highlightthickness=1,
                                          highlightcolor=self.theme['primary'])
        self.confirm_pass_entry.pack(fill='x', pady=(0, 20))

        # Şifre değiştir butonu
        change_btn = tk.Button(password_frame, text=self.lm.tr("change_password_btn", "Şifreyi Değiştir"),
                              font=('Segoe UI', 12, 'bold'),
                              fg=self.theme['white'],
                              bg=self.theme['primary'],
                              relief='flat', bd=0,
                              cursor='hand2',
                              command=self.change_password,
                              pady=10)
        change_btn.pack(fill='x')

    def setup_email_tab(self):
        """Email değiştir tabını oluştur"""
        # Email değiştir frame
        email_frame = tk.Frame(self.email_frame, bg=self.theme['white'])
        email_frame.pack(fill='x', padx=20, pady=20)

        # Mevcut email
        current_email_label = tk.Label(email_frame, text=self.lm.tr("current_email_label", "Mevcut Email:"),
                                      font=('Segoe UI', 12, 'bold'),
                                      fg=self.theme['text_dark'],
                                      bg=self.theme['white'])
        current_email_label.pack(anchor='w', pady=(0, 5))

        self.current_email_display = tk.Label(email_frame, text="",
                                             font=('Segoe UI', 12),
                                             fg=self.theme['text_muted'],
                                             bg=self.theme['white'])
        self.current_email_display.pack(anchor='w', pady=(0, 15))

        # Yeni email
        new_email_label = tk.Label(email_frame, text=self.lm.tr("new_email_label", "Yeni Email:"),
                                  font=('Segoe UI', 12, 'bold'),
                                  fg=self.theme['text_dark'],
                                  bg=self.theme['white'])
        new_email_label.pack(anchor='w', pady=(0, 5))

        self.new_email_entry = tk.Entry(email_frame, font=('Segoe UI', 12),
                                       relief='solid', bd=1,
                                       highlightthickness=1,
                                       highlightcolor=self.theme['primary'])
        self.new_email_entry.pack(fill='x', pady=(0, 20))

        # Email değiştir butonu
        change_email_btn = tk.Button(email_frame, text=self.lm.tr("change_email_btn", "Email Değiştir"),
                                    font=('Segoe UI', 12, 'bold'),
                                    fg=self.theme['white'],
                                    bg=self.theme['primary'],
                                    relief='flat', bd=0,
                                    cursor='hand2',
                                    command=self.change_email,
                                    pady=10)
        change_email_btn.pack(fill='x')

    def load_user_data(self):
        """Kullanıcı verilerini yükle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT username, email, created_at, last_login 
                FROM users WHERE id = ?
            """, (self.user_id,))

            user_data = cursor.fetchone()

            if user_data:
                username, email, created_at, last_login = user_data

                # Profil bilgilerini güncelle
                self.email_display.config(text=email or self.lm.tr("not_specified", "Belirtilmemiş"))
                self.current_email_display.config(text=email or self.lm.tr("not_specified", "Belirtilmemiş"))

                if created_at:
                    self.reg_date_display.config(text=created_at)
                else:
                    self.reg_date_display.config(text=self.lm.tr("unknown", "Bilinmiyor"))

                if last_login:
                    self.last_login_display.config(text=last_login)
                else:
                    self.last_login_display.config(text=self.lm.tr("first_login", "İlk giriş"))

            conn.close()

        except Exception as e:
            logging.error(f"Kullanıcı verisi yükleme hatası: {e}")

    def change_password(self):
        """Şifre değiştir"""
        try:
            current_password = self.current_pass_entry.get().strip()
            new_password = self.new_pass_entry.get().strip()
            confirm_password = self.confirm_pass_entry.get().strip()

            if not current_password or not new_password or not confirm_password:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("fill_all_fields", "Lütfen tüm alanları doldurun!"))
                return

            if new_password != confirm_password:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("passwords_not_match", "Yeni şifreler eşleşmiyor!"))
                return

            if len(new_password) < 6:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("password_too_short", "Şifre en az 6 karakter olmalı!"))
                return

            # Mevcut şifreyi kontrol et
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT password_hash FROM users WHERE id = ?", (self.user_id,))
            stored_password = cursor.fetchone()[0]

            if not verify_password(current_password, stored_password):
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("current_password_wrong", "Mevcut şifre yanlış!"))
                conn.close()
                return

            # Yeni şifreyi kaydet
            hashed_password = hash_password(new_password)
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                          (hashed_password, self.user_id))

            conn.commit()
            conn.close()

            messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("password_changed_success", "Şifre başarıyla değiştirildi!"))

            # Formu temizle
            self.current_pass_entry.delete(0, tk.END)
            self.new_pass_entry.delete(0, tk.END)
            self.confirm_pass_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("password_change_error", "Şifre değiştirme hatası: ") + str(e))

    def change_email(self):
        """Email değiştir"""
        try:
            new_email = self.new_email_entry.get().strip()

            if not new_email:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("enter_new_email", "Lütfen yeni email adresini girin!"))
                return

            if '@' not in new_email:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("invalid_email", "Geçerli bir email adresi girin!"))
                return

            # Email'i güncelle
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("UPDATE users SET email = ? WHERE id = ?",
                          (new_email, self.user_id))

            conn.commit()
            conn.close()

            # Profil bilgilerini güncelle
            self.email_display.config(text=new_email)
            self.current_email_display.config(text=new_email)

            messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("email_changed_success", "Email adresi başarıyla değiştirildi!"))

            # Formu temizle
            self.new_email_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("email_change_error", "Email değiştirme hatası: ") + str(e))

def show_user_profile(parent, db_path, user_id, username):
    """Kullanıcı profil penceresini göster"""
    UserProfileGUI(parent, db_path, user_id, username)
