#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
"""
Kullanıcı Yetkilendirme GUI
Admin'in kullanıcılar için modül ve program yetkilerini yönetmesi
"""

import os
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Set

from utils.language_manager import LanguageManager
from config.database import DB_PATH


class UserPermissionsGUI:
    """Kullanıcı Yetkilendirme Arayüzü"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()
        # DB yolu: proje köküne göre mutlak ve ortam değişkeniyle override edilebilir
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            env_db = os.environ.get('SDG_DB_PATH')
            self.db_path = env_db if env_db else os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
        except Exception as e:
            logging.warning(f"Failed to determine DB path from environment/abspath, using default: {e}")
            self.db_path = DB_PATH
        self.selected_user_id = None
        self.selected_user_name = None

        # Modül izinleri yapısı
        self.module_permissions = {
            'General': {
                'name': self.lm.tr("module_general", 'Genel İzinler'),
                'permissions': [
                    'view', 'import', 'manage'
                ]
            },
            'Dijital Güvenlik': {
                'name': self.lm.tr("module_digital_security", 'Dijital Güvenlik'),
                'permissions': [
                    'view', 'edit', 'delete',
                    'export', 'import', 'manage'
                ]
            },
            'GRI': {
                'name': self.lm.tr("module_gri", 'GRI'),
                'permissions': [
                    'view', 'edit', 'delete', 'export'
                ]
            },
            'TSRS': {
                'name': self.lm.tr("module_tsrs", 'TSRS'),
                'permissions': [
                    'view', 'edit', 'delete', 'export', 'import'
                ]
            },
            'SDG': {
                'name': self.lm.tr("module_sdg", 'SDG'),
                'permissions': [
                    'view', 'edit', 'delete', 'export', 'import'
                ]
            },
            'ESG': {
                'name': self.lm.tr("module_esg", 'ESG'),
                'permissions': [
                    'view', 'edit', 'delete', 'export', 'import'
                ]
            },
            'SKDM': {
                'name': self.lm.tr("module_skdm", 'SKDM'),
                'permissions': [
                    'view', 'edit', 'delete', 'export'
                ]
            },
            'Raporlama': {
                'name': self.lm.tr("module_reporting", 'Raporlama'),
                'permissions': [
                    'view', 'edit', 'delete', 'export', 'import'
                ]
            },
            'Yönetim': {
                'name': self.lm.tr("module_management", 'Yönetim'),
                'permissions': [
                    'view', 'edit', 'delete', 'manage'
                ]
            },
            'Eşleştirme': {
                'name': self.lm.tr("module_matching", 'Eşleştirme'),
                'permissions': [
                    'view', 'edit', 'delete', 'export'
                ]
            },
            'Önceliklendirme': {
                'name': self.lm.tr("module_prioritization", 'Önceliklendirme'),
                'permissions': [
                    'view', 'edit', 'delete', 'export'
                ]
            },
            'Su Yönetimi': {
                'name': self.lm.tr("module_water_management", 'Su Yönetimi'),
                'permissions': [
                    'view', 'edit', 'delete', 'export', 'import'
                ]
            },
            'Atık Yönetimi': {
                'name': self.lm.tr("module_waste_management", 'Atık Yönetimi'),
                'permissions': [
                    'view', 'edit', 'delete', 'export', 'import'
                ]
            },
            'Tedarik Zinciri': {
                'name': self.lm.tr("module_supply_chain", 'Tedarik Zinciri'),
                'permissions': [
                    'view', 'edit', 'delete', 'export'
                ]
            }
        }

        self.permission_checkboxes = {}
        self.module_checkboxes = {}
        self.current_module = 'General'  # Aktif modül
        self._dirty = False

        self.setup_ui()
        self.load_users()

        self._module_prefix = {
            'General': 'dashboard',
            'Dijital Güvenlik': 'digital_security',
            'GRI': 'gri',
            'TSRS': 'tsrs',
            'SDG': 'sdg',
            'ESG': 'esg',
            'SKDM': 'skdm',
            'Raporlama': 'reporting',
            'Yönetim': 'management',
            'Eşleştirme': 'matching',
            'Önceliklendirme': 'prioritization',
            'Su Yönetimi': 'water_management',
            'Atık Yönetimi': 'waste_management',
            'Tedarik Zinciri': 'supply_chain'
        }
        self._action_tr_to_en = {
            'view': 'view',
            'edit': 'edit',
            'delete': 'delete',
            'export': 'export',
            'import': 'import',
            'manage': 'manage',
        }
        self._action_en_to_tr = {v: k for k, v in self._action_tr_to_en.items()}

    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=self.lm.tr("title_metric_permissions", "Metrik Yetkilendirmeleri"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)

        # İçerik alanı - iki panel yan yana
        content_frame = tk.Frame(main_frame, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Sağ panel - Modül izinleri (sola yanaştırıldı)
        self.setup_permissions_panel(content_frame)

        # Sol panel - Kullanıcı seçimi (sağa kaydırıldı)
        self.setup_user_panel(content_frame)

    def setup_user_panel(self, parent) -> None:
        """Sol panel - Kullanıcı listesi"""
        # Sol panel frame (eşit genişlik)
        right_panel = tk.Frame(parent, bg='#f8f9fa', width=400)
        right_panel.pack(side='left', fill='both', padx=(0, 0))
        right_panel.pack_propagate(False)

        # Panel başlığı
        user_title = tk.Label(right_panel, text=self.lm.tr("title_select_user", "Kullanıcı Seçin"),
                             font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='#f8f9fa')
        user_title.pack(pady=15)

        # Kullanıcı tablosu için frame
        table_frame = tk.Frame(right_panel, bg='#f8f9fa')
        table_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        # Treeview (tablo) oluştur
        columns = ('Kullanıcı', 'Rol')
        self.user_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)

        # Sütun ayarları
        self.user_tree.heading('Kullanıcı', text=self.lm.tr("col_user", 'Kullanıcı'))
        self.user_tree.heading('Rol', text=self.lm.tr("col_role", 'Rol'))
        self.user_tree.column('Kullanıcı', width=180, minwidth=150)
        self.user_tree.column('Rol', width=120, minwidth=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar.set)

        # Grid layout kullan (pack yerine)
        self.user_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Grid ağırlıkları
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Seçim eventi
        self.user_tree.bind('<<TreeviewSelect>>', self.on_user_select)

    def on_module_button_click(self, module_key) -> None:
        """Modül butonuna tıklandığında çalışır"""
        try:
            proceed = self._confirm_save_if_dirty()
            if not proceed:
                return
        except Exception as e:
            logging.error(f'Silent error in user_permissions_gui.py: {str(e)}')

        self.current_module = module_key

        # Tüm butonları normal duruma getir ve seçili olanı devre dışı bırakarak vurgula
        try:
            for key, btn in self.module_buttons.items():
                if key == module_key:
                    btn.state(['disabled'])
                else:
                    btn.state(['!disabled'])
        except Exception as e:
            logging.error(f'Silent error in user_permissions_gui.py: {str(e)}')

        # İlgili modülün izinlerini göster
        self.create_permission_checkboxes(module_key)

        # Eğer kullanıcı seçiliyse, o kullanıcının bu modüldeki izinlerini yükle
        if self.selected_user_id:
            self.load_user_permissions_for_module(self.selected_user_id, module_key)

    def setup_permissions_panel(self, parent) -> None:
        """Sağ panel - Modül izinleri"""
        # Sağ panel frame (eşit genişlik)
        left_panel = tk.Frame(parent, bg='white', width=560, height=520)
        left_panel.pack(side='right', fill='both', padx=(0, 0))
        left_panel.pack_propagate(False)

        # Panel başlığı
        perm_title = tk.Label(left_panel, text=self.lm.tr("title_module_permissions", "Modül İzinleri"),
                             font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white')
        perm_title.pack(pady=15)

        # Hızlı işlem ve kaydet butonları (üstte, görünür)
        button_frame = tk.Frame(left_panel, bg='white')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))

        # Tüm izinler butonu
        all_perm_btn = ttk.Button(button_frame, text=self.lm.tr("btn_all_permissions", " Tüm İzinler"), style='Menu.TButton',
                                  command=self.grant_all_permissions)
        all_perm_btn.pack(side='left', padx=(0, 10))

        # İzin yok butonu
        no_perm_btn = ttk.Button(button_frame, text=self.lm.tr("btn_no_permissions", " İzin Yok"), style='Menu.TButton',
                                 command=self.revoke_all_permissions)
        no_perm_btn.pack(side='left')

        # Kaydet/İptal butonlarını sağa hizala
        self.save_btn = ttk.Button(button_frame, text=self.lm.tr("btn_save", " Kaydet"), style='Menu.TButton',
                                   command=self.save_permissions)
        self.save_btn.pack(side='right', padx=(10, 0))

        cancel_btn = ttk.Button(button_frame, text=self.lm.tr("btn_cancel", " İptal"), style='Menu.TButton',
                                command=self.cancel_changes)
        cancel_btn.pack(side='right', padx=(10, 0))

        # Başlangıçta kaydet butonu pasif, kullanıcı seçilince aktif edilecek
        try:
            self.save_btn.configure(state='disabled')
        except Exception as e:
            logging.error(f'Silent error in user_permissions_gui.py: {str(e)}')

        # İzinler başlığı
        perm_subtitle = tk.Label(left_panel, text=self.lm.tr("subtitle_permissions", "İzinler"),
                                font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        perm_subtitle.pack(anchor='w', padx=20, pady=(10, 5))

        # Modül butonları - birbirine yapışık
        modules_strip_container = tk.Frame(left_panel, bg='white')
        modules_strip_container.pack(fill='x', padx=20, pady=(0, 8))

        # Modül butonları frame'i
        self.modules_frame = tk.Frame(modules_strip_container, bg='white')
        self.modules_frame.pack()

        # Modül butonları oluştur - birbirine yapışık
        self.module_buttons = {}
        for i, module_key in enumerate(self.module_permissions.keys()):
            name = self.module_permissions[module_key]['name']

            # İlk buton aktif (Genel İzinler)
            if i == 0:
                pass

            btn = ttk.Button(
                self.modules_frame,
                text=f" {name}",
                style='Menu.TButton',
                command=lambda key=module_key: self.on_module_button_click(key)
            )
            btn.pack(side='left', padx=4, pady=0)
            try:
                from utils.tooltip import add_tooltip
                add_tooltip(btn, self.lm.tr("tooltip_module_permissions", f"{name} modül izinleri").replace("{name}", name))
            except Exception as e:
                logging.error(f'Silent error in user_permissions_gui.py: {str(e)}')

            self.module_buttons[module_key] = btn

        # İzinler için canvas ve scrollbar
        self.permissions_canvas_frame = tk.Frame(left_panel, bg='white', height=380)
        self.permissions_canvas_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        self.permissions_canvas_frame.pack_propagate(False)

        # Canvas oluştur
        self.permissions_canvas = tk.Canvas(
            self.permissions_canvas_frame,
            bg='white',
            highlightthickness=0,
        )
        self.permissions_scrollbar = ttk.Scrollbar(
            self.permissions_canvas_frame,
            orient="vertical",
            command=self.permissions_canvas.yview,
        )
        try:
            self.permissions_scrollbar.configure(width=14)
        except Exception as e:
            logging.error(f'Silent error in user_permissions_gui.py: {str(e)}')

        self.permissions_scrollable_frame = tk.Frame(self.permissions_canvas, bg='white')

        self.permissions_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.permissions_canvas.configure(scrollregion=self.permissions_canvas.bbox("all"))
        )

        self.permissions_canvas.create_window((0, 0), window=self.permissions_scrollable_frame, anchor="nw")
        self.permissions_canvas.configure(yscrollcommand=self.permissions_scrollbar.set)

        # Pack
        self.permissions_canvas.pack(side="left", fill="both", expand=True)
        self.permissions_scrollbar.pack(side="right", fill="y")

        # Mouse wheel desteği
        def _on_mousewheel(event) -> None:
            try:
                self.permissions_canvas.yview_scroll(
                    int(-1*(event.delta/120)),
                    "units",
                )
            except Exception as e:
                logging.error(f'Silent error in user_permissions_gui.py: {str(e)}')
        self.permissions_canvas.bind("<MouseWheel>", _on_mousewheel)

        # İzinleri oluştur - ilk modül için
        self.active_module_button = None
        try:
            from utils.tooltip import add_tooltip
            add_tooltip(all_perm_btn, self.lm.tr("tooltip_grant_all", 'Tüm izinleri ver'))
            add_tooltip(no_perm_btn, self.lm.tr("tooltip_revoke_all", 'Tüm izinleri kaldır'))
            add_tooltip(self.save_btn, self.lm.tr("tooltip_save_changes", 'Değişiklikleri kaydet'))
            add_tooltip(cancel_btn, self.lm.tr("tooltip_cancel_changes", 'Değişiklikleri iptal et'))
        except Exception as e:
            logging.error(f'Silent error in user_permissions_gui.py: {str(e)}')
        # İlk modül seçili olsun
        first_key = next(iter(self.module_permissions.keys())) if self.module_permissions else None
        if first_key:
            self.on_module_button_click(first_key)
        else:
            self.create_permission_checkboxes('General')

        # Alt butonlar kaldırıldı; üstte görünecek şekilde hizalandı

    def create_permission_checkboxes(self, module_key) -> None:
        """Belirtilen modül için izin checkboxlarını oluştur"""
        # Önceki widget'ları temizle
        for widget in self.permissions_scrollable_frame.winfo_children():
            widget.destroy()

        # Yeni modül için checkbox'ları oluştur
        if module_key not in self.module_permissions:
            return

        module_info = self.module_permissions[module_key]
        row = 0

        # Modül ana checkbox'ı
        if module_key not in self.module_checkboxes:
            self.module_checkboxes[module_key] = {}

        module_var = tk.BooleanVar()
        module_checkbox = tk.Checkbutton(
            self.permissions_scrollable_frame,
            text=module_info['name'],
            variable=module_var,
            font=('Segoe UI', 11, 'bold'),
            bg='white',
            fg='#2c3e50',
            command=lambda m=module_key: self.on_module_check(m),
            cursor='hand2'
        )
        module_checkbox.grid(row=row, column=0, sticky='n', pady=(6, 2), padx=(0, 0))

        self.module_checkboxes[module_key] = {
            'var': module_var,
            'checkbox': module_checkbox
        }

        row += 1

        # Alt izinler
        if module_key not in self.permission_checkboxes:
            self.permission_checkboxes[module_key] = {}

        for permission in module_info['permissions']:
            perm_var = tk.BooleanVar()
            perm_checkbox = tk.Checkbutton(
                self.permissions_scrollable_frame,
                text=f"  {self.lm.tr(f'perm_{permission}', permission.capitalize())}",
                variable=perm_var,
                font=('Segoe UI', 10),
                bg='white',
                fg='#7f8c8d',
                command=lambda m=module_key: self.on_permission_check(m),
                cursor='hand2'
            )
            perm_checkbox.grid(row=row, column=0, sticky='w', pady=2, padx=(20, 0))

            # Tooltip
            try:
                from utils.tooltip import add_tooltip
                add_tooltip(perm_checkbox, self.lm.tr(f"tooltip_perm_{permission}", f"{permission} izni"))
            except Exception as e:
                logging.error(f'Silent error in user_permissions_gui.py: {str(e)}')

            self.permission_checkboxes[module_key][permission] = {
                'var': perm_var,
                'checkbox': perm_checkbox
            }

            row += 1

        # Canvas'ı güncelle
        self.permissions_canvas.configure(scrollregion=self.permissions_canvas.bbox("all"))

    def load_users(self) -> None:
        """Kullanıcıları yükle (şema-toleranslı)"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            try:
                cursor.execute("PRAGMA busy_timeout=5000")
            except Exception as e:
                logging.error(f'Silent error in user_permissions_gui.py: {str(e)}')
            # Kullanıcı tablosu kolonlarını al
            cursor.execute("PRAGMA table_info(users)")
            user_cols = [row[1] for row in cursor.fetchall()]
            has_is_active = 'is_active' in user_cols
            # Rol alanı ifadesini belirle
            if 'role_name' in user_cols:
                role_expr = 'u.role_name'
            elif 'role' in user_cols:
                role_expr = 'u.role'
            else:
                role_expr = (
                    "(SELECT r.name FROM roles r JOIN user_roles ur ON ur.role_id = r.id "
                    "WHERE ur.user_id = u.id LIMIT 1)"
                )
            query = f"""
                SELECT u.id,
                       u.username,
                       COALESCE(NULLIF(u.first_name,''),'') AS first_name,
                       COALESCE(NULLIF(u.last_name,''),'')  AS last_name,
                       {role_expr} AS role_name
                FROM users u
            """
            if has_is_active:
                query += " WHERE u.is_active = 1"
            query += " ORDER BY u.username"
            users = []
            try:
                cursor.execute(query)
                users = cursor.fetchall()
            except Exception:
                # Fallback: minimum alanlarla
                cursor.execute("SELECT id, username FROM users")
                users = [(row[0], row[1], None, None, None) for row in cursor.fetchall()]
            # Treeview'ı temizle
            for item in self.user_tree.get_children():
                self.user_tree.delete(item)
            # Kullanıcıları ekle
            for user_id, username, first_name, last_name, role_name in users:
                display_name = (f"{first_name} {last_name}".strip() if (first_name or last_name) else username)
                role_display = role_name if role_name else 'User'
                self.user_tree.insert('', 'end', values=(display_name, role_display), tags=(str(user_id),))
            logging.info(self.lm.tr("log_users_loaded", "Toplam {} kullanıcı yüklendi (DB: {})").format(len(users), self.db_path))
        except Exception as e:
            logging.error(self.lm.tr("log_users_load_error", "Kullanıcılar yüklenirken hata: {}").format(e))
            try:
                messagebox.showerror(self.lm.tr("msg_error", "Hata"), self.lm.tr("msg_error_loading_users", f"Kullanıcılar yüklenirken hata: {e}").replace("{e}", str(e)))
            except Exception as e:
                logging.error(f'Silent error in user_permissions_gui.py: {str(e)}')
        finally:
            try:
                conn.close()
            except Exception as e:
                logging.error(f'Silent error in user_permissions_gui.py: {str(e)}')

    def on_user_select(self, event) -> None:
        """Kullanıcı seçildiğinde"""
        try:
            proceed = self._confirm_save_if_dirty()
            if not proceed:
                return
        except Exception as e:
            logging.error(f'Silent error in user_permissions_gui.py: {str(e)}')
        selection = self.user_tree.selection()
        if not selection:
            return

        item = self.user_tree.item(selection[0])
        user_id = int(item['tags'][0])

        # Kullanıcı adını al
        values = item['values']
        username = values[0]

        self.selected_user_id = user_id
        self.selected_user_name = username

        # Kaydet butonunu etkinleştir
        try:
            self.save_btn.configure(state='normal')
        except Exception as e:
            logging.error(f'Silent error in user_permissions_gui.py: {str(e)}')

        # Bu kullanıcının izinlerini yükle (aktif modül için)
        self.load_user_permissions_for_module(user_id, self.current_module)

    def load_user_permissions_for_module(self, user_id, module_key) -> None:
        """Belirtilen modül için kullanıcının izinlerini yükle"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()

            try:
                cursor.execute("PRAGMA busy_timeout=5000")
            except Exception as e:
                logging.error(f'Silent error in user_permissions_gui.py: {str(e)}')

            # Rol bazlı izinleri al (user_roles: user_id, role_id; permissions: code)
            cursor.execute(
                """
                SELECT DISTINCT p.code 
                FROM user_roles ur
                JOIN role_permissions rp ON ur.role_id = rp.role_id
                JOIN permissions p ON rp.permission_id = p.id
                WHERE ur.user_id = ?
                """,
                (user_id,)
            )
            raw_codes = [row[0] for row in cursor.fetchall()]
            mapped = set()
            for code in raw_codes:
                if isinstance(code, str) and '.' in code:
                    prefix, action = code.split('.', 1)
                    for mk, pf in self._module_prefix.items():
                        if pf == prefix and action in self._action_en_to_tr:
                            mapped.add(f"{mk}.{self._action_en_to_tr[action]}")
                            break
            self.update_permission_checkboxes_for_module(mapped, module_key)

        except Exception as e:
            logging.error(self.lm.tr("log_user_permissions_load_error", "Kullanıcı izinleri yüklenirken hata: {}").format(e))
            messagebox.showerror(self.lm.tr("msg_error", "Hata"), self.lm.tr("msg_load_perm_error", f"Kullanıcı izinleri yüklenirken hata: {e}").replace("{e}", str(e)))
        finally:
            try:
                conn.close()
            except Exception as e:
                logging.error(f'Silent error in user_permissions_gui.py: {str(e)}')

    def load_user_permissions(self, user_id) -> None:
        """Kullanıcının tüm izinlerini yükle (eski fonksiyon - uyumluluk için)"""
        self.load_user_permissions_for_module(user_id, self.current_module)

    def update_permission_checkboxes_for_module(self, user_permissions: Set[str], module_key: str) -> None:
        """Belirtilen modülün izin checkboxlarını güncelle"""
        if module_key not in self.module_checkboxes:
            return

        module_info = self.module_permissions[module_key]

        # Modül ana checkbox'ı
        module_permissions = [f"{module_key}.{perm}" for perm in module_info['permissions']]
        module_has_all = all(perm in user_permissions for perm in module_permissions)

        self.module_checkboxes[module_key]['var'].set(module_has_all)

        # Alt izinler
        for permission in module_info['permissions']:
            permission_key = f"{module_key}.{permission}"
            has_permission = permission_key in user_permissions

            if (module_key in self.permission_checkboxes and
                permission in self.permission_checkboxes[module_key]):
                self.permission_checkboxes[module_key][permission]['var'].set(has_permission)

    def update_permission_checkboxes(self, user_permissions: Set[str]) -> None:
        """Tüm modüllerin izin checkboxlarını güncelle (eski fonksiyon - uyumluluk için)"""
        self.update_permission_checkboxes_for_module(user_permissions, self.current_module)

    def on_module_check(self, module_key) -> None:
        """Modül checkbox'ı değiştiğinde"""
        is_checked = self.module_checkboxes[module_key]['var'].get()

        # Tüm alt izinleri güncelle
        if module_key in self.permission_checkboxes:
            for permission, checkbox_info in self.permission_checkboxes[module_key].items():
                checkbox_info['var'].set(is_checked)
        self._dirty = True

    def on_permission_check(self, module_key) -> None:
        """İzin checkbox'ı değiştiğinde"""
        # Modül checkbox'ını kontrol et
        if module_key in self.permission_checkboxes:
            all_checked = all(
                checkbox_info['var'].get()
                for checkbox_info in self.permission_checkboxes[module_key].values()
            )

            self.module_checkboxes[module_key]['var'].set(all_checked)
        self._dirty = True

    def grant_all_permissions(self) -> None:
        """Aktif modülün tüm izinlerini ver"""
        if self.current_module in self.module_checkboxes:
            self.module_checkboxes[self.current_module]['var'].set(True)
            self.on_module_check(self.current_module)
        self._dirty = True

    def revoke_all_permissions(self) -> None:
        """Aktif modülün tüm izinlerini kaldır"""
        if self.current_module in self.module_checkboxes:
            self.module_checkboxes[self.current_module]['var'].set(False)
            self.on_module_check(self.current_module)
        self._dirty = True

    def get_current_permissions(self) -> Set[str]:
        """Mevcut checkbox durumlarından izinleri al (sadece aktif modül)"""
        permissions = set()

        # Sadece aktif modülün izinlerini al
        module_key = self.current_module
        if module_key in self.permission_checkboxes:
            module_info = self.module_permissions[module_key]
            for permission in module_info['permissions']:
                if (permission in self.permission_checkboxes[module_key] and
                    self.permission_checkboxes[module_key][permission]['var'].get()):
                    perm_name = f"{module_key}.{permission}"
                    permissions.add(perm_name)

        return permissions

    def save_permissions(self) -> None:
        """İzinleri kaydet"""
        if not self.selected_user_id:
            messagebox.showwarning(self.lm.tr("msg_warning", "Uyarı"), self.lm.tr("msg_select_user_first", "Lütfen önce bir kullanıcı seçin."))
            return

        try:
            # Veritabanı bağlantısını aç
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()

            try:
                # Veritabanı ayarları
                cursor.execute("PRAGMA busy_timeout=10000")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
            except Exception as e:
                logging.error(f'Silent error in user_permissions_gui.py: {str(e)}')

            # Mevcut izinleri al
            current_permissions = self.get_current_permissions()
            logging.debug(f"DEBUG: Seçilen izinler: {current_permissions}")
            logging.debug(f"DEBUG: Kullanıcı ID: {self.selected_user_id}")
            logging.debug(f"DEBUG: Kullanıcı Adı: {self.selected_user_name}")

            # Özel rol oluştur veya güncelle
            custom_role_name = f"Custom_{self.selected_user_id}"

            # Önce özel rolü kontrol et
            cursor.execute("SELECT id FROM roles WHERE name = ?", (custom_role_name,))
            custom_role = cursor.fetchone()

            if custom_role:
                custom_role_id = custom_role[0]
                prefix = self._module_prefix.get(self.current_module)
                if prefix:
                    cursor.execute(
                        """
                        DELETE FROM role_permissions 
                        WHERE role_id = ? AND permission_id IN (
                            SELECT id FROM permissions WHERE module = ?
                        )
                        """,
                        (custom_role_id, prefix)
                    )
            else:
                # Yeni özel rol oluştur
                cursor.execute("""
                    INSERT INTO roles (name)
                    VALUES (?)
                """, (custom_role_name,))
                custom_role_id = cursor.lastrowid

            for permission in current_permissions:
                if '.' not in permission:
                    continue
                mk, tr = permission.split('.', 1)
                prefix = self._module_prefix.get(mk)
                action_en = self._action_tr_to_en.get(tr)
                if not prefix or not action_en:
                    continue
                code = f"{prefix}.{action_en}"
                cursor.execute("SELECT id FROM permissions WHERE code = ?", (code,))
                perm = cursor.fetchone()
                if not perm:
                    try:
                        cursor.execute("PRAGMA table_info(permissions)")
                        cols = [r[1] for r in cursor.fetchall()]
                        if 'code' in cols:
                            cursor.execute(
                                """
                                INSERT OR IGNORE INTO permissions (code, name, display_name, module, action, resource, is_active)
                                VALUES (?, ?, ?, ?, ?, ?, 1)
                                """,
                                (code, code.replace('.', '_'), code, prefix, action_en, prefix,)
                            )
                    except Exception as e:
                        logging.error(f'Silent error in user_permissions_gui.py: {str(e)}')
                    cursor.execute("SELECT id FROM permissions WHERE code = ?", (code,))
                    perm = cursor.fetchone()
                if perm:
                    permission_id = perm[0]
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                        VALUES (?, ?)
                        """,
                        (custom_role_id, permission_id)
                    )

            # Kullanıcının mevcut özel rol atamasını kontrol et
            cursor.execute("""
                SELECT 1 FROM user_roles 
                WHERE user_id = ? AND role_id = ?
            """, (self.selected_user_id, custom_role_id))

            existing_assignment = cursor.fetchone()

            if not existing_assignment:
                # Özel rol atamasını ekle
                cursor.execute("""
                    INSERT INTO user_roles (user_id, role_id)
                    VALUES (?, ?)
                """, (self.selected_user_id, custom_role_id))

            # Diğer rollerin kaldırılması: sadece özel rol kalsın
            cursor.execute("""
                DELETE FROM user_roles 
                WHERE user_id = ? AND role_id != ?
            """, (self.selected_user_id, custom_role_id))

            # Değişiklikleri kaydet
            conn.commit()
            messagebox.showinfo(self.lm.tr("msg_success", "Başarılı"), self.lm.tr("msg_permissions_saved_success", f"{self.selected_user_name} kullanıcısının izinleri başarıyla kaydedildi.").replace("{user}", str(self.selected_user_name)))
            try:
                self.load_user_permissions_for_module(self.selected_user_id, self.current_module)
            except Exception as e:
                logging.error(f'Silent error in user_permissions_gui.py: {str(e)}')
            self._dirty = False

        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                messagebox.showerror(self.lm.tr("msg_error", "Hata"), self.lm.tr("msg_db_locked", "Veritabanı kilitli. Lütfen birkaç saniye bekleyip tekrar deneyin."))
            else:
                messagebox.showerror(self.lm.tr("msg_error", "Hata"), self.lm.tr("msg_db_error", f"Veritabanı hatası: {e}").replace("{e}", str(e)))
        except Exception as e:
            logging.error(self.lm.tr("log_permissions_save_error", "İzinler kaydedilirken hata: {}").format(e))
            messagebox.showerror(self.lm.tr("msg_error", "Hata"), self.lm.tr("msg_error_saving_permissions", f"İzinler kaydedilirken hata: {e}").replace("{e}", str(e)))
        finally:
            # Bağlantıyı kapat
            try:
                conn.close()
            except Exception as e:
                logging.error(f'Silent error in user_permissions_gui.py: {str(e)}')

    def cancel_changes(self) -> None:
        """Değişiklikleri iptal et"""
        if self.selected_user_id:
            self.load_user_permissions_for_module(self.selected_user_id, self.current_module)
            messagebox.showinfo(self.lm.tr("msg_cancelled", "İptal"), self.lm.tr("msg_changes_cancelled", "Değişiklikler iptal edildi."))
            self._dirty = False
        else:
            # Aktif modülün checkboxlarını temizle
            if self.current_module in self.module_checkboxes:
                self.module_checkboxes[self.current_module]['var'].set(False)
                self.on_module_check(self.current_module)
                self._dirty = False

    def _confirm_save_if_dirty(self) -> bool:
        """Kaydedilmemiş değişiklikler varsa kullanıcıdan onay al"""
        if self._dirty and self.selected_user_id:
            try:
                res = messagebox.askyesnocancel(
                    self.lm.tr("msg_warning", "Uyarı"),
                    self.lm.tr("msg_unsaved_changes", "Kaydedilmemiş değişiklikler var.\nKaydetmek ister misiniz?")
                )
            except Exception:
                # askyesnocancel yoksa askyesno kullan
                res = messagebox.askyesno(
                    self.lm.tr("msg_warning", "Uyarı"),
                    self.lm.tr("msg_unsaved_changes", "Kaydedilmemiş değişiklikler var.\nKaydetmek ister misiniz?")
                )
                # askyesno: True=Kaydet, False=Devam (kaydetme)
                if res:
                    self.save_permissions()
                    return True
                else:
                    self._dirty = False
                    return True

            # askyesnocancel: True=Kaydet, False=Devam (kaydetme), None=İptal
            if res is True:
                self.save_permissions()
                return True
            if res is False:
                self._dirty = False
                return True
            return False
        return True
