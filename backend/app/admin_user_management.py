#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUSTAINAGE SDG - Admin Kullanıcı Yönetimi
- Yeni kullanıcı oluşturma
- Kullanıcı listesi
- Kullanıcı düzenleme
- Kullanıcı silme
"""

import logging
import os
import secrets
import sqlite3
import string
import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from utils.language_manager import LanguageManager
from utils.tooltip import bind_treeview_header_tooltips

# Email servisi import
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.email_service import EmailService
from yonetim.security.core.crypto import hash_password


class AdminUserManagement:
    def __init__(self, parent, db_path, admin_user_id):
        self.parent = parent
        self.db_path = db_path
        self.admin_user_id = admin_user_id
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
        self.load_users()

    def setup_window(self):
        """Admin kullanıcı yönetimi penceresini oluştur"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Kullanıcı Yönetimi - Admin Panel")
        self.window.geometry("800x600")
        self.window.configure(bg=self.theme['white'])
        self.window.resizable(True, True)

        # Pencereyi ortala
        self.window.transient(self.parent)
        self.window.grab_set()

        # Ana frame
        main_frame = tk.Frame(self.window, bg=self.theme['white'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        title_label = tk.Label(main_frame, text="Kullanıcı Yönetimi",
                              font=('Segoe UI', 12, 'bold'),
                              fg=self.theme['primary'],
                              bg=self.theme['white'])
        title_label.pack(pady=(0, 20))

        # Kullanıcı listesi
        self.setup_user_list()

    def setup_user_list(self):
        """Kullanıcı listesini oluştur"""
        container = tk.Frame(self.window, bg=self.theme['white'])
        container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        paned = ttk.Panedwindow(container, orient='horizontal')
        paned.pack(fill='both', expand=True)
        left_menu = tk.Frame(paned, bg=self.theme['white'], relief='solid', bd=1)
        tree_frame = tk.Frame(paned, bg=self.theme['white'], relief='solid', bd=1)
        paned.add(left_menu, weight=1)
        paned.add(tree_frame, weight=4)

        # Treeview
        columns = ('ID', 'Kullanıcı Adı', 'Email', 'Kayıt Tarihi', 'Son Giriş', 'Durum')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        # Sütun başlıkları
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        try:
            bind_treeview_header_tooltips(self.tree)
        except Exception as e:
            logging.error(f"Warning: Failed to bind treeview tooltips: {e}")

        # Çift tıklama olayı
        self.tree.bind('<Double-1>', self.edit_user)

    def load_users(self):
        """Kullanıcıları yükle"""
        try:
            # Mevcut verileri temizle
            for item in self.tree.get_children():
                self.tree.delete(item)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, username, email, created_at, last_login, first_login, must_change_password
                FROM users ORDER BY created_at DESC
            """)

            users = cursor.fetchall()

            for user in users:
                user_id, username, email, created_at, last_login, first_login, must_change = user

                # Durum belirleme
                if (first_login == 1) or (must_change == 1):
                    status = "İlk Giriş Gerekli"
                elif last_login:
                    status = "Aktif"
                else:
                    status = "Pasif"

                # Kayıt tarihi formatla
                if created_at:
                    reg_date = created_at[:10] if len(created_at) > 10 else created_at
                else:
                    reg_date = "Bilinmiyor"

                # Son giriş formatla
                if last_login:
                    login_date = last_login[:10] if len(last_login) > 10 else last_login
                else:
                    login_date = "Hiç giriş yapmamış"

                self.tree.insert('', 'end', values=(
                    user_id, username, email or "Belirtilmemiş",
                    reg_date, login_date, status
                ))

            conn.close()

        except Exception as e:
            messagebox.showerror("Hata", f"Kullanıcı listesi yükleme hatası: {str(e)}")

    def create_new_user(self):
        """Yeni kullanıcı oluştur"""
        try:
            # Yeni kullanıcı penceresi
            user_window = tk.Toplevel(self.window)
            user_window.title(self.lm.tr("create_user_title", "Yeni Kullanıcı Oluştur"))
            user_window.geometry("500x400")
            user_window.configure(bg=self.theme['white'])
            user_window.resizable(False, False)
            user_window.transient(self.window)
            user_window.grab_set()

            # Ana frame
            main_frame = tk.Frame(user_window, bg=self.theme['white'])
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)

            # Başlık
            title_label = tk.Label(main_frame, text=self.lm.tr("create_user_header", "Yeni Kullanıcı Oluştur"),
                                  font=('Segoe UI', 16, 'bold'),
                                  fg=self.theme['primary'],
                                  bg=self.theme['white'])
            title_label.pack(pady=(0, 20))

            # Form frame
            form_frame = tk.Frame(main_frame, bg=self.theme['white'])
            form_frame.pack(fill='x', pady=(0, 20))

            # Kullanıcı adı
            username_label = tk.Label(form_frame, text=self.lm.tr("username_label", "Kullanıcı Adı:"),
                                     font=('Segoe UI', 12, 'bold'),
                                     fg=self.theme['text_dark'],
                                     bg=self.theme['white'])
            username_label.pack(anchor='w', pady=(0, 5))

            username_entry = tk.Entry(form_frame, font=('Segoe UI', 12),
                                     relief='solid', bd=1,
                                     highlightthickness=1,
                                     highlightcolor=self.theme['primary'])
            username_entry.pack(fill='x', pady=(0, 15))

            # Email
            email_label = tk.Label(form_frame, text=self.lm.tr("email_label", "Email Adresi:"),
                                  font=('Segoe UI', 12, 'bold'),
                                  fg=self.theme['text_dark'],
                                  bg=self.theme['white'])
            email_label.pack(anchor='w', pady=(0, 5))

            email_entry = tk.Entry(form_frame, font=('Segoe UI', 12),
                                  relief='solid', bd=1,
                                  highlightthickness=1,
                                  highlightcolor=self.theme['primary'])
            email_entry.pack(fill='x', pady=(0, 15))

            # Geçici şifre
            temp_pass_label = tk.Label(form_frame, text=self.lm.tr("temp_pass_label", "Geçici Şifre:"),
                                      font=('Segoe UI', 12, 'bold'),
                                      fg=self.theme['text_dark'],
                                      bg=self.theme['white'])
            temp_pass_label.pack(anchor='w', pady=(0, 5))

            temp_pass_entry = tk.Entry(form_frame, font=('Segoe UI', 12),
                                      relief='solid', bd=1, show='*',
                                      highlightthickness=1,
                                      highlightcolor=self.theme['primary'])
            temp_pass_entry.pack(fill='x', pady=(0, 20))

            # Geçici şifre oluştur butonu
            def generate_temp_password():
                temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
                temp_pass_entry.delete(0, tk.END)
                temp_pass_entry.insert(0, temp_password)

            gen_pass_btn = tk.Button(form_frame, text=self.lm.tr("generate_temp_pass_btn", "Geçici Şifre Oluştur"),
                                    font=('Segoe UI', 10),
                                    fg=self.theme['white'],
                                    bg=self.theme['success'],
                                    relief='flat', bd=0,
                                    cursor='hand2',
                                    command=generate_temp_password,
                                    pady=5)
            gen_pass_btn.pack(anchor='w', pady=(0, 20))

            # Oluştur butonu
            def create_user():
                username = username_entry.get().strip()
                email = email_entry.get().strip()
                temp_password = temp_pass_entry.get().strip()

                if not username or not email or not temp_password:
                    messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("fill_all_fields", "Lütfen tüm alanları doldurun!"))
                    return

                if '@' not in email:
                    messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("invalid_email", "Geçerli bir email adresi girin!"))
                    return

                try:
                    # Kullanıcıyı oluştur
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    # Kullanıcı adı kontrolü
                    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                    if cursor.fetchone():
                        messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("username_taken", "Bu kullanıcı adı zaten kullanılıyor!"))
                        conn.close()
                        return

                    # Email kontrolü
                    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                    if cursor.fetchone():
                        messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("email_taken", "Bu email adresi zaten kullanılıyor!"))
                        conn.close()
                        return

                    # Kullanıcıyı oluştur
                    hashed_password = hash_password(temp_password)
                    cursor.execute("""
                        INSERT INTO users (username, password_hash, email, created_at, first_login, must_change_password)
                        VALUES (?, ?, ?, ?, 1, 1)
                    """, (username, hashed_password, email, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

                    conn.commit()
                    conn.close()

                    try:
                        email_service = EmailService(self.db_path)
                        variables = {
                            'user_name': username,
                            'username': username,
                            'temp_password': temp_password,
                            'login_url': 'https://sustainage.cloud/login',
                            'support_email': 'sdg@digage.tr'
                        }
                        email_service.send_template_email(
                            to_email=email,
                            template_key='new_user_credentials',
                            variables=variables
                        )
                    except Exception as e:
                        logging.error(f"Email gönderme hatası: {e}")

                    messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("user_created_success", "Kullanıcı '{username}' başarıyla oluşturuldu!\nGeçici şifre: {temp_password}").format(username=username, temp_password=temp_password))

                    user_window.destroy()
                    self.load_users()

                except Exception as e:
                    messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("user_create_error", "Kullanıcı oluşturma hatası: ") + str(e))

            create_btn = tk.Button(form_frame, text=self.lm.tr("create_user_btn", "Kullanıcı Oluştur"),
                                 font=('Segoe UI', 12, 'bold'),
                                 fg=self.theme['white'],
                                 bg=self.theme['primary'],
                                 relief='flat', bd=0,
                                 cursor='hand2',
                                 command=create_user,
                                 pady=10)
            create_btn.pack(fill='x')

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("new_user_window_error", "Yeni kullanıcı penceresi hatası: ") + str(e))

    def edit_user(self, event):
        """Kullanıcı düzenle"""
        try:
            selected_item = self.tree.selection()[0]
            user_data = self.tree.item(selected_item, 'values')

            if not user_data:
                return

            user_id = user_data[0]
            username = user_data[1]

            # Kullanıcı profil penceresini aç
            from app.user_profile_gui import show_user_profile
            show_user_profile(self.window, self.db_path, user_id, username)

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("user_edit_error", "Kullanıcı düzenleme hatası: ") + str(e))

def show_admin_user_management(parent, db_path, admin_user_id):
    """Admin kullanıcı yönetimi penceresini göster"""
    AdminUserManagement(parent, db_path, admin_user_id)
