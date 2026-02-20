#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUSTAINAGE SDG - İlk Giriş Şifre Değiştirme
- İlk giriş yapan kullanıcılar için zorunlu şifre değiştirme
- Güvenlik kontrolü
"""

import os
import sqlite3
import sys
import tkinter as tk
from tkinter import messagebox, ttk

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from yonetim.security.core.crypto import hash_password, verify_password

try:
    from security.core.secure_password import PasswordPolicy as GlobalPasswordPolicy
except Exception:
    GlobalPasswordPolicy = None


class FirstLoginPasswordChange:
    def __init__(self, parent, db_path, user_id, username):
        self.parent = parent
        self.db_path = db_path
        self.user_id = user_id
        self.username = username

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

    def setup_window(self):
        """İlk giriş şifre değiştirme penceresini oluştur"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("İlk Giriş - Şifre Değiştirme")
        self.window.geometry("500x500")
        self.window.configure(bg=self.theme['white'])
        self.window.resizable(True, True)
        self.window.minsize(500, 500)

        # Pencereyi ortala ve modal yap
        self.window.transient(self.parent)
        self.window.grab_set()

        # Pencere kapatma kontrolü
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Ana frame - scrollable
        canvas = tk.Canvas(self.window, bg=self.theme['white'])
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme['white'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        main_frame = scrollable_frame

        # Başlık
        title_label = tk.Label(main_frame, text="İlk Giriş - Şifre Değiştirme",
                              font=('Segoe UI', 18, 'bold'),
                              fg=self.theme['primary'],
                              bg=self.theme['white'])
        title_label.pack(pady=(0, 10))

        # Açıklama
        desc_label = tk.Label(main_frame,
                              text=f"Merhaba {self.username}!\n\nGüvenlik nedeniyle ilk girişinizde şifrenizi değiştirmeniz gerekmektedir.",
                              font=('Segoe UI', 12),
                              fg=self.theme['text_dark'],
                              bg=self.theme['white'],
                              justify='center')
        desc_label.pack(pady=(0, 20))

        # Form frame
        form_frame = tk.Frame(main_frame, bg=self.theme['white'])
        form_frame.pack(fill='x', pady=(0, 20), padx=20)

        # Mevcut şifre
        current_pass_label = tk.Label(form_frame, text="Mevcut Şifre:",
                                     font=('Segoe UI', 12, 'bold'),
                                     fg=self.theme['text_dark'],
                                     bg=self.theme['white'])
        current_pass_label.pack(anchor='w', pady=(0, 5))

        self.current_pass_entry = tk.Entry(form_frame, font=('Segoe UI', 12),
                                          relief='solid', bd=1, show='*',
                                          highlightthickness=1,
                                          highlightcolor=self.theme['primary'])
        self.current_pass_entry.pack(fill='x', pady=(0, 15))

        # Yeni şifre
        new_pass_label = tk.Label(form_frame, text="Yeni Şifre:",
                                 font=('Segoe UI', 12, 'bold'),
                                 fg=self.theme['text_dark'],
                                 bg=self.theme['white'])
        new_pass_label.pack(anchor='w', pady=(0, 5))

        self.new_pass_entry = tk.Entry(form_frame, font=('Segoe UI', 12),
                                       relief='solid', bd=1, show='*',
                                       highlightthickness=1,
                                       highlightcolor=self.theme['primary'])
        self.new_pass_entry.pack(fill='x', pady=(0, 15))

        # Şifre tekrar
        confirm_pass_label = tk.Label(form_frame, text="Şifre Tekrar:",
                                     font=('Segoe UI', 12, 'bold'),
                                     fg=self.theme['text_dark'],
                                     bg=self.theme['white'])
        confirm_pass_label.pack(anchor='w', pady=(0, 5))

        self.confirm_pass_entry = tk.Entry(form_frame, font=('Segoe UI', 12),
                                          relief='solid', bd=1, show='*',
                                          highlightthickness=1,
                                          highlightcolor=self.theme['primary'])
        self.confirm_pass_entry.pack(fill='x', pady=(0, 20))

        # Şifre değiştir butonu
        change_btn = tk.Button(form_frame, text="Şifreyi Değiştir",
                              font=('Segoe UI', 12, 'bold'),
                              fg=self.theme['white'],
                              bg=self.theme['primary'],
                              relief='flat', bd=0,
                              cursor='hand2',
                              command=self.change_password,
                              pady=10)
        change_btn.pack(fill='x', pady=(10, 20))

        # Hata mesajı
        self.error_label = tk.Label(main_frame, text="",
                                   font=('Segoe UI', 10),
                                   fg=self.theme['danger'],
                                   bg=self.theme['white'])

        # Enter tuşu ile şifre değiştir
        self.window.bind('<Return>', lambda e: self.change_password())

        # ESC tuşu ile çıkış
        self.window.bind('<Escape>', lambda e: self.on_closing())

    def change_password(self):
        """Şifre değiştir"""
        try:
            current_password = self.current_pass_entry.get().strip()
            new_password = self.new_pass_entry.get().strip()
            confirm_password = self.confirm_pass_entry.get().strip()

            if not current_password or not new_password or not confirm_password:
                self.show_error("Lütfen tüm alanları doldurun!")
                return

            if new_password != confirm_password:
                self.show_error("Yeni şifreler eşleşmiyor!")
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

            # Mevcut şifreyi kontrol et
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT password_hash FROM users WHERE id = ?", (self.user_id,))
            result = cursor.fetchone()

            if not result:
                self.show_error("Kullanıcı bulunamadı!")
                conn.close()
                return

            stored_password = result[0]

            is_valid = False
            try:
                from yonetim.security.core.crypto import verify_password_compat
            except Exception:
                verify_password_compat = None

            if (stored_password or '').startswith('$argon2'):
                is_valid = verify_password(stored_password, current_password)
            elif (stored_password or '').startswith('pbkdf2$') or (':' in (stored_password or '')):
                if verify_password_compat:
                    is_valid = verify_password_compat(stored_password, current_password)
                else:
                    try:
                        payload = stored_password or ''
                        if payload.startswith('pbkdf2$'):
                            payload = payload.split('pbkdf2$', 1)[1]
                        if ':' in payload:
                            salt, h = payload.split(':', 1)
                            import hashlib
                            calc = hashlib.pbkdf2_hmac('sha256', current_password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
                            is_valid = (calc == h)
                    except Exception:
                        is_valid = False
            else:
                import hashlib
                old_hash = hashlib.sha256(current_password.encode()).hexdigest()
                is_valid = (stored_password == old_hash)

            if not is_valid:
                self.show_error("Mevcut şifre yanlış!")
                conn.close()
                return

            # Yeni şifreyi kaydet ve ilk giriş/mecburi değişim bayraklarını temizle
            hashed_password = hash_password(new_password)
            cursor.execute("UPDATE users SET password_hash = ?, first_login = 0, must_change_password = 0 WHERE id = ?",
                          (hashed_password, self.user_id))

            conn.commit()
            conn.close()

            self.show_success("Şifre başarıyla değiştirildi!")

            # 2 saniye sonra pencereyi kapat
            self.window.after(2000, self.window.destroy)

        except Exception as e:
            self.show_error(f"Şifre değiştirme hatası: {str(e)}")

    def show_error(self, message):
        """Hata mesajı göster"""
        self.error_label.config(text=message, fg=self.theme['danger'])
        self.error_label.pack(anchor='w', pady=(10, 0))

    def show_success(self, message):
        """Başarı mesajı göster"""
        self.error_label.config(text=message, fg=self.theme['success'])
        self.error_label.pack(anchor='w', pady=(10, 0))

    def on_closing(self):
        """Pencere kapatma - onay iste"""
        result = messagebox.askyesno(
            "Çıkış Onayı",
            "İlk giriş şifre değiştirme zorunludur!\n\nÇıkmak istediğinizden emin misiniz?\n\nÇıkarsanız sistem güvenliği için tekrar giriş yapmanız gerekecek."
        )

        if result:
            # Kullanıcı çıkmak istiyor - pencereyi kapat
            self.window.destroy()
            # Ana pencereyi de kapat (güvenlik için)
            if hasattr(self.parent, 'destroy'):
                self.parent.destroy()

def show_first_login_password_change(parent, db_path, user_id, username):
    """İlk giriş şifre değiştirme penceresini göster"""
    FirstLoginPasswordChange(parent, db_path, user_id, username)
