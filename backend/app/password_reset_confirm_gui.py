#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Şifre Sıfırlama Onay GUI
Token doğrulama ve yeni şifre belirleme
"""

import logging
import os
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

from yonetim.security.core.crypto import hash_password as secure_hash_password


class PasswordResetConfirmGUI:
    def __init__(self, parent, token: str) -> None:
        self.parent = parent
        self.token = token

        # Veritabanı yolu
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(self.base_dir, "data", "sdg_desktop.sqlite")

        # Token doğrulama
        self.user_id = self.verify_token()
        if not self.user_id:
            messagebox.showerror("Hata", "Geçersiz veya süresi dolmuş şifre sıfırlama bağlantısı.")
            return

        # Şifre sıfırlama penceresi
        self.window = tk.Toplevel(parent)
        self.window.title("Yeni Şifre Belirle")
        self.window.geometry("500x450")
        self.window.configure(bg='white')
        self.window.resizable(False, False)

        # Pencereyi ortala
        self.center_window()

        # UI oluştur
        self.setup_ui()

        # Pencereyi modal yap
        self.window.transient(parent)
        self.window.grab_set()

    def center_window(self) -> None:
        """Pencereyi ekranın ortasına yerleştir"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self) -> None:
        """UI oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.window, bg='white')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#f8f9fa', relief='solid', bd=1)
        title_frame.pack(fill='x', pady=(0, 20))

        title_label = tk.Label(title_frame, text=" Yeni Şifre Belirle",
                              font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='#f8f9fa')
        title_label.pack(pady=15)

        # Açıklama
        desc_frame = tk.Frame(main_frame, bg='white')
        desc_frame.pack(fill='x', pady=(0, 20))

        desc_label = tk.Label(desc_frame,
                             text="Güvenli bir şifre belirleyin.\n"
                                  "Şifreniz en az 8 karakter olmalı ve harf, rakam içermelidir.",
                             font=('Segoe UI', 10), fg='#666666', bg='white', justify='center')
        desc_label.pack()

        # Form frame
        form_frame = tk.Frame(main_frame, bg='white')
        form_frame.pack(fill='x', pady=(0, 20))

        # Yeni şifre alanı
        password_frame = tk.Frame(form_frame, bg='white')
        password_frame.pack(fill='x', pady=(0, 15))

        tk.Label(password_frame, text="Yeni Şifre:",
                font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w')

        self.password_entry = tk.Entry(password_frame, font=('Segoe UI', 11), width=40,
                                     relief='solid', bd=1, show='*')
        self.password_entry.pack(fill='x', pady=(5, 0), ipady=8)

        # Şifre göster/gizle butonu
        show_frame = tk.Frame(password_frame, bg='white')
        show_frame.pack(fill='x', pady=(5, 0))

        self.show_var = tk.BooleanVar()
        show_check = tk.Checkbutton(show_frame, text="Şifreyi göster",
                                   variable=self.show_var, bg='white',
                                   command=self.toggle_password_visibility)
        show_check.pack(anchor='w')

        # Şifre tekrar alanı
        confirm_frame = tk.Frame(form_frame, bg='white')
        confirm_frame.pack(fill='x', pady=(0, 15))

        tk.Label(confirm_frame, text="Şifre Tekrar:",
                font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w')

        self.confirm_entry = tk.Entry(confirm_frame, font=('Segoe UI', 11), width=40,
                                     relief='solid', bd=1, show='*')
        self.confirm_entry.pack(fill='x', pady=(5, 0), ipady=8)

        # Şifre güçlülük göstergesi
        strength_frame = tk.Frame(form_frame, bg='white')
        strength_frame.pack(fill='x', pady=(0, 15))

        tk.Label(strength_frame, text="Şifre Güçlülüğü:",
                font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w')

        self.strength_label = tk.Label(strength_frame, text="",
                                      font=('Segoe UI', 9), bg='white')
        self.strength_label.pack(anchor='w', pady=(5, 0))

        # Şifre değişikliği olayını dinle
        self.password_entry.bind('<KeyRelease>', self.check_password_strength)
        self.confirm_entry.bind('<KeyRelease>', self.check_password_match)

        # Butonlar
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill='x', pady=(20, 0))

        tk.Button(button_frame, text=" Şifreyi Güncelle",
                 font=('Segoe UI', 11, 'bold'), bg='#27ae60', fg='white',
                 relief='raised', bd=2, padx=20, pady=10, cursor='hand2',
                 command=self.update_password).pack(side='left')

        tk.Button(button_frame, text=" İptal",
                 font=('Segoe UI', 11, 'bold'), bg='#95a5a6', fg='white',
                 relief='raised', bd=2, padx=20, pady=10, cursor='hand2',
                 command=self.window.destroy).pack(side='right')

        # Durum mesajı
        self.status_label = tk.Label(main_frame, text="",
                                    font=('Segoe UI', 9), bg='white')
        self.status_label.pack(pady=(20, 0))

        # Enter tuşu ile güncelle
        self.window.bind('<Return>', lambda e: self.update_password())

        # Şifre alanına focus
        self.password_entry.focus()

    def toggle_password_visibility(self) -> None:
        """Şifre görünürlüğünü değiştir"""
        if self.show_var.get():
            self.password_entry.config(show='')
            self.confirm_entry.config(show='')
        else:
            self.password_entry.config(show='*')
            self.confirm_entry.config(show='*')

    def check_password_strength(self, event=None) -> None:
        """Şifre güçlülüğünü kontrol et"""
        password = self.password_entry.get()

        if not password:
            self.strength_label.config(text="", fg='black')
            return

        strength = 0
        feedback = []

        # Uzunluk kontrolü
        if len(password) >= 8:
            strength += 1
        else:
            feedback.append("En az 8 karakter")

        # Küçük harf kontrolü
        if any(c.islower() for c in password):
            strength += 1
        else:
            feedback.append("Küçük harf")

        # Büyük harf kontrolü
        if any(c.isupper() for c in password):
            strength += 1
        else:
            feedback.append("Büyük harf")

        # Rakam kontrolü
        if any(c.isdigit() for c in password):
            strength += 1
        else:
            feedback.append("Rakam")

        # Özel karakter kontrolü
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            strength += 1
        else:
            feedback.append("Özel karakter")

        # Güçlülük seviyesini göster
        if strength <= 2:
            level = "Zayıf"
            color = "#e74c3c"
        elif strength <= 4:
            level = "Orta"
            color = "#f39c12"
        else:
            level = "Güçlü"
            color = "#27ae60"

        if feedback:
            feedback_text = f"{level} - Eksik: {', '.join(feedback)}"
        else:
            feedback_text = f"{level} - Şifre güvenli"

        self.strength_label.config(text=feedback_text, fg=color)

    def check_password_match(self, event=None) -> None:
        """Şifre eşleşmesini kontrol et"""
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        if confirm and password != confirm:
            self.status_label.config(text="Şifreler eşleşmiyor!", fg='#e74c3c')
        else:
            self.status_label.config(text="", fg='black')

    def verify_token(self) -> int:
        """Token'ı doğrula ve kullanıcı ID'sini döndür"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Token tablosunu kontrol et
            cursor.execute("""
                SELECT user_id FROM password_reset_tokens 
                WHERE token = ? AND expires_at > ? AND used = 0
            """, (self.token, datetime.now().isoformat()))

            result = cursor.fetchone()
            conn.close()

            return result[0] if result else None

        except Exception as e:
            logging.error(f"Token doğrulanırken hata: {e}")
            return None

    def update_password(self) -> None:
        """Şifreyi güncelle"""
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        # Validasyon
        if not password or not confirm:
            self.show_status("Tüm alanları doldurun.", "error")
            return

        if password != confirm:
            self.show_status("Şifreler eşleşmiyor!", "error")
            return

        if len(password) < 8:
            self.show_status("Şifre en az 8 karakter olmalıdır.", "error")
            return

        if not self.is_password_strong_enough(password):
            self.show_status("Şifre çok zayıf. Lütfen daha güçlü bir şifre seçin.", "error")
            return

        try:
            # Şifreyi güvenli biçimde hash'le (Argon2)
            password_hash = secure_hash_password(password)

            # Veritabanında güncelle
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE users SET password_hash = ?, updated_at = ?
                WHERE id = ?
            """, (password_hash, datetime.now().isoformat(), self.user_id))

            # Token'ı kullanılmış olarak işaretle
            cursor.execute("""
                UPDATE password_reset_tokens SET used = 1 
                WHERE token = ?
            """, (self.token,))

            conn.commit()
            conn.close()

            self.show_status("Şifreniz başarıyla güncellendi!", "success")

            # 2 saniye sonra pencereyi kapat
            self.window.after(2000, self.window.destroy)

        except Exception as e:
            self.show_status(f"Hata: {str(e)}", "error")

    def is_password_strong_enough(self, password: str) -> bool:
        """Şifrenin yeterince güçlü olup olmadığını kontrol et"""
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)

        return has_lower and has_upper and has_digit

    def show_status(self, message: str, status_type: str = "info") -> None:
        """Durum mesajını göster"""
        colors = {
            "success": "#27ae60",
            "error": "#e74c3c",
            "warning": "#f39c12",
            "info": "#3498db"
        }

        self.status_label.config(text=message, fg=colors.get(status_type, "#3498db"))

def show_password_reset_confirm_window(parent, token: str) -> None:
    """Şifre sıfırlama onay penceresini göster"""
    PasswordResetConfirmGUI(parent, token)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ana pencereyi gizle
    show_password_reset_confirm_window(root, "test_token")
    root.mainloop()
