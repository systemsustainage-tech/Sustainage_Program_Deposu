#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kullanıcı Yönetimi GUI
Kullanıcı, rol, yetki ve departman yönetimi arayüzü
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk

from utils.tooltip import bind_treeview_header_tooltips

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from typing import Any, Dict, Optional

from modules.security.advanced_security_gui import AdvancedSecurityGUI
from tasks.task_manager import TaskManager
from utils.phone import format_tr_phone, is_valid_tr_phone
from utils.ui_theme import apply_theme
from yonetim.kullanici_yonetimi.models.user_manager import UserManager
from yonetim.kullanici_yonetimi.secure_user_create import generate_temp_password
from config.icons import Icons

try:
    from security.core.secure_password import PasswordPolicy as GlobalPasswordPolicy
except Exception:
    GlobalPasswordPolicy = None


class UserManagementGUI:
    """Kullanıcı Yönetimi GUI"""

    def __init__(self, parent, current_user_id: int = 1) -> None:
        self.parent = parent
        self.current_user_id = current_user_id
        self.lm = LanguageManager()
        self.user_manager = UserManager()

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Kullanıcı yönetimi arayüzünü oluştur"""
        # Ana frame
        apply_theme(self.parent)
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#2F6DB2', height=32)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=self.lm.tr("user_management_title", "Kullanıcı Yönetimi"), font=('Segoe UI', 12, 'bold'), fg='white', bg='#2F6DB2')
        title_label.pack(side='left', padx=12)

        # Ana içerik - Notebook (Sekmeler)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Kullanıcılar sekmesi
        self.users_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.users_frame, text=self.lm.tr("tab_users", " Kullanıcılar"))

        # Roller sekmesi
        self.roles_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.roles_frame, text=self.lm.tr("tab_roles", " Roller"))

        # Departmanlar sekmesi
        self.departments_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.departments_frame, text=self.lm.tr("tab_departments", " Departmanlar"))

        # İstatistikler sekmesi
        self.statistics_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.statistics_frame, text=self.lm.tr("tab_statistics", " İstatistikler"))

        # Audit Log sekmesi
        self.audit_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.audit_frame, text=self.lm.tr("tab_audit_log", " Audit Log"))

        # Sekmeleri oluştur
        self.create_users_tab()
        self.create_roles_tab()
        self.create_departments_tab()
        self.create_statistics_tab()
        self.create_audit_tab()

    def create_users_tab(self) -> None:
        """Kullanıcılar sekmesi - sade görünüm"""
        container = tk.Frame(self.users_frame, bg='#f5f5f5')
        container.pack(fill='both', expand=True, padx=15, pady=15)

        # Araç çubuğu
        toolbar = tk.Frame(container, bg='white', relief='flat', bd=0)
        toolbar.pack(fill='x', pady=(0, 15))

        search_frame = tk.Frame(toolbar, bg='white')
        search_frame.pack(side='left', padx=10, pady=10)
        tk.Label(search_frame, text=self.lm.tr("lbl_search", "Ara:"), bg='white', font=('Segoe UI', 10, 'bold')).pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=(6, 10))
        search_entry.bind('<KeyRelease>', self.on_search_change)

        # Filtreler
        self.dept_var = tk.StringVar(value=self.lm.tr("filter_all", "Tümü"))
        self.status_var = tk.StringVar(value=self.lm.tr("filter_all", "Tümü"))

        self.dept_combo = ttk.Combobox(toolbar, textvariable=self.dept_var, state='readonly', width=20)
        self.dept_combo.pack(side='left', padx=5, pady=10)
        self.dept_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

        status_values = [
            self.lm.tr("filter_all", "Tümü"),
            self.lm.tr("status_active", "Aktif"),
            self.lm.tr("status_passive", "Pasif")
        ]
        self.status_combo = ttk.Combobox(
            toolbar,
            textvariable=self.status_var,
            state='readonly',
            values=status_values,
            width=12
        )
        self.status_combo.pack(side='left', padx=5, pady=10)
        self.status_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

        ttk.Button(toolbar, text=self.lm.tr("btn_clear_filters", "Filtreleri Temizle"), command=self.clear_filters).pack(side='left', padx=5)

        self.action_buttons = {}

        # Seçim gerektiren butonları devre dışı bırak
        for key in ('edit', 'assign', 'delete', 'reset'):
            try:
                self.action_buttons[key].state(['disabled'])
            except Exception as e:
                logging.error(f'Silent error in user_management_gui.py: {str(e)}')

        # Liste ve detay alanı
        paned = ttk.Panedwindow(container, orient='horizontal')
        paned.pack(fill='both', expand=True)

        left_menu = tk.Frame(paned, bg='white', relief='solid', bd=1)
        list_panel = tk.Frame(paned, bg='white', relief='solid', bd=1)
        detail_panel = tk.Frame(paned, bg='white', relief='solid', bd=1)
        paned.add(left_menu, weight=1)
        paned.add(list_panel, weight=6)
        paned.add(detail_panel, weight=4)

        tk.Label(left_menu, text=self.lm.tr("lbl_actions", "Eylemler"), font=('Segoe UI', 11, 'bold'), bg='white').pack(anchor='w', padx=10, pady=(10,4))

        def _add_action(key, text, command):
            btn = ttk.Button(left_menu, text=text, style='Menu.TButton', command=command)
            btn.pack(fill='x', padx=10, pady=6)
            self.action_buttons[key] = btn

        _add_action('new', self.lm.tr("btn_new_user", f"{Icons.ADD} Yeni Kullanıcı"), self.create_user)
        _add_action('edit', self.lm.tr("btn_edit", f"{Icons.EDIT} Düzenle"), self.edit_user)
        _add_action('assign', self.lm.tr("btn_assign_task", "📌 Görev Ata"), self.assign_task_to_user)
        _add_action('delete', self.lm.tr("btn_delete", f"{Icons.DELETE} Sil"), self.delete_user)
        _add_action('reset', self.lm.tr("btn_reset_password", f"{Icons.KEY} Şifre Sıfırla"), self.reset_password_for_user)
        _add_action('refresh', self.lm.tr("btn_refresh", f"{Icons.LOADING} Yenile"), self.refresh_users)

        tk.Label(list_panel, text=self.lm.tr("tab_users", "Kullanıcılar"), font=('Segoe UI', 12, 'bold'), bg='white').pack(anchor='w', padx=15, pady=(15, 5))

        columns = ('username', 'name', 'email', 'department', 'roles', 'status')
        self.user_table = ttk.Treeview(list_panel, columns=columns, show='headings', selectmode='browse', height=18)
        headings = {
            'username': self.lm.tr("col_username", "Kullanıcı Adı"),
            'name': self.lm.tr("col_full_name", "Ad Soyad"),
            'email': self.lm.tr("col_email", "E-posta"),
            'department': self.lm.tr("col_department", "Departman"),
            'roles': self.lm.tr("col_roles", "Roller"),
            'status': self.lm.tr("col_status", "Durum")
        }

        for col, label in headings.items():
            self.user_table.heading(col, text=label)
            self.user_table.column(col, anchor='w', width=140 if col != 'email' else 200)

        list_scroll = ttk.Scrollbar(list_panel, orient='vertical', command=self.user_table.yview)
        self.user_table.configure(yscrollcommand=list_scroll.set)
        self.user_table.pack(side='left', fill='both', expand=True, padx=(15, 0), pady=(0, 15))
        list_scroll.pack(side='right', fill='y', padx=(0, 15), pady=(0, 15))
        self.user_table.bind('<<TreeviewSelect>>', self.on_user_select)

        # Detay kartı
        detail_header = tk.Frame(detail_panel, bg='#2F6DB2', height=44)
        detail_header.pack(fill='x')
        detail_header.pack_propagate(False)
        tk.Label(detail_header, text=self.lm.tr("lbl_user_details", "Kullanıcı Detayları"), font=('Segoe UI', 13, 'bold'), fg='white', bg='#2F6DB2').pack(padx=10)

        detail_body = tk.Frame(detail_panel, bg='white')
        detail_body.pack(fill='both', expand=True, padx=20, pady=20)

        self.detail_vars = {
            'full_name': tk.StringVar(value="-"),
            'username': tk.StringVar(value="-"),
            'email': tk.StringVar(value="-"),
            'department': tk.StringVar(value="-"),
            'roles': tk.StringVar(value="-"),
            'status': tk.StringVar(value="-"),
            'phone': tk.StringVar(value="-")
        }

        for label, var in self.detail_vars.items():
            row = tk.Frame(detail_body, bg='white')
            row.pack(fill='x', pady=6)
            tk.Label(row, text=f"{label.replace('_',' ').title()}:", font=('Segoe UI', 11, 'bold'), bg='white', width=16, anchor='w').pack(side='left')
            ttk.Label(row, textvariable=var, style='Muted.TLabel').pack(side='left', padx=8)

        self.detail_note = tk.Label(
            detail_body,
            text=self.lm.tr("msg_view_details_hint", "Bir kullanıcı seçerek detayları görüntüleyin."),
            font=('Segoe UI', 10),
            fg='#7f8c8d',
            bg='white',
            wraplength=360,
            justify='left'
        )
        self.detail_note.pack(fill='x', pady=(15, 0))

        self.user_cache = {}
        self.selected_user_id = None

    def create_roles_tab(self) -> None:
        """Roller sekmesi"""
        content_frame = tk.Frame(self.roles_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        title_frame = tk.Frame(content_frame, bg='#2F6DB2', height=50)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        ttk.Label(title_frame, text=self.lm.tr("lbl_role_management", " Rol ve Yetki Yönetimi"), style='Header.TLabel').pack(expand=True)

        # Ana içerik - iki panel yan yana
        main_content = tk.Frame(content_frame, bg='white')
        main_content.pack(fill='both', expand=True)

        # Sol panel - Roller
        left_panel = tk.Frame(main_content, bg='white', relief='solid', bd=1)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # Rol başlığı
        role_header = tk.Frame(left_panel, bg='#2F6DB2', height=40)
        role_header.pack(fill='x')
        role_header.pack_propagate(False)

        ttk.Label(role_header, text=self.lm.tr("lbl_roles", "Roller"), style='Section.TLabel').pack(expand=True)

        # Rol işlem butonları
        role_buttons = tk.Frame(left_panel, bg='white')
        role_buttons.pack(fill='x', padx=10, pady=10)

        new_btn = ttk.Button(role_buttons, text=self.lm.tr("btn_new_role", " Yeni Rol"), style='Menu.TButton',
                             command=self.create_role)
        new_btn.pack(side='left', padx=(0, 6))
        edit_btn = ttk.Button(role_buttons, text=self.lm.tr("btn_edit_role", " Düzenle"), style='Menu.TButton',
                              command=self.edit_role)
        edit_btn.pack(side='left', padx=6)
        del_btn = ttk.Button(role_buttons, text=self.lm.tr("btn_delete_role", " Sil"), style='Menu.TButton',
                             command=self.delete_role)
        del_btn.pack(side='left', padx=6)
        ref_btn = ttk.Button(role_buttons, text=self.lm.tr("btn_refresh", " Yenile"), style='Menu.TButton',
                             command=self.load_roles)
        ref_btn.pack(side='right')
        try:
            from utils.tooltip import add_tooltip
            add_tooltip(new_btn, self.lm.tr("btn_new_role", 'Yeni rol ekle'))
            add_tooltip(edit_btn, self.lm.tr("btn_edit_role", 'Seçili rolü düzenle'))
            add_tooltip(del_btn, self.lm.tr("btn_delete_role", 'Seçili rolü sil'))
            add_tooltip(ref_btn, self.lm.tr("btn_refresh", 'Rol listesini yenile'))
        except Exception as e:
            import logging
            logging.debug(f"Tooltip setup failed: {e}")
            pass

        # Rol listesi
        self.role_tree = ttk.Treeview(left_panel, columns=('name', 'users', 'permissions', 'description'),
                                     show='headings', height=12, style='Custom.Treeview')

        self.role_tree.heading('name', text=self.lm.tr("col_role_name", 'Rol Adı'))
        self.role_tree.heading('users', text=self.lm.tr("col_user_count", 'Kullanıcı'))
        self.role_tree.heading('permissions', text=self.lm.tr("col_permissions", 'Yetki'))
        self.role_tree.heading('description', text=self.lm.tr("col_description", 'Açıklama'))

        self.role_tree.column('name', width=120)
        self.role_tree.column('users', width=60)
        self.role_tree.column('permissions', width=60)
        self.role_tree.column('description', width=150)

        self.role_tree.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Rol seçim eventi
        self.role_tree.bind('<<TreeviewSelect>>', self.on_role_select)

        # Sağ panel - Rol Detayları ve Yetkiler
        right_panel = tk.Frame(main_content, bg='white', relief='solid', bd=1)
        right_panel.pack(side='right', fill='both', expand=True)

        # Rol detayları başlığı
        detail_header = tk.Frame(right_panel, bg='#2F6DB2', height=40)
        detail_header.pack(fill='x')
        detail_header.pack_propagate(False)

        ttk.Label(detail_header, text=self.lm.tr("lbl_role_details", "Rol Detayları"), style='Section.TLabel').pack(expand=True)

        # Sağ panel: solda kullanıcı isim listesi, sağda detaylar
        paned = ttk.Panedwindow(right_panel, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=20, pady=20)

        names_frame = tk.Frame(paned, bg='white', relief='solid', bd=1)
        details_outer = tk.Frame(paned, bg='white')
        paned.add(names_frame)
        paned.add(details_outer)
        try:
            paned.paneconfigure(names_frame, weight=1, minsize=240)
            paned.paneconfigure(details_outer, weight=3, minsize=360)
        except Exception as e:
            import logging
            logging.warning(f"Pane configuration failed: {e}")
            pass

        # Kullanıcı isimleri listesi
        ttk.Label(names_frame, text=self.lm.tr("lbl_users", "Kullanıcılar"), style='Section.TLabel').pack(fill='x')
        names_list_container = tk.Frame(names_frame, bg='white')
        names_list_container.pack(fill='both', expand=True)
        self.side_user_tree = ttk.Treeview(names_list_container, columns=('username','name'), show='headings', height=12, style='Custom.Treeview')
        self.side_user_tree.heading('username', text=self.lm.tr("col_username", 'Kullanıcı Adı'))
        self.side_user_tree.heading('name', text=self.lm.tr("col_full_name", 'Ad Soyad'))
        self.side_user_tree.column('username', width=140)
        self.side_user_tree.column('name', width=160)
        side_scroll = ttk.Scrollbar(names_list_container, orient='vertical', command=self.side_user_tree.yview)
        self.side_user_tree.configure(yscrollcommand=side_scroll.set)
        self.side_user_tree.pack(side='left', fill='both', expand=True)
        side_scroll.pack(side='right', fill='y')
        self.side_user_tree.bind('<<TreeviewSelect>>', self.on_side_user_select)

        # Detay içeriği - Scrollable (standart helper)
        from utils.ui_theme import create_scrollable
        _canvas, _inner, _scroll = create_scrollable(details_outer, bg='white')
        self.detail_canvas = _canvas
        self.scrollable_detail_frame = _inner
        # Varsayılan mesaj
        self.detail_label = ttk.Label(self.scrollable_detail_frame, text=self.lm.tr("msg_select_user_details", "Bir kullanıcı seçin"), style='Muted.TLabel')
        self.detail_label.pack(expand=True, padx=12, pady=12)

        # Yetkiler bölümü - Sistem Yetkileri listesi
        permission_section = tk.Frame(right_panel, bg='white', relief='solid', bd=1)
        permission_section.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        perm_header = tk.Frame(permission_section, bg='#2F6DB2', height=36)
        perm_header.pack(fill='x')
        perm_header.pack_propagate(False)

        ttk.Label(perm_header, text=self.lm.tr("lbl_system_permissions", "Sistem Yetkileri"), style='Section.TLabel').pack(side='left', padx=10)

        ttk.Button(perm_header, text=self.lm.tr("btn_refresh", " Yenile"), style='Menu.TButton', command=self.load_permissions).pack(side='right', padx=10)

        # Yetki listesi ağacı
        perm_list_frame = tk.Frame(permission_section, bg='white')
        perm_list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.permission_tree = ttk.Treeview(perm_list_frame,
                                            columns=('name', 'module', 'action'),
                                            show='headings', height=10, style='Custom.Treeview')
        self.permission_tree.heading('name', text=self.lm.tr("col_permission_name", 'Yetki Adı'))
        self.permission_tree.heading('module', text=self.lm.tr("col_module", 'Modül'))
        self.permission_tree.heading('action', text=self.lm.tr("col_action", 'Eylem'))

        self.permission_tree.column('name', width=180)
        self.permission_tree.column('module', width=120)
        self.permission_tree.column('action', width=120)

        perm_scrollbar = ttk.Scrollbar(perm_list_frame, orient='vertical', command=self.permission_tree.yview)
        self.permission_tree.configure(yscrollcommand=perm_scrollbar.set)

        self.permission_tree.pack(side='left', fill='both', expand=True)
        perm_scrollbar.pack(side='right', fill='y')

        # Seçili rol ID'si
        self.selected_role_id: Optional[int] = None

        # Butonlar
        role_btn_frame = tk.Frame(content_frame, bg='white')
        role_btn_frame.pack(fill='x', pady=10)

        ttk.Button(role_btn_frame, text=self.lm.tr("btn_new_role", " Yeni Rol"), style='Menu.TButton', command=self.create_role).pack(side='left', padx=5)

        ttk.Button(role_btn_frame, text=self.lm.tr("btn_role_edit_long", " Rol Düzenle"), style='Menu.TButton', command=self.edit_role).pack(side='left', padx=5)

    def create_departments_tab(self) -> None:
        """Departmanlar sekmesi"""
        content_frame = tk.Frame(self.departments_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        ttk.Label(content_frame, text=self.lm.tr("lbl_department_management", "Departman Yönetimi"), style='Header.TLabel').pack(pady=(0, 20))

        # Departman listesi
        dept_frame = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
        dept_frame.pack(fill='both', expand=True)

        ttk.Label(dept_frame, text=self.lm.tr("lbl_departments", "Departmanlar"), style='Section.TLabel').pack(pady=10)

        # Departman ağacı
        columns = ('name', 'code', 'users', 'manager')
        self.dept_tree = ttk.Treeview(dept_frame, columns=columns, show='headings', height=12, style='Custom.Treeview')

        self.dept_tree.heading('name', text=self.lm.tr("col_department_name", 'Departman Adı'))
        self.dept_tree.heading('code', text=self.lm.tr("col_code", 'Kod'))
        self.dept_tree.heading('users', text=self.lm.tr("col_dept_user_count", 'Kullanıcı Sayısı'))
        self.dept_tree.heading('manager', text=self.lm.tr("col_manager", 'Müdür'))

        self.dept_tree.column('name', width=200)
        self.dept_tree.column('code', width=80)
        self.dept_tree.column('users', width=100)
        self.dept_tree.column('manager', width=150)

        self.dept_tree.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Butonlar
        dept_btn_frame = tk.Frame(content_frame, bg='white')
        dept_btn_frame.pack(fill='x', pady=10)

        ttk.Button(dept_btn_frame, text=self.lm.tr("btn_new_department", " Yeni Departman"), style='Menu.TButton', command=self.create_department).pack(side='left', padx=5)

        ttk.Button(dept_btn_frame, text=self.lm.tr("btn_edit_department", " Departman Düzenle"), style='Menu.TButton', command=self.edit_department).pack(side='left', padx=5)

    def create_statistics_tab(self) -> None:
        """İstatistikler sekmesi"""
        content_frame = tk.Frame(self.statistics_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        ttk.Label(content_frame, text=self.lm.tr("lbl_user_statistics", "Kullanıcı İstatistikleri"), style='Header.TLabel').pack(pady=(0, 20))

        # İstatistik kartları
        stats_frame = tk.Frame(content_frame, bg='white')
        stats_frame.pack(fill='x', pady=20)

        self.stats_labels = {}

        stats_data = [
            (self.lm.tr("lbl_total_users", "Toplam Kullanıcı"), "total_users", "#3498db"),
            (self.lm.tr("lbl_active_users", "Aktif Kullanıcı"), "active_users", "#2ecc71"),
            (self.lm.tr("lbl_verified_users", "Doğrulanmış"), "verified_users", "#f39c12"),
            (self.lm.tr("lbl_total_departments", "Departman"), "total_departments", "#e74c3c")
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

        # Departman istatistikleri
        dept_stats_frame = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        dept_stats_frame.pack(fill='both', expand=True, pady=20)

        ttk.Label(dept_stats_frame, text=self.lm.tr("lbl_dept_user_counts", "Departman Bazlı Kullanıcı Sayıları"), style='Section.TLabel').pack(pady=10)

        self.dept_stats_tree = ttk.Treeview(dept_stats_frame, columns=('department', 'count'),
                                           show='headings', height=8, style='Custom.Treeview')
        self.dept_stats_tree.heading('department', text=self.lm.tr("col_department_name", 'Departman'))
        self.dept_stats_tree.heading('count', text=self.lm.tr("col_count", 'Kullanıcı Sayısı'))

        self.dept_stats_tree.column('department', width=200)
        self.dept_stats_tree.column('count', width=100)

        dept_stats_scrollbar = ttk.Scrollbar(dept_stats_frame, orient="vertical",
                                            command=self.dept_stats_tree.yview)
        self.dept_stats_tree.configure(yscrollcommand=dept_stats_scrollbar.set)

        self.dept_stats_tree.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        dept_stats_scrollbar.pack(side='right', fill='y', pady=(0, 10))

        # Rol istatistikleri
        role_stats_frame = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        role_stats_frame.pack(fill='both', expand=True, pady=(0, 20))

        ttk.Label(role_stats_frame, text=self.lm.tr("lbl_role_user_counts", "Rol Bazlı Kullanıcı Sayıları"), style='Section.TLabel').pack(pady=10)

        self.role_stats_tree = ttk.Treeview(role_stats_frame, columns=('role', 'count'),
                                           show='headings', height=8, style='Custom.Treeview')
        self.role_stats_tree.heading('role', text=self.lm.tr("col_role", 'Rol'))
        self.role_stats_tree.heading('count', text=self.lm.tr("col_count", 'Kullanıcı Sayısı'))

        self.role_stats_tree.column('role', width=200)
        self.role_stats_tree.column('count', width=100)

        role_stats_scrollbar = ttk.Scrollbar(role_stats_frame, orient="vertical",
                                            command=self.role_stats_tree.yview)
        self.role_stats_tree.configure(yscrollcommand=role_stats_scrollbar.set)

        self.role_stats_tree.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        role_stats_scrollbar.pack(side='right', fill='y', pady=(0, 10))

    def create_audit_tab(self) -> None:
        """Audit Log sekmesi"""
        content_frame = tk.Frame(self.audit_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        ttk.Label(content_frame, text=self.lm.tr("lbl_audit_log_title", "Audit Log - Sistem Aktivite Geçmişi"), style='Header.TLabel').pack(pady=(0, 20))

        # Filtreler
        filter_frame = tk.Frame(content_frame, bg='white')
        filter_frame.pack(fill='x', pady=10)

        tk.Label(filter_frame, text=self.lm.tr("lbl_filters", "Filtreler:"),
                font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w')

        filter_content = tk.Frame(filter_frame, bg='white')
        filter_content.pack(fill='x', pady=5)

        # Kullanıcı filtresi
        tk.Label(filter_content, text=self.lm.tr("lbl_filter_user", "Kullanıcı:"), bg='white').pack(side='left')
        self.audit_user_var = tk.StringVar()
        audit_user_combo = ttk.Combobox(filter_content, textvariable=self.audit_user_var,
                                       state='readonly', width=15)
        audit_user_combo.pack(side='left', padx=(5, 10))

        # İşlem filtresi
        tk.Label(filter_content, text=self.lm.tr("lbl_filter_action", "İşlem:"), bg='white').pack(side='left')
        self.audit_action_var = tk.StringVar()
        audit_action_combo = ttk.Combobox(filter_content, textvariable=self.audit_action_var,
                                         values=["create", "update", "delete", "login", "logout"],
                                         state='readonly', width=15)
        audit_action_combo.pack(side='left', padx=(5, 10))

        # Kaynak filtresi
        tk.Label(filter_content, text=self.lm.tr("lbl_filter_resource", "Kaynak:"), bg='white').pack(side='left')
        self.audit_resource_var = tk.StringVar()
        audit_resource_combo = ttk.Combobox(filter_content, textvariable=self.audit_resource_var,
                                           values=["user", "role", "permission", "department"],
                                           state='readonly', width=15)
        audit_resource_combo.pack(side='left', padx=(5, 10))

        # Filtrele butonu
        filter_btn = ttk.Button(filter_content, text=self.lm.tr("btn_filter", " Filtrele"), style='Menu.TButton', command=self.filter_audit_logs)
        filter_btn.pack(side='left', padx=(10, 0))

        # Audit log listesi
        audit_frame = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
        audit_frame.pack(fill='both', expand=True, pady=10)

        ttk.Label(audit_frame, text=self.lm.tr("lbl_audit_log_records", "Audit Log Kayıtları"), style='Section.TLabel').pack(pady=10)

        # Audit log ağacı
        columns = ('timestamp', 'user', 'action', 'resource', 'details')
        self.audit_tree = ttk.Treeview(audit_frame, columns=columns, show='headings', height=15, style='Custom.Treeview')

        self.audit_tree.heading('timestamp', text=self.lm.tr("col_timestamp", 'Tarih/Saat'))
        self.audit_tree.heading('user', text=self.lm.tr("col_user", 'Kullanıcı'))
        self.audit_tree.heading('action', text=self.lm.tr("col_action_audit", 'İşlem'))
        self.audit_tree.heading('resource', text=self.lm.tr("col_resource", 'Kaynak'))
        self.audit_tree.heading('details', text=self.lm.tr("col_details", 'Detaylar'))

        self.audit_tree.column('timestamp', width=120)
        self.audit_tree.column('user', width=100)
        self.audit_tree.column('action', width=80)
        self.audit_tree.column('resource', width=100)
        self.audit_tree.column('details', width=200)

        # Scrollbar
        audit_scrollbar = ttk.Scrollbar(audit_frame, orient="vertical", command=self.audit_tree.yview)
        self.audit_tree.configure(yscrollcommand=audit_scrollbar.set)

        self.audit_tree.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        audit_scrollbar.pack(side='right', fill='y', pady=(0, 10))

        try:
            bind_treeview_header_tooltips(self.audit_tree)
        except Exception as e:
            logging.error(f'Silent error in user_management_gui.py: {str(e)}')

    def load_data(self) -> None:
        """Verileri yükle"""
        self.load_users()
        self.load_departments()
        self.load_roles()
        self.load_permissions()
        self.load_statistics()
        self.load_audit_logs()

    def load_users(self) -> None:
        """Kullanıcıları yükle"""
        if not hasattr(self, 'user_table'):
            return

        for item in self.user_table.get_children():
            self.user_table.delete(item)
        self.user_cache = {}
        self.selected_user_id = None
        self._set_user_actions_state(False)
        try:
            for var in self.detail_vars.values():
                var.set("-")
            self.detail_note.configure(text=self.lm.tr("msg_view_details_hint", "Bir kullanıcı seçerek detayları görüntüleyin."))
        except Exception as e:
            logging.error(f'Silent error in user_management_gui.py: {str(e)}')

        try:
            self.user_table.tag_configure('even', background='#f9fbff')
            self.user_table.tag_configure('odd', background='#ffffff')
        except Exception as e:
            logging.error(f'Silent error in user_management_gui.py: {str(e)}')

        try:
            # Filtreleri uygula
            filters: Dict[str, Any] = {}
            if self.search_var.get():
                filters['search'] = self.search_var.get()
            if self.dept_var.get() and self.dept_var.get() != self.lm.tr("filter_all", "Tümü"):
                filters['department'] = self.dept_var.get()
            if self.status_var.get() == self.lm.tr("status_active", "Aktif"):
                filters['is_active'] = True
            elif self.status_var.get() == self.lm.tr("status_passive", "Pasif"):
                filters['is_active'] = False

            users = self.user_manager.get_users(filters)
            if not users:
                self.user_table.insert('', 'end', values=(
                    self.lm.tr("msg_no_users_registered", "Kayıtlı kullanıcı yok"),
                    '',
                    '',
                    '',
                    '',
                    ''
                ), iid='empty')
                return

            row_index = 0
            for user in users:
                # Gizli super admin'i gizle
                if user['username'] == '__super__':
                    continue

                status = self.lm.tr("status_active", "Aktif") if user['is_active'] else self.lm.tr("status_passive", "Pasif")
                name = f"{user['first_name']} {user['last_name']}"

                self.user_cache[user['id']] = user
                stripe_tag = 'even' if (row_index % 2 == 0) else 'odd'
                self.user_table.insert('', 'end', iid=str(user['id']), values=(
                    user['username'],
                    name,
                    user['email'],
                    user['department'] or '',
                    user['roles'] or '',
                    status
                ), tags=(str(user['id']), stripe_tag))
                row_index += 1

        except Exception as e:
            logging.error(self.lm.tr("err_users_load", "Kullanıcılar yüklenirken hata: {}").format(e))

    def load_departments(self) -> None:
        """Departmanları yükle"""
        try:
            departments = self.user_manager.get_departments()

            # Departman combo için
            dept_names = [self.lm.tr("filter_all", "Tümü")] + [dept['name'] for dept in departments]
            self.dept_combo['values'] = dept_names

            # Departman sekmesi için
            for item in self.dept_tree.get_children():
                self.dept_tree.delete(item)

            for dept in departments:
                self.dept_tree.insert('', 'end', values=(
                    dept['name'],
                    dept['code'],
                    dept['user_count'],
                    dept.get('manager_name', '') or ''
                ), tags=(str(dept['id']),))

        except Exception as e:
            logging.error(self.lm.tr("err_departments_load", "Departmanlar yüklenirken hata: {}").format(e))

    # removed duplicate load_roles

    def load_permissions(self) -> None:
        """Yetkileri yükle"""
        for item in self.permission_tree.get_children():
            self.permission_tree.delete(item)

        try:
            permissions = self.user_manager.get_permissions()

            for permission in permissions:
                self.permission_tree.insert('', 'end', values=(
                    permission['display_name'],
                    permission['module'],
                    permission['action']
                ))

        except Exception as e:
            logging.error(self.lm.tr("err_permissions_load", "Yetkiler yüklenirken hata: {}").format(e))

    def load_statistics(self) -> None:
        """İstatistikleri yükle"""
        try:
            stats = self.user_manager.get_user_statistics()

            # Ana istatistikler
            self.stats_labels['total_users'].config(text=str(stats.get('total_users', 0)))
            self.stats_labels['active_users'].config(text=str(stats.get('active_users', 0)))
            self.stats_labels['verified_users'].config(text=str(stats.get('verified_users', 0)))
            self.stats_labels['total_departments'].config(text=str(len(stats.get('department_stats', {}))))

            # Departman istatistikleri
            for item in self.dept_stats_tree.get_children():
                self.dept_stats_tree.delete(item)

            department_stats = stats.get('department_stats', {})
            for department, count in department_stats.items():
                self.dept_stats_tree.insert('', 'end', values=(department, count))

            # Rol istatistikleri
            for item in self.role_stats_tree.get_children():
                self.role_stats_tree.delete(item)

            role_stats = stats.get('role_stats', {})
            for role, count in role_stats.items():
                self.role_stats_tree.insert('', 'end', values=(role, count))

        except Exception as e:
            logging.error(f"İstatistikler yüklenirken hata: {e}")

    def load_audit_logs(self) -> None:
        """Audit logları yükle"""
        for item in self.audit_tree.get_children():
            self.audit_tree.delete(item)

        try:
            logs = self.user_manager.get_audit_logs(limit=100)

            for log in logs:
                user_name = f"{log.get('first_name', '')} {log.get('last_name', '')}".strip() or log.get('username', self.lm.tr("user_system", 'Sistem'))
                timestamp = log['created_at'][:19] if log['created_at'] else ''
                
                action = log['action']
                localized_action = self.lm.tr(f"action_{action}", action)
                
                resource_type = log['resource_type']
                localized_resource = self.lm.tr(f"resource_{resource_type}", resource_type)

                self.audit_tree.insert('', 'end', values=(
                    timestamp,
                    user_name,
                    localized_action,
                    localized_resource,
                    f"ID: {log['resource_id']}" if log['resource_id'] else ''
                ))

        except Exception as e:
            logging.error(self.lm.tr("err_audit_logs_load", "Audit loglar yüklenirken hata: {}").format(e))

    def on_user_select(self, event) -> None:
        """Kullanıcı seçildiğinde"""
        user_id = self.get_selected_user_id()
        if user_id:
            self.show_user_details(user_id)

    def on_side_user_select(self, event) -> None:
        """Eski kullanıcı listesi seçimleri için geriye dönük uyumluluk"""
        try:
            tree = getattr(self, 'side_user_tree', None)
            if not tree:
                return
            selection = tree.selection()
            if not selection:
                return
            item = tree.item(selection[0])
            tags = item.get('tags')
            if not tags:
                return
            tag0 = tags[0]
            if not str(tag0).isdigit():
                return
            self.show_user_details(int(tag0))
        except Exception as e:
            logging.error(f'Silent error in user_management_gui.py: {str(e)}')

    def on_search_change(self, event) -> None:
        """Arama değiştiğinde"""
        self.load_users()

    def on_filter_change(self, event) -> None:
        """Filtre değiştiğinde"""
        self.load_users()

    def clear_filters(self) -> None:
        """Filtreleri temizle"""
        self.search_var.set("")
        self.dept_var.set(self.lm.tr("filter_all", "Tümü"))
        self.status_var.set(self.lm.tr("filter_all", "Tümü"))
        self.load_users()

    def show_user_details(self, user_id: int) -> None:
        """Kullanıcı detaylarını göster"""
        try:
            user = self.user_cache.get(user_id) or self.user_manager.get_user_by_id(user_id)
            if not user:
                return
            self.selected_user_id = user_id
            self.detail_vars['full_name'].set(f"{user.get('first_name','')} {user.get('last_name','')}".strip() or "-")
            self.detail_vars['username'].set(user.get('username', '-'))
            self.detail_vars['email'].set(user.get('email', '-'))
            self.detail_vars['department'].set(user.get('department', '-') or '-')
            
            # Rolleri localize et
            roles_display = user.get('roles') or self.lm.tr("msg_no_role_assigned", 'Rol atanmadı')
            if user.get('role_keys'):
                role_keys = user['role_keys'].split(',')
                localized_roles = []
                for rk in role_keys:
                    rk = rk.strip()
                    if rk:
                        localized_roles.append(self.lm.tr(f"role_{rk}", rk))
                if localized_roles:
                    roles_display = ", ".join(localized_roles)
            
            self.detail_vars['roles'].set(roles_display)
            self.detail_vars['status'].set(self.lm.tr("status_active", "Aktif") if user.get('is_active') else self.lm.tr("status_passive", "Pasif"))
            self.detail_vars['phone'].set(user.get('phone', '-') or '-')
            note = user.get('notes') or f"{self.lm.tr('msg_last_login', 'Son giriş:')} {user.get('last_login', self.lm.tr('msg_unspecified', 'Belirtilmemiş'))}"
            self.detail_note.configure(text=note)
            self._set_user_actions_state(True)
        except Exception as e:
            logging.error(f"Kullanıcı detayları gösterilirken hata: {e}")

    def create_user(self) -> None:
        """Yeni kullanıcı oluştur"""
        self.show_user_form()

    def edit_user(self) -> None:
        """Kullanıcı düzenle"""
        user_id = self.get_selected_user_id()
        if not user_id:
            messagebox.showwarning(self.lm.tr("title_warning", "Uyarı"), self.lm.tr("msg_select_user_to_edit", "Lütfen düzenlemek istediğiniz kullanıcıyı seçin."))
            return
        self.show_user_form(user_id)

    def delete_user(self) -> None:
        """Kullanıcı sil"""
        user_id = self.get_selected_user_id()
        username = 'kullanıcı'
        if user_id and self.user_cache.get(user_id):
            username = self.user_cache[user_id].get('username', username)
        if not user_id:
            messagebox.showwarning(self.lm.tr("title_warning", "Uyarı"), self.lm.tr("msg_select_user_to_delete", "Lütfen silmek istediğiniz kullanıcıyı seçin."))
            return
        try:
            target_user = self.user_cache.get(user_id) or self.user_manager.get_user_by_id(user_id)
            roles_str = str((target_user or {}).get('roles') or '')
            roles = [r.strip().lower() for r in roles_str.split(',') if r]
            if ('admin' in roles) and (not self._current_is_super_admin()):
                messagebox.showerror(self.lm.tr("title_access_denied", "Erişim Reddedildi"), self.lm.tr("msg_admin_delete_restriction", "Admin kullanıcısını silme yetkiniz yok. Bu işlem sadece Süper Admin tarafından yapılabilir."))
                return
        except Exception as e:
            logging.error(f'Silent error in user_management_gui.py: {str(e)}')

        if messagebox.askyesno(self.lm.tr("title_delete_user", "Kullanıcı Sil"), self.lm.tr("msg_delete_user_confirm", f"'{username}' kullanıcısını KALICI olarak silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz!").replace("{username}", username)):
            try:
                # Kullanıcıyı kalıcı olarak sil
                success = self.user_manager.permanent_delete_user(user_id, self.current_user_id)
                if success:
                    messagebox.showinfo(self.lm.tr("title_success", "Başarılı"), self.lm.tr("msg_user_deleted", "Kullanıcı kalıcı olarak silindi."))
                    self.refresh_users()
                else:
                    messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_user_delete_failed", "Kullanıcı silinemedi."))
            except Exception as e:
                messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('msg_user_delete_error', 'Kullanıcı silinirken hata oluştu:')} {e}")
                logging.error(self.lm.tr("log_delete_user_error", "Kullanıcı silme hatası: {}").format(e))

    def _current_is_super_admin(self) -> bool:
        try:
            u = self.user_manager.get_user_by_id(int(self.current_user_id))
            if not u:
                return False
            if str(u.get('username') or '') == '__super__':
                return True
            roles_str = str(u.get('roles') or '')
            roles = [r.strip().lower() for r in roles_str.split(',') if r]
            return 'super_admin' in roles
        except Exception:
            return False

    def get_selected_user_id(self) -> Optional[int]:
        """Seçili kullanıcı ID'sini döndür"""
        try:
            if hasattr(self, 'user_table'):
                selection = self.user_table.selection()
                if selection:
                    item = selection[0]
                    try:
                        tags = self.user_table.item(item, 'tags')
                    except Exception:
                        tags = ()
                    if tags:
                        tag0 = tags[0]
                        if str(tag0).isdigit():
                            return int(tag0)
                    if str(item).isdigit():
                        return int(item)
        except Exception:
            return None
        return None

    def assign_task_to_user(self) -> None:
        user_id = self.get_selected_user_id()
        if not user_id:
            messagebox.showwarning(self.lm.tr("title_warning", "Uyarı"), self.lm.tr("msg_select_user_for_task", "Lütfen görev atamak istediğiniz kullanıcıyı seçin."))
            return
        user = self.user_cache.get(user_id) or self.user_manager.get_user_by_id(user_id)
        if not user:
            messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_user_not_found", "Kullanıcı bulunamadı."))
            return
        win = tk.Toplevel(self.parent)
        win.title(self.lm.tr("title_assign_task", "Görev Ata"))
        win.geometry("520x420")
        win.configure(bg='white')
        header = tk.Frame(win, bg='#2F6DB2', height=48)
        header.pack(fill='x')
        header.pack_propagate(False)
        ttk.Label(header, text=f"{self.lm.tr('lbl_assign_task_header', ' Görev Atama: ')}{user.get('username','')}", style='Header.TLabel').pack(padx=10)
        content = tk.Frame(win, bg='white')
        content.pack(fill='both', expand=True, padx=16, pady=16)
        tk.Label(content, text=self.lm.tr("lbl_title", "Başlık:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w')
        title_entry = tk.Entry(content, font=('Segoe UI', 10), width=50, relief='solid', bd=1)
        title_entry.pack(pady=(0, 10))
        tk.Label(content, text=self.lm.tr("lbl_description", "Açıklama:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w')
        desc_text = tk.Text(content, font=('Segoe UI', 10), height=5, width=50, relief='solid', bd=1)
        desc_text.pack(pady=(0, 10))
        tk.Label(content, text=self.lm.tr("lbl_priority", "Öncelik:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w')
        priority_var = tk.StringVar(value=self.lm.tr("priority_medium", 'Orta'))
        priority_combo = ttk.Combobox(content, textvariable=priority_var, state='readonly', 
                                      values=[self.lm.tr("priority_high", 'Yüksek'), self.lm.tr("priority_medium", 'Orta'), self.lm.tr("priority_low", 'Düşük')], width=20)
        priority_combo.pack(pady=(0, 10))
        tk.Label(content, text=self.lm.tr("lbl_due_date", "Son Tarih (YYYY-MM-DD):"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w')
        due_entry = tk.Entry(content, font=('Segoe UI', 10), width=20, relief='solid', bd=1)
        due_entry.pack(pady=(0, 10))
        btns = tk.Frame(content, bg='white')
        btns.pack(fill='x', pady=(10,0))
        def _save_task() -> None:
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_task_title_required", "Görev başlığı zorunludur."))
                return
            description = desc_text.get('1.0','end').strip()
            priority = priority_var.get()
            due_date = due_entry.get().strip() or None
            try:
                tm = TaskManager()
                task_id = tm.create_task(1, title, description, priority, due_date, self.current_user_id, user_id)
                if task_id > 0:
                    messagebox.showinfo(self.lm.tr("title_success", "Başarılı"), self.lm.tr("msg_task_created", "Görev oluşturuldu ve kullanıcıya atandı."))
                    win.destroy()
                else:
                    messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_task_creation_failed", "Görev oluşturulamadı."))
            except Exception as e:
                messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('msg_task_creation_error', 'Görev oluşturulurken hata:')} {e}")
        ttk.Button(btns, text=self.lm.tr("btn_create", " Oluştur"), style='Primary.TButton', command=_save_task).pack(side='left', padx=(0,8))
        ttk.Button(btns, text=self.lm.tr("btn_cancel", " İptal"), style='TButton', command=win.destroy).pack(side='left')

    def reset_password_for_user(self) -> None:
        user_id = self.get_selected_user_id()
        if not user_id:
            messagebox.showwarning(self.lm.tr("title_warning", "Uyarı"), self.lm.tr("msg_select_user_for_password_reset", "Lütfen şifresini sıfırlamak istediğiniz kullanıcıyı seçin."))
            return
        user = self.user_cache.get(user_id) or self.user_manager.get_user_by_id(user_id)
        if not user:
            messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_user_not_found", "Kullanıcı bulunamadı."))
            return
        username = user.get('username') or ''
        win = tk.Toplevel(self.parent)
        win.title(self.lm.tr("title_reset_password", "Şifre Sıfırla"))
        win.geometry("480x240")
        win.configure(bg='white')
        header = tk.Frame(win, bg='#2F6DB2', height=44)
        header.pack(fill='x')
        header.pack_propagate(False)
        ttk.Label(header, text=f"{self.lm.tr('lbl_reset_password_header', ' Şifre Sıfırla: ')}{username}", style='Header.TLabel').pack(padx=10)
        content = tk.Frame(win, bg='white')
        content.pack(fill='both', expand=True, padx=16, pady=16)
        tk.Label(content, text=self.lm.tr("lbl_new_password", "Yeni Şifre:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w')
        pw_row = tk.Frame(content, bg='white')
        pw_row.pack(fill='x')
        pw_entry = tk.Entry(pw_row, font=('Segoe UI', 10), width=32, show='*', relief='solid', bd=1)
        pw_entry.pack(side='left')
        def _gen() -> None:
            pwd = generate_temp_password(14)
            pw_entry.delete(0, tk.END)
            pw_entry.insert(0, pwd)
            try:
                win.clipboard_clear()
                win.clipboard_append(pwd)
            except Exception as e:
                logging.error(f'Silent error in user_management_gui.py: {str(e)}')
        ttk.Button(pw_row, text=self.lm.tr("btn_generate_password", " Şifre Oluştur"), style='Menu.TButton', command=_gen).pack(side='left', padx=8)
        btns = tk.Frame(content, bg='white')
        btns.pack(fill='x', pady=(12,0))
        def _apply() -> None:
            pwd = str(pw_entry.get()).strip()
            if not pwd:
                pwd = generate_temp_password(14)
            if GlobalPasswordPolicy is not None:
                ok, _ = GlobalPasswordPolicy.validate(pwd)
                if not ok:
                    messagebox.showwarning(self.lm.tr("title_warning", "Uyarı"), self.lm.tr("msg_password_policy_fail", "Şifre politikası kriterleri karşılanmıyor. Otomatik güçlü şifre kullanılacak."))
                    for _ in range(5):
                        candidate = generate_temp_password(14)
                        ok2, _ = GlobalPasswordPolicy.validate(candidate)
                        if ok2:
                            pwd = candidate
                            break
            else:
                specials = "!@#$%^&*"
                if (
                    len(pwd) < 12 or
                    not any(c.isupper() for c in pwd) or
                    not any(c.islower() for c in pwd) or
                    not any(c.isdigit() for c in pwd) or
                    not any(c in specials for c in pwd)
                ):
                    messagebox.showwarning(self.lm.tr("title_warning", "Uyarı"), self.lm.tr("msg_password_policy_fail", "Şifre politikası kriterleri karşılanmıyor. Otomatik güçlü şifre kullanılacak."))
                    pwd = generate_temp_password(14)
            try:
                ok = self.user_manager.update_user_password(username, pwd, self.current_user_id)
                if ok:
                    try:
                        win.clipboard_clear()
                        win.clipboard_append(pwd)
                    except Exception as e:
                        logging.error(f'Silent error in user_management_gui.py: {str(e)}')
                    messagebox.showinfo(self.lm.tr("title_success", "Başarılı"), self.lm.tr("msg_password_updated", "Şifre güncellendi. Şifre panoya kopyalandı."))
                    win.destroy()
                else:
                    messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_password_update_failed", "Şifre güncellenemedi."))
            except Exception as e:
                messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('msg_password_update_error', 'Şifre güncellenirken hata:')} {e}")
        ttk.Button(btns, text=self.lm.tr("btn_apply", " Uygula"), style='Primary.TButton', command=_apply).pack(side='left', padx=(0,8))
        ttk.Button(btns, text=self.lm.tr("btn_cancel", " İptal"), style='TButton', command=win.destroy).pack(side='left')

    def _set_user_actions_state(self, enabled: bool) -> None:
        """Seçime göre eylem butonlarını aç/kapat"""
        state = '!disabled' if enabled else 'disabled'
        for key in ('edit', 'assign', 'delete', 'reset'):
            btn = self.action_buttons.get(key)
            if btn:
                btn.state([state])

    def refresh_users(self) -> None:
        """Kullanıcıları yenile"""
        self.load_users()
        self.load_statistics()
        self._set_user_actions_state(False)

    def show_user_form(self, user_id=None) -> None:
        """Kullanıcı formu göster"""
        # Yeni pencere oluştur
        form_window = tk.Toplevel(self.parent)
        form_window.title(self.lm.tr("title_new_user", "Yeni Kullanıcı") if not user_id else self.lm.tr("title_edit_user", "Kullanıcı Düzenle"))
        form_window.geometry("500x700")
        form_window.configure(bg='white')
        form_window.resizable(True, True)

        # Başlık
        title = tk.Label(form_window, text=self.lm.tr("lbl_new_user", "Yeni Kullanıcı") if not user_id else self.lm.tr("lbl_edit_user", "Kullanıcı Düzenle"),
                        font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='white')
        title.pack(pady=20)

        # Ana container
        main_container = tk.Frame(form_window, bg='white')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Scrollable frame
        canvas = tk.Canvas(main_container, bg='white')
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Canvas ve scrollbar'ı pack et
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Form frame
        form_frame = tk.Frame(scrollable_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Mouse wheel desteği ekle
        def _on_mousewheel(event) -> None:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def bind_to_mousewheel(event) -> None:
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def unbind_from_mousewheel(event) -> None:
            canvas.unbind_all("<MouseWheel>")

        canvas.bind('<Enter>', bind_to_mousewheel)
        canvas.bind('<Leave>', unbind_from_mousewheel)

        # Form alanları
        fields = {}

        # Kullanıcı adı
        tk.Label(form_frame, text=self.lm.tr("lbl_username", "Kullanıcı Adı:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(5, 0))
        fields['username'] = tk.Entry(form_frame, font=('Segoe UI', 10), width=40, relief='solid', bd=1)
        fields['username'].pack(pady=(0, 10))

        # E-posta
        tk.Label(form_frame, text=self.lm.tr("lbl_email", "E-posta:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(5, 0))
        fields['email'] = tk.Entry(form_frame, font=('Segoe UI', 10), width=40, relief='solid', bd=1)
        fields['email'].pack(pady=(0, 10))

        # Şifre
        tk.Label(form_frame, text=self.lm.tr("lbl_password", "Şifre:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(5, 0))
        pw_row = tk.Frame(form_frame, bg='white')
        pw_row.pack(fill='x')
        fields['password'] = tk.Entry(pw_row, font=('Segoe UI', 10), width=32, show='*', relief='solid', bd=1)
        fields['password'].pack(side='left', pady=(0, 10))
        def _generate_password() -> None:
            try:
                pwd = generate_temp_password(14)
                fields['password'].delete(0, tk.END)
                fields['password'].insert(0, pwd)
                form_window.clipboard_clear()
                form_window.clipboard_append(pwd)
                messagebox.showinfo(self.lm.tr("title_password_generated", "Şifre Oluşturuldu"), self.lm.tr("msg_password_generated", "Güçlü şifre oluşturuldu ve panoya kopyalandı."))
            except Exception as e:
                messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('msg_password_generation_error', 'Şifre oluşturma hatası:')} {e}")
        ttk.Button(pw_row, text=self.lm.tr("btn_generate_password", " Şifre Oluştur"), style='Menu.TButton', command=_generate_password).pack(side='left', padx=(8, 0))

        # Ad
        tk.Label(form_frame, text=self.lm.tr("lbl_first_name", "Ad:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(5, 0))
        fields['first_name'] = tk.Entry(form_frame, font=('Segoe UI', 10), width=40, relief='solid', bd=1)
        fields['first_name'].pack(pady=(0, 10))

        # Soyad
        tk.Label(form_frame, text=self.lm.tr("lbl_last_name", "Soyad:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(5, 0))
        fields['last_name'] = tk.Entry(form_frame, font=('Segoe UI', 10), width=40, relief='solid', bd=1)
        fields['last_name'].pack(pady=(0, 10))

        # Telefon
        tk.Label(form_frame, text=self.lm.tr("lbl_phone", "Telefon:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(5, 0))
        fields['phone'] = tk.Entry(form_frame, font=('Segoe UI', 10), width=40, relief='solid', bd=1)
        fields['phone'].pack(pady=(0, 10))
        # Odak kaybında telefon biçimlendirme
        def _format_phone_field(_=None) -> None:
            try:
                val = fields['phone'].get().strip()
                if val:
                    fields['phone'].delete(0, tk.END)
                    fields['phone'].insert(0, format_tr_phone(val))
            except Exception as e:
                logging.error(f'Silent error in user_management_gui.py: {str(e)}')
        try:
            fields['phone'].bind('<FocusOut>', _format_phone_field)
        except Exception as e:
            logging.error(f'Silent error in user_management_gui.py: {str(e)}')

        # Departman - Combo Box
        ttk.Label(form_frame, text=self.lm.tr("lbl_department", "Departman:")).pack(anchor='w', pady=(5, 0))
        department_combo = ttk.Combobox(form_frame, font=('Segoe UI', 10), width=37, state='readonly')
        department_combo.pack(pady=(0, 10))

        # Departman listesini yükle
        try:
            departments = self.user_manager.get_departments()
            dept_names = [dept['name'] for dept in departments if dept.get('name')]
            department_combo['values'] = dept_names
            if dept_names:
                department_combo.set(dept_names[0])
        except Exception as e:
            logging.error(f"Departmanlar yüklenirken hata: {e}")
            department_combo['values'] = ['Genel Müdürlük', 'İnsan Kaynakları', 'Bilgi İşlem']

        # Pozisyon
        tk.Label(form_frame, text=self.lm.tr("lbl_position", "Pozisyon:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(5, 0))
        fields['position'] = tk.Entry(form_frame, font=('Segoe UI', 10), width=40, relief='solid', bd=1)
        fields['position'].pack(pady=(0, 10))

        # Durum
        status_frame = tk.Frame(form_frame, bg='white')
        status_frame.pack(fill='x', pady=(10, 30))
        ttk.Label(status_frame, text=self.lm.tr("lbl_status", "Durum:")).pack(side='left')
        is_active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(status_frame, variable=is_active_var).pack(side='left', padx=(10, 5))
        ttk.Label(status_frame, text=self.lm.tr("lbl_active", "Aktif")).pack(side='left')

        # Butonlar - Form frame'in altında ortada
        button_frame = tk.Frame(form_frame, bg='white')
        button_frame.pack(fill='x', pady=(20, 10))

        original_user = None
        def save_user() -> None:
            try:
                # Form verilerini topla
                user_data = {
                    'username': fields['username'].get(),
                    'email': fields['email'].get(),
                    'password': fields['password'].get(),
                    'first_name': fields['first_name'].get(),
                    'last_name': fields['last_name'].get(),
                    'phone': fields['phone'].get(),
                    'department': department_combo.get(),
                    'position': fields['position'].get(),
                    'is_active': is_active_var.get()
                }

                # Telefonu standart biçime getir ve doğrula
                if user_data['phone']:
                    user_data['phone'] = format_tr_phone(str(user_data['phone']))
                    if not is_valid_tr_phone(str(user_data['phone'])):
                        messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_invalid_phone_format", "Geçersiz telefon formatı. Örnek: +90 (5XX) XXX XX XX"))
                        return

                is_edit_mode = bool(user_id)
                if not is_edit_mode:
                    if not user_data['username'] or not user_data['email'] or not user_data['first_name'] or not user_data['last_name']:
                        messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_fill_all_required_fields", "Lütfen tüm zorunlu alanları doldurun."))
                        return

                # Şifre kontrolü (yeni kullanıcı için)
                if not user_id and not user_data['password']:
                    user_data['password'] = generate_temp_password(14)

                # Şifre politikası doğrulaması
                if user_data['password']:
                    pwd = str(user_data['password'])
                    specials = "!@#$%^&*"
                    if (
                        len(pwd) < 12 or
                        not any(c.isupper() for c in pwd) or
                        not any(c.islower() for c in pwd) or
                        not any(c.isdigit() for c in pwd) or
                        not any(c in specials for c in pwd)
                    ):
                        messagebox.showwarning(
                            self.lm.tr("title_warning", "Uyarı"),
                            self.lm.tr("msg_password_policy_auto_fix", "Şifre politikası kriterleri karşılanmıyor. Otomatik güçlü şifre üretildi ve kullanılacak.")
                        )
                        user_data['password'] = generate_temp_password(14)

                if user_id:
                    changed_payload = {}
                    if original_user:
                        for k in ['username', 'email', 'first_name', 'last_name', 'phone', 'department', 'position', 'is_active']:
                            if k in user_data:
                                if str(user_data[k]) != str(original_user.get(k, '')):
                                    changed_payload[k] = user_data[k]
                    else:
                        for k in ['username', 'email', 'first_name', 'last_name', 'phone', 'department', 'position', 'is_active']:
                            if k in user_data:
                                changed_payload[k] = user_data[k]

                    if user_data.get('password'):
                        changed_payload['password'] = user_data['password']

                    if not changed_payload:
                        messagebox.showinfo(self.lm.tr("title_info", "Bilgi"), self.lm.tr("msg_no_changes_found", "Değişiklik bulunamadı."))
                        form_window.destroy()
                        self.refresh_users()
                        return

                    success = self.user_manager.update_user(user_id, changed_payload, self.current_user_id)

                    if success:
                        messagebox.showinfo(self.lm.tr("title_success", "Başarılı"), self.lm.tr("msg_user_updated_success", "Kullanıcı başarıyla güncellendi."))
                    else:
                        messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_user_update_failed", "Kullanıcı güncellenemedi."))
                else:
                    # Yeni kullanıcı
                    new_user_id = self.user_manager.create_user(user_data, self.current_user_id)
                    if new_user_id > 0:
                        messagebox.showinfo(self.lm.tr("title_success", "Başarılı"), self.lm.tr("msg_user_created_success", "Kullanıcı başarıyla oluşturuldu."))
                    else:
                        messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_user_creation_failed", "Kullanıcı oluşturulamadı."))

                form_window.destroy()
                self.refresh_users()

            except Exception as e:
                messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('msg_user_save_error', 'Kullanıcı kaydedilirken hata oluştu:')} {e}")

        # Butonları ortaya al
        center_frame = tk.Frame(button_frame, bg='white')
        center_frame.pack(expand=True)

        ttk.Button(center_frame, text=self.lm.tr("btn_save", " Kaydet"), style='Primary.TButton', command=save_user).pack(side='left', padx=(0, 15))

        ttk.Button(center_frame, text=self.lm.tr("btn_cancel", " İptal"), style='TButton', command=form_window.destroy).pack(side='left', padx=(15, 0))

        if user_id:
            def open_security_gui() -> None:
                sec_win = tk.Toplevel(self.parent)
                sec_win.title(self.lm.tr("title_advanced_security", "Gelişmiş Güvenlik - MFA"))
                AdvancedSecurityGUI(sec_win, user_id)
            ttk.Button(center_frame, text=self.lm.tr("btn_mfa_security", " MFA / Güvenlik"), style='TButton', command=open_security_gui).pack(side='left', padx=(15, 0))

        # Eğer düzenleme modundaysa, mevcut verileri yükle
        if user_id:
            try:
                user = self.user_manager.get_user(user_id)
                original_user = user
                if user:
                    fields['username'].delete(0, 'end')
                    fields['username'].insert(0, user.get('username', ''))
                    fields['email'].delete(0, 'end')
                    fields['email'].insert(0, user.get('email', ''))
                    fields['first_name'].delete(0, 'end')
                    fields['first_name'].insert(0, user.get('first_name', ''))
                    fields['last_name'].delete(0, 'end')
                    fields['last_name'].insert(0, user.get('last_name', ''))
                    fields['phone'].delete(0, 'end')
                    try:
                        fields['phone'].insert(0, format_tr_phone(user.get('phone', '')))
                    except Exception:
                        fields['phone'].insert(0, user.get('phone', ''))
                    # Departman combo box için
                    dept_name = user.get('department', '')
                    if dept_name:
                        try:
                            # Combo box'ta bu departman varsa seç
                            current_values = department_combo['values']
                            if dept_name in current_values:
                                department_combo.set(dept_name)
                        except Exception as e:
                            logging.error(f"Departman seçimi hatası: {e}")
                    fields['position'].delete(0, 'end')
                    fields['position'].insert(0, user.get('position', ''))
                    is_active_var.set(user.get('is_active', True))
            except Exception as e:
                logging.error(f"Kullanıcı verileri yüklenirken hata: {e}")

    def create_role(self) -> None:
        self.show_role_form()

    def edit_role(self) -> None:
        selection = self.role_tree.selection()
        if not selection:
            messagebox.showwarning(self.lm.tr("title_warning", "Uyarı"), self.lm.tr("msg_select_role_to_edit", "Lütfen düzenlemek istediğiniz rolü seçin."))
            return
        item = selection[0]
        tags = self.role_tree.item(item, 'tags')
        if not tags:
            messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_role_id_not_found", "Rol ID bulunamadı."))
            return
        role_id = int(tags[0])
        self.show_role_form(role_id)

    def show_role_form(self, role_id: Optional[int] = None) -> None:
        """Rol oluştur/düzenle formu"""
        form_window = tk.Toplevel(self.parent)
        form_window.title(self.lm.tr("title_new_role", "Yeni Rol") if not role_id else self.lm.tr("title_edit_role", "Rol Düzenle"))
        form_window.geometry("900x700")
        form_window.configure(bg='white')

        tk.Label(form_window, text=(self.lm.tr("lbl_new_role", "Yeni Rol") if not role_id else self.lm.tr("lbl_edit_role", "Rol Düzenle")),
                 font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='white').pack(pady=15)

        main_container = tk.Frame(form_window, bg='white')
        main_container.pack(fill='both', expand=True, padx=15, pady=10)

        # Üst Kısım: Rol Bilgileri
        info_frame = tk.Frame(main_container, bg='white')
        info_frame.pack(fill='x', pady=(0, 10))

        # Sol: Ad ve Display Name
        tk.Label(info_frame, text=self.lm.tr("lbl_system_name", "Sistem Adı (name):"), font=('Segoe UI', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', padx=5)
        name_entry = tk.Entry(info_frame, font=('Segoe UI', 10), width=30, relief='solid', bd=1)
        name_entry.grid(row=1, column=0, sticky='w', padx=5, pady=(0, 10))

        tk.Label(info_frame, text=self.lm.tr("lbl_display_name", "Görünen Ad:"), font=('Segoe UI', 10, 'bold'), bg='white').grid(row=0, column=1, sticky='w', padx=5)
        display_entry = tk.Entry(info_frame, font=('Segoe UI', 10), width=30, relief='solid', bd=1)
        display_entry.grid(row=1, column=1, sticky='w', padx=5, pady=(0, 10))

        # Sağ: Açıklama
        tk.Label(info_frame, text=self.lm.tr("lbl_description", "Açıklama:"), font=('Segoe UI', 10, 'bold'), bg='white').grid(row=0, column=2, sticky='w', padx=5)
        desc_text = tk.Text(info_frame, font=('Segoe UI', 10), height=3, width=40, relief='solid', bd=1)
        desc_text.grid(row=1, column=2, rowspan=2, sticky='w', padx=5)

        # Durum
        flags_frame = tk.Frame(info_frame, bg='white')
        flags_frame.grid(row=2, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        is_active_var = tk.BooleanVar(value=True)
        is_system_var = tk.BooleanVar(value=False)
        tk.Checkbutton(flags_frame, text=self.lm.tr("lbl_active", "Aktif"), variable=is_active_var, bg='white').pack(side='left', padx=(0, 10))
        tk.Checkbutton(flags_frame, text=self.lm.tr("lbl_system_role", "Sistem Rolü"), variable=is_system_var, bg='white').pack(side='left')

        # Alt Kısım: Yetkiler (Scrollable & Grouped)
        tk.Label(main_container, text=self.lm.tr("lbl_permissions_select", "Yetkiler (Modül Bazlı):"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        
        perm_canvas_frame = tk.Frame(main_container, bg='white', relief='solid', bd=1)
        perm_canvas_frame.pack(fill='both', expand=True)
        
        perm_canvas = tk.Canvas(perm_canvas_frame, bg='white')
        perm_scrollbar = ttk.Scrollbar(perm_canvas_frame, orient='vertical', command=perm_canvas.yview)
        scrollable_frame = tk.Frame(perm_canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: perm_canvas.configure(scrollregion=perm_canvas.bbox("all"))
        )

        perm_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        perm_canvas.configure(yscrollcommand=perm_scrollbar.set)

        perm_canvas.pack(side="left", fill="both", expand=True)
        perm_scrollbar.pack(side="right", fill="y")

        # Fare tekerleği ile kaydırma
        def _on_mousewheel(event):
            perm_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        perm_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Pencere kapandığında bind'ı kaldır (diğer pencereleri etkilemesin)
        def _on_close():
            perm_canvas.unbind_all("<MouseWheel>")
            form_window.destroy()
        form_window.protocol("WM_DELETE_WINDOW", _on_close)

        # Yetkileri yükle ve grupla
        perm_vars = {} # {perm_id: BooleanVar}
        permissions = []
        try:
            permissions = self.user_manager.get_permissions()
            # Gruplama: module -> [permissions]
            perms_by_module = {}
            for p in permissions:
                mod = p['module']
                if mod not in perms_by_module:
                    perms_by_module[mod] = []
                perms_by_module[mod].append(p)
            
            # Arayüzü oluştur (Grid layout for modules)
            row_idx = 0
            col_idx = 0
            max_cols = 3 # 3 sütun
            
            for mod_code, perms in perms_by_module.items():
                mod_name = mod_code.upper() # Modül kodu başlık olarak
                
                # Modül çerçevesi
                mod_frame = tk.LabelFrame(scrollable_frame, text=f" {mod_name} ", font=('Segoe UI', 9, 'bold'), bg='white', fg='#2F6DB2', padx=5, pady=5)
                mod_frame.grid(row=row_idx, column=col_idx, sticky='nsew', padx=5, pady=5)
                
                for p in perms:
                    var = tk.BooleanVar()
                    perm_vars[p['id']] = var
                    # Display name'i biraz kısaltabiliriz gerekirse ama şimdilik tam gösterelim
                    chk = tk.Checkbutton(mod_frame, text=p['display_name'], variable=var, bg='white', anchor='w', wraplength=250)
                    chk.pack(fill='x', anchor='w')
                
                col_idx += 1
                if col_idx >= max_cols:
                    col_idx = 0
                    row_idx += 1

        except Exception as e:
            logging.error(f"Yetkiler yüklenirken hata: {e}")
            messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('msg_permissions_load_error', 'Yetkiler yüklenirken hata:')} {e}")

        # Düzenleme ise mevcut verileri doldur
        if role_id:
            try:
                role = self.user_manager.get_role_by_id(role_id)
                if role:
                    name_entry.insert(0, role.get('name', ''))
                    display_entry.insert(0, role.get('display_name', ''))
                    desc_text.insert('1.0', role.get('description', '') or '')
                    is_active_var.set(bool(role.get('is_active', 1)))
                    is_system_var.set(bool(role.get('is_system_role', 0)))
                
                current_perms = self.user_manager.get_role_permissions(role_id)
                current_ids = {p['id'] for p in current_perms}
                for pid, var in perm_vars.items():
                    if pid in current_ids:
                        var.set(True)
            except Exception as e:
                logging.error(f"Rol verileri yüklenirken hata: {e}")
                messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('msg_role_data_load_error', 'Rol verileri yüklenirken hata:')} {e}")

        # Kaydet/İptal
        btn_frame = tk.Frame(form_window, bg='white')
        btn_frame.pack(fill='x', pady=10, padx=15)

        def save_role() -> None:
            try:
                name = name_entry.get().strip()
                display = display_entry.get().strip() or name
                description = desc_text.get('1.0', 'end').strip()
                if not name:
                    messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_role_name_required", "Rol sistem adı (name) zorunludur."))
                    return
                
                # Seçilen izin ID'leri
                selected_perm_ids = [pid for pid, var in perm_vars.items() if var.get()]

                role_data = {
                    'name': name,
                    'display_name': display,
                    'description': description,
                    'is_system_role': is_system_var.get(),
                    'is_active': is_active_var.get(),
                    'permission_ids': selected_perm_ids,
                }
                current_user_id = self.current_user_id

                if role_id:
                    # update_role_full kullanıyoruz
                    success = self.user_manager.update_role_full(role_id, role_data, current_user_id)
                    if success:
                        messagebox.showinfo(self.lm.tr("title_success", "Başarılı"), self.lm.tr("msg_role_updated_success", "Rol başarıyla güncellendi."))
                    else:
                        messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_role_update_failed", "Rol güncellenemedi."))
                else:
                    new_role_id = self.user_manager.create_role(role_data, current_user_id)
                    if new_role_id > 0:
                        messagebox.showinfo(self.lm.tr("title_success", "Başarılı"), self.lm.tr("msg_role_created_success", "Rol başarıyla oluşturuldu."))
                    else:
                        messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_role_creation_failed", "Rol oluşturulamadı."))

                perm_canvas.unbind_all("<MouseWheel>")
                form_window.destroy()
                self.load_roles()
            except Exception as e:
                messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('msg_role_save_error', 'Rol kaydedilirken hata oluştu:')} {e}")

        ttk.Button(btn_frame, text=self.lm.tr("btn_save", " Kaydet"), style='Primary.TButton', command=save_role).pack(side='right', padx=5)
        ttk.Button(btn_frame, text=self.lm.tr("btn_cancel", " İptal"), style='TButton', command=_on_close).pack(side='right', padx=5)

    def create_department(self) -> None:
        """Yeni departman oluştur"""
        self._show_department_form()

    def edit_department(self) -> None:
        """Departman düzenle"""
        selection = self.dept_tree.selection()
        if not selection:
            messagebox.showwarning(self.lm.tr("title_warning", "Uyarı"), self.lm.tr("msg_select_department_to_edit", "Lütfen düzenlemek istediğiniz departmanı seçin."))
            return
        item = selection[0]
        tags = self.dept_tree.item(item, 'tags')
        if not tags:
            messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_department_id_not_found", "Departman ID bulunamadı."))
            return
        dept_id = int(tags[0])
        self._show_department_form(dept_id)

    def _show_department_form(self, dept_id: Optional[int] = None) -> None:
        """Departman oluştur/düzenle formu"""
        form_window = tk.Toplevel(self.parent)
        form_window.title(self.lm.tr("title_new_department", "Yeni Departman") if not dept_id else self.lm.tr("title_edit_department", "Departman Düzenle"))
        form_window.geometry("520x420")
        form_window.configure(bg='white')

        tk.Label(form_window, text=(self.lm.tr("lbl_new_department", "Yeni Departman") if not dept_id else self.lm.tr("lbl_edit_department", "Departman Düzenle")),
                 font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='white').pack(pady=15)

        container = tk.Frame(form_window, bg='white')
        container.pack(fill='both', expand=True, padx=15, pady=10)

        tk.Label(container, text=self.lm.tr("lbl_system_name", "Sistem Adı (name):"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w')
        name_entry = tk.Entry(container, font=('Segoe UI', 10), width=40, relief='solid', bd=1)
        name_entry.pack(pady=(0, 10))

        tk.Label(container, text=self.lm.tr("lbl_code", "Kod (code):"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w')
        code_entry = tk.Entry(container, font=('Segoe UI', 10), width=40, relief='solid', bd=1)
        code_entry.pack(pady=(0, 10))

        tk.Label(container, text=self.lm.tr("lbl_description", "Açıklama:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w')
        desc_text = tk.Text(container, font=('Segoe UI', 10), height=4, width=50, relief='solid', bd=1)
        desc_text.pack(pady=(0, 10))

        is_active_var = tk.BooleanVar(value=True)
        tk.Checkbutton(container, text=self.lm.tr("lbl_active", "Aktif"), variable=is_active_var, bg='white').pack(anchor='w', pady=5)

        # Düzenleme ise doldur
        if dept_id:
            try:
                dept = self.user_manager.get_department_by_id(dept_id)
                if dept:
                    name_entry.insert(0, dept.get('name', ''))
                    code_entry.insert(0, dept.get('code', '') or '')
                    desc_text.insert('1.0', dept.get('description', '') or '')
                    is_active_var.set(bool(dept.get('is_active', 1)))
            except Exception as e:
                logging.error(f"Departman verileri yüklenirken hata: {e}")
                messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('msg_department_data_load_error', 'Departman verileri yüklenirken hata:')} {e}")

        btn_frame = tk.Frame(container, bg='white')
        btn_frame.pack(fill='x', pady=10)

        def save_department() -> None:
            try:
                name = name_entry.get().strip()
                code = code_entry.get().strip()
                description = desc_text.get('1.0', 'end').strip()
                if not name:
                    messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_department_name_required", "Departman sistem adı (name) zorunludur."))
                    return
                dept_data = {
                    'name': name,
                    'code': code,
                    'display_name': name,  # display_name mevcut yapıda name ile aynı kullanılabilir
                    'description': description,
                    'is_active': is_active_var.get(),
                }
                getattr(self, 'current_user_id', None)
                if dept_id:
                    success = self.user_manager.update_department(dept_id, dept_data, int(self.current_user_id))
                    if success:
                        messagebox.showinfo(self.lm.tr("title_success", "Başarılı"), self.lm.tr("msg_department_updated_success", "Departman başarıyla güncellendi."))
                    else:
                        messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_department_update_failed", "Departman güncellenemedi."))
                else:
                    new_dept_id = self.user_manager.create_department(dept_data, int(self.current_user_id))
                    if new_dept_id > 0:
                        messagebox.showinfo(self.lm.tr("title_success", "Başarılı"), self.lm.tr("msg_department_created_success", "Departman başarıyla oluşturuldu."))
                    else:
                        messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_department_creation_failed", "Departman oluşturulamadı."))
                form_window.destroy()
                self.load_departments()
            except Exception as e:
                messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('msg_department_save_error', 'Departman kaydedilirken hata oluştu:')} {e}")

        ttk.Button(btn_frame, text=self.lm.tr("btn_save", " Kaydet"), style='Primary.TButton', command=save_department).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=self.lm.tr("btn_cancel", " İptal"), style='TButton', command=form_window.destroy).pack(side='left', padx=5)

    def filter_audit_logs(self) -> None:
        """Audit logları filtrele"""
        self.load_audit_logs()

    # === ROL YÖNETİMİ FONKSİYONLARI ===

    def load_roles(self) -> None:
        """Rolleri yükle"""
        try:
            # Treeview'ı temizle
            for item in self.role_tree.get_children():
                self.role_tree.delete(item)

            # Rolleri getir
            roles = self.user_manager.get_all_roles()

            for role in roles:
                # Kullanıcı sayısını getir
                user_count = self.user_manager.get_role_user_count(role['id'])

                # Yetki sayısını getir
                permission_count = self.user_manager.get_role_permission_count(role['id'])

                self.role_tree.insert('', 'end', values=(
                    self.lm.tr(f"role_{role['name']}", role['name']),
                    user_count,
                    permission_count,
                    role.get('description', '')
                ), tags=(str(role['id']),))

        except Exception as e:
            logging.error(f"Roller yüklenirken hata: {e}")
            messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('msg_roles_load_error', 'Roller yüklenirken hata:')} {e}")

    def on_role_select(self, event) -> None:
        """Rol seçildiğinde"""
        selection = self.role_tree.selection()
        if not selection:
            return

        item = self.role_tree.item(selection[0])
        role_id = int(item['tags'][0])

        self.selected_role_id = role_id
        self.show_role_details(role_id)

    def show_role_details(self, role_id) -> None:
        """Rol detaylarını göster"""
        try:
            # Detay panelini temizle
            for widget in self.scrollable_detail_frame.winfo_children():
                if widget != self.role_detail_label:
                    widget.destroy()

            # Rol bilgilerini getir
            role = self.user_manager.get_role_by_id(role_id)
            if not role:
                self.role_detail_label.config(text=self.lm.tr("msg_role_not_found", "Rol bulunamadı"))
                return

            # Kullanıcıları getir
            users = self.user_manager.get_role_users(role_id)

            # Yetkileri getir
            permissions = self.user_manager.get_role_permissions(role_id)

            # Detay içeriği oluştur - Daha detaylı ve düzenli
            raw_role_name = role.get('name') or role.get('role_name')
            if raw_role_name:
                role_name = self.lm.tr(f"role_{raw_role_name}", raw_role_name)
            else:
                role_name = self.lm.tr("msg_unknown", 'Bilinmeyen')

            # Ana bilgi kartı
            info_frame = tk.Frame(self.scrollable_detail_frame, bg='#ecf0f1', relief='solid', bd=1)
            info_frame.pack(fill='x', pady=(0, 10))

            # Rol adı
            name_label = tk.Label(info_frame, text=f"{self.lm.tr('lbl_role_prefix', 'Rol:')} {role_name}",
                                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='#ecf0f1')
            name_label.pack(anchor='w', padx=10, pady=(10, 5))

            # Açıklama
            desc_text = role.get('description', self.lm.tr("msg_unspecified", 'Belirtilmemiş'))
            desc_label = tk.Label(info_frame, text=f"{self.lm.tr('lbl_description_prefix', 'Açıklama:')} {desc_text}",
                                font=('Segoe UI', 10), fg='#34495e', bg='#ecf0f1', wraplength=400, justify='left')
            desc_label.pack(anchor='w', padx=10, pady=(0, 5))

            # Durum
            status = self.lm.tr("active", 'Aktif') if role.get('is_active', 1) else self.lm.tr("passive", 'Pasif')
            status_color = '#27ae60' if role.get('is_active', 1) else '#e74c3c'
            status_label = tk.Label(info_frame, text=self.lm.tr("lbl_status_with_value", "Durum: {status}").format(status=status),
                                  font=('Segoe UI', 10, 'bold'), fg=status_color, bg='#ecf0f1')
            status_label.pack(anchor='w', padx=10, pady=(0, 10))

            # İstatistikler
            stats_frame = tk.Frame(self.scrollable_detail_frame, bg='#3498db', relief='solid', bd=1)
            stats_frame.pack(fill='x', pady=(0, 10))

            stats_title = tk.Label(stats_frame, text=self.lm.tr("title_statistics", "İstatistikler"),
                                 font=('Segoe UI', 12, 'bold'), fg='white', bg='#3498db')
            stats_title.pack(anchor='w', padx=10, pady=(10, 5))

            stats_content = tk.Frame(stats_frame, bg='#3498db')
            stats_content.pack(fill='x', padx=10, pady=(0, 10))

            # Kullanıcı sayısı
            user_count_label = tk.Label(stats_content, text=self.lm.tr("lbl_user_count", "Kullanıcı Sayısı: {count}").format(count=len(users)),
                                      font=('Segoe UI', 10), fg='white', bg='#3498db')
            user_count_label.pack(side='left', padx=(0, 20))

            # Yetki sayısı
            perm_count_label = tk.Label(stats_content, text=self.lm.tr("lbl_perm_count", "Yetki Sayısı: {count}").format(count=len(permissions)),
                                      font=('Segoe UI', 10), fg='white', bg='#3498db')
            perm_count_label.pack(side='left')

            # Kullanıcılar listesi
            if users:
                users_frame = tk.Frame(self.scrollable_detail_frame, bg='#e8f5e8', relief='solid', bd=1)
                users_frame.pack(fill='x', pady=(0, 10))

                users_title = tk.Label(users_frame, text=self.lm.tr("title_users", "Kullanıcılar"),
                                     font=('Segoe UI', 12, 'bold'), fg='#27ae60', bg='#e8f5e8')
                users_title.pack(anchor='w', padx=10, pady=(10, 5))

                for i, user in enumerate(users[:10]):  # İlk 10 kullanıcı
                    user_label = tk.Label(users_frame, text=f"• {user['username']}",
                                        font=('Segoe UI', 9), fg='#2c3e50', bg='#e8f5e8')
                    user_label.pack(anchor='w', padx=20, pady=1)

                if len(users) > 10:
                    more_label = tk.Label(users_frame, text=self.lm.tr("lbl_more_users", "... ve {count} kullanıcı daha").format(count=len(users)-10),
                                        font=('Segoe UI', 9, 'italic'), fg='#7f8c8d', bg='#e8f5e8')
                    more_label.pack(anchor='w', padx=20, pady=(0, 10))
                else:
                    tk.Label(users_frame, text="", bg='#e8f5e8').pack(pady=(0, 10))

            # Yetkiler listesi
            if permissions:
                perms_frame = tk.Frame(self.scrollable_detail_frame, bg='#fff3cd', relief='solid', bd=1)
                perms_frame.pack(fill='x', pady=(0, 10))

                perms_title = tk.Label(perms_frame, text=self.lm.tr("title_permissions", "Yetkiler"),
                                     font=('Segoe UI', 12, 'bold'), fg='#f39c12', bg='#fff3cd')
                perms_title.pack(anchor='w', padx=10, pady=(10, 5))

                for i, perm in enumerate(permissions[:15]):  # İlk 15 yetki
                    perm_name = perm.get('display_name', perm.get('name', 'Bilinmeyen'))
                    perm_module = perm.get('module', 'Genel')
                    perm_label = tk.Label(perms_frame, text=f"• {perm_name} ({perm_module})",
                                        font=('Segoe UI', 9), fg='#2c3e50', bg='#fff3cd')
                    perm_label.pack(anchor='w', padx=20, pady=1)

                if len(permissions) > 15:
                    more_perms_label = tk.Label(perms_frame, text=self.lm.tr("lbl_more_perms", "... ve {count} yetki daha").format(count=len(permissions)-15),
                                              font=('Segoe UI', 9, 'italic'), fg='#7f8c8d', bg='#fff3cd')
                    more_perms_label.pack(anchor='w', padx=20, pady=(0, 10))
                else:
                    tk.Label(perms_frame, text="", bg='#fff3cd').pack(pady=(0, 10))

            # Canvas'ı güncelle
            self.detail_canvas.update_idletasks()
            self.detail_canvas.configure(scrollregion=self.detail_canvas.bbox("all"))

        except Exception as e:
            logging.error(f"Rol detayları gösterilirken hata: {e}")
            error_label = tk.Label(self.scrollable_detail_frame, text=self.lm.tr("msg_error_with_detail", "Hata: {error}").format(error=e),
                                 font=('Segoe UI', 10), fg='#e74c3c', bg='white')
            error_label.pack(expand=True)

    # duplicate definitions removed

    def delete_role(self) -> None:
        """Rol sil"""
        if not self.selected_role_id:
            messagebox.showwarning(self.lm.tr("title_warning", "Uyarı"), self.lm.tr("msg_select_role_to_delete", "Lütfen silmek için bir rol seçin."))
            return

        try:
            role = self.user_manager.get_role_by_id(self.selected_role_id)
            if not role:
                messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_role_not_found", "Rol bulunamadı."))
                return

            # Kullanıcı kontrolü
            users = self.user_manager.get_role_users(self.selected_role_id)
            if users:
                messagebox.showwarning(self.lm.tr("title_warning", "Uyarı"), self.lm.tr("msg_role_has_users", "Bu role bağlı kullanıcılar var. Önce kullanıcıların rolünü değiştirin."))
                return

            # Onay
            role_name = role.get('name') or role.get('role_name', self.lm.tr("msg_unknown", 'Bilinmeyen'))
            result = messagebox.askyesno(self.lm.tr("title_confirmation", "Onay"), self.lm.tr("msg_confirm_role_delete", "{role} rolünü silmek istediğinize emin misiniz?").format(role=role_name))
            if result:
                success = self.user_manager.delete_role(self.selected_role_id)
                if success:
                    messagebox.showinfo(self.lm.tr("title_success", "Başarılı"), self.lm.tr("msg_role_deleted_success", "Rol başarıyla silindi."))
                    self.load_roles()
                    self.selected_role_id = None
                    self.role_detail_label.config(text=self.lm.tr("msg_select_role", "Bir rol seçin"))
                else:
                    messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_role_delete_error", "Rol silinirken hata oluştu."))

        except Exception as e:
            logging.error(f"Rol silinirken hata: {e}")
            messagebox.showerror(self.lm.tr("title_error", "Hata"), self.lm.tr("msg_role_delete_error", "Rol silinirken hata: {error}").format(error=e))

    # removed duplicate show_role_form
