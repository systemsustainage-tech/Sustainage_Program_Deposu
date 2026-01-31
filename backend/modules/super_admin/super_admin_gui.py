import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUSTAINAGE SDG - SÜPER ADMIN MODÜLÜ
Sistem yönetimi, kullanıcı kontrolü, veritabanı yönetimi ve daha fazlası
"""

import os
import shutil
import sqlite3
import subprocess
import sys
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from yonetim.kullanici_yonetimi.models.user_manager import UserManager
from yonetim.security.core.crypto import hash_password
from utils.language_manager import LanguageManager

# Security Tabs Components
from .security_tabs import SecurityTabsMixin
from .security_tabs_complete import SecurityTabsComplete
from config.icons import Icons


class SuperAdminGUI(SecurityTabsMixin, SecurityTabsComplete):
    """Süper Admin Modülü - Tam sistem kontrolü"""

    def __init__(self, parent, user, company_id: int, db_path: str, host_app=None):
        self.parent = parent
        self.user = user
        self.company_id = company_id
        self.db_path = db_path
        self.host_app = host_app
        self.lm = LanguageManager()
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # Yetki kontrolü
        if not self._is_super_admin():
            messagebox.showerror(self.lm.tr('error_access_denied', "Erişim Reddedildi"),
                               self.lm.tr('error_super_admin_only', "Bu modüle sadece Süper Admin erişebilir!"))
            return

        self.setup_ui()

    def _is_super_admin(self) -> bool:
        """Kullanıcının süper admin olup olmadığını kontrol et"""
        if isinstance(self.user, (tuple, list)) and len(self.user) >= 2:
            return self.user[1] == '__super__'
        elif isinstance(self.user, dict):
            return self.user.get('username') == '__super__'
        return False

    def setup_ui(self):
        """Ana arayüzü oluştur"""
        # Parent konfigürasyonu (window veya frame)
        try:
            self.parent.configure(bg='#1a1a2e')
        except Exception as e:
            logging.error(f"Parent configure error: {e}")

        # Ana container - PARENT PADDING KALDIR (beyaz boşluk fix)
        self.main_frame = tk.Frame(self.parent, bg='#1a1a2e')
        self.main_frame.pack(fill='both', expand=True, padx=0, pady=0)

        # Başlık - daha geniş yükseklik
        header_frame = tk.Frame(self.main_frame, bg='#16213e', height=80)
        header_frame.pack(fill='x', side='top')
        header_frame.pack_propagate(False)

        # Butonlar
        # Use a separate frame for buttons to better control layout
        btn_frame = tk.Frame(header_frame, bg='#16213e')
        btn_frame.pack(side='right', padx=15, pady=20, anchor='e')
        
        close_btn = tk.Button(
            btn_frame,
            text=f"✕ {self.lm.tr('btn_close', 'Kapat')}",
            font=('Segoe UI', 10, 'bold'),
            bg='#0f3460',
            fg='#ffffff',
            activebackground='#e94560',
            activeforeground='#ffffff',
            relief='flat',
            bd=0,
            cursor='hand2',
            command=self._close_view
        )
        
        back_btn = tk.Button(
            btn_frame,
            text=f"← {self.lm.tr('btn_back', 'Geri')}",
            font=('Segoe UI', 10, 'bold'),
            bg='#0f3460',
            fg='#ffffff',
            activebackground='#e94560',
            activeforeground='#ffffff',
            relief='flat',
            bd=0,
            cursor='hand2',
            command=self._go_back
        )
        
        # Butonları sağa al
        close_btn.pack(side='right', padx=(10, 0))
        back_btn.pack(side='right', padx=(0, 0))

        title_label = tk.Label(
            header_frame,
            text=f"⚡ {self.lm.tr('super_admin_panel_title', 'SÜPER ADMIN KONTROL PANELİ')}",
            font=('Segoe UI', 18, 'bold'),
            bg='#16213e',
            fg='#e94560'
        )
        title_label.pack(side='left', padx=20, pady=20)

        # İçerik alanı - NO PADDING (beyaz boşluk fix)
        content_frame = tk.Frame(self.main_frame, bg='#1a1a2e')
        content_frame.pack(fill='both', expand=True, padx=0, pady=0)

        # Sol panel - Menü (SCROLLABLE - scrollbar fix)
        left_container = tk.Frame(content_frame, bg='#16213e', width=250, relief='ridge', bd=2)
        left_container.pack(side='left', fill='y', padx=(0, 5))
        left_container.pack_propagate(False)

        # Canvas + Scrollbar için menü
        canvas = tk.Canvas(left_container, bg='#16213e', width=248, highlightthickness=0)
        scrollbar = tk.Scrollbar(left_container, orient="vertical", command=canvas.yview)
        left_frame = tk.Frame(canvas, bg='#16213e')

        left_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=left_frame, anchor="nw", width=230)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)

        menu_title = tk.Label(
            left_frame,
            text=self.lm.tr('admin_menu_title', "YÖNETİM MODÜLLERI"),
            font=('Segoe UI', 12, 'bold'),
            bg='#16213e',
            fg='#ffffff'
        )
        menu_title.pack(pady=15)

        # Menü butonları
        menu_items = [
            (Icons.LOADING, self.lm.tr('admin_menu_refresh', "Uygulamayı Yenile"), self.refresh_application),
            (Icons.DB, self.lm.tr('admin_menu_db', "Veritabanı Yönetimi"), self.show_database_management),
            (Icons.CHART_UP, self.lm.tr('admin_menu_stats', "Sistem İstatistikleri"), self.show_system_stats),
            (Icons.CLIPBOARD, self.lm.tr('admin_menu_audit', "Audit Logları"), self.show_audit_logs),
            (Icons.SETTINGS, self.lm.tr('admin_menu_settings', "Sistem Ayarları"), self.show_system_settings),
            (Icons.WRENCH, self.lm.tr('admin_menu_maintenance', "Bakım & Onarım"), self.show_maintenance),
            (Icons.SAVE, self.lm.tr('admin_menu_backup', "Yedekleme & Geri Yükleme"), self.show_backup),
            (Icons.ROCKET, self.lm.tr('admin_menu_performance', "Performans İzleme"), self.show_performance),
            (Icons.SECURE, self.lm.tr('admin_menu_security', "Güvenlik Ayarları"), self.show_security),

            (Icons.USERS, self.lm.tr('admin_menu_users', "Kullanıcı Yönetimi"), self.show_user_management),
            (Icons.WRENCH, self.lm.tr('admin_menu_admin_users', "Admin Kullanıcı Yönetimi"), self.show_admin_controls),
            (Icons.KEY, self.lm.tr('admin_menu_license', "Lisans Yönetimi"), self.show_license_management),
            ("🛡️", self.lm.tr('admin_menu_ip', "IP Kontrolü"), self.show_ip_control),
            ("⚡", self.lm.tr('admin_menu_rate', "Rate Limiting"), self.show_rate_limiting),
            (Icons.REPORT, self.lm.tr('admin_menu_monitor', "Monitoring Dashboard"), self.show_monitoring_dashboard),
            (Icons.LOCKED_KEY, self.lm.tr('admin_menu_2fa', "2FA Yönetimi"), self.show_twofa_management),
        ]

        self._nav_stack = []
        self._current_view = None

        for icon, text, command in menu_items:
            btn = tk.Button(
                left_frame,
                text=f"{icon}  {text}",
                font=('Segoe UI', 10),
                bg='#0f3460',
                fg='#ffffff',
                activebackground='#e94560',
                activeforeground='#ffffff',
                relief='flat',
                bd=0,
                cursor='hand2',
                anchor='w',
                padx=15,
                pady=12,
                command=lambda fn=command: self._navigate_to(fn)
            )
            btn.pack(fill='x', padx=10, pady=2)

            # Hover efekti
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg='#e94560'))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg='#0f3460'))

        # Sağ panel - İçerik
        self.right_frame = tk.Frame(content_frame, bg='#16213e', relief='ridge', bd=2)
        self.right_frame.pack(side='right', fill='both', expand=True)

        # İlk ekran
        self.show_welcome()
        self._current_view = self.show_welcome

    def _find_main_app(self):
        """MainApp örneğini bulmaya çalış"""
        if self.host_app:
            return self.host_app
        
        parent = self.parent
        while parent:
            if hasattr(parent, 'show_dashboard_classic'):
                return parent
            parent = getattr(parent, 'master', None)
        return None

    def _go_back(self):
        try:
            if self._nav_stack:
                prev = self._nav_stack.pop()
                prev()
                self._current_view = prev
            else:
                # Geri gidecek yer yoksa kapat
                self._close_view()
        except Exception:
            self.show_welcome()
            self._current_view = self.show_welcome

    def _navigate_to(self, view_fn):
        try:
            if self._current_view and self._current_view is not view_fn:
                self._nav_stack.append(self._current_view)
            view_fn()
            self._current_view = view_fn
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def _close_view(self):
        try:
            # First, check if we are in a Toplevel and should close it
            is_toplevel = False
            if self.parent.winfo_class() == 'Toplevel':
                is_toplevel = True

            # If hosted in MainApp, return to dashboard
            main_app = self._find_main_app()
            
            if main_app and hasattr(main_app, 'show_dashboard_classic'):
                main_app.show_dashboard_classic()
                # If we are a separate window, we must destroy ourselves too!
                if is_toplevel:
                    self.parent.destroy()
                return
            
            # If no main app link, just close if Toplevel
            if is_toplevel:
                self.parent.destroy()
            else:
                # Embedded but no host_app? Try finding main app
                top = self.parent.winfo_toplevel()
                # Don't destroy if it's the main root and we are just a frame
                if top == self.parent:
                    top.destroy()
                
        except Exception as e:
            logging.error(f"Kapatma hatası: {e}")
            try:
                self.show_welcome()
                self._current_view = self.show_welcome
                self._nav_stack.clear()
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")

    def refresh_application(self):
        try:
            main_app = self._find_main_app()
            if main_app and hasattr(main_app, 'hot_reload'):
                main_app.hot_reload()
            else:
                try:
                    messagebox.showinfo(self.lm.tr('info_title', "Bilgi"), self.lm.tr('info_refresh_na', "Yenileme ana uygulamada mevcut değil."))
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
        except Exception as e:
            try:
                messagebox.showerror(self.lm.tr('title_error', "Hata"), self.lm.tr('err_refresh_error', "Yenileme hatası: {e}").format(e=e))
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")

    def clear_right_panel(self):
        """Sağ paneli temizle"""
        try:
            for widget in self.right_frame.winfo_children():
                widget.destroy()
        except Exception as e:
            logging.error(f"Clear panel hatası: {e}")

    def show_welcome(self):
        """Hoş geldin ekranı"""
        self.clear_right_panel()

        welcome_frame = tk.Frame(self.right_frame, bg='#16213e')
        welcome_frame.pack(fill='both', expand=True)

        # Hoş geldin mesajı
        welcome_text = tk.Label(
            welcome_frame,
            text=self.lm.tr('admin_welcome_title', "Hoş Geldiniz, Süper Admin!"),
            font=('Segoe UI', 24, 'bold'),
            bg='#16213e',
            fg='#e94560'
        )
        welcome_text.pack(pady=50)

        info_text = tk.Label(
            welcome_frame,
            text=self.lm.tr('admin_welcome_desc', "Bu panel ile tüm sistem kontrolünü elinizde tutabilirsiniz.\n\n"
                 "Sol menüden bir modül seçerek başlayın."),
            font=('Segoe UI', 12),
            bg='#16213e',
            fg='#ffffff',
            justify='center'
        )
        info_text.pack(pady=20)

        # Hızlı istatistikler
        stats_frame = tk.Frame(welcome_frame, bg='#16213e')
        stats_frame.pack(pady=30)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Kullanıcı sayısı
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
            user_count = cursor.fetchone()[0]

            # Firma sayısı
            # company_info tablosundan al (Login ekranı ile tutarlı olması için)
            try:
                cursor.execute("SELECT COUNT(*) FROM company_info WHERE aktif = 1")
            except sqlite3.OperationalError:
                # Fallback to companies table if company_info doesn't exist yet
                cursor.execute("SELECT COUNT(*) FROM companies WHERE is_active = 1")
            
            company_count = cursor.fetchone()[0]

            conn.close()

            self._create_stat_card(stats_frame, f" {self.lm.tr('active_users', 'Aktif Kullanıcılar')}", str(user_count), 0, 0)
            self._create_stat_card(stats_frame, f" {self.lm.tr('active_companies', 'Aktif Firmalar')}", str(company_count), 0, 1)

        except Exception as e:
            logging.error(f"İstatistik yükleme hatası: {e}")

    def _create_stat_card(self, parent, title: str, value: str, row: int, col: int):
        """İstatistik kartı oluştur"""
        card = tk.Frame(parent, bg='#0f3460', relief='raised', bd=2)
        card.grid(row=row, column=col, padx=20, pady=10, ipadx=30, ipady=20)

        title_label = tk.Label(
            card,
            text=title,
            font=('Segoe UI', 10),
            bg='#0f3460',
            fg='#ffffff'
        )
        title_label.pack(pady=(10, 5))

        value_label = tk.Label(
            card,
            text=value,
            font=('Segoe UI', 24, 'bold'),
            bg='#0f3460',
            fg='#e94560'
        )
        value_label.pack(pady=(5, 10))

    def show_user_management(self):
        """Kullanıcı yönetimi ekranı"""
        self.clear_right_panel()

        title = tk.Label(
            self.right_frame,
            text=f" {self.lm.tr('user_management_title', 'Kullanıcı Yönetimi')}",
            font=('Segoe UI', 16, 'bold'),
            bg='#16213e',
            fg='#e94560'
        )
        title.pack(pady=20)

        # Buton çerçevesi
        button_frame = tk.Frame(self.right_frame, bg='#16213e')
        button_frame.pack(pady=10)

        buttons = [
            (f" {self.lm.tr('new_user_btn', 'Yeni Kullanıcı')}", self.add_user),
            (f" {self.lm.tr('edit_user_btn', 'Kullanıcı Düzenle')}", self.edit_user),
            (f" {self.lm.tr('lock_user_btn', 'Kullanıcı Kilitle')}", self.lock_user),
            (f" {self.lm.tr('delete_user_btn', 'Kullanıcı Sil')}", self.delete_user),
        ]

        for text, command in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                font=('Segoe UI', 10),
                bg='#0f3460',
                fg='#ffffff',
                activebackground='#e94560',
                command=command,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2'
            )
            btn.pack(side='left', padx=5)

        # Kullanıcı listesi
        list_frame = tk.Frame(self.right_frame, bg='#16213e')
        list_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Treeview
        columns = ('ID', 'username', 'name', 'surname', 'role', 'active', '2fa', 'last_login')
        headers = {
            'ID': 'ID',
            'username': self.lm.tr('col_username', 'Kullanıcı Adı'),
            'name': self.lm.tr('col_name', 'Ad'),
            'surname': self.lm.tr('col_surname', 'Soyad'),
            'role': self.lm.tr('col_role', 'Rol'),
            'active': self.lm.tr('col_active', 'Aktif'),
            '2fa': self.lm.tr('col_2fa', '2FA'),
            'last_login': self.lm.tr('col_last_login', 'Son Giriş')
        }
        
        self.user_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.user_tree.heading(col, text=headers.get(col, col))
            self.user_tree.column(col, width=120)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar.set)

        self.user_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Kullanıcıları yükle
        self.load_users()

    def show_company_management(self):
        """Şirket yönetimi ekranı"""
        self.clear_right_panel()
        
        # CompanyManagementGUI'yi yükle
        try:
            from yonetim.company.company_management_gui import CompanyManagementGUI
            
            # Container frame
            container = tk.Frame(self.right_frame, bg='#16213e')
            container.pack(fill='both', expand=True)
            
            # CompanyManagementGUI'yi başlat
            # Not: CompanyManagementGUI parent olarak bir pencere bekliyor olabilir,
            # bu yüzden frame içine gömmek için adaptasyon gerekebilir.
            # Ancak mevcut yapıda genellikle Toplevel veya Frame kabul eder.
            # Biz burada frame veriyoruz.
            
            # Parametre düzeltme: CompanyManagementGUI(parent, current_user_id)
            user_id = 1
            if isinstance(self.user, dict):
                user_id = self.user.get('id', 1)
            elif isinstance(self.user, (list, tuple)) and len(self.user) > 0:
                user_id = self.user[0]
                
            app = CompanyManagementGUI(container, current_user_id=user_id)
            # Eğer main_frame attribute'u varsa pack et
            if hasattr(app, 'main_frame'):
                app.main_frame.pack(fill='both', expand=True)
                
        except Exception as e:
            logging.error(f"Şirket yönetimi yüklenemedi: {e}")
            messagebox.showerror(self.lm.tr('error', "Hata"), 
                               f"Şirket yönetimi modülü yüklenemedi: {e}")

    def show_admin_controls(self):
        self.clear_right_panel()
        title = tk.Label(
            self.right_frame,
            text=f" {self.lm.tr('title_admin_management', 'Admin Kullanıcı Yönetimi')}",
            font=('Segoe UI', 16, 'bold'),
            bg='#16213e',
            fg='#e94560'
        )
        title.pack(pady=20)
        content = tk.Frame(self.right_frame, bg='#16213e')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        delete_btn = tk.Button(
            content,
            text=f" {self.lm.tr('btn_delete_admin', 'Admin Kullanıcısını Sil')}",
            font=('Segoe UI', 11, 'bold'),
            bg='#e94560',
            fg='#ffffff',
            activebackground='#c0392b',
            relief='flat',
            cursor='hand2',
            command=self._delete_admin_user
        )
        delete_btn.pack(fill='x', pady=(0, 16))
        form = tk.Frame(content, bg='#16213e')
        form.pack(fill='x')
        tk.Label(form, text=f" {self.lm.tr('lbl_new_admin_username', 'Yeni Admin Kullanıcı Adı:')}", font=('Segoe UI', 10), bg='#16213e', fg='#ffffff').pack(anchor='w')
        self._admin_username_entry = tk.Entry(form, font=('Segoe UI', 10), width=32)
        self._admin_username_entry.pack(fill='x', pady=(0, 10))
        tk.Label(form, text=f" {self.lm.tr('lbl_new_admin_password', 'Yeni Admin Şifresi:')}", font=('Segoe UI', 10), bg='#16213e', fg='#ffffff').pack(anchor='w')
        self._admin_password_entry = tk.Entry(form, font=('Segoe UI', 10), width=32, show='*')
        self._admin_password_entry.pack(fill='x', pady=(0, 10))
        save_btn = tk.Button(
            form,
            text=f" {self.lm.tr('btn_save', 'Kaydet')}",
            font=('Segoe UI', 11, 'bold'),
            bg='#27ae60',
            fg='#ffffff',
            activebackground='#1e8449',
            relief='flat',
            cursor='hand2',
            command=self._save_admin_credentials
        )
        save_btn.pack(pady=(10, 0))

    def _get_admin_user_id(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT u.id FROM users u
                LEFT JOIN user_roles ur ON u.id = ur.user_id AND ur.is_active = 1
                LEFT JOIN roles r ON ur.role_id = r.id AND r.is_active = 1
                WHERE LOWER(r.name) = 'admin' OR LOWER(u.username) = 'admin'
                ORDER BY u.id LIMIT 1
                """
            )
            row = cursor.fetchone()
            conn.close()
            return int(row[0]) if row and row[0] is not None else None
        except Exception:
            return None

    def _ensure_admin_role(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM roles WHERE LOWER(name) = 'admin' AND is_active = 1")
            r = cursor.fetchone()
            if r and r[0]:
                conn.close()
                return int(r[0])
            conn.close()
            um = UserManager(self.db_path)
            rid = um.create_role({
                'name': 'admin',
                'display_name': 'Admin',
                'description': 'Yönetim yetkileri',
                'is_system_role': True,
                'is_active': True,
            }, None)
            return int(rid if rid is not None else -1)
        except Exception:
            return None

    def _delete_admin_user(self):
        try:
            admin_id = self._get_admin_user_id()
            if not admin_id:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('admin_not_found', "Admin kullanıcısı bulunamadı."))
                return
            if not messagebox.askyesno(self.lm.tr('confirmation', "Onay"), self.lm.tr('confirm_delete_admin', "Admin kullanıcısını kalıcı olarak silmek istiyor musunuz? Bu işlem geri alınamaz.")):
                return
            um = UserManager(self.db_path)
            ok = um.permanent_delete_user(admin_id, None)
            if ok:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('admin_deleted', "Admin kullanıcısı silindi."))
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('admin_delete_fail', "Admin kullanıcısı silinemedi."))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('process_error', "İşlem hatası: {e}").format(e=e))

    def _save_admin_credentials(self):
        try:
            new_username = str(self._admin_username_entry.get()).strip()
            new_password = str(self._admin_password_entry.get()).strip()
            um = UserManager(self.db_path)
            admin_id = self._get_admin_user_id()
            if admin_id:
                if not new_username and not new_password:
                    messagebox.showwarning(self.lm.tr('title_warning', "Uyarı"), self.lm.tr('msg_fill_one_field', "En az bir alanı doldurun."))
                    return
                if new_username:
                    um.update_user(admin_id, {'username': new_username}, None)
                uname = new_username
                if not uname:
                    u = um.get_user_by_id(admin_id)
                    uname = str((u or {}).get('username') or '')
                if new_password and uname:
                    um.update_user_password(uname, new_password, None)
                messagebox.showinfo(self.lm.tr('title_success', "Başarılı"), self.lm.tr('msg_admin_updated', "Admin bilgileri güncellendi."))
                return
            if not new_username or not new_password:
                messagebox.showwarning(self.lm.tr('title_warning', "Uyarı"), self.lm.tr('msg_enter_admin_creds', "Admin oluşturmak için kullanıcı adı ve şifre girin."))
                return
            rid = self._ensure_admin_role()
            user_data = {
                'username': new_username,
                'email': 'admin@local',
                'password': new_password,
                'first_name': 'Admin',
                'last_name': '',
                'is_active': True,
                'is_verified': True,
                'role_ids': [rid] if rid else []
            }
            new_id = um.create_user(user_data, None)
            if int(new_id if new_id is not None else -1) > 0:
                messagebox.showinfo(self.lm.tr('title_success', "Başarılı"), self.lm.tr('msg_admin_created', "Admin kullanıcısı oluşturuldu."))
            else:
                messagebox.showerror(self.lm.tr('title_error', "Hata"), self.lm.tr('msg_admin_create_error', "Admin kullanıcısı oluşturulamadı."))
        except Exception as e:
            messagebox.showerror(self.lm.tr('title_error', "Hata"), self.lm.tr('err_save_error', "Kaydetme hatası: {e}").format(e=e))

    def load_users(self):
        """Kullanıcıları yükle"""
        try:
            for item in self.user_tree.get_children():
                self.user_tree.delete(item)
            um = UserManager(self.db_path)
            users = um.get_users()
            totp_map = {}
            try:
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                try:
                    cur.execute("PRAGMA table_info(users)")
                    cols = [c[1] for c in cur.fetchall()]
                    if 'totp_enabled' not in cols:
                        cur.execute("ALTER TABLE users ADD COLUMN totp_enabled INTEGER DEFAULT 0")
                        conn.commit()
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
                cur.execute("SELECT id, COALESCE(totp_enabled,0) FROM users")
                for uid, te in cur.fetchall():
                    totp_map[uid] = int(te or 0)
                conn.close()
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
            for u in users:
                uid = u.get('id')
                username = u.get('username') or ''
                first_name = u.get('first_name') or ''
                last_name = u.get('last_name') or ''
                roles = u.get('roles') or ''
                is_active = bool(u.get('is_active'))
                last_login = u.get('last_login') or self.lm.tr('never', 'Hiç')
                totp_enabled = totp_map.get(uid, 0)
                self.user_tree.insert('', 'end', values=(
                    uid,
                    username,
                    first_name,
                    last_name,
                    roles if roles else 'user',
                    self.lm.tr('yes', 'Evet') if is_active else self.lm.tr('no', 'Hayır'),
                    self.lm.tr('active', 'Aktif') if int(totp_enabled) == 1 else self.lm.tr('passive', 'Pasif'),
                    last_login
                ))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('users_load_error', "Kullanıcılar yüklenemedi: {e}").format(e=e))

    def add_user(self):
        """Yeni kullanıcı ekle"""
        self.show_add_user_dialog()

    def edit_user(self):
        """Kullanıcı düzenle"""
        try:
            selected = self.user_tree.selection()
            if not selected:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_user', "Lütfen bir kullanıcı seçin!"))
                return
            item = self.user_tree.item(selected[0])
            user_data = item['values']
            if not isinstance(user_data, (list, tuple)) or len(user_data) < 8:
                self.load_users()
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('invalid_user_data', "Seçili kullanıcı verisi beklenen biçimde değil. Liste yenilendi."))
                return
            self.show_edit_user_dialog(user_data)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('edit_user_error', "Kullanıcı düzenleme açılamadı: {e}").format(e=e))

    def lock_user(self):
        """Kullanıcı kilitle/aç"""
        try:
            selected = self.user_tree.selection()
            if not selected:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_user', "Lütfen bir kullanıcı seçin!"))
                return
            item = self.user_tree.item(selected[0])
            user_data = item['values']
            if not isinstance(user_data, (list, tuple)) or len(user_data) < 8:
                self.load_users()
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('invalid_user_data', "Seçili kullanıcı verisi beklenen biçimde değil. Liste yenilendi."))
                return
            user_id, username, first_name, last_name, role, is_active, twofa_state, last_login = user_data
            if username == '__super__':
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('cannot_lock_super_admin', "Süper admin kullanıcısı kilitlenemez!"))
                return
            
            is_currently_active = (is_active == self.lm.tr('yes', "Evet"))
            
            if is_currently_active:
                confirm_msg = self.lm.tr('confirm_lock_user', "{username} kullanıcısını kilitlemek istediğinizden emin misiniz?").format(username=username)
                success_msg = self.lm.tr('user_locked', "Kullanıcı kilitlendi!")
                error_prefix = self.lm.tr('user_lock_error', "Kullanıcı kilitleme hatası")
                new_status = 0
            else:
                confirm_msg = self.lm.tr('confirm_unlock_user', "{username} kullanıcısının kilidini açmak istediğinizden emin misiniz?").format(username=username)
                success_msg = self.lm.tr('user_unlocked', "Kullanıcı kilidi açıldı!")
                error_prefix = self.lm.tr('user_unlock_error', "Kullanıcı kilidi açma hatası")
                new_status = 1

            if messagebox.askyesno(self.lm.tr('confirmation', "Onay"), confirm_msg):
                try:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET is_active = ? WHERE id = ?", (new_status, int(user_id)))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo(self.lm.tr('success', "Başarılı"), success_msg)
                    self.load_users()
                except Exception as ex:
                    messagebox.showerror(self.lm.tr('error', "Hata"), f"{error_prefix}: {ex}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('lock_dialog_error', "Kullanıcı kilitleme açılamadı: {e}").format(e=e))

    def delete_user(self):
        """Kullanıcı sil"""
        try:
            selected = self.user_tree.selection()
            if not selected:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_user', "Lütfen bir kullanıcı seçin!"))
                return
            item = self.user_tree.item(selected[0])
            user_data = item['values']
            if not isinstance(user_data, (list, tuple)) or len(user_data) < 8:
                self.load_users()
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('invalid_user_data', "Seçili kullanıcı verisi beklenen biçimde değil. Liste yenilendi."))
                return
            user_id, username, first_name, last_name, role, is_active, twofa_state, last_login = user_data
            if username == '__super__':
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('cannot_delete_super_admin', "Süper admin kullanıcısı silinemez!"))
                return
            if messagebox.askyesno(self.lm.tr('confirmation', "Onay"), self.lm.tr('confirm_delete_user', "{username} kullanıcısını silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz!").format(username=username)):
                try:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM users WHERE id = ?", (int(user_id),))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('user_deleted', "Kullanıcı silindi!"))
                    self.load_users()
                except Exception as ex:
                    messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('user_delete_error', "Kullanıcı silme hatası: {ex}").format(ex=ex))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('user_delete_error', "Kullanıcı silme hatası: {e}").format(e=e))

    def show_add_user_dialog(self):
        """Yeni kullanıcı ekleme dialogu"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('add_new_user', "Yeni Kullanıcı Ekle"))
        dialog.geometry("400x500")
        dialog.resizable(False, False)
        dialog.grab_set()

        # Başlık
        title_label = tk.Label(dialog, text=self.lm.tr('add_new_user', "Yeni Kullanıcı Ekle"), font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=20)

        # Form çerçevesi
        form_frame = tk.Frame(dialog)
        form_frame.pack(padx=30, pady=20, fill='both', expand=True)

        # Form alanları
        fields = [
            (self.lm.tr('lbl_username', "Kullanıcı Adı:"), "username"),
            (self.lm.tr('lbl_name', "Ad:"), "first_name"),
            (self.lm.tr('lbl_surname', "Soyad:"), "last_name"),
            (self.lm.tr('lbl_email', "E-posta:"), "email"),
            (self.lm.tr('lbl_password', "Şifre:"), "password"),
            (self.lm.tr('lbl_role', "Rol:"), "role")
        ]

        self.form_vars = {}
        self.form_entries = {}

        for i, (label_text, field_name) in enumerate(fields):
            # Label
            label = tk.Label(form_frame, text=label_text, font=('Segoe UI', 10))
            label.grid(row=i, column=0, sticky='w', pady=5)

            # Entry
            if field_name == "password":
                entry = tk.Entry(form_frame, show="*", font=('Segoe UI', 10), width=30)
            elif field_name == "role":
                entry = ttk.Combobox(form_frame, values=[
                    f"user - {self.lm.tr('role_user', 'Kullanıcı')}", 
                    f"admin - {self.lm.tr('role_admin', 'Yönetici')}", 
                    f"manager - {self.lm.tr('role_manager', 'Müdür')}"
                ], font=('Segoe UI', 10), width=27)
                entry.set(f"user - {self.lm.tr('role_user', 'Kullanıcı')}")
            else:
                entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=30)

            entry.grid(row=i, column=1, sticky='ew', pady=5, padx=(10, 0))
            self.form_entries[field_name] = entry

        # Butonlar
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)

        save_btn = tk.Button(button_frame, text=self.lm.tr('btn_save', "Kaydet"), command=lambda: self.save_new_user(dialog),
                           bg='#28a745', fg='white', font=('Segoe UI', 10), padx=20)
        save_btn.pack(side='left', padx=5)

        cancel_btn = tk.Button(button_frame, text=self.lm.tr('btn_cancel', "İptal"), command=dialog.destroy,
                             bg='#dc3545', fg='white', font=('Segoe UI', 10), padx=20)
        cancel_btn.pack(side='left', padx=5)

    def show_edit_user_dialog(self, user_data):
        """Kullanıcı düzenleme dialogu"""
        user_id, username, first_name, last_name, role, is_active, twofa_state, last_login = user_data

        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('edit_user_title', "Kullanıcı Düzenle: {username}").format(username=username))
        dialog.geometry("400x500")
        dialog.resizable(False, False)
        dialog.grab_set()

        # Başlık
        title_label = tk.Label(dialog, text=self.lm.tr('edit_user_title', "Kullanıcı Düzenle: {username}").format(username=username), font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=20)

        # Form çerçevesi
        form_frame = tk.Frame(dialog)
        form_frame.pack(padx=30, pady=20, fill='both', expand=True)

        # Form alanları
        fields = [
            (self.lm.tr('lbl_username', "Kullanıcı Adı:"), "username", username),
            (self.lm.tr('lbl_name', "Ad:"), "first_name", first_name),
            (self.lm.tr('lbl_surname', "Soyad:"), "last_name", last_name),
            (self.lm.tr('lbl_email', "E-posta:"), "email", ""),
            (self.lm.tr('lbl_new_password', "Yeni Şifre:"), "password", ""),
            (self.lm.tr('lbl_role', "Rol:"), "role", role),
            (self.lm.tr('lbl_active', "Aktif:"), "is_active", is_active)
        ]

        self.edit_entries = {}

        for i, (label_text, field_name, current_value) in enumerate(fields):
            # Label
            label = tk.Label(form_frame, text=label_text, font=('Segoe UI', 10))
            label.grid(row=i, column=0, sticky='w', pady=5)

            # Entry
            if field_name == "password":
                entry = tk.Entry(form_frame, show="*", font=('Segoe UI', 10), width=30)
                entry.insert(0, self.lm.tr('new_password_placeholder', "Yeni şifre girin (boş bırakırsanız değişmez)"))
            elif field_name == "role":
                entry = ttk.Combobox(form_frame, values=[
                    f"user - {self.lm.tr('role_user', 'Kullanıcı')}",
                    f"admin - {self.lm.tr('role_admin', 'Yönetici')}",
                    f"manager - {self.lm.tr('role_manager', 'Müdür')}"
                ], font=('Segoe UI', 10), width=27)
                
                # Mevcut değeri eşleştir
                current_val_map = {
                    "user": f"user - {self.lm.tr('role_user', 'Kullanıcı')}",
                    "admin": f"admin - {self.lm.tr('role_admin', 'Yönetici')}",
                    "manager": f"manager - {self.lm.tr('role_manager', 'Müdür')}"
                }
                entry.set(current_val_map.get(current_value, current_value))
            elif field_name == "is_active":
                entry = ttk.Combobox(form_frame, values=[self.lm.tr('yes', "Evet"), self.lm.tr('no', "Hayır")], font=('Segoe UI', 10), width=27)
                entry.set(current_value)
            else:
                entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=30)
                entry.insert(0, current_value)

            entry.grid(row=i, column=1, sticky='ew', pady=5, padx=(10, 0))
            self.edit_entries[field_name] = entry

        # Butonlar
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)

        save_btn = tk.Button(button_frame, text=self.lm.tr('btn_update', "Güncelle"), command=lambda: self.update_user(user_id, dialog),
                           bg='#28a745', fg='white', font=('Segoe UI', 10), padx=20)
        save_btn.pack(side='left', padx=5)

        cancel_btn = tk.Button(button_frame, text=self.lm.tr('btn_cancel', "İptal"), command=dialog.destroy,
                             bg='#dc3545', fg='white', font=('Segoe UI', 10), padx=20)
        cancel_btn.pack(side='left', padx=5)

    def save_new_user(self, dialog):
        """Yeni kullanıcıyı kaydet"""
        try:
            # Form verilerini al
            username = self.form_entries['username'].get().strip()
            first_name = self.form_entries['first_name'].get().strip()
            last_name = self.form_entries['last_name'].get().strip()
            email = self.form_entries['email'].get().strip()
            password = self.form_entries['password'].get().strip()
            role = self.form_entries['role'].get().split(' - ')[0]

            # Validasyon
            if not username:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('username_required', "Kullanıcı adı gereklidir!"))
                return

            if not password:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('password_required', "Şifre gereklidir!"))
                return

            # Şifreyi hash'le (Argon2)
            password_hash = hash_password(password)

            # Veritabanına ekle
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO users (username, first_name, last_name, email, password_hash, role, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
            """, (username, first_name, last_name, email, password_hash, role, datetime.now().isoformat()))

            conn.commit()
            conn.close()

            messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('user_added_success', "Kullanıcı başarıyla eklendi!"))
            dialog.destroy()
            self.load_users()

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('user_add_error', "Kullanıcı ekleme hatası: {e}").format(e=e))

    def update_user(self, user_id, dialog):
        """Kullanıcıyı güncelle"""
        try:
            # Form verilerini al
            username = self.edit_entries['username'].get().strip()
            first_name = self.edit_entries['first_name'].get().strip()
            last_name = self.edit_entries['last_name'].get().strip()
            email = self.edit_entries['email'].get().strip()
            password = self.edit_entries['password'].get().strip()
            role = self.edit_entries['role'].get().split(' - ')[0]
            is_active = 1 if self.edit_entries['is_active'].get() == self.lm.tr('yes', "Evet") else 0

            # Validasyon
            if not username:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('username_required', "Kullanıcı adı gereklidir!"))
                return

            # Veritabanını güncelle
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if password and password != self.lm.tr('new_password_placeholder', "Yeni şifre girin (boş bırakırsanız değişmez)"):
                # Şifre değiştir (Argon2)
                password_hash = hash_password(password)
                cursor.execute("""
                    UPDATE users SET username=?, first_name=?, last_name=?, email=?, 
                                   password_hash=?, role=?, is_active=?, updated_at=?
                    WHERE id=?
                """, (username, first_name, last_name, email, password_hash, role, is_active,
                      datetime.now().isoformat(), user_id))
            else:
                # Şifre değiştirme
                cursor.execute("""
                    UPDATE users SET username=?, first_name=?, last_name=?, email=?, 
                                   role=?, is_active=?, updated_at=?
                    WHERE id=?
                """, (username, first_name, last_name, email, role, is_active,
                      datetime.now().isoformat(), user_id))

            conn.commit()
            conn.close()

            messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('user_updated_success', "Kullanıcı başarıyla güncellendi!"))
            dialog.destroy()
            self.load_users()

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('user_update_error', "Kullanıcı güncelleme hatası: {e}").format(e=e))

    def show_database_management(self):
        """Veritabanı yönetimi"""
        self.clear_right_panel()

        title = tk.Label(
            self.right_frame,
            text=self.lm.tr('db_management', " Veritabanı Yönetimi"),
            font=('Segoe UI', 16, 'bold'),
            bg='#16213e',
            fg='#e94560'
        )
        title.pack(pady=20)

        # Buton çerçevesi
        button_frame = tk.Frame(self.right_frame, bg='#16213e')
        button_frame.pack(pady=10)

        buttons = [
            (self.lm.tr('btn_db_stats', " Veritabanı İstatistikleri"), self.show_db_stats),
            (self.lm.tr('btn_table_structure', " Tablo Yapısı"), self.show_table_structure),
            (self.lm.tr('btn_clean_db', " Veritabanı Temizle"), self.clean_database),
            (self.lm.tr('btn_sql_query', " SQL Sorgu"), self.show_sql_query),
        ]

        for text, command in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                font=('Segoe UI', 10),
                bg='#0f3460',
                fg='#ffffff',
                activebackground='#e94560',
                command=command,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2'
            )
            btn.pack(side='left', padx=5)

        # Veritabanı bilgileri
        info_frame = tk.Frame(self.right_frame, bg='#16213e')
        info_frame.pack(fill='both', expand=True, padx=20, pady=20)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Tablo sayısı
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            # Veritabanı boyutu
            db_size = os.path.getsize(self.db_path) / (1024 * 1024)  # MB

            info_text = self.lm.tr('db_info_header', "Veritabanı Bilgileri:") + "\n"
            info_text += f"• {self.lm.tr('db_path', 'Dosya Yolu')}: {self.db_path}\n"
            info_text += f"• {self.lm.tr('table_count', 'Tablo Sayısı')}: {len(tables)}\n"
            info_text += f"• {self.lm.tr('file_size', 'Dosya Boyutu')}: {db_size:.2f} MB\n"
            info_text += f"• {self.lm.tr('last_update', 'Son Güncelleme')}: {datetime.fromtimestamp(os.path.getmtime(self.db_path)).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            info_text += self.lm.tr('current_tables', "Mevcut Tablolar:") + "\n"
            
            for table in tables:
                info_text += f"• {table[0]}\n"

            info_label = tk.Label(
                info_frame,
                text=info_text,
                font=('Segoe UI', 10),
                bg='#16213e',
                fg='#ffffff',
                justify='left'
            )
            info_label.pack(anchor='w')

            conn.close()

        except Exception as e:
            error_label = tk.Label(
                info_frame,
                text=self.lm.tr('db_info_error', "Veritabanı bilgileri alınamadı: {e}").format(e=e),
                font=('Segoe UI', 10),
                bg='#16213e',
                fg='#e94560'
            )
            error_label.pack(anchor='w')

    def show_db_stats(self):
        """Veritabanı istatistikleri"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('db_stats_title', "Veritabanı İstatistikleri"))
        dialog.geometry("600x400")
        dialog.grab_set()

        # Başlık
        title_label = tk.Label(dialog, text=self.lm.tr('db_stats_title', " Veritabanı İstatistikleri"), font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=20)

        # İçerik
        content_frame = tk.Frame(dialog)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            stats_text = self.lm.tr('db_stats_header', "VERİTABANI İSTATİSTİKLERİ") + "\n" + "="*50 + "\n\n"

            # Tablo bilgileri
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                stats_text += f" {table_name}: {count} {self.lm.tr('record_count_suffix', 'kayıt')}\n"

            conn.close()

            text_widget = tk.Text(content_frame, font=('Consolas', 10), wrap='word')
            text_widget.pack(fill='both', expand=True)
            text_widget.insert('1.0', stats_text)
            text_widget.config(state='disabled')

        except Exception as e:
            error_label = tk.Label(content_frame, text=self.lm.tr('error_prefix', "Hata: {e}").format(e=e), fg='red')
            error_label.pack()

    def show_table_structure(self):
        """Tablo yapısını göster"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('table_structure_title', "Tablo Yapısı"))
        dialog.geometry("800x600")
        dialog.grab_set()

        # Başlık
        title_label = tk.Label(dialog, text=self.lm.tr('table_structure_title', " Tablo Yapısı"), font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=20)

        # Tablo seçimi
        table_frame = tk.Frame(dialog)
        table_frame.pack(pady=10)

        tk.Label(table_frame, text=self.lm.tr('select_table', "Tablo Seçin:"), font=('Segoe UI', 10)).pack(side='left')

        table_combo = ttk.Combobox(table_frame, width=30)
        table_combo.pack(side='left', padx=10)

        # İçerik
        content_frame = tk.Frame(dialog)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        text_widget = tk.Text(content_frame, font=('Consolas', 9), wrap='word')
        text_widget.pack(fill='both', expand=True)

        def load_table_info():
            table_name = table_combo.get()
            if not table_name:
                return

            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Tablo yapısı
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()

                info_text = f"{self.lm.tr('table_prefix', 'TABLO')}: {table_name}\n" + "="*50 + "\n\n"
                info_text += f"{self.lm.tr('columns_header', 'SÜTUNLAR')}:\n" + "-"*30 + "\n"

                for col in columns:
                    col_id, name, col_type, not_null, default, pk = col
                    info_text += f"• {name} ({col_type})"
                    if pk:
                        info_text += f" [{self.lm.tr('primary_key', 'BİRİNCİL ANAHTAR')}]"
                    if not_null:
                        info_text += f" [{self.lm.tr('not_null', 'BOŞ OLAMAZ')}]"
                    info_text += "\n"

                # Örnek veriler
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cursor.fetchall()

                if rows:
                    info_text += f"\n{self.lm.tr('sample_data_header', 'ÖRNEK VERİLER (İlk 5 kayıt)')}:\n" + "-"*30 + "\n"
                    for row in rows:
                        info_text += f"{row}\n"

                conn.close()

                text_widget.delete('1.0', tk.END)
                text_widget.insert('1.0', info_text)

            except Exception as e:
                text_widget.delete('1.0', tk.END)
                text_widget.insert('1.0', self.lm.tr('error_prefix', "Hata: {e}").format(e=e))

        # Tabloları yükle
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in cursor.fetchall()]
            table_combo['values'] = tables
            conn.close()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        table_combo.bind('<<ComboboxSelected>>', lambda e: load_table_info())

        # İlk tabloyu yükle
        if tables:
            table_combo.set(tables[0])
            load_table_info()

    def clean_database(self):
        """Veritabanını temizle"""
        if messagebox.askyesno(self.lm.tr('confirmation', "Onay"), self.lm.tr('confirm_clean_db', "Veritabanını temizlemek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz!")):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Tüm tabloları temizle (users hariç)
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()

                for table in tables:
                    table_name = table[0]
                    if table_name != 'users':  # Kullanıcıları koru
                        cursor.execute(f"DELETE FROM {table_name}")

                conn.commit()
                conn.close()

                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('db_cleaned', "Veritabanı temizlendi!"))

            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('clean_error', "Temizleme hatası: {e}").format(e=e))

    def show_sql_query(self):
        """SQL sorgu penceresi"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('sql_query_title', "SQL Sorgu"))
        dialog.geometry("800x600")
        dialog.grab_set()

        # Başlık
        title_label = tk.Label(dialog, text=self.lm.tr('sql_query_title', " SQL Sorgu"), font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=10)

        # SQL girişi
        sql_frame = tk.Frame(dialog)
        sql_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(sql_frame, text=self.lm.tr('sql_query_label', "SQL Sorgusu:"), font=('Segoe UI', 10)).pack(anchor='w')

        sql_entry = tk.Text(sql_frame, height=3, font=('Consolas', 10))
        sql_entry.pack(fill='x', pady=5)

        # Butonlar
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)

        def execute_query():
            sql = sql_entry.get('1.0', tk.END).strip()
            if not sql:
                return

            # Yalnızca tek satırlı SELECT sorgularına izin ver
            upper = sql.upper()
            if ';' in sql or not upper.startswith('SELECT'):
                result_text.delete('1.0', tk.END)
                result_text.insert(tk.END, self.lm.tr('sql_select_only', "Yalnızca tek satırlı SELECT sorgularına izin verilir"))
                return

            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(sql)
                results = cursor.fetchall()

                # Sonuçları göster
                result_text.delete('1.0', tk.END)
                for row in results:
                    result_text.insert(tk.END, f"{row}\n")

                conn.close()

            except Exception as e:
                result_text.delete('1.0', tk.END)
                result_text.insert(tk.END, self.lm.tr('error_prefix', "Hata: {e}").format(e=e))


        execute_btn = tk.Button(button_frame, text=self.lm.tr('execute_btn', "Çalıştır"), command=execute_query,
                              bg='#28a745', fg='white', font=('Segoe UI', 10), padx=20)
        execute_btn.pack(side='left', padx=5)

        clear_btn = tk.Button(button_frame, text=self.lm.tr('clear_btn', "Temizle"), command=lambda: sql_entry.delete('1.0', tk.END),
                            bg='#dc3545', fg='white', font=('Segoe UI', 10), padx=20)
        clear_btn.pack(side='left', padx=5)

        # Sonuç alanı
        result_frame = tk.Frame(dialog)
        result_frame.pack(fill='both', expand=True, padx=20, pady=10)

        tk.Label(result_frame, text=self.lm.tr('results_label', "Sonuçlar:"), font=('Segoe UI', 10)).pack(anchor='w')

        result_text = tk.Text(result_frame, font=('Consolas', 9), wrap='word')
        result_text.pack(fill='both', expand=True)

    def show_system_stats(self):
        """Sistem istatistikleri"""
        self.clear_right_panel()

        title = tk.Label(
            self.right_frame,
            text=f" {self.lm.tr('system_stats_title', 'Sistem İstatistikleri')}",
            font=('Segoe UI', 16, 'bold'),
            bg='#16213e',
            fg='#e94560'
        )
        title.pack(pady=20)

        # İstatistikler
        stats_frame = tk.Frame(self.right_frame, bg='#16213e')
        stats_frame.pack(pady=20)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Tablolar
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            table_count = len(tables)

            # Kullanıcılar
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]

            # Firmalar
            try:
                cursor.execute("SELECT COUNT(*) FROM company_info")
                company_count = cursor.fetchone()[0]
            except Exception:
                company_count = 0

            conn.close()

            stats = [
                (f" {self.lm.tr('table_count', 'Tablo Sayısı')}", str(table_count)),
                (f" {self.lm.tr('total_users', 'Toplam Kullanıcı')}", str(user_count)),
                (f" {self.lm.tr('total_companies', 'Toplam Firma')}", str(company_count)),
            ]

            for i, (label, value) in enumerate(stats):
                self._create_stat_card(stats_frame, label, value, i // 3, i % 3)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('stats_load_error', "İstatistikler yüklenemedi: {e}").format(e=e))

    def show_role_management(self):
        """Rol ve izin yönetimi"""
        self.clear_right_panel()

        title = tk.Label(
            self.right_frame,
            text=f" {self.lm.tr('role_permission_management', 'Rol & İzin Yönetimi')}",
            font=('Segoe UI', 16, 'bold'),
            bg='#16213e',
            fg='#e94560'
        )
        title.pack(pady=20)

        # Buton çerçevesi
        button_frame = tk.Frame(self.right_frame, bg='#16213e')
        button_frame.pack(pady=10)

        buttons = [
            (f" {self.lm.tr('new_role', 'Yeni Rol')}", self.add_role),
            (f" {self.lm.tr('edit_role', 'Rol Düzenle')}", self.edit_role),
            (f" {self.lm.tr('delete_role', 'Rol Sil')}", self.delete_role),
            (f" {self.lm.tr('permission_management', 'İzin Yönetimi')}", self.manage_permissions),
        ]

        for text, command in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                font=('Segoe UI', 10),
                bg='#0f3460',
                fg='#ffffff',
                activebackground='#e94560',
                command=command,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2'
            )
            btn.pack(side='left', padx=5)

        # Rol listesi
        list_frame = tk.Frame(self.right_frame, bg='#16213e')
        list_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Treeview
        columns = ('ID', 'role_name', 'description', 'user_count')
        self.role_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        headers = {
            'ID': 'ID',
            'role_name': self.lm.tr('col_role_name', 'Rol Adı'),
            'description': self.lm.tr('col_description', 'Açıklama'),
            'user_count': self.lm.tr('col_user_count', 'Kullanıcı Sayısı')
        }

        for col in columns:
            self.role_tree.heading(col, text=headers.get(col, col))
            self.role_tree.column(col, width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.role_tree.yview)
        self.role_tree.configure(yscrollcommand=scrollbar.set)

        self.role_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Rolleri yükle
        self.load_roles()

    def load_roles(self):
        """Rolleri yükle"""
        try:
            # Mevcut verileri temizle
            for item in self.role_tree.get_children():
                self.role_tree.delete(item)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Rolleri al
            cursor.execute("""
                SELECT r.id, r.name, r.description, COUNT(ur.user_id) as user_count
                FROM roles r
                LEFT JOIN user_roles ur ON r.id = ur.role_id
                GROUP BY r.id, r.name, r.description
                ORDER BY r.id
            """)

            roles = cursor.fetchall()
            conn.close()

            for role in roles:
                role_id, name, description, user_count = role
                self.role_tree.insert('', 'end', values=(
                    role_id,
                    name or 'Bilinmiyor',
                    description or 'Açıklama yok',
                    user_count
                ))

        except Exception:
            # Roller tablosu yoksa oluştur
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS roles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(50) NOT NULL UNIQUE,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Varsayılan roller
                default_roles = [
                    ('admin', 'Sistem Yöneticisi'),
                    ('manager', 'Yönetici'),
                    ('user', 'Kullanıcı'),
                    ('viewer', 'Görüntüleyici')
                ]

                for role_name, description in default_roles:
                    cursor.execute("INSERT OR IGNORE INTO roles (name, description) VALUES (?, ?)",
                                 (role_name, description))

                conn.commit()
                conn.close()

                # Tekrar yükle
                self.load_roles()

            except Exception as e2:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('roles_load_error', "Roller yüklenemedi: {e2}").format(e2=e2))

    def add_role(self):
        """Yeni rol ekle"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('add_role_title', "Yeni Rol Ekle"))
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.grab_set()

        # Başlık
        title_label = tk.Label(dialog, text=self.lm.tr('add_role_title', "Yeni Rol Ekle"), font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=20)

        # Form çerçevesi
        form_frame = tk.Frame(dialog)
        form_frame.pack(padx=30, pady=20, fill='both', expand=True)

        # Form alanları
        tk.Label(form_frame, text=self.lm.tr('role_name', "Rol Adı:"), font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', pady=5)
        name_entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=30)
        name_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))

        tk.Label(form_frame, text=self.lm.tr('description', "Açıklama:"), font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', pady=5)
        desc_entry = tk.Text(form_frame, height=4, font=('Segoe UI', 10), width=30)
        desc_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))

        # Butonlar
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)

        def save_role():
            name = name_entry.get().strip()
            description = desc_entry.get('1.0', tk.END).strip()

            if not name:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('role_name_required', "Rol adı gereklidir!"))
                return

            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("INSERT INTO roles (name, description) VALUES (?, ?)", (name, description))
                conn.commit()
                conn.close()

                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('role_added', "Rol başarıyla eklendi!"))
                dialog.destroy()
                self.load_roles()

            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('role_add_error', "Rol ekleme hatası: {e}").format(e=e))

        save_btn = tk.Button(button_frame, text=self.lm.tr('btn_save', "Kaydet"), command=save_role,
                           bg='#28a745', fg='white', font=('Segoe UI', 10), padx=20)
        save_btn.pack(side='left', padx=5)

        cancel_btn = tk.Button(button_frame, text=self.lm.tr('btn_cancel', "İptal"), command=dialog.destroy,
                             bg='#dc3545', fg='white', font=('Segoe UI', 10), padx=20)
        cancel_btn.pack(side='left', padx=5)

    def edit_role(self):
        """Rol düzenle"""
        selected = self.role_tree.selection()
        if not selected:
            messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_role', "Lütfen bir rol seçin!"))
            return

        item = self.role_tree.item(selected[0])
        role_data = item['values']
        role_id, name, description, user_count = role_data

        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('edit_role_title', "Rol Düzenle: {name}").format(name=name))
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.grab_set()

        # Başlık
        title_label = tk.Label(dialog, text=self.lm.tr('edit_role_title', "Rol Düzenle: {name}").format(name=name), font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=20)

        # Form çerçevesi
        form_frame = tk.Frame(dialog)
        form_frame.pack(padx=30, pady=20, fill='both', expand=True)

        # Form alanları
        tk.Label(form_frame, text=self.lm.tr('role_name', "Rol Adı:"), font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', pady=5)
        name_entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=30)
        name_entry.insert(0, name)
        name_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))

        tk.Label(form_frame, text=self.lm.tr('description', "Açıklama:"), font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', pady=5)
        desc_entry = tk.Text(form_frame, height=4, font=('Segoe UI', 10), width=30)
        desc_entry.insert('1.0', description)
        desc_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))

        # Butonlar
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)

        def update_role():
            new_name = name_entry.get().strip()
            new_description = desc_entry.get('1.0', tk.END).strip()

            if not new_name:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('role_name_required', "Rol adı gereklidir!"))
                return

            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("UPDATE roles SET name=?, description=? WHERE id=?",
                             (new_name, new_description, role_id))
                conn.commit()
                conn.close()

                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('role_updated', "Rol başarıyla güncellendi!"))
                dialog.destroy()
                self.load_roles()

            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('role_update_error', "Rol güncelleme hatası: {e}").format(e=e))

        save_btn = tk.Button(button_frame, text=self.lm.tr('btn_update', "Güncelle"), command=update_role,
                           bg='#28a745', fg='white', font=('Segoe UI', 10), padx=20)
        save_btn.pack(side='left', padx=5)

        cancel_btn = tk.Button(button_frame, text=self.lm.tr('btn_cancel', "İptal"), command=dialog.destroy,
                             bg='#dc3545', fg='white', font=('Segoe UI', 10), padx=20)
        cancel_btn.pack(side='left', padx=5)

    def delete_role(self):
        """Rol sil"""
        selected = self.role_tree.selection()
        if not selected:
            messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_role', "Lütfen bir rol seçin!"))
            return

        item = self.role_tree.item(selected[0])
        role_data = item['values']
        role_id, name, description, user_count = role_data

        if int(user_count) > 0:
            messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('role_in_use', "Bu rol {user_count} kullanıcı tarafından kullanılıyor. Önce kullanıcıları başka rollere atayın!").format(user_count=user_count))
            return

        if messagebox.askyesno(self.lm.tr('confirmation', "Onay"), self.lm.tr('confirm_delete_role', "{name} rolünü silmek istediğinizden emin misiniz?").format(name=name)):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("DELETE FROM roles WHERE id = ?", (role_id,))
                conn.commit()
                conn.close()

                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('role_deleted', "Rol silindi!"))
                self.load_roles()

            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('role_delete_error', "Rol silme hatası: {e}").format(e=e))

    def manage_permissions(self):
        """İzin yönetimi - Rol-İzin Matrix"""
        self.clear_right_panel()

        # Başlık
        header = tk.Frame(self.right_frame, bg='#8e44ad', height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(
            header,
            text=f"{Icons.LOCKED_KEY} {self.lm.tr('permission_management_matrix', 'İZİN YÖNETİMİ - ROL-İZİN MATRİXİ')}",
            font=('Segoe UI', 16, 'bold'),
            bg='#8e44ad',
            fg='white'
        ).pack(pady=15)

        # İçerik
        content = tk.Frame(self.right_frame, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)

        # Açıklama
        info_frame = tk.LabelFrame(content, text=self.lm.tr('about_permission_management', "İzin Yönetimi Hakkında"),
                                   font=('Segoe UI', 11, 'bold'), bg='white')
        info_frame.pack(fill='x', pady=10)

        info_text = self.lm.tr('permission_info_text', f"""
{Icons.LOCKED_KEY} İzin Yönetimi Sistemi

Bu bölümde roller ve izinler yönetilir:

• ROLLER: Kullanıcı grupları (Admin, Manager, User, vb.)
• İZİNLER: Sistem işlemleri (Create, Read, Update, Delete)
• ROL-İZİN MATRİXİ: Hangi rolün hangi izinlere sahip olduğu

MEVCUT İZİNLER:
├─ Kullanıcı Yönetimi (Create/Read/Update/Delete Users)
├─ Rapor Yönetimi (Create/Read/Export Reports)
├─ Veri Yönetimi (Create/Read/Update Data)
├─ Ayar Yönetimi (Read/Update Settings)
└─ Sistem Yönetimi (Full Access - Sadece Super Admin)

MEVCUT ROLLERsuperadmin / admin / manager / user / guest)
        """)

        tk.Label(info_frame, text=info_text, font=('Segoe UI', 9),
                bg='white', justify='left').pack(pady=15, padx=20)

        # Rol-İzin Matrix
        matrix_frame = tk.LabelFrame(content, text=self.lm.tr('role_permission_matrix', "Rol-İzin Matrix"),
                                     font=('Segoe UI', 11, 'bold'), bg='white')
        matrix_frame.pack(fill='both', expand=True, pady=10)

        # Matrix tablosu
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Rolleri al
            cursor.execute("SELECT id, name, description FROM roles ORDER BY name")
            roles = cursor.fetchall()

            # İzinleri al
            cursor.execute("""
                SELECT DISTINCT p.name, p.description, p.category 
                FROM permissions p 
                ORDER BY p.category, p.name
            """)
            permissions = cursor.fetchall()

            if not roles:
                tk.Label(matrix_frame, text=self.lm.tr('no_roles_warning', f"{Icons.WARNING} Henüz rol tanımlanmamış. 'Rol Yönetimi' bölümünden rol ekleyin."),
                        font=('Segoe UI', 10), bg='white', fg='orange').pack(pady=20)
                conn.close()
                return

            if not permissions:
                tk.Label(matrix_frame, text=self.lm.tr('no_permissions_warning', f"{Icons.WARNING} Henüz izin tanımlanmamış."),
                        font=('Segoe UI', 10), bg='white', fg='orange').pack(pady=20)
                conn.close()
                return

            # Canvas + Scrollbar
            canvas = tk.Canvas(matrix_frame, bg='white')
            scrollbar = ttk.Scrollbar(matrix_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='white')

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Header
            header_frame = tk.Frame(scrollable_frame, bg='#ecf0f1', relief='solid', bd=1)
            header_frame.pack(fill='x', padx=5, pady=5)

            tk.Label(header_frame, text=self.lm.tr('permission_role_header', "İzin / Rol"), font=('Segoe UI', 9, 'bold'),
                    bg='#ecf0f1', width=25, anchor='w').grid(row=0, column=0, sticky='w', padx=5, pady=5)

            for i, role in enumerate(roles):
                tk.Label(header_frame, text=role[1], font=('Segoe UI', 9, 'bold'),
                        bg='#ecf0f1', width=12).grid(row=0, column=i+1, padx=2, pady=5)

            # Matrix rows
            current_category = None

            for perm in permissions:
                perm_name, perm_desc, perm_cat = perm

                # Kategori başlığı
                if perm_cat != current_category:
                    current_category = perm_cat
                    cat_label = tk.Label(scrollable_frame, text=f"▼ {perm_cat or self.lm.tr('general', 'Genel')}",
                                        font=('Segoe UI', 10, 'bold'),
                                        bg='#3498db', fg='white', anchor='w', padx=10)
                    cat_label.pack(fill='x', padx=5, pady=(10, 2))

                # İzin satırı
                perm_frame = tk.Frame(scrollable_frame, bg='white', relief='solid', bd=1)
                perm_frame.pack(fill='x', padx=5, pady=1)

                tk.Label(perm_frame, text=f"  {perm_name}", font=('Segoe UI', 9),
                        bg='white', width=25, anchor='w').grid(row=0, column=0, sticky='w', padx=5, pady=3)

                # Her rol için checkbox
                for i, role in enumerate(roles):
                    role_id = role[0]

                    # Bu rol bu izne sahip mi kontrol et
                    cursor.execute("""
                        SELECT COUNT(*) FROM role_permissions rp
                        JOIN permissions p ON rp.permission_id = p.id
                        WHERE rp.role_id = ? AND p.name = ?
                    """, (role_id, perm_name))

                    has_permission = cursor.fetchone()[0] > 0

                    var = tk.BooleanVar(value=has_permission)

                    # Checkbox
                    cb = tk.Checkbutton(
                        perm_frame,
                        variable=var,
                        bg='white',
                        command=lambda r=role_id, p=perm_name, v=var: self._toggle_permission(r, p, v.get())
                    )
                    cb.grid(row=0, column=i+1, padx=20, pady=3)

            canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            scrollbar.pack(side="right", fill="y", pady=10)

            conn.close()

        except Exception as e:
            tk.Label(matrix_frame, text=self.lm.tr('matrix_load_error', f"{Icons.FAIL} Matrix yükleme hatası: {str(e)}"),
                    font=('Segoe UI', 10), bg='white', fg='red').pack(pady=20)
            import traceback
            traceback.print_exc()

    def _toggle_permission(self, role_id, permission_name, is_enabled):
        """Rol-izin ilişkisini değiştir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Permission ID'yi bul
            cursor.execute("SELECT id FROM permissions WHERE name = ?", (permission_name,))
            perm_result = cursor.fetchone()

            if not perm_result:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('permission_not_found', "İzin bulunamadı: {permission_name}").format(permission_name=permission_name))
                return

            permission_id = perm_result[0]

            if is_enabled:
                # İzni ekle
                try:
                    cursor.execute("""
                        INSERT INTO role_permissions (role_id, permission_id)
                        VALUES (?, ?)
                    """, (role_id, permission_id))
                    conn.commit()
                except sqlite3.IntegrityError as e:
                    logging.error(f'Silent error in super_admin_gui.py: {str(e)}')  # Zaten var
            else:
                # İzni kaldır
                cursor.execute("""
                    DELETE FROM role_permissions
                    WHERE role_id = ? AND permission_id = ?
                """, (role_id, permission_id))
                conn.commit()

            conn.close()

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('permission_update_error', "İzin güncelleme hatası: {e}").format(e=str(e)))
            import traceback
            traceback.print_exc()

    def show_company_management(self):
        """Firma yönetimi"""
        self.clear_right_panel()

        title = tk.Label(
            self.right_frame,
            text=f" {self.lm.tr('company_management', 'Firma Yönetimi')}",
            font=('Segoe UI', 16, 'bold'),
            bg='#16213e',
            fg='#e94560'
        )
        title.pack(pady=20)

        # Buton çerçevesi
        button_frame = tk.Frame(self.right_frame, bg='#16213e')
        button_frame.pack(pady=10)

        buttons = [
            (f" {self.lm.tr('new_company', 'Yeni Firma')}", self.add_company),
            (f" {self.lm.tr('edit_company', 'Firma Düzenle')}", self.edit_company),
            (f" {self.lm.tr('delete_company', 'Firma Sil')}", self.delete_company),
            (f" {self.lm.tr('company_details', 'Firma Detayları')}", self.show_company_details),
        ]

        for text, command in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                font=('Segoe UI', 10),
                bg='#0f3460',
                fg='#ffffff',
                activebackground='#e94560',
                command=command,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2'
            )
            btn.pack(side='left', padx=5)

        # Firma listesi
        list_frame = tk.Frame(self.right_frame, bg='#16213e')
        list_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Treeview
        columns = ('ID', 'company_name', 'sector', 'active', 'created_at')
        self.company_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        headers = {
            'ID': 'ID',
            'company_name': self.lm.tr('col_company_name', 'Firma Adı'),
            'sector': self.lm.tr('col_sector', 'Sektör'),
            'active': self.lm.tr('col_active', 'Aktif'),
            'created_at': self.lm.tr('col_created_at', 'Oluşturulma')
        }

        for col in columns:
            self.company_tree.heading(col, text=headers.get(col, col))
            self.company_tree.column(col, width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.company_tree.yview)
        self.company_tree.configure(yscrollcommand=scrollbar.set)

        self.company_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Firmaları yükle
        self.load_companies()

    def load_companies(self):
        """Firmaları yükle"""
        try:
            # Mevcut verileri temizle
            for item in self.company_tree.get_children():
                self.company_tree.delete(item)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # company_info tablosundan verileri çek
            cursor.execute("""
                SELECT company_id, COALESCE(ticari_unvan, sirket_adi, 'Firma'), sektor_kod, aktif, created_at
                FROM company_info
                ORDER BY company_id
            """)

            companies = cursor.fetchall()
            conn.close()

            for company in companies:
                company_id, name, sector, is_active, created_at = company
                self.company_tree.insert('', 'end', values=(
                    company_id,
                    name or self.lm.tr('unknown', 'Bilinmiyor'),
                    sector or self.lm.tr('unspecified', 'Belirtilmemiş'),
                    self.lm.tr('yes', 'Evet') if is_active else self.lm.tr('no', 'Hayır'),
                    created_at or self.lm.tr('unknown', 'Bilinmiyor')
                ))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('companies_load_error', "Firmalar yüklenemedi: {e}").format(e=e))

    def add_company(self):
        """Yeni firma ekle"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('add_company_title', "Yeni Firma Ekle"))
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.grab_set()

        # Başlık
        title_label = tk.Label(dialog, text=self.lm.tr('add_company_title', "Yeni Firma Ekle"), font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=20)

        # Form çerçevesi
        form_frame = tk.Frame(dialog)
        form_frame.pack(padx=30, pady=20, fill='both', expand=True)

        # Form alanları
        tk.Label(form_frame, text=self.lm.tr('company_name', "Firma Adı:"), font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', pady=5)
        name_entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=30)
        name_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))

        tk.Label(form_frame, text=self.lm.tr('sector', "Sektör:"), font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', pady=5)
        sector_entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=30)
        sector_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))

        # Butonlar
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)

        def save_company():
            name = name_entry.get().strip()
            sector = sector_entry.get().strip()

            if not name:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('company_name_required', "Firma adı gereklidir!"))
                return

            try:
                # Use CompanyManager for consistent creation
                from modules.company.company_manager import CompanyManager
                manager = CompanyManager(self.db_path)
                
                # create_company syncs with companies table and initializes modules
                cid = manager.create_company({
                    'sirket_adi': name,
                    'ticari_unvan': name,
                    'sektor': sector,
                    'aktif': 1
                })
                
                if cid:
                    messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('company_added', "Firma başarıyla eklendi!"))
                    dialog.destroy()
                    self.load_companies()
                else:
                    messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('company_add_error', "Firma oluşturulamadı. Logları kontrol edin."))
                    
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('company_add_error', "Firma ekleme hatası: {e}").format(e=e))

        save_btn = tk.Button(button_frame, text=self.lm.tr('btn_save', "Kaydet"), command=save_company,
                           bg='#28a745', fg='white', font=('Segoe UI', 10), padx=20)
        save_btn.pack(side='left', padx=5)

        cancel_btn = tk.Button(button_frame, text=self.lm.tr('btn_cancel', "İptal"), command=dialog.destroy,
                             bg='#dc3545', fg='white', font=('Segoe UI', 10), padx=20)
        cancel_btn.pack(side='left', padx=5)

    def edit_company(self):
        """Firma düzenle"""
        selected = self.company_tree.selection()
        if not selected:
            messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_company', "Lütfen bir firma seçin!"))
            return

        item = self.company_tree.item(selected[0])
        company_data = item['values']
        company_id, name, sector, is_active, created_at = company_data

        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('edit_company_title', "Firma Düzenle: {name}").format(name=name))
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.grab_set()

        # Başlık
        title_label = tk.Label(dialog, text=self.lm.tr('edit_company_title', "Firma Düzenle: {name}").format(name=name), font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=20)

        # Form çerçevesi
        form_frame = tk.Frame(dialog)
        form_frame.pack(padx=30, pady=20, fill='both', expand=True)

        # Form alanları
        tk.Label(form_frame, text=self.lm.tr('company_name', "Firma Adı:"), font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', pady=5)
        name_entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=30)
        name_entry.insert(0, name)
        name_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))

        tk.Label(form_frame, text=self.lm.tr('sector', "Sektör:"), font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', pady=5)
        sector_entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=30)
        sector_entry.insert(0, sector)
        sector_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))

        tk.Label(form_frame, text=self.lm.tr('active', "Aktif:"), font=('Segoe UI', 10)).grid(row=2, column=0, sticky='w', pady=5)
        active_combo = ttk.Combobox(form_frame, values=[self.lm.tr('yes', "Evet"), self.lm.tr('no', "Hayır")], font=('Segoe UI', 10), width=27)
        active_combo.set(is_active)
        active_combo.grid(row=2, column=1, sticky='ew', pady=5, padx=(10, 0))

        # Butonlar
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)

        def update_company():
            new_name = name_entry.get().strip()
            new_sector = sector_entry.get().strip()
            new_active = 1 if active_combo.get() == self.lm.tr('yes', "Evet") else 0

            if not new_name:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('company_name_required', "Firma adı gereklidir!"))
                return

            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("UPDATE company_info SET sirket_adi=?, ticari_unvan=?, sektor_kod=?, aktif=? WHERE company_id=?",
                             (new_name, new_name, new_sector, new_active, company_id))
                conn.commit()
                conn.close()

                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('company_updated', "Firma başarıyla güncellendi!"))
                dialog.destroy()
                self.load_companies()

            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('company_update_error', "Firma güncelleme hatası: {e}").format(e=e))

        save_btn = tk.Button(button_frame, text=self.lm.tr('btn_update', "Güncelle"), command=update_company,
                           bg='#28a745', fg='white', font=('Segoe UI', 10), padx=20)
        save_btn.pack(side='left', padx=5)

        cancel_btn = tk.Button(button_frame, text=self.lm.tr('btn_cancel', "İptal"), command=dialog.destroy,
                             bg='#dc3545', fg='white', font=('Segoe UI', 10), padx=20)
        cancel_btn.pack(side='left', padx=5)

    def delete_company(self):
        """Firma sil"""
        selected = self.company_tree.selection()
        if not selected:
            messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_company', "Lütfen bir firma seçin!"))
            return

        item = self.company_tree.item(selected[0])
        company_data = item['values']
        company_id, name, sector, is_active, created_at = company_data

        warning_msg = (
            f"{name} firmasını silmek istediğinizden emin misiniz?\n\n"
            "DİKKAT: Bu işlem geri alınamaz!\n\n"
            "Bu şirkete ait TÜM VERİLER (Kullanıcılar, raporlar, enerji kayıtları vb.) "
            "kalıcı olarak SİLİNECEKTİR!"
        )

        if messagebox.askyesno(self.lm.tr('confirmation', "Kritik İşlem Onayı"), warning_msg, icon='warning'):
            try:
                from modules.company.company_manager import CompanyManager
                manager = CompanyManager(self.db_path)
                
                if manager.hard_delete_company(company_id):
                    messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{name} firması ve tüm verileri silindi!")
                    self.load_companies()
                else:
                    messagebox.showerror(self.lm.tr('error', "Hata"), "Firma silinemedi! (Varsayılan şirket silinemez veya bir hata oluştu)")
                    
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), f"Firma silme hatası: {e}")

    def show_company_details(self):
        """Firma detaylarını göster"""
        selected = self.company_tree.selection()
        if not selected:
            messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_company', "Lütfen bir firma seçin!"))
            return

        item = self.company_tree.item(selected[0])
        company_data = item['values']
        company_id, name, sector, is_active, created_at = company_data

        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('company_details_title', "Firma Detayları: {name}").format(name=name))
        dialog.geometry("500x400")
        dialog.grab_set()

        # Başlık
        title_label = tk.Label(dialog, text=self.lm.tr('company_details_title', "Firma Detayları: {name}").format(name=name), font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=20)

        # İçerik
        content_frame = tk.Frame(dialog)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        details_text = f"""
{self.lm.tr('company_info_header', 'FIRMA BİLGİLERİ')}
================
{self.lm.tr('company_name', 'Firma Adı')}: {name}
{self.lm.tr('sector', 'Sektör')}: {sector}
{self.lm.tr('status', 'Durum')}: {is_active}
{self.lm.tr('created_at', 'Oluşturulma Tarihi')}: {created_at}

{self.lm.tr('user_stats_header', 'KULLANICI İSTATİSTİKLERİ')}
========================
"""

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Bu firmaya ait kullanıcı sayısı
            cursor.execute("SELECT COUNT(*) FROM users WHERE company_id = ?", (company_id,))
            user_count = cursor.fetchone()[0]

            details_text += f"{self.lm.tr('total_users', 'Toplam Kullanıcı')}: {user_count}\n"

            conn.close()

        except Exception as e:
            details_text += f"{self.lm.tr('error', 'Hata')}: {e}\n"

        text_widget = tk.Text(content_frame, font=('Consolas', 10), wrap='word')
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', details_text)
        text_widget.config(state='disabled')

    def show_audit_logs(self):
        """Audit logları"""
        self.clear_right_panel()

        title = tk.Label(
            self.right_frame,
            text=f" {self.lm.tr('audit_logs_title', 'Audit Logları')}",
            font=('Segoe UI', 16, 'bold'),
            bg='#16213e',
            fg='#e94560'
        )
        title.pack(pady=20)

        # Buton çerçevesi
        button_frame = tk.Frame(self.right_frame, bg='#16213e')
        button_frame.pack(pady=10)

        buttons = [
            (f" {self.lm.tr('clear_logs', 'Logları Temizle')}", self.clear_audit_logs),
            (f" {self.lm.tr('export_logs', 'Logları Dışa Aktar')}", self.export_audit_logs),
            (f" {self.lm.tr('refresh_logs', 'Logları Yenile')}", self.refresh_audit_logs),
        ]

        for text, command in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                font=('Segoe UI', 10),
                bg='#0f3460',
                fg='#ffffff',
                activebackground='#e94560',
                command=command,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2'
            )
            btn.pack(side='left', padx=5)

        # Log listesi
        list_frame = tk.Frame(self.right_frame, bg='#16213e')
        list_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Treeview
        columns = ('ID', 'Kullanıcı', 'İşlem', 'Tarih', 'Detay')
        display_columns = (
            self.lm.tr('col_id', 'ID'),
            self.lm.tr('col_user', 'Kullanıcı'),
            self.lm.tr('col_action', 'İşlem'),
            self.lm.tr('col_date', 'Tarih'),
            self.lm.tr('col_details', 'Detay')
        )
        self.audit_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        for col, display_name in zip(columns, display_columns):
            self.audit_tree.heading(col, text=display_name)
            self.audit_tree.column(col, width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.audit_tree.yview)
        self.audit_tree.configure(yscrollcommand=scrollbar.set)

        self.audit_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Logları yükle
        self.load_audit_logs()

    def load_audit_logs(self):
        """Audit loglarını yükle"""
        try:
            # Mevcut verileri temizle
            for item in self.audit_tree.get_children():
                self.audit_tree.delete(item)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Audit logs tablosunu kontrol et ve oluştur
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username VARCHAR(50),
                    action VARCHAR(100),
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address VARCHAR(45)
                )
            """)

            # Mevcut tabloya username kolonunu ekle (yoksa)
            cursor.execute("PRAGMA table_info(audit_logs)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'username' not in columns:
                cursor.execute("ALTER TABLE audit_logs ADD COLUMN username VARCHAR(50)")
                conn.commit()

            def fetch_from_audit_logs(cur):
                cols = []
                try:
                    cur.execute("PRAGMA table_info(audit_logs)")
                    cols = [c[1] for c in cur.fetchall()]
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
                ts_col = 'timestamp' if 'timestamp' in cols else ('created_at' if 'created_at' in cols else ('ts' if 'ts' in cols else None))
                det_col = 'details' if 'details' in cols else ('payload_json' if 'payload_json' in cols else ('metadata' if 'metadata' in cols else "''"))
                if ts_col is None:
                    ts_expr = "datetime('now')"
                else:
                    ts_expr = f"COALESCE(a.{ts_col}, datetime('now'))"
                det_expr = f"COALESCE(a.{det_col}, '')" if det_col != "''" else "''"
                query = f"""
                    SELECT a.id,
                           COALESCE(a.username, u.username, 'Sistem') as username,
                           a.action,
                           {ts_expr} as ts,
                           {det_expr} as details
                    FROM audit_logs a
                    LEFT JOIN users u ON a.user_id = u.id
                    ORDER BY a.id DESC
                    LIMIT 1000
                """
                cur.execute(query)
                return cur.fetchall()

            def fetch_from_security_logs(cur):
                cols = []
                try:
                    cur.execute("PRAGMA table_info(security_logs)")
                    cols = [c[1] for c in cur.fetchall()]
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
                ts_col = 'created_at' if 'created_at' in cols else ('timestamp' if 'timestamp' in cols else None)
                det_col = 'details' if 'details' in cols else ('metadata' if 'metadata' in cols else "''")
                ts_expr = f"COALESCE({ts_col}, datetime('now'))" if ts_col else "datetime('now')"
                det_expr = f"COALESCE({det_col}, '')" if det_col != "''" else "''"
                # Kullanıcı alanı: username varsa doğrudan, yoksa user_id üzerinden JOIN
                if 'username' in cols:
                    user_expr = 'username'
                elif 'user_id' in cols:
                    user_expr = "COALESCE((SELECT username FROM users WHERE id = user_id), 'Sistem')"
                else:
                    user_expr = "'Sistem'"
                # İşlem alanı: action yoksa event_type
                if 'action' in cols:
                    action_col = 'action'
                elif 'event_type' in cols:
                    action_col = 'event_type'
                else:
                    return []
                query = f"""
                    SELECT id,
                           {user_expr} as username,
                           {action_col} as action,
                           {ts_expr} as ts,
                           {det_expr} as details
                    FROM security_logs
                    ORDER BY id DESC
                    LIMIT 1000
                """
                cur.execute(query)
                return cur.fetchall()

            # Öncelik: audit_logs, yoksa security_logs
            logs = []
            try:
                cursor.execute("SELECT COUNT(*) FROM audit_logs")
                count_a = cursor.fetchone()[0]
            except Exception:
                count_a = 0
            if count_a:
                logs = fetch_from_audit_logs(cursor)
            else:
                # audit_logs boşsa security_logs'dan getir
                try:
                    cursor.execute("SELECT COUNT(*) FROM security_logs")
                    count_s = cursor.fetchone()[0]
                except Exception:
                    count_s = 0
                if count_s:
                    logs = fetch_from_security_logs(cursor)
                else:
                    logs = []

            try:
                conn.commit()
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
            conn.close()

            for log in logs:
                log_id, username, action, timestamp, details = log
                self.audit_tree.insert('', 'end', values=(
                    log_id,
                    username or self.lm.tr('system_user', 'Sistem'),
                    action or self.lm.tr('unknown', 'Bilinmiyor'),
                    timestamp or self.lm.tr('unknown', 'Bilinmiyor'),
                    (details or self.lm.tr('no_details', 'Detay yok'))[:50] + '...' if details and len(details) > 50 else (details or self.lm.tr('no_details', 'Detay yok'))
                ))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('err_audit_load', 'Audit logları yüklenemedi')}: {e}")

    def clear_audit_logs(self):
        """Audit loglarını temizle"""
        if messagebox.askyesno(self.lm.tr('confirm', 'Onay'), self.lm.tr('confirm_clear_logs', "Tüm audit loglarını silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz!")):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("DELETE FROM audit_logs")
                conn.commit()
                conn.close()

                messagebox.showinfo(self.lm.tr('success', 'Başarılı'), self.lm.tr('logs_cleared', "Audit logları temizlendi!"))
                self.load_audit_logs()

            except Exception as e:
                messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('err_log_clear', 'Log temizleme hatası')}: {e}")

    def export_audit_logs(self):
        """Audit loglarını dışa aktar"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[(self.lm.tr("csv_files", "CSV Dosyaları"), "*.csv"), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")],
                title=self.lm.tr('save_audit_logs', "Audit Loglarını Kaydet")
            )

            if not filename:
                return

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT username, action, timestamp, details
                FROM audit_logs
                ORDER BY timestamp DESC
            """)

            logs = cursor.fetchall()
            conn.close()

            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    self.lm.tr('col_user', 'Kullanıcı'),
                    self.lm.tr('col_action', 'İşlem'),
                    self.lm.tr('col_date', 'Tarih'),
                    self.lm.tr('col_details', 'Detay')
                ])
                writer.writerows(logs)

            messagebox.showinfo(self.lm.tr('success', 'Başarılı'), self.lm.tr('logs_exported', "Audit logları {filename} dosyasına kaydedildi!").format(filename=filename))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('err_export', 'Dışa aktarma hatası')}: {e}")

    def refresh_audit_logs(self):
        """Audit loglarını yenile"""
        self.load_audit_logs()

    def show_system_settings(self):
        """Sistem ayarları"""
        self.clear_right_panel()

        title = tk.Label(
            self.right_frame,
            text=f" {self.lm.tr('system_settings_title', 'Sistem Ayarları')}",
            font=('Segoe UI', 16, 'bold'),
            bg='#16213e',
            fg='#e94560'
        )
        title.pack(pady=20)

        # Ayarlar çerçevesi
        settings_frame = tk.Frame(self.right_frame, bg='#16213e')
        settings_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Sistem bilgileri
        info_frame = tk.LabelFrame(settings_frame, text=self.lm.tr('system_info_header', "Sistem Bilgileri"),
                                 font=('Segoe UI', 12, 'bold'), bg='#16213e', fg='#ffffff')
        info_frame.pack(fill='x', pady=10)

        try:
            import platform

            import psutil

            system_info = f"""
{self.lm.tr('os_label', 'İşletim Sistemi')}: {platform.system()} {platform.release()}
{self.lm.tr('python_ver', 'Python Sürümü')}: {platform.python_version()}
{self.lm.tr('processor', 'İşlemci')}: {platform.processor()}
{self.lm.tr('ram', 'RAM')}: {psutil.virtual_memory().total // (1024**3)} GB
{self.lm.tr('disk_space', 'Disk Alanı')}: {psutil.disk_usage('/').total // (1024**3)} GB
"""

            info_label = tk.Label(info_frame, text=system_info,
                                font=('Consolas', 9), bg='#16213e', fg='#ffffff', justify='left')
            info_label.pack(padx=10, pady=10)

        except ImportError:
            info_label = tk.Label(info_frame, text=self.lm.tr('sys_info_error', "Sistem bilgileri alınamadı (psutil eksik)"),
                                font=('Segoe UI', 10), bg='#16213e', fg='#e94560')
            info_label.pack(padx=10, pady=10)

        # Veritabanı ayarları
        db_frame = tk.LabelFrame(settings_frame, text=self.lm.tr('db_settings_header', "Veritabanı Ayarları"),
                               font=('Segoe UI', 12, 'bold'), bg='#16213e', fg='#ffffff')
        db_frame.pack(fill='x', pady=10)

        db_info = f"""
{self.lm.tr('db_path', 'Veritabanı Yolu')}: {self.db_path}
{self.lm.tr('db_size', 'Veritabanı Boyutu')}: {os.path.getsize(self.db_path) / (1024*1024):.2f} MB
{self.lm.tr('last_update', 'Son Güncelleme')}: {datetime.fromtimestamp(os.path.getmtime(self.db_path)).strftime('%Y-%m-%d %H:%M:%S')}
"""

        db_label = tk.Label(db_frame, text=db_info,
                          font=('Consolas', 9), bg='#16213e', fg='#ffffff', justify='left')
        db_label.pack(padx=10, pady=10)

        # Butonlar
        button_frame = tk.Frame(settings_frame, bg='#16213e')
        button_frame.pack(pady=20)

        buttons = [
            (f" {self.lm.tr('optimize_db', 'Veritabanını Optimize Et')}", self.optimize_database),
            (f" {self.lm.tr('system_cleanup', 'Sistem Temizliği')}", self.system_cleanup),
            (f" {self.lm.tr('reset_settings', 'Ayarları Sıfırla')}", self.reset_settings),
        ]

        for text, command in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                font=('Segoe UI', 10),
                bg='#0f3460',
                fg='#ffffff',
                activebackground='#e94560',
                command=command,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2'
            )
            btn.pack(side='left', padx=5)

    def optimize_database(self):
        """Veritabanını optimize et"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # VACUUM işlemi
            cursor.execute("VACUUM")

            # ANALYZE işlemi
            cursor.execute("ANALYZE")

            conn.close()

            messagebox.showinfo(self.lm.tr('success', 'Başarılı'), self.lm.tr('db_optimized', "Veritabanı optimize edildi!"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('err_optimize', 'Optimizasyon hatası')}: {e}")

    def system_cleanup(self):
        """Sistem temizliği"""
        try:
            import tempfile

            # Geçici dosyaları temizle
            temp_dir = tempfile.gettempdir()
            temp_files = [f for f in os.listdir(temp_dir) if f.startswith('sustainage')]

            cleaned = 0
            for file in temp_files:
                try:
                    os.remove(os.path.join(temp_dir, file))
                    cleaned += 1
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")

            messagebox.showinfo(self.lm.tr('success', 'Başarılı'), self.lm.tr('cleanup_complete', "Sistem temizliği tamamlandı!\n{cleaned} geçici dosya silindi.").format(cleaned=cleaned))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('err_cleanup', 'Temizlik hatası')}: {e}")

    def reset_settings(self):
        """Ayarları sıfırla"""
        if messagebox.askyesno(self.lm.tr('confirm', 'Onay'), self.lm.tr('confirm_reset', "Tüm sistem ayarlarını sıfırlamak istediğinizden emin misiniz?\n\nBu işlem geri alınamaz!")):
            try:
                # UI ayarları dosyasını sil
                ui_settings_path = os.path.join(self.base_dir, 'config', 'ui_settings.json')
                if os.path.exists(ui_settings_path):
                    os.remove(ui_settings_path)

                messagebox.showinfo(self.lm.tr('success', 'Başarılı'), self.lm.tr('settings_reset', "Ayarları sıfırlandı!\nProgramı yeniden başlatın."))

            except Exception as e:
                messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('err_reset', 'Ayar sıfırlama hatası')}: {e}")

    def show_maintenance(self):
        """Bakım ve onarım"""
        self.clear_right_panel()

        title = tk.Label(
            self.right_frame,
            text=f" {self.lm.tr('maintenance_title', 'Bakım & Onarım')}",
            font=('Segoe UI', 16, 'bold'),
            bg='#16213e',
            fg='#e94560'
        )
        title.pack(pady=20)

        # Bakım araçları
        tools_frame = tk.Frame(self.right_frame, bg='#16213e')
        tools_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Veritabanı bakımı
        db_frame = tk.LabelFrame(tools_frame, text=self.lm.tr('db_maintenance_header', "Veritabanı Bakımı"),
                               font=('Segoe UI', 12, 'bold'), bg='#16213e', fg='#ffffff')
        db_frame.pack(fill='x', pady=10)

        db_buttons = [
            (f" {self.lm.tr('db_check', 'Veritabanı Kontrolü')}", self.check_database),
            (f" {self.lm.tr('repair_db', 'Bozuk Kayıtları Temizle')}", self.repair_database),
            (f" {self.lm.tr('rebuild_indexes', 'İndeksleri Yeniden Oluştur')}", self.rebuild_indexes),
        ]

        for text, command in db_buttons:
            btn = tk.Button(
                db_frame,
                text=text,
                font=('Segoe UI', 10),
                bg='#0f3460',
                fg='#ffffff',
                activebackground='#e94560',
                command=command,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2'
            )
            btn.pack(side='left', padx=5, pady=5)

        # Dosya sistemi bakımı
        fs_frame = tk.LabelFrame(tools_frame, text=self.lm.tr('fs_maintenance_header', "Dosya Sistemi Bakımı"),
                               font=('Segoe UI', 12, 'bold'), bg='#16213e', fg='#ffffff')
        fs_frame.pack(fill='x', pady=10)

        fs_buttons = [
            (f" {self.lm.tr('find_corrupted', 'Bozuk Dosyaları Bul')}", self.find_corrupted_files),
            (f" {self.lm.tr('cleanup_unnecessary', 'Gereksiz Dosyaları Temizle')}", self.cleanup_files),
            (f" {self.lm.tr('check_disk', 'Disk Alanını Kontrol Et')}", self.check_disk_space),
        ]

        for text, command in fs_buttons:
            btn = tk.Button(
                fs_frame,
                text=text,
                font=('Segoe UI', 10),
                bg='#0f3460',
                fg='#ffffff',
                activebackground='#e94560',
                command=command,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2'
            )
            btn.pack(side='left', padx=5, pady=5)

        # Sistem bakımı
        sys_frame = tk.LabelFrame(tools_frame, text=self.lm.tr('sys_maintenance_header', "Sistem Bakımı"),
                                font=('Segoe UI', 12, 'bold'), bg='#16213e', fg='#ffffff')
        sys_frame.pack(fill='x', pady=10)

        sys_buttons = [
            (f" {self.lm.tr('check_perf', 'Sistem Performansını Kontrol Et')}", self.check_performance),
            (f" {self.lm.tr('check_mem', 'Bellek Kullanımını Kontrol Et')}", self.check_memory),
            (f" {self.lm.tr('cleanup_logs_btn', 'Log Dosyalarını Temizle')}", self.cleanup_logs),
            (f" {self.lm.tr('run_quality', 'Kalite Kontrollerini Çalıştır')}", self.run_quality_checks),
            (f" {self.lm.tr('run_style', 'Kod Stili Düzeltmeleri (Ruff + isort)')}", self.run_code_style_fixes),
        ]

        for text, command in sys_buttons:
            btn = tk.Button(
                sys_frame,
                text=text,
                font=('Segoe UI', 10),
                bg='#0f3460',
                fg='#ffffff',
                activebackground='#e94560',
                command=command,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2'
            )
            btn.pack(side='left', padx=5, pady=5)

    def check_database(self):
        """Veritabanı kontrolü"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # PRAGMA integrity_check
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]

            if result == "ok":
                messagebox.showinfo(self.lm.tr('db_check_title', "Veritabanı Kontrolü"), self.lm.tr('db_healthy', "Veritabanı sağlıklı!"))
            else:
                messagebox.showwarning(self.lm.tr('db_check_title', "Veritabanı Kontrolü"), self.lm.tr('db_issues', "Veritabanı sorunları tespit edildi:\n{result}").format(result=result))

            conn.close()

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('err_db_check', 'Veritabanı kontrolü hatası')}: {e}")

    def repair_database(self):
        """Bozuk kayıtları temizle"""
        if messagebox.askyesno(self.lm.tr('confirm', 'Onay'), self.lm.tr('confirm_repair', "Bozuk kayıtları temizlemek istediğinizden emin misiniz?")):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Boş kayıtları temizle
                tables = ['users', 'companies', 'audit_logs']
                cleaned = 0

                for table in tables:
                    try:
                        cursor.execute(f"DELETE FROM {table} WHERE id IS NULL")
                        cleaned += cursor.rowcount
                    except Exception as e:
                        logging.error(f"Silent error caught: {str(e)}")

                conn.commit()
                conn.close()

                messagebox.showinfo(self.lm.tr('success', 'Başarılı'), self.lm.tr('repair_complete', "Bakım tamamlandı!\n{cleaned} bozuk kayıt temizlendi.").format(cleaned=cleaned))

            except Exception as e:
                messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('err_repair', 'Onarım hatası')}: {e}")

    def rebuild_indexes(self):
        """İndeksleri yeniden oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # ANALYZE işlemi
            cursor.execute("ANALYZE")

            conn.close()

            messagebox.showinfo(self.lm.tr('success', 'Başarılı'), self.lm.tr('indexes_rebuilt', "İndeksler yeniden oluşturuldu!"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('err_rebuild', 'İndeks yenileme hatası')}: {e}")

    def find_corrupted_files(self):
        """Bozuk dosyaları bul"""
        try:
            corrupted_files = []

            # Modules klasöründeki Python dosyalarını kontrol et
            modules_dir = os.path.join(self.base_dir, 'modules')
            if os.path.exists(modules_dir):
                for root, dirs, files in os.walk(modules_dir):
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    f.read()
                            except Exception:
                                corrupted_files.append(file_path)

            if corrupted_files:
                message = self.lm.tr('corrupted_files_found', "{count} bozuk dosya bulundu:\n\n").format(count=len(corrupted_files))
                for file in corrupted_files[:10]:
                    message += f"• {file}\n"
                if len(corrupted_files) > 10:
                    message += self.lm.tr('and_more', "... ve {count} tane daha").format(count=len(corrupted_files)-10)

                messagebox.showwarning(self.lm.tr('corrupted_files_title', "Bozuk Dosyalar"), message)
            else:
                messagebox.showinfo(self.lm.tr('file_check_title', "Dosya Kontrolü"), self.lm.tr('no_corrupted', "Bozuk dosya bulunamadı!"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('err_file_check', 'Dosya kontrolü hatası')}: {e}")

    def cleanup_files(self):
        """Gereksiz dosyaları temizle"""
        try:
            cleaned = 0

            # __pycache__ klasörlerini temizle
            modules_dir = os.path.join(self.base_dir, 'modules')
            if os.path.exists(modules_dir):
                for root, dirs, files in os.walk(modules_dir):
                    if '__pycache__' in dirs:
                        pycache_path = os.path.join(root, '__pycache__')
                        try:
                            shutil.rmtree(pycache_path)
                            cleaned += 1
                        except Exception as e:
                            logging.error(f"Silent error caught: {str(e)}")

            messagebox.showinfo(self.lm.tr('success', 'Başarılı'), self.lm.tr('cleanup_complete_pycache', "Temizlik tamamlandı!\n{cleaned} __pycache__ klasörü silindi.").format(cleaned=cleaned))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('err_cleanup', 'Temizlik hatası')}: {e}")

    def check_disk_space(self):
        """Disk alanını kontrol et"""
        try:
            import shutil

            total, used, free = shutil.disk_usage(self.base_dir)

            total_gb = total // (1024**3)
            used_gb = used // (1024**3)
            free_gb = free // (1024**3)

            usage_percent = (used / total) * 100

            status = self.lm.tr('status_critical', 'Kritik') if usage_percent > 90 else self.lm.tr('status_normal', 'Normal') if usage_percent < 80 else self.lm.tr('status_warning', 'Dikkat')

            message = self.lm.tr('disk_info_msg', """
Disk Alanı Bilgileri:
====================

Toplam Alan: {total} GB
Kullanılan: {used} GB ({percent:.1f}%)
Boş Alan: {free} GB

Durum: {status}
""").format(total=total_gb, used=used_gb, percent=usage_percent, free=free_gb, status=status)

            messagebox.showinfo(self.lm.tr('disk_info_title', "Disk Alanı"), message)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('err_disk_check', 'Disk kontrolü hatası')}: {e}")

    def check_performance(self):
        """Sistem performansını kontrol et"""
        try:
            import time

            # Veritabanı performans testi
            start_time = time.time()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            cursor.fetchone()
            conn.close()

            db_time = time.time() - start_time

            status = self.lm.tr('status_slow', 'Yavaş') if db_time > 1.0 else self.lm.tr('status_normal', 'Normal') if db_time < 0.5 else self.lm.tr('status_medium', 'Orta')
            suggestion = self.lm.tr('sugg_optimize', 'Veritabanını optimize edin') if db_time > 1.0 else self.lm.tr('sugg_normal', 'Performans normal')

            message = self.lm.tr('perf_report_msg', """
Sistem Performans Raporu:
========================

Veritabanı Yanıt Süresi: {time:.3f} saniye
Durum: {status}

Öneriler:
• {suggestion}
""").format(time=db_time, status=status, suggestion=suggestion)

            messagebox.showinfo(self.lm.tr('perf_report_title', "Performans Kontrolü"), message)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('err_perf_check', 'Performans kontrolü hatası')}: {e}")

    def check_memory(self):
        """Bellek kullanımını kontrol et"""
        try:
            import psutil

            memory = psutil.virtual_memory()

            status = self.lm.tr('status_critical', 'Kritik') if memory.percent > 90 else self.lm.tr('status_normal', 'Normal') if memory.percent < 70 else self.lm.tr('status_warning', 'Dikkat')

            message = self.lm.tr('mem_check_msg', """
Bellek Kullanımı:
================

Toplam RAM: {total} GB
Kullanılan: {used} GB
Boş: {free} GB
Kullanım Oranı: {percent:.1f}%

Durum: {status}
""").format(
                total=memory.total // (1024**3),
                used=memory.used // (1024**3),
                free=memory.available // (1024**3),
                percent=memory.percent,
                status=status
            )

            messagebox.showinfo(self.lm.tr('mem_check_title', "Bellek Kontrolü"), message)

        except ImportError:
            messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('warn_psutil', "psutil modülü eksik. Bellek bilgileri alınamadı."))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('err_mem_check', 'Bellek kontrolü hatası')}: {e}")

    def cleanup_logs(self):
        """Log dosyalarını temizle"""
        try:
            cleaned = 0
            for rel in ['logs', os.path.join('data', 'logs')]:
                target = os.path.join(self.base_dir, rel)
                if os.path.exists(target):
                    for file in os.listdir(target):
                        if file.endswith('.log'):
                            file_path = os.path.join(target, file)
                            try:
                                os.remove(file_path)
                                cleaned += 1
                            except Exception as e:
                                logging.error(f"Silent error caught: {str(e)}")

            messagebox.showinfo(self.lm.tr('success', 'Başarılı'), self.lm.tr('logs_cleaned', "Log temizliği tamamlandı!\n{cleaned} log dosyası silindi.").format(cleaned=cleaned))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('err_log_clean', 'Log temizliği hatası')}: {e}")

    def run_quality_checks(self):
        try:
            script_path = os.path.join(self.base_dir, 'tools', 'quality_checks.py')
            if not os.path.exists(script_path):
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('warn_quality_script', "Kalite kontrol scripti bulunamadı: tools/quality_checks.py"))
                return

            progress = tk.Toplevel(self.parent)
            progress.title(self.lm.tr('quality_running_title', "Kalite Kontrolleri Çalışıyor"))
            progress.geometry("420x160")
            try:
                progress.transient(self.parent)
                progress.grab_set()
                progress.protocol("WM_DELETE_WINDOW", lambda: None)
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")

            frm = tk.Frame(progress, bg='white')
            frm.pack(fill='both', expand=True, padx=20, pady=20)
            lbl = tk.Label(
                frm,
                text=self.lm.tr('quality_running_msg', "Kalite kontrolleri çalışıyor...\nLütfen işlem bitene kadar bekleyin."),
                font=('Segoe UI', 11),
                bg='white'
            )
            lbl.pack(pady=8)

            pb = ttk.Progressbar(frm, mode='indeterminate', length=300)
            pb.pack(pady=8)
            try:
                pb.start(10)
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
            try:
                self.parent.config(cursor='watch')
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")

            result = {'output': '', 'error': ''}

            def _finish():
                try:
                    pb.stop()
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
                try:
                    progress.destroy()
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
                try:
                    self.parent.config(cursor='')
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")

                output = (result.get('output') or '').strip()
                error = (result.get('error') or '').strip()
                combined = (output + ("\n" + error if error else '')).strip()

                dialog = tk.Toplevel(self.parent)
                dialog.title(self.lm.tr('quality_result_title', "Kalite Kontrolleri Sonucu"))
                dialog.geometry("900x600")
                try:
                    dialog.transient(self.parent)
                    dialog.focus_force()
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
                frame = tk.Frame(dialog, bg='#ffffff')
                frame.pack(fill='both', expand=True)
                scrollbar = ttk.Scrollbar(frame, orient='vertical')
                scrollbar.pack(side='right', fill='y')
                text = tk.Text(frame, font=('Consolas', 10), wrap='word', yscrollcommand=scrollbar.set)
                text.pack(side='left', fill='both', expand=True)
                scrollbar.config(command=text.yview)

                if not combined:
                    combined = self.lm.tr('quality_success_msg', "Kalite kontrolleri başarıyla tamamlandı.\n\n• Script herhangi bir çıktı üretmedi.\n• Bu genellikle kontrol edilen öğelerde kritik bir sorun bulunmadığı anlamına gelir.\n• Ayrıntı gerekiyorsa 'tools/quality_checks.py' ve varsa log dosyalarını kontrol edebilirsiniz.")

                text.insert('1.0', combined)
                text.config(state='disabled')

            def _worker():
                try:
                    p = subprocess.run([sys.executable, script_path], capture_output=True, text=True, cwd=self.base_dir)
                    result['output'] = p.stdout or ''
                    result['error'] = p.stderr or ''
                except Exception as ex:
                    result['error'] = str(ex)
                finally:
                    try:
                        progress.after(0, _finish)
                    except Exception:
                        _finish()

            try:
                import threading
                t = threading.Thread(target=_worker, daemon=True)
                t.start()
            except Exception:
                # Fallback: çalıştır ve bitişi göster
                _worker()

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('err_quality', 'Kalite kontrolleri çalıştırılamadı')}: {e}")

    def run_code_style_fixes(self):
        try:
            cmd1 = [
                sys.executable, "-m", "ruff", "check", ".", "--fix",
                "--exclude", "archive/**,**/backup/**,**/md_backup_*/**"
            ]
            p1 = subprocess.run(cmd1, capture_output=True, text=True, cwd=self.base_dir)
            out1 = (p1.stdout or '') + ("\n" + p1.stderr if p1.stderr else '')

            cmd2 = [
                sys.executable, "-m", "isort", ".",
                "--skip", "archive",
                "--skip", "backup",
                "--skip", "md_backup_20251111_194638"
            ]
            p2 = subprocess.run(cmd2, capture_output=True, text=True, cwd=self.base_dir)
            out2 = (p2.stdout or '') + ("\n" + p2.stderr if p2.stderr else '')

            info = self.lm.tr('style_fixes_msg', """
Kod Stili Düzeltmeleri Tamamlandı
================================

RUFF ÇIKTISI:
-------------
{ruff}

ISORT ÇIKTISI:
--------------
{isort}

Not: Değişikliklerin etkili olması için uygulamayı yeniden başlatmanız gerekebilir.
""").format(ruff=out1, isort=out2)

            dialog = tk.Toplevel(self.parent)
            dialog.title(self.lm.tr('style_fixes_title', "Kod Stili Düzeltmeleri"))
            dialog.geometry("800x600")
            
            frame = tk.Frame(dialog, bg='#ffffff')
            frame.pack(fill='both', expand=True)
            scrollbar = ttk.Scrollbar(frame, orient='vertical')
            scrollbar.pack(side='right', fill='y')
            text = tk.Text(frame, font=('Consolas', 10), wrap='word', yscrollcommand=scrollbar.set)
            text.pack(side='left', fill='both', expand=True)
            scrollbar.config(command=text.yview)
            
            text.insert('1.0', info)
            text.config(state='disabled')

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('err_style', 'Kod stili düzeltme hatası')}: {e}")

    def show_backup(self):
        """Yedekleme ve geri yükleme"""
        self.clear_right_panel()

        title = tk.Label(
            self.right_frame,
            text=f" {self.lm.tr('backup_restore_title', 'Yedekleme & Geri Yükleme')}",
            font=('Segoe UI', 16, 'bold'),
            bg='#16213e',
            fg='#e94560'
        )
        title.pack(pady=20)

        # Yedekleme araçları
        backup_frame = tk.Frame(self.right_frame, bg='#16213e')
        backup_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Veritabanı yedekleme
        db_frame = tk.LabelFrame(backup_frame, text=self.lm.tr('db_backup_section', "Veritabanı Yedekleme"),
                               font=('Segoe UI', 12, 'bold'), bg='#16213e', fg='#ffffff')
        db_frame.pack(fill='x', pady=10)

        db_buttons = [
            (f" {self.lm.tr('backup_db_btn', 'Veritabanını Yedekle')}", self.backup_database),
            (f" {self.lm.tr('restore_db_btn', 'Yedekten Geri Yükle')}", self.restore_database),
            (f" {self.lm.tr('setup_auto_backup_btn', 'Otomatik Yedekleme Ayarla')}", self.setup_auto_backup),
        ]

        for text, command in db_buttons:
            btn = tk.Button(
                db_frame,
                text=text,
                font=('Segoe UI', 10),
                bg='#0f3460',
                fg='#ffffff',
                activebackground='#e94560',
                command=command,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2'
            )
            btn.pack(side='left', padx=5, pady=5)

        # Dosya yedekleme
        file_frame = tk.LabelFrame(backup_frame, text=self.lm.tr('file_backup_section', "Dosya Yedekleme"),
                                 font=('Segoe UI', 12, 'bold'), bg='#16213e', fg='#ffffff')
        file_frame.pack(fill='x', pady=10)

        file_buttons = [
            (f" {self.lm.tr('backup_all_files_btn', 'Tüm Dosyaları Yedekle')}", self.backup_all_files),
            (f" {self.lm.tr('backup_modules_btn', 'Modülleri Yedekle')}", self.backup_modules),
            (f" {self.lm.tr('backup_config_btn', 'Konfigürasyonu Yedekle')}", self.backup_config),
        ]

        for text, command in file_buttons:
            btn = tk.Button(
                file_frame,
                text=text,
                font=('Segoe UI', 10),
                bg='#0f3460',
                fg='#ffffff',
                activebackground='#e94560',
                command=command,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2'
            )
            btn.pack(side='left', padx=5, pady=5)

    def backup_database(self):
        """Veritabanını yedekle"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[(self.lm.tr("file_sqlite", "SQLite Dosyaları"), "*.db"), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")],
                title=self.lm.tr('save_db_backup_title', "Veritabanı Yedeğini Kaydet")
            )

            if not filename:
                return

            shutil.copy2(self.db_path, filename)
            messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{self.lm.tr('db_backup_success', 'Veritabanı yedeği kaydedildi')}: {filename}")

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('backup_error', 'Yedekleme hatası')}: {e}")

    def restore_database(self):
        """Yedekten geri yükle"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[(self.lm.tr("file_sqlite", "SQLite Dosyaları"), "*.db"), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")],
                title=self.lm.tr('select_backup_db_title', "Yedek Veritabanını Seç")
            )

            if not filename:
                return

            if messagebox.askyesno(self.lm.tr('confirm', "Onay"), self.lm.tr('restore_confirm_msg', "Mevcut veritabanını değiştirmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz!")):
                shutil.copy2(filename, self.db_path)
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('restore_success_msg', "Veritabanı geri yüklendi!\nProgramı yeniden başlatın."))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('restore_error', 'Geri yükleme hatası')}: {e}")

    def setup_auto_backup(self):
        """Otomatik yedekleme ayarla"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('auto_backup_title', "Otomatik Yedekleme"))
        dialog.geometry("500x400")
        dialog.grab_set()

        tk.Label(dialog, text=self.lm.tr('auto_backup_settings_header', "Otomatik Yedekleme Ayarları"),
                font=('Segoe UI', 14, 'bold')).pack(pady=20)

        form = tk.Frame(dialog)
        form.pack(padx=30, pady=20)

        # Yedekleme sıklığı
        tk.Label(form, text=self.lm.tr('backup_frequency', "Yedekleme Sıklığı:"), font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=10)

        frequency_var = tk.StringVar(value='daily')
        freq_frame = tk.Frame(form)
        freq_frame.grid(row=0, column=1, sticky='w', pady=10, padx=10)

        tk.Radiobutton(freq_frame, text=self.lm.tr('daily', 'Günlük'), variable=frequency_var, value='daily').pack(anchor='w')
        tk.Radiobutton(freq_frame, text=self.lm.tr('weekly', 'Haftalık'), variable=frequency_var, value='weekly').pack(anchor='w')
        tk.Radiobutton(freq_frame, text=self.lm.tr('monthly', 'Aylık'), variable=frequency_var, value='monthly').pack(anchor='w')

        # Yedek sayısı
        tk.Label(form, text=self.lm.tr('backup_keep_count', "Saklanacak Yedek Sayısı:"), font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=10)
        backup_count = tk.Entry(form, font=('Segoe UI', 10), width=10)
        backup_count.insert(0, "7")
        backup_count.grid(row=1, column=1, sticky='w', pady=10, padx=10)

        # Yedek klasörü
        tk.Label(form, text=self.lm.tr('backup_folder', "Yedek Klasörü:"), font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=10)
        folder_entry = tk.Entry(form, font=('Segoe UI', 10), width=30)
        folder_entry.insert(0, "backups/")
        folder_entry.grid(row=2, column=1, sticky='w', pady=10, padx=10)

        def save_auto_backup():
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO system_settings (key, value, category, description)
                    VALUES ('auto_backup_enabled', '1', 'backup', 'Auto backup enabled')
                    ON CONFLICT(key) DO UPDATE SET value = '1'
                """)

                cursor.execute("""
                    INSERT INTO system_settings (key, value, category, description)
                    VALUES ('auto_backup_frequency', ?, 'backup', 'Backup frequency')
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """, (frequency_var.get(),))

                cursor.execute("""
                    INSERT INTO system_settings (key, value, category, description)
                    VALUES ('auto_backup_keep_count', ?, 'backup', 'Number of backups to keep')
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """, (backup_count.get(),))

                cursor.execute("""
                    INSERT INTO system_settings (key, value, category, description)
                    VALUES ('auto_backup_folder', ?, 'backup', 'Backup folder path')
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """, (folder_entry.get(),))

                conn.commit()
                conn.close()

                messagebox.showinfo(self.lm.tr('saved', "Kaydedildi"),
                    f"{self.lm.tr('auto_backup_saved', 'Otomatik yedekleme ayarları kaydedildi!')}\n\n"
                    f"{self.lm.tr('frequency', 'Sıklık')}: {frequency_var.get()}\n"
                    f"{self.lm.tr('backup_count', 'Yedek sayısı')}: {backup_count.get()}\n"
                    f"{self.lm.tr('folder', 'Klasör')}: {folder_entry.get()}")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('save_error', 'Kaydetme hatası')}: {e}")

        tk.Button(dialog, text=f"{Icons.SAVE} {self.lm.tr('save_settings', 'Ayarları Kaydet')}", font=('Segoe UI', 11, 'bold'),
                 bg='#27ae60', fg='white', padx=30, pady=10,
                 command=save_auto_backup).pack(pady=20)

    def backup_all_files(self):
        """Tüm dosyaları yedekle"""
        try:
            folder = filedialog.askdirectory(title=self.lm.tr('select_backup_folder', "Yedek Klasörünü Seç"))

            if not folder:
                return

            backup_dir = os.path.join(folder, f"sustainage_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            os.makedirs(backup_dir, exist_ok=True)

            # Ana klasörü kopyala
            shutil.copytree(self.base_dir, backup_dir, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))

            messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{self.lm.tr('all_files_backup_success', 'Tüm dosyalar yedeklendi')}: {backup_dir}")

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('backup_error', 'Yedekleme hatası')}: {e}")

    def backup_modules(self):
        """Modülleri yedekle"""
        try:
            folder = filedialog.askdirectory(title=self.lm.tr('select_backup_folder', "Yedek Klasörünü Seç"))

            if not folder:
                return

            modules_dir = os.path.join(self.base_dir, 'modules')
            backup_dir = os.path.join(folder, f"modules_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

            shutil.copytree(modules_dir, backup_dir, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))

            messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{self.lm.tr('modules_backup_success', 'Modüller yedeklendi')}: {backup_dir}")

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('backup_error', 'Yedekleme hatası')}: {e}")

    def backup_config(self):
        """Konfigürasyonu yedekle"""
        try:
            folder = filedialog.askdirectory(title=self.lm.tr('select_backup_folder', "Yedek Klasörünü Seç"))

            if not folder:
                return

            config_dir = os.path.join(self.base_dir, 'config')
            backup_dir = os.path.join(folder, f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

            if os.path.exists(config_dir):
                shutil.copytree(config_dir, backup_dir)
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{self.lm.tr('config_backup_success', 'Konfigürasyon yedeklendi')}: {backup_dir}")
            else:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('config_folder_not_found', "Config klasörü bulunamadı!"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('backup_error', 'Yedekleme hatası')}: {e}")

    def show_module_management(self):
        """Modül yönetimi"""
        self.clear_right_panel()

        title = tk.Label(
            self.right_frame,
            text=f" {self.lm.tr('module_management_title', 'Modül Yönetimi')}",
            font=('Segoe UI', 16, 'bold'),
            bg='#16213e',
            fg='#e94560'
        )
        title.pack(pady=20)

        # Modül listesi
        list_frame = tk.Frame(self.right_frame, bg='#16213e')
        list_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Treeview
        columns = ('module_name', 'status', 'file_count', 'last_update')
        self.module_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        headers = {
            'module_name': self.lm.tr('module_name', 'Modül Adı'),
            'status': self.lm.tr('status', 'Durum'),
            'file_count': self.lm.tr('file_count', 'Dosya Sayısı'),
            'last_update': self.lm.tr('last_update', 'Son Güncelleme')
        }

        for col, text in headers.items():
            self.module_tree.heading(col, text=text)
            self.module_tree.column(col, width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.module_tree.yview)
        self.module_tree.configure(yscrollcommand=scrollbar.set)

        self.module_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Modülleri yükle
        self.load_modules()

    def load_modules(self):
        """Modülleri yükle"""
        try:
            # Mevcut verileri temizle
            for item in self.module_tree.get_children():
                self.module_tree.delete(item)

            modules_dir = os.path.join(self.base_dir, 'modules')
            if not os.path.exists(modules_dir):
                return

            modules = [d for d in os.listdir(modules_dir)
                      if os.path.isdir(os.path.join(modules_dir, d)) and d != '__pycache__']

            for module in modules:
                module_path = os.path.join(modules_dir, module)

                # Dosya sayısı
                file_count = len([f for f in os.listdir(module_path)
                                if os.path.isfile(os.path.join(module_path, f))])

                # Son güncelleme
                try:
                    mtime = os.path.getmtime(module_path)
                    last_update = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
                except Exception:
                    last_update = 'Bilinmiyor'

                # Durum kontrolü - Çoklu GUI dosya formatını kontrol et
                possible_gui_files = [
                    os.path.join(module_path, f"{module}_gui.py"),
                    os.path.join(module_path, "gui.py"),
                    os.path.join(module_path, f"{module}_dashboard.py"),
                    os.path.join(module_path, "dashboard.py"),
                ]

                # Herhangi bir GUI dosyası var mı?
                has_gui = any(os.path.exists(f) for f in possible_gui_files)

                # Eğer GUI yoksa, manager.py veya başka Python dosyası var mı kontrol et
                if not has_gui:
                    py_files = [f for f in os.listdir(module_path)
                               if f.endswith('.py') and not f.startswith('__')
                               and 'test' not in f.lower()]
                    has_gui = len(py_files) > 0

                status = 'Aktif' if has_gui else 'Backend Only'

                self.module_tree.insert('', 'end', values=(
                    module,
                    status,
                    file_count,
                    last_update
                ))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('modules_load_error', "Modüller yüklenemedi: {e}").format(e=e))

    def show_performance(self):
        """Performans izleme"""
        self.clear_right_panel()

        title = tk.Label(
            self.right_frame,
            text=f" {self.lm.tr('performance_monitor_title', 'Performans İzleme')}",
            font=('Segoe UI', 16, 'bold'),
            bg='#16213e',
            fg='#e94560'
        )
        title.pack(pady=20)

        # Performans metrikleri
        metrics_frame = tk.Frame(self.right_frame, bg='#16213e')
        metrics_frame.pack(fill='both', expand=True, padx=20, pady=20)

        try:
            import psutil

            # CPU kullanımı
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_frame = tk.LabelFrame(metrics_frame, text=self.lm.tr('cpu_usage', "CPU Kullanımı"),
                                    font=('Segoe UI', 12, 'bold'), bg='#16213e', fg='#ffffff')
            cpu_frame.pack(fill='x', pady=10)

            cpu_label = tk.Label(cpu_frame, text=f"{cpu_percent:.1f}%",
                               font=('Segoe UI', 24, 'bold'), bg='#16213e', fg='#e94560')
            cpu_label.pack(pady=10)

            # RAM kullanımı
            memory = psutil.virtual_memory()
            ram_frame = tk.LabelFrame(metrics_frame, text=self.lm.tr('ram_usage', "RAM Kullanımı"),
                                    font=('Segoe UI', 12, 'bold'), bg='#16213e', fg='#ffffff')
            ram_frame.pack(fill='x', pady=10)

            ram_label = tk.Label(ram_frame, text=f"{memory.percent:.1f}%",
                               font=('Segoe UI', 24, 'bold'), bg='#16213e', fg='#e94560')
            ram_label.pack(pady=10)

            # Disk kullanımı
            disk = psutil.disk_usage(self.base_dir)
            disk_percent = (disk.used / disk.total) * 100

            disk_frame = tk.LabelFrame(metrics_frame, text=self.lm.tr('disk_usage', "Disk Kullanımı"),
                                     font=('Segoe UI', 12, 'bold'), bg='#16213e', fg='#ffffff')
            disk_frame.pack(fill='x', pady=10)

            disk_label = tk.Label(disk_frame, text=f"{disk_percent:.1f}%",
                                font=('Segoe UI', 24, 'bold'), bg='#16213e', fg='#e94560')
            disk_label.pack(pady=10)

        except ImportError:
            error_label = tk.Label(metrics_frame, text=self.lm.tr('psutil_missing_error', "psutil modülü eksik. Performans bilgileri alınamadı."),
                                 font=('Segoe UI', 12), bg='#16213e', fg='#e94560')
            error_label.pack(pady=50)

    def show_security(self):
        """Güvenlik ayarları"""
        self.clear_right_panel()

        title = tk.Label(
            self.right_frame,
            text=f" {self.lm.tr('security_settings_title', 'Güvenlik Ayarları')}",
            font=('Segoe UI', 16, 'bold'),
            bg='#16213e',
            fg='#e94560'
        )
        title.pack(pady=20)

        # Güvenlik araçları
        security_frame = tk.Frame(self.right_frame, bg='#16213e')
        security_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Şifre politikaları
        password_frame = tk.LabelFrame(security_frame, text=self.lm.tr('password_policies', "Şifre Politikaları"),
                                     font=('Segoe UI', 12, 'bold'), bg='#16213e', fg='#ffffff')
        password_frame.pack(fill='x', pady=10)

        password_buttons = [
            (f" {self.lm.tr('set_password_policies_btn', 'Şifre Politikalarını Ayarla')}", self.set_password_policies),
            (f" {self.lm.tr('check_weak_passwords_btn', 'Zayıf Şifreleri Kontrol Et')}", self.check_weak_passwords),
            (f" {self.lm.tr('clear_password_history_btn', 'Şifre Geçmişini Temizle')}", self.clear_password_history),
        ]

        for text, command in password_buttons:
            btn = tk.Button(
                password_frame,
                text=text,
                font=('Segoe UI', 10),
                bg='#0f3460',
                fg='#ffffff',
                activebackground='#e94560',
                command=command,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2'
            )
            btn.pack(side='left', padx=5, pady=5)

        # Erişim kontrolü
        access_frame = tk.LabelFrame(security_frame, text=self.lm.tr('access_control', "Erişim Kontrolü"),
                                   font=('Segoe UI', 12, 'bold'), bg='#16213e', fg='#ffffff')
        access_frame.pack(fill='x', pady=10)

        access_buttons = [
            (f" {self.lm.tr('check_failed_logins_btn', 'Başarısız Girişleri Kontrol Et')}", self.check_failed_logins),
            (f" {self.lm.tr('set_ip_restrictions_btn', 'IP Kısıtlamalarını Ayarla')}", self.set_ip_restrictions),
            (f" {self.lm.tr('set_session_timeouts_btn', 'Oturum Sürelerini Ayarla')}", self.set_session_timeouts),
        ]

        for text, command in access_buttons:
            btn = tk.Button(
                access_frame,
                text=text,
                font=('Segoe UI', 10),
                bg='#0f3460',
                fg='#ffffff',
                activebackground='#e94560',
                command=command,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2'
            )
            btn.pack(side='left', padx=5, pady=5)

    def set_password_policies(self):
        """Şifre politikalarını ayarla"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS security_settings (
                    id INTEGER PRIMARY KEY,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            def _get(key, default):
                try:
                    cursor.execute("SELECT setting_value FROM security_settings WHERE setting_key=?", (key,))
                    row = cursor.fetchone()
                    if row and row[0] is not None:
                        return row[0]
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
                return default

            defaults = {
                'pw_min_length': '10',
                'pw_require_upper': '1',
                'pw_require_lower': '1',
                'pw_require_digit': '1',
                'pw_require_special': '1',
                'pw_max_age_days': '90',
                'pw_history_count': '5',
                'lockout_max_attempts': '5',
                'lockout_window_minutes': '15',
                'lockout_duration_minutes': '30',
            }

            values = {k: _get(k, v) for k, v in defaults.items()}

            dialog = tk.Toplevel(self.parent)
            dialog.title(self.lm.tr('password_policies_title', "Şifre Politikaları"))
            dialog.geometry("520x520")
            dialog.grab_set()
            frm = tk.Frame(dialog, bg='white')
            frm.pack(fill='both', expand=True, padx=16, pady=16)

            tk.Label(frm, text=self.lm.tr('password_requirements_header', "Parola Zorunlu Kurallar"), font=('Segoe UI', 12, 'bold'), bg='white').pack(anchor='w', pady=(0, 10))

            # Min length
            min_len_frame = tk.Frame(frm, bg='white')
            min_len_frame.pack(fill='x', pady=6)
            tk.Label(min_len_frame, text=self.lm.tr('min_length', "Minimum uzunluk:"), bg='white').pack(side='left')
            min_len_var = tk.StringVar(value=str(values['pw_min_length']))
            tk.Entry(min_len_frame, textvariable=min_len_var, width=6).pack(side='left', padx=8)

            # Requirements
            req_frame = tk.Frame(frm, bg='white')
            req_frame.pack(fill='x', pady=6)
            upper_var = tk.BooleanVar(value=str(values['pw_require_upper']) == '1')
            lower_var = tk.BooleanVar(value=str(values['pw_require_lower']) == '1')
            digit_var = tk.BooleanVar(value=str(values['pw_require_digit']) == '1')
            special_var = tk.BooleanVar(value=str(values['pw_require_special']) == '1')
            tk.Checkbutton(req_frame, text=self.lm.tr('uppercase', "Büyük harf"), variable=upper_var, bg='white').pack(side='left')
            tk.Checkbutton(req_frame, text=self.lm.tr('lowercase', "Küçük harf"), variable=lower_var, bg='white').pack(side='left', padx=8)
            tk.Checkbutton(req_frame, text=self.lm.tr('digit', "Rakam"), variable=digit_var, bg='white').pack(side='left', padx=8)
            tk.Checkbutton(req_frame, text=self.lm.tr('special_char', "Özel karakter"), variable=special_var, bg='white').pack(side='left', padx=8)

            tk.Label(frm, text=self.lm.tr('policy_extra_settings', "Politika Ek Ayarları"), font=('Segoe UI', 12, 'bold'), bg='white').pack(anchor='w', pady=(16, 10))

            # Max age days
            age_frame = tk.Frame(frm, bg='white')
            age_frame.pack(fill='x', pady=6)
            tk.Label(age_frame, text=self.lm.tr('max_password_age', "Maks. şifre yaşı (gün):"), bg='white').pack(side='left')
            max_age_var = tk.StringVar(value=str(values['pw_max_age_days']))
            tk.Entry(age_frame, textvariable=max_age_var, width=6).pack(side='left', padx=8)

            # History count
            hist_frame = tk.Frame(frm, bg='white')
            hist_frame.pack(fill='x', pady=6)
            tk.Label(hist_frame, text=self.lm.tr('password_history_count', "Şifre geçmişi (adet):"), bg='white').pack(side='left')
            hist_var = tk.StringVar(value=str(values['pw_history_count']))
            tk.Entry(hist_frame, textvariable=hist_var, width=6).pack(side='left', padx=8)

            tk.Label(frm, text=self.lm.tr('lockout_settings', "Kilitlenme Ayarları"), font=('Segoe UI', 12, 'bold'), bg='white').pack(anchor='w', pady=(16, 10))

            # Lockout attempts
            att_frame = tk.Frame(frm, bg='white')
            att_frame.pack(fill='x', pady=6)
            tk.Label(att_frame, text=self.lm.tr('max_lockout_attempts', "Kilit için maksimum deneme:"), bg='white').pack(side='left')
            att_var = tk.StringVar(value=str(values['lockout_max_attempts']))
            tk.Entry(att_frame, textvariable=att_var, width=6).pack(side='left', padx=8)

            # Lockout window
            win_frame = tk.Frame(frm, bg='white')
            win_frame.pack(fill='x', pady=6)
            tk.Label(win_frame, text=self.lm.tr('attempt_window_min', "Deneme penceresi (dk):"), bg='white').pack(side='left')
            win_var = tk.StringVar(value=str(values['lockout_window_minutes']))
            tk.Entry(win_frame, textvariable=win_var, width=6).pack(side='left', padx=8)

            # Lockout duration
            dur_frame = tk.Frame(frm, bg='white')
            dur_frame.pack(fill='x', pady=6)
            tk.Label(dur_frame, text=self.lm.tr('lockout_duration_min', "Kilitlenme süresi (dk):"), bg='white').pack(side='left')
            dur_var = tk.StringVar(value=str(values['lockout_duration_minutes']))
            tk.Entry(dur_frame, textvariable=dur_var, width=6).pack(side='left', padx=8)

            def _save():
                try:
                    pairs = [
                        ('pw_min_length', str(min_len_var.get()).strip() or '10'),
                        ('pw_require_upper', '1' if upper_var.get() else '0'),
                        ('pw_require_lower', '1' if lower_var.get() else '0'),
                        ('pw_require_digit', '1' if digit_var.get() else '0'),
                        ('pw_require_special', '1' if special_var.get() else '0'),
                        ('pw_max_age_days', str(max_age_var.get()).strip() or '90'),
                        ('pw_history_count', str(hist_var.get()).strip() or '5'),
                        ('lockout_max_attempts', str(att_var.get()).strip() or '5'),
                        ('lockout_window_minutes', str(win_var.get()).strip() or '15'),
                        ('lockout_duration_minutes', str(dur_var.get()).strip() or '30'),
                    ]
                    for k, v in pairs:
                        cursor.execute(
                            "INSERT INTO security_settings(setting_key, setting_value) VALUES(?, ?) "
                            "ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value, updated_at=CURRENT_TIMESTAMP",
                            (k, v)
                        )
                    conn.commit()
                    messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('password_policies_saved', "Şifre politikaları kaydedildi."))
                except Exception as e:
                    messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('save_error', 'Kaydetme hatası')}: {e}")

            # Buttons
            btns = tk.Frame(frm, bg='white')
            btns.pack(fill='x', pady=16)
            tk.Button(btns, text=f" {self.lm.tr('btn_save', 'Kaydet')}", font=('Segoe UI', 10, 'bold'), bg='#27ae60', fg='white', relief='flat', padx=18, command=_save).pack(side='left')
            tk.Button(btns, text=f" {self.lm.tr('btn_close', 'Kapat')}", font=('Segoe UI', 10), bg='#95a5a6', fg='white', relief='flat', padx=18, command=dialog.destroy).pack(side='left', padx=8)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('password_policies_error', 'Şifre politikaları açılırken hata')}: {e}")

    def check_weak_passwords(self):
        """Zayıf şifreleri kontrol et"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Argon2 olmayan eski hash'leri bul
            cursor.execute("""
                SELECT username, password_hash FROM users 
                WHERE password_hash NOT LIKE 'argon2$%'
            """)
            weak_users = cursor.fetchall()
            conn.close()

            if weak_users:
                msg = self.lm.tr('weak_passwords_warning', "{count} kullanıcı eski hash formatı kullanıyor!\n\nBu kullanıcılar ilk girişte otomatik olarak Argon2'ye upgrade edilecek.\n\nKullanıcılar: {users}").format(
                    count=len(weak_users),
                    users=', '.join([u[0] for u in weak_users[:5]])
                )
                messagebox.showwarning(self.lm.tr('weak_passwords_title', "Zayıf Şifreler"), msg)
            else:
                messagebox.showinfo(self.lm.tr('safe_title', "Güvenli"), self.lm.tr('all_users_argon2_msg', "Tüm kullanıcılar Argon2 hash kullanıyor! Icons.SUCCESS"))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('check_error', 'Kontrol hatası')}: {e}")

    def clear_password_history(self):
        """Şifre geçmişini temizle"""
        confirm = messagebox.askyesno(self.lm.tr('confirm', "Onay"),
            self.lm.tr('clear_password_history_confirm', "Tüm kullanıcıların şifre geçmişini temizlemek istiyor musunuz?\n\nBu işlem geri alınamaz!"))

        if confirm:
            try:
                # Şifre geçmişi tablosu varsa temizle
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM password_history")
                deleted = cursor.rowcount
                conn.commit()
                conn.close()
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{deleted} {self.lm.tr('password_history_cleared_msg', 'şifre geçmişi kaydı temizlendi!')}")
            except Exception:
                messagebox.showinfo(self.lm.tr('info', "Bilgi"), self.lm.tr('password_history_empty_msg', "Şifre geçmişi tablosu yok veya boş."))

    def check_failed_logins(self):
        """Başarısız girişleri kontrol et"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Son 24 saatteki başarısız girişler
            cursor.execute("""
                SELECT username, ip_address, COUNT(*) as attempts, MAX(timestamp) as last_attempt
                FROM login_attempts
                WHERE success = 0 
                AND timestamp > datetime('now', '-1 day')
                GROUP BY username, ip_address
                HAVING attempts >= 3
                ORDER BY attempts DESC
                LIMIT 20
            """)

            failed = cursor.fetchall()
            conn.close()

            if failed:
                msg = self.lm.tr('suspicious_activity_msg_header', "Son 24 saatte {count} kullanıcıda şüpheli aktivite!\n\n").format(count=len(failed))
                for user, ip, attempts, last in failed[:5]:
                    msg += f"• {user} ({ip}): {attempts} {self.lm.tr('failed_attempts', 'başarısız deneme')}\n"
                messagebox.showwarning(self.lm.tr('suspicious_activity_title', "Şüpheli Aktivite"), msg)
            else:
                messagebox.showinfo(self.lm.tr('safe_title', "Güvenli"), self.lm.tr('no_suspicious_activity_msg', "Son 24 saatte şüpheli aktivite yok! Icons.SUCCESS"))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('check_error', 'Kontrol hatası')}: {e}")

    def set_ip_restrictions(self):
        """IP kısıtlamalarını ayarla"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS security_settings (
                    id INTEGER PRIMARY KEY,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            def _get(key, default):
                try:
                    cursor.execute("SELECT setting_value FROM security_settings WHERE setting_key=?", (key,))
                    row = cursor.fetchone()
                    if row and row[0] is not None:
                        return row[0]
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
                return default

            import json
            import re
            wl_raw = _get('ip_whitelist', '[]')
            bl_raw = _get('ip_blacklist', '[]')
            block_unknown_raw = _get('ip_block_unknown', '0')
            try:
                wl_list = json.loads(wl_raw)
            except Exception:
                wl_list = []
            try:
                bl_list = json.loads(bl_raw)
            except Exception:
                bl_list = []
            block_unknown_init = (str(block_unknown_raw) == '1')

            dialog = tk.Toplevel(self.parent)
            dialog.title(self.lm.tr('ip_restrictions_title', "IP Kısıtlamaları"))
            dialog.geometry("560x520")
            dialog.grab_set()
            frm = tk.Frame(dialog, bg='white')
            frm.pack(fill='both', expand=True, padx=16, pady=16)

            tk.Label(frm, text=self.lm.tr('whitelist_label', "Whitelist (izinli IP'ler)"), font=('Segoe UI', 12, 'bold'), bg='white').pack(anchor='w')
            wl_text = tk.Text(frm, height=8, font=('Segoe UI', 10))
            wl_text.pack(fill='x', pady=(6, 12))
            for ip in wl_list:
                wl_text.insert(tk.END, f"{ip}\n")

            tk.Label(frm, text=self.lm.tr('blacklist_label', "Blacklist (engelli IP'ler)"), font=('Segoe UI', 12, 'bold'), bg='white').pack(anchor='w')
            bl_text = tk.Text(frm, height=8, font=('Segoe UI', 10))
            bl_text.pack(fill='x', pady=(6, 12))
            for ip in bl_list:
                bl_text.insert(tk.END, f"{ip}\n")

            block_unknown_var = tk.BooleanVar(value=block_unknown_init)
            tk.Checkbutton(frm, text=self.lm.tr('block_unknown_label', "Bilinmeyen IP'leri otomatik engelle"), variable=block_unknown_var, bg='white').pack(anchor='w', pady=(4, 12))

            def _normalize(lines):
                return [l.strip() for l in lines if l.strip()]

            def _is_valid_ip(s: str) -> bool:
                if s == '*':
                    return True
                m = re.match(r"^(?:\d{1,3}\.){3}\d{1,3}(?:/(?:\d|[12]\d|3[0-2]))?$", s)
                if not m:
                    return False
                parts = s.split('/')[0].split('.')
                return all(0 <= int(p) <= 255 for p in parts)

            def _save():
                try:
                    wl_lines = wl_text.get('1.0', tk.END).splitlines()
                    bl_lines = bl_text.get('1.0', tk.END).splitlines()
                    wl = _normalize(wl_lines)
                    bl = _normalize(bl_lines)

                    for ip in wl + bl:
                        if not _is_valid_ip(ip):
                            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('invalid_ip_msg', 'Geçersiz IP/CIDR')}: {ip}")
                            return

                    pairs = [
                        ('ip_whitelist', json.dumps(wl, ensure_ascii=False)),
                        ('ip_blacklist', json.dumps(bl, ensure_ascii=False)),
                        ('ip_block_unknown', '1' if block_unknown_var.get() else '0'),
                    ]
                    for k, v in pairs:
                        cursor.execute(
                            "INSERT INTO security_settings(setting_key, setting_value) VALUES(?, ?) "
                            "ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value, updated_at=CURRENT_TIMESTAMP",
                            (k, v)
                        )
                    conn.commit()
                    messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('ip_restrictions_saved_msg', "IP kısıtlamaları kaydedildi."))
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('save_error', 'Kaydetme hatası')}: {e}")

            btns = tk.Frame(frm, bg='white')
            btns.pack(fill='x', pady=12)
            tk.Button(btns, text=f" {self.lm.tr('btn_save', 'Kaydet')}", font=('Segoe UI', 10, 'bold'), bg='#27ae60', fg='white', relief='flat', padx=18, command=_save).pack(side='left')
            tk.Button(btns, text=f" {self.lm.tr('btn_close', 'Kapat')}", font=('Segoe UI', 10), bg='#95a5a6', fg='white', relief='flat', padx=18, command=dialog.destroy).pack(side='left', padx=8)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('ip_restrictions_open_error', 'IP kısıtlamaları açılırken hata')}: {e}")

    def set_session_timeouts(self):
        """Oturum sürelerini ayarla"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS security_settings (
                    id INTEGER PRIMARY KEY,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            def _get(key, default):
                try:
                    cursor.execute("SELECT setting_value FROM security_settings WHERE setting_key=?", (key,))
                    row = cursor.fetchone()
                    if row and row[0] is not None:
                        return row[0]
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
                return default

            timeout_init = _get('session_timeout', '30')
            max_sess_init = _get('max_concurrent_sessions', '3')

            dialog = tk.Toplevel(self.parent)
            dialog.title(self.lm.tr('session_timeouts_title', "Oturum Süreleri"))
            dialog.geometry("420x300")
            dialog.grab_set()

            tk.Label(dialog, text=self.lm.tr('session_timeout_settings_title', "Oturum Timeout Ayarları"), font=('Segoe UI', 14, 'bold')).pack(pady=20)
            form = tk.Frame(dialog)
            form.pack(padx=30, pady=20)

            tk.Label(form, text=self.lm.tr('inactivity_timeout_label', "İnaktivite Timeout (dakika):"), font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', pady=10)
            timeout_entry = tk.Entry(form, font=('Segoe UI', 10), width=10)
            timeout_entry.insert(0, str(timeout_init))
            timeout_entry.grid(row=0, column=1, padx=10, pady=10)

            tk.Label(form, text=self.lm.tr('max_concurrent_sessions_label', "Max Concurrent Sessions:"), font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', pady=10)
            sessions_entry = tk.Entry(form, font=('Segoe UI', 10), width=10)
            sessions_entry.insert(0, str(max_sess_init))
            sessions_entry.grid(row=1, column=1, padx=10, pady=10)

            def save_settings():
                try:
                    timeout = int(timeout_entry.get())
                    max_sessions = int(sessions_entry.get())

                    pairs = [
                        ('session_timeout', str(timeout)),
                        ('max_concurrent_sessions', str(max_sessions)),
                    ]
                    for k, v in pairs:
                        cursor.execute(
                            "INSERT INTO security_settings(setting_key, setting_value) VALUES(?, ?) "
                            "ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value, updated_at=CURRENT_TIMESTAMP",
                            (k, v)
                        )
                    conn.commit()
                    messagebox.showinfo(self.lm.tr('saved_title', "Kaydedildi"), f"{self.lm.tr('session_settings_updated_msg', 'Oturum ayarları güncellendi!')}\n\nTimeout: {timeout} {self.lm.tr('minutes', 'dakika')}\nMax Sessions: {max_sessions}")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('save_error', 'Kaydetme hatası')}: {e}")

            tk.Button(dialog, text=f"{Icons.SAVE} {self.lm.tr('btn_save', 'Kaydet')}", font=('Segoe UI', 11, 'bold'), bg='#27ae60', fg='white', padx=30, pady=10, command=save_settings).pack(pady=20)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('session_settings_open_error', 'Oturum süresi ayarları açılırken hata')}: {e}")

