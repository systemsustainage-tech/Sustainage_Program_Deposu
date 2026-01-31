#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUSTAINAGE SDG - Şifre Sıfırlama GUI
- OTP bazlı güvenli şifre sıfırlama
- Email gönderimi
- Yeni şifre belirleme
"""

import logging
import os
import secrets
import sqlite3
import string
import sys
import tkinter as tk
from datetime import datetime, timedelta

from utils.ui_theme import apply_theme

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.email_service import EmailService
from config.icons import Icons

try:
    from security.core.secure_password import PasswordPolicy as GlobalPasswordPolicy
except Exception:
    GlobalPasswordPolicy = None


class PasswordResetGUI:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.otp_code = None
        self.username = None
        self.email = None

        # Tema
        self.theme = {
            'primary': '#2E8B57',
            'primary_hover': '#3CB371',
            'danger': '#DC143C',
            'bg_light': '#f0f0f0',
            'white': '#ffffff',
            'text_dark': '#333333',
            'text_muted': '#666666'
        }

        self.setup_window()

    def setup_window(self):
        """Şifre sıfırlama penceresini oluştur"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Şifre Sıfırlama - Sustainage")
        self.window.geometry("450x400")
        self.window.configure(bg=self.theme['white'])
        self.window.resizable(False, False)
        apply_theme(self.window)

        # Pencereyi ortala
        self.window.transient(self.parent)
        self.window.grab_set()

        # Ana frame
        main_frame = tk.Frame(self.window, bg=self.theme['white'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        title_label = tk.Label(main_frame, text="Şifre Sıfırlama",
                              font=('Segoe UI', 18, 'bold'),
                              fg=self.theme['primary'],
                              bg=self.theme['white'])
        title_label.pack(pady=(0, 20))

        # Açıklama
        desc_label = tk.Label(main_frame,
                              text="Kullanıcı adınızı girin, email adresinize OTP kodu gönderilecek.",
                              font=('Segoe UI', 10),
                              fg=self.theme['text_muted'],
                              bg=self.theme['white'],
                              wraplength=400)
        desc_label.pack(pady=(0, 20))

        # Form frame
        form_frame = tk.Frame(main_frame, bg=self.theme['white'])
        form_frame.pack(fill='x', pady=(0, 20))

        # Kullanıcı adı
        username_label = tk.Label(form_frame, text="Kullanıcı Adı:",
                                 font=('Segoe UI', 12, 'bold'),
                                 fg=self.theme['text_dark'],
                                 bg=self.theme['white'])
        username_label.pack(anchor='w', pady=(0, 5))

        self.username_entry = tk.Entry(form_frame, font=('Segoe UI', 12),
                                      relief='solid', bd=1,
                                      highlightthickness=1,
                                      highlightcolor=self.theme['primary'])
        self.username_entry.pack(fill='x', pady=(0, 15))

        # OTP gönder butonu
        self.send_otp_btn = tk.Button(form_frame, text="OTP Kodu Gönder",
                                     font=('Segoe UI', 12, 'bold'),
                                     fg=self.theme['white'],
                                     bg=self.theme['primary'],
                                     relief='flat', bd=0,
                                     cursor='hand2',
                                     command=self.send_otp_code,
                                     pady=10)
        self.send_otp_btn.pack(fill='x', pady=(0, 20))

        # OTP kodu frame (başlangıçta gizli)
        self.otp_frame = tk.Frame(form_frame, bg=self.theme['white'])

        # OTP kodu
        otp_label = tk.Label(self.otp_frame, text="OTP Kodu:",
                            font=('Segoe UI', 12, 'bold'),
                            fg=self.theme['text_dark'],
                            bg=self.theme['white'])
        otp_label.pack(anchor='w', pady=(0, 5))

        self.otp_entry = tk.Entry(self.otp_frame, font=('Segoe UI', 12),
                                 relief='solid', bd=1,
                                 highlightthickness=1,
                                 highlightcolor=self.theme['primary'])
        self.otp_entry.pack(fill='x', pady=(0, 10))

        # Yeni şifre
        new_pass_label = tk.Label(self.otp_frame, text="Yeni Şifre:",
                                 font=('Segoe UI', 12, 'bold'),
                                 fg=self.theme['text_dark'],
                                 bg=self.theme['white'])
        new_pass_label.pack(anchor='w', pady=(0, 5))

        self.new_pass_entry = tk.Entry(self.otp_frame, font=('Segoe UI', 12),
                                       relief='solid', bd=1,
                                       show='*',
                                       highlightthickness=1,
                                       highlightcolor=self.theme['primary'])
        self.new_pass_entry.pack(fill='x', pady=(0, 15))

        # Şifre tekrar
        confirm_pass_label = tk.Label(self.otp_frame, text="Şifre Tekrar:",
                                     font=('Segoe UI', 12, 'bold'),
                                     fg=self.theme['text_dark'],
                                     bg=self.theme['white'])
        confirm_pass_label.pack(anchor='w', pady=(0, 5))

        self.confirm_pass_entry = tk.Entry(self.otp_frame, font=('Segoe UI', 12),
                                          relief='solid', bd=1,
                                          show='*',
                                          highlightthickness=1,
                                          highlightcolor=self.theme['primary'])
        self.confirm_pass_entry.pack(fill='x', pady=(0, 15))

        # Şifre sıfırla butonu
        self.reset_btn = tk.Button(self.otp_frame, text=f"{Icons.SUCCESS} Şifreyi Sıfırla",
                                 font=('Segoe UI', 12, 'bold'),
                                 fg=self.theme['white'],
                                 bg=self.theme['primary'],
                                 relief='flat', bd=0,
                                 cursor='hand2',
                                 command=self.reset_password,
                                 pady=10)
        self.reset_btn.pack(fill='x', pady=(10, 0))

        # Hata mesajı
        self.error_label = tk.Label(form_frame, text="",
                                   font=('Segoe UI', 10),
                                   fg=self.theme['danger'],
                                   bg=self.theme['white'])
        self.error_label.pack(anchor='w', pady=(10, 0))

        # Başlangıçta OTP frame'i gizle
        self.otp_frame.pack_forget()

    def send_otp_code(self):
        """OTP kodu gönder"""
        try:
            username = self.username_entry.get().strip()
            if not username:
                self.show_error("Lütfen kullanıcı adınızı girin!")
                return

            # Kullanıcıyı kontrol et
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT id, username, email FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()

            if not user:
                self.show_error("Kullanıcı bulunamadı!")
                conn.close()
                return

            user_id, username, email = user
            self.username = username
            self.email = email

            # OTP kodu oluştur
            self.otp_code = ''.join(secrets.choice(string.digits) for _ in range(6))

            # OTP'yi veritabanına kaydet (15 dakika geçerli)
            expires_at = datetime.now() + timedelta(minutes=15)
            cursor.execute("""
                INSERT OR REPLACE INTO password_reset_tokens 
                (user_id, token, expires_at, created_at) 
                VALUES (?, ?, ?, ?)
            """, (user_id, self.otp_code, expires_at, datetime.now()))

            conn.commit()
            conn.close()

            # Email gönder
            try:
                email_service = EmailService(self.db_path)
                subject = "Sustainage - Şifre Sıfırlama Kodu"
                body = f"""
Merhaba {username},

Şifre sıfırlama talebiniz alınmıştır.

OTP Kodunuz: {self.otp_code}

Bu kod 15 dakika geçerlidir.

Güvenliğiniz için bu kodu kimseyle paylaşmayın.

Sustainage
"""

                success = email_service.send_email(email, subject, body)

                if success:
                    self.show_success(f"OTP kodu {email} adresine gönderildi!")
                    self.show_otp_form()
                else:
                    self.show_error("Email gönderilemedi! Lütfen tekrar deneyin.")

            except Exception as e:
                self.show_error(f"Email gönderme hatası: {str(e)}")

        except Exception as e:
            self.show_error(f"Hata: {str(e)}")

    def show_otp_form(self):
        """OTP formunu göster - alanlar zaten setup_window'da oluşturuldu"""
        # OTP frame'i görünür yap
        self.otp_frame.pack(fill='x', pady=(0, 20))

        # Pencereyi büyüt (tüm alanlar sığsın)
        self.window.geometry("500x650")

        # OTP input'a focus ver
        self.otp_entry.focus_set()

    def reset_password(self):
        """Şifreyi sıfırla"""
        try:
            otp = self.otp_entry.get().strip()
            new_password = self.new_pass_entry.get().strip()
            confirm_password = self.confirm_pass_entry.get().strip()

            if not otp or not new_password or not confirm_password:
                self.show_error("Lütfen tüm alanları doldurun!")
                return

            if new_password != confirm_password:
                self.show_error("Şifreler eşleşmiyor!")
                return

            if GlobalPasswordPolicy is not None:
                ok, msg = GlobalPasswordPolicy.validate(new_password)
                if not ok:
                    self.show_error(msg or "Şifre politikaya uymuyor!")
                    return
            else:
                if len(new_password) < 6:
                    self.show_error("Şifre en az 6 karakter olmalı!")
                    return

            # OTP'yi kontrol et
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT user_id FROM password_reset_tokens 
                WHERE token = ? AND expires_at > ? AND user_id = (
                    SELECT id FROM users WHERE username = ?
                )
            """, (otp, datetime.now(), self.username))

            result = cursor.fetchone()

            if not result:
                self.show_error("Geçersiz veya süresi dolmuş OTP kodu!")
                conn.close()
                return

            # Şifreyi güncelle
            from yonetim.security.core.crypto import hash_password
            hashed_password = hash_password(new_password)

            cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?",
                          (hashed_password, self.username))

            # OTP'yi sil
            cursor.execute("DELETE FROM password_reset_tokens WHERE token = ?", (otp,))

            conn.commit()
            conn.close()

            self.show_success("Şifre başarıyla sıfırlandı!")

            # 2 saniye sonra pencereyi kapat
            self.window.after(2000, self.window.destroy)

        except Exception as e:
            self.show_error(f"Hata: {str(e)}")

    def show_error(self, message):
        """Hata mesajı göster"""
        self.error_label.config(text=message)
        self.error_label.pack(anchor='w', pady=(10, 0))

    def show_success(self, message):
        """Başarı mesajı göster"""
        self.error_label.config(text=message, fg='#28a745')
        self.error_label.pack(anchor='w', pady=(10, 0))

def show_password_reset_window(parent, db_path):
    """Şifre sıfırlama penceresini göster"""
    # Önce password_reset_tokens tablosunu oluştur
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Tablo oluşturma hatası: {e}")

    # GUI'yi başlat
    PasswordResetGUI(parent, db_path)
