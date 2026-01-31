#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yönetim Modülü GUI - İKİ SATIR BUTON DÜZENİ
"""

import os
import sqlite3
import sys
import tkinter as tk
import logging
from tkinter import ttk

from utils.language_manager import LanguageManager
from utils.ui_theme import apply_theme
from config.icons import Icons
from config.database import DB_PATH

try:
    from utils.progress_engine import (STATUS_BLOCKED, STATUS_COMPLETED,
                                       STATUS_IN_PROGRESS, STATUS_NOT_STARTED,
                                       ProgressEngine)
except Exception as e:
    logging.warning(f"ProgressEngine not found: {e}")
    ProgressEngine = None
    STATUS_NOT_STARTED = 'not_started'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_BLOCKED = 'blocked'
    STATUS_COMPLETED = 'completed'

# Güvenli import'lar - Hata vermeden yükler
def safe_import(module_name, class_name):
    try:
        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)
    except Exception as e:
        logging.debug(f"Failed to safe_import {module_name}.{class_name}: {e}")
        return None

class YonetimGUI:
    """Yönetim Modülü Ana GUI - İKİ SATIR BUTON DÜZENİ"""

    def __init__(self, parent, current_user_id: int = 1) -> None:
        self.parent = parent
        self.current_user_id = current_user_id
        self.lm = LanguageManager()

        # Tab yönetimi için değişkenler
        self.frames = {}
        self.tab_buttons = []
        self.active_tab = None
        self.module_instances = {}
        self._tab_loaders = {}
        self._tabs_loaded = set()

        self.setup_ui()
        self.create_all_tabs()
        self.create_welcome_page()

    def _is_super_admin(self) -> bool:
        """Kullanıcının süper admin olup olmadığını kontrol et"""
        try:
            if not os.path.exists(DB_PATH):
                return False
                
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            # Check for super_admin role (role_id=1)
            # Assuming user_roles table exists and role_id 1 is super_admin
            cur.execute("""
                SELECT 1 FROM user_roles 
                WHERE user_id=? AND role_id=1
            """, (self.current_user_id,))
            has_role = cur.fetchone()
            
            # Also check username just in case
            cur.execute("SELECT username FROM users WHERE id=?", (self.current_user_id,))
            user = cur.fetchone()
            
            conn.close()
            
            if has_role:
                return True
                
            if user and user[0] == '__super__':
                return True
                
            return False
        except Exception as e:
            logging.error(f"Super admin check error: {e}")
            return False

    def _get_current_user_info(self):
        """Kullanıcı bilgilerini getir"""
        try:
            if not os.path.exists(DB_PATH):
                logging.error(f"DB not found at {DB_PATH}")
                return None
                
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE id=?", (self.current_user_id,))
            # Get columns to make a dict if needed, but tuple is fine if SuperAdminGUI handles it
            # SuperAdminGUI expects tuple index 1 to be username
            user = cur.fetchone()
            conn.close()
            
            if user is None:
                logging.warning(f"User not found for id {self.current_user_id} in {DB_PATH}")
                
            return user
        except Exception as e:
            logging.error(f"Get user info error: {e}")
            return None

    def setup_ui(self) -> None:
        apply_theme(self.parent)
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if base_dir not in sys.path:
            sys.path.append(base_dir)
        cwd_dir = os.getcwd()
        if cwd_dir not in sys.path:
            sys.path.append(cwd_dir)
        main_paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=8)
        main_paned.pack(fill='both', expand=True)
        left_panel = tk.Frame(main_paned, bg='#1e40af')
        main_paned.add(left_panel, minsize=280, width=280)
        right_panel = tk.Frame(main_paned, bg='#f5f5f5')
        main_paned.add(right_panel, minsize=400)
        button_header = tk.Frame(left_panel, bg='#1e40af', height=50)
        button_header.pack(fill='x')
        button_header.pack_propagate(False)
        tk.Label(button_header, text=f"{Icons.TOOLS} {self.lm.tr('admin_module_title', 'Yönetim Modülleri')}",
                font=('Segoe UI', 14, 'bold'), fg='white', bg='#1e40af').pack(expand=True)
        scroll_container = tk.Frame(left_panel, bg='#1e40af')
        scroll_container.pack(fill='both', expand=True, padx=5, pady=10)
        scrollbar = ttk.Scrollbar(scroll_container, orient='vertical')
        scrollbar.pack(side='right', fill='y')
        canvas = tk.Canvas(scroll_container, bg='#1e40af', highlightthickness=0,
                          yscrollcommand=scrollbar.set, width=250)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=canvas.yview)
        buttons_frame = tk.Frame(canvas, bg='#1e40af')
        canvas_window = canvas.create_window((0, 0), window=buttons_frame, anchor='nw')

        # Tab bilgileri (koşullu Super Admin)
        self.tabs_info = [
            (f"{Icons.USER} {self.lm.tr('tab_users', 'Kullanıcılar')}", "user_management_frame"),
            (self.lm.tr("tab_departments", "🏢 Departmanlar"), "department_management_frame"),
            (f"{Icons.LOCKED_KEY} {self.lm.tr('tab_permissions', 'Yetkiler')}", "user_permissions_frame"),
            (self.lm.tr("tab_company_mgmt", "🏢 Firma Yönetimi"), "company_management_frame"),
            (self.lm.tr("tab_security", "🛡️ Güvenlik"), "security_management_frame"),
            (self.lm.tr("tab_license", "📜 Lisans"), "license_management_frame"),
            (f"{Icons.SETTINGS} {self.lm.tr('tab_settings', 'Ayarlar')}", "system_settings_frame"),
            (f"{Icons.WRENCH} {self.lm.tr('tab_product_tech', 'Ürün & Teknoloji')}", "product_tech_frame"),
            (f"{Icons.SAVE} {self.lm.tr('tab_backup', 'Backup')}", "backup_frame"),
            (f"{Icons.REPORT} {self.lm.tr('tab_system_status', 'Sistem Durumu')}", "system_status_frame"),
            (f"{Icons.CLIPBOARD} {self.lm.tr('tab_documents', 'Doküman')}", "document_comparison_frame"),
            (self.lm.tr("tab_policies", "📖 Politika"), "policy_library_frame"),
            (f"{Icons.MEMO} {self.lm.tr('tab_forms', 'Formlar')}", "forms_frame"),
            (self.lm.tr("tab_data_import", "📥 Veri İçe Aktarma"), "data_import_frame"),
            (self.lm.tr("tab_file_manager", "📁 Dosya Yönetimi"), "file_manager_frame"),
            (f"{Icons.SUCCESS} {self.lm.tr('tab_validation', 'Validasyon')}", "validation_frame"),
            (f"{Icons.REPORT} {self.lm.tr('tab_issb_status', 'ISSB Durum')}", "issb_status_frame"),
            (f"{Icons.CHART_UP} {self.lm.tr('tab_progress', 'İlerleme Durumu')}", "progress_status_frame"),
        ]

        try:
            if self._is_super_admin():
                self.tabs_info.append((self.lm.tr("tab_super_admin", "👑 Super Admin"), "super_admin_frame"))
        except Exception as e:
            logging.error(f"Error checking super admin status: {e}")

        # Tab butonları oluştur - DİKEY SIRALI (external stiline yakın)
        self.tab_buttons = []
        self.active_tab = None

        for i, (tab_name, frame_name) in enumerate(self.tabs_info):
            btn_bg = '#3b82f6'
            btn = tk.Button(buttons_frame, text=tab_name,
                            font=('Segoe UI', 10, 'bold'), fg='white', bg=btn_bg,
                            relief='flat', bd=0, cursor='hand2',
                            padx=15, pady=10, width=22, anchor='w',
                            command=lambda idx=i: self.switch_tab(idx))
            btn.pack(fill='x', padx=8, pady=3)
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg='#2563eb'))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg=btn_bg))
            self.tab_buttons.append(btn)

        # Canvas scroll alanını güncelle
        def configure_canvas(event=None):
            canvas.configure(scrollregion=canvas.bbox('all'))
            # Canvas genişliğini window genişliğine eşitle
            canvas_width = canvas.winfo_width()
            canvas.itemconfig(canvas_window, width=canvas_width)

        buttons_frame.bind('<Configure>', configure_canvas)
        canvas.bind('<Configure>', configure_canvas)

        # Mouse wheel ile scroll (Windows/Mac/Linux)
        def on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception as e:
                logging.debug(f"Mousewheel error: {e}")
        def on_scroll_up(_):
            try:
                canvas.yview_scroll(-1, "units")
            except Exception as e:
                logging.debug(f"Scroll up error: {e}")
        def on_scroll_down(_):
            try:
                canvas.yview_scroll(1, "units")
            except Exception as e:
                logging.debug(f"Scroll down error: {e}")
        canvas.bind("<MouseWheel>", on_mousewheel)
        buttons_frame.bind("<MouseWheel>", on_mousewheel)
        scroll_container.bind("<MouseWheel>", on_mousewheel)
        # Linux
        canvas.bind("<Button-4>", on_scroll_up)
        canvas.bind("<Button-5>", on_scroll_down)
        buttons_frame.bind("<Button-4>", on_scroll_up)
        buttons_frame.bind("<Button-5>", on_scroll_down)
        # Basit scroll bind'ları
        canvas.bind("<MouseWheel>", on_mousewheel)
        buttons_frame.bind("<MouseWheel>", on_mousewheel)
        scroll_container.bind("<MouseWheel>", on_mousewheel)

        self.frames = {}
        self.content_area = tk.Frame(right_panel, bg='#ffffff', relief='solid', bd=2)
        self.content_area.pack(fill='both', expand=True)
        for tab_name, frame_name in self.tabs_info:
            frame = tk.Frame(self.content_area, bg='#ffffff')
            self.frames[frame_name] = frame
            setattr(self, frame_name, frame)

        # Varsayılan hoş geldin sayfası oluştur
        self.create_welcome_page()

        # Sekmeleri oluştur
        self.create_all_tabs()

        # İlk açılışta hoş geldin sayfasını göster; sekme otomatik açılmaz

    def switch_tab(self, tab_index):
        """Sekme değiştir"""
        # Önceki aktif buton rengini değiştir
        if self.active_tab is not None:
            try:
                self.tab_buttons[self.active_tab].state(['!pressed'])
            except Exception as e:
                logging.debug(f"Button state error: {e}")
        try:
            self.tab_buttons[tab_index].state(['pressed'])
        except Exception as e:
            logging.debug(f"Button press error: {e}")
        self.active_tab = tab_index



        # Tüm frame'leri gizle
        for frame in self.frames.values():
            frame.pack_forget()

        # Hoş geldin sayfasını gizle (varsa)
        for widget in self.content_area.winfo_children():
            if hasattr(widget, '_is_welcome_page'):
                widget.destroy()

        # Seçili frame'i göster - SADECE SOL PANELİ KAPLA
        selected_frame_name = self.tabs_info[tab_index][1]
        selected_frame = self.frames[selected_frame_name]
        selected_frame.pack(fill='both', expand=True, padx=10, pady=10)
        try:
            if selected_frame_name not in self._tabs_loaded:
                loader = self._tab_loaders.get(selected_frame_name)
                if callable(loader):
                    loader(selected_frame)
                self._tabs_loaded.add(selected_frame_name)
        except Exception as e:
            logging.error(f"Tab loader error: {e}")
        try:
            if selected_frame_name == 'user_management_frame':
                um = self.module_instances.get('user_management')
                if um and hasattr(um, 'refresh_users'):
                    um.refresh_users()
            elif selected_frame_name == 'department_management_frame':
                dm = self.module_instances.get('department_management')
                if dm and hasattr(dm, 'load_departments'):
                    dm.load_departments()
        except Exception as e:
            logging.error(f"Tab refresh error: {e}")
        try:
            self.content_area.update_idletasks()
        except Exception as e:
            logging.debug(f"Update idletasks error: {e}")

    def create_all_tabs(self) -> None:
        """Tüm sekmeleri oluştur"""
        try:
            def load_user_management(frame):
                GUIClass = safe_import('yonetim.kullanici_yonetimi.gui.user_management_gui', 'UserManagementGUI')
                if GUIClass:
                    self.module_instances['user_management'] = GUIClass(frame, self.current_user_id)
                else:
                    self.create_placeholder_tab(frame, f"{Icons.USER} {self.lm.tr('placeholder_user_mgmt', 'Kullanıcı Yönetimi')}")
            def load_department_management(frame):
                GUIClass = safe_import('yonetim.kullanici_yonetimi.gui.department_management_gui', 'DepartmentManagementGUI')
                if GUIClass:
                    self.module_instances['department_management'] = GUIClass(frame, self.current_user_id)
                else:
                    self.create_placeholder_tab(frame, self.lm.tr("placeholder_dept_mgmt", "🏢 Departman Yönetimi"))
            def load_company_management(frame):
                GUIClass = safe_import('yonetim.company.company_management_gui', 'CompanyManagementGUI')
                if GUIClass:
                    GUIClass(frame, self.current_user_id)
                else:
                    self.create_placeholder_tab(frame, self.lm.tr("tab_company_mgmt", "🏢 Firma Yönetimi"))
            def load_user_permissions(frame):
                GUIClass = safe_import('yonetim.kullanici_yonetimi.user_permissions_gui', 'UserPermissionsGUI')
                if GUIClass:
                    GUIClass(frame, 1)
                else:
                    self.create_placeholder_tab(frame, f"{Icons.LOCKED_KEY} {self.lm.tr('placeholder_user_perm', 'Kullanıcı Yetkilendirme')}")
            def load_security_management(frame):
                GUIClass = safe_import('yonetim.security.gui.security_management_gui', 'SecurityManagementGUI')
                if GUIClass:
                    GUIClass(frame, self.current_user_id)
                else:
                    self.create_placeholder_tab(frame, self.lm.tr("placeholder_sec_mgmt", "🛡️ Güvenlik Yönetimi"))
            def load_license_management(frame):
                GUIClass = safe_import('yonetim.licensing.gui.license_management_gui', 'LicenseManagementGUI')
                if GUIClass:
                    GUIClass(frame, self.current_user_id)
                else:
                    self.create_placeholder_tab(frame, self.lm.tr("placeholder_lic_mgmt", "📜 Lisanslama Yönetimi"))
            def load_product_tech(frame):
                GUIClass = safe_import('yonetim.product_technology.product_tech_gui', 'ProductTechGUI')
                if GUIClass:
                    GUIClass(frame, self.current_user_id)
                else:
                    self.create_placeholder_tab(frame, f"{Icons.WRENCH} {self.lm.tr('tab_product_tech', 'Ürün & Teknoloji')}")
            def load_system_settings(frame):
                GUIClass = safe_import('yonetim.system_settings.gui.system_settings_gui', 'SystemSettingsGUI')
                if GUIClass:
                    GUIClass(frame, self.current_user_id)
                else:
                    self.create_placeholder_tab(frame, f"{Icons.SETTINGS} {self.lm.tr('placeholder_sys_settings', 'Sistem Ayarları')}")
            def load_backup(frame):
                GUIClass = safe_import('yonetim.backup.backup_gui', 'BackupGUI')
                if GUIClass:
                    GUIClass(frame, self.current_user_id)
                else:
                    self.create_placeholder_tab(frame, f"{Icons.SAVE} {self.lm.tr('placeholder_backup', 'Yedekleme')}")
            def load_system_status(frame):
                GUIClass = safe_import('yonetim.system_logs.system_logs_gui', 'SystemLogsGUI')
                if GUIClass:
                    GUIClass(frame, 1)
                else:
                    self.create_placeholder_tab(frame, f"{Icons.REPORT} {self.lm.tr('placeholder_sys_status', 'Sistem Durumu')}")
            def load_document_comparison(frame):
                GUIClass = safe_import('yonetim.document_comparison.document_comparison_gui', 'DocumentComparisonGUI')
                if GUIClass:
                    GUIClass(frame, self.current_user_id)
                else:
                    self.create_placeholder_tab(frame, f"{Icons.CLIPBOARD} {self.lm.tr('placeholder_doc_comp', 'Doküman Karşılaştırma')}")
            def load_policy_library(frame):
                GUIClass = safe_import('yonetim.policy_library.policy_library_gui', 'PolicyLibraryGUI')
                if GUIClass:
                    GUIClass(frame, self.current_user_id)
                else:
                    self.create_placeholder_tab(frame, self.lm.tr("placeholder_policy_lib", "📖 Politika Kütüphanesi"))
            def load_forms(frame):
                GUIClass = safe_import('yonetim.forms.forms_gui', 'FormsGUI')
                if GUIClass:
                    GUIClass(frame, self.current_user_id)
                else:
                    self.create_placeholder_tab(frame, f"{Icons.MEMO} {self.lm.tr('placeholder_dyn_forms', 'Dinamik Formlar')}")
            def load_data_import(frame):
                GUIClass = safe_import('yonetim.data_import.data_import_gui', 'DataImportGUI')
                if GUIClass:
                    GUIClass(frame, self.current_user_id)
                else:
                    self.create_placeholder_tab(frame, self.lm.tr("placeholder_data_import", "📥 Veri İçe Aktarma"))
            def load_file_manager(frame):
                GUIClass = safe_import('yonetim.file_manager.file_manager_gui', 'FileManagerGUI')
                if GUIClass:
                    GUIClass(frame, self.current_user_id)
                else:
                    self.create_placeholder_tab(frame, self.lm.tr("placeholder_file_mgmt", "📁 Dosya Yönetimi"))
            def load_validation(frame):
                GUIClass = safe_import('yonetim.validation.validation_gui', 'ValidationGUI')
                if GUIClass:
                    GUIClass(frame, self.current_user_id)
                else:
                    self.create_placeholder_tab(frame, f"{Icons.SUCCESS} {self.lm.tr('placeholder_validation', 'Veri Validasyonu')}")
            def load_super_admin(frame):
                GUIClass = safe_import('modules.super_admin.super_admin_gui', 'SuperAdminGUI')
                if GUIClass and self._is_super_admin():
                    user_info = self._get_current_user_info()
                    GUIClass(frame, user_info, 1, DB_PATH)
                else:
                    self.create_placeholder_tab(frame, self.lm.tr("placeholder_super_admin", "👑 Super Admin"))
            def load_issb_status(frame):
                GUIClass = safe_import('yonetim.issb.issb_status_gui', 'ISSBStatusDashboardGUI')
                if GUIClass:
                    GUIClass(frame, default_company_id=1)
                else:
                    self.create_placeholder_tab(frame, f"{Icons.REPORT} {self.lm.tr('placeholder_issb_status', 'ISSB Durum Panosu')}")
            def load_progress_status(frame):
                try:
                    self._create_progress_status_tab(frame)
                except Exception as e:
                    self.create_placeholder_tab(frame, f"{Icons.CHART_UP} {self.lm.tr('placeholder_progress', 'İlerleme Durumu')}", str(e))

            self._tab_loaders['user_management_frame'] = load_user_management
            self._tab_loaders['department_management_frame'] = load_department_management
            self._tab_loaders['company_management_frame'] = load_company_management
            self._tab_loaders['user_permissions_frame'] = load_user_permissions
            self._tab_loaders['security_management_frame'] = load_security_management
            self._tab_loaders['license_management_frame'] = load_license_management
            self._tab_loaders['system_settings_frame'] = load_system_settings
            self._tab_loaders['product_tech_frame'] = load_product_tech
            self._tab_loaders['backup_frame'] = load_backup
            self._tab_loaders['system_status_frame'] = load_system_status
            self._tab_loaders['document_comparison_frame'] = load_document_comparison
            self._tab_loaders['policy_library_frame'] = load_policy_library
            self._tab_loaders['forms_frame'] = load_forms
            self._tab_loaders['data_import_frame'] = load_data_import
            self._tab_loaders['file_manager_frame'] = load_file_manager
            self._tab_loaders['validation_frame'] = load_validation
            self._tab_loaders['issb_status_frame'] = load_issb_status
            self._tab_loaders['progress_status_frame'] = load_progress_status
            
            # Check if super_admin_frame is in the tabs list (using frame_name at index 1)
            if any(t[1] == 'super_admin_frame' for t in self.tabs_info):
                self._tab_loaders['super_admin_frame'] = load_super_admin
        except Exception as e:
            logging.error(f"Create all tabs error: {e}")

    def _create_progress_status_tab(self, parent) -> None:
        """İlerleme Durumu sekmesi"""
        container = tk.Frame(parent, bg='white')
        container.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(container, text=self.lm.tr("progress_title", "İlerleme Durumu"), font=('Segoe UI', 18, 'bold'), fg='#2c3e50', bg='white').pack(pady=(0, 15))

        filters = tk.Frame(container, bg='white')
        filters.pack(fill='x', pady=(0, 10))

        tk.Label(filters, text=self.lm.tr("lbl_module", "Modül:"), bg='white').pack(side='left')
        self._progress_module_var = tk.StringVar(value=self.lm.tr("opt_all", "Tümü"))
        module_values = [self.lm.tr("opt_all", "Tümü"), 'sdg', 'gri', 'tsrs', 'report_center']
        module_combo = ttk.Combobox(filters, textvariable=self._progress_module_var, values=module_values, state='readonly', width=20)
        module_combo.pack(side='left', padx=8)

        tk.Button(filters, text=self.lm.tr("btn_refresh", " Yenile"), bg='#27ae60', fg='white', relief='flat', padx=12, command=lambda: self._refresh_progress_status()).pack(side='left', padx=6)

        # Özet kartları
        cards_frame = tk.Frame(container, bg='white')
        cards_frame.pack(fill='x', pady=10)
        self._progress_cards = {}
        for mod, title, color in [('sdg', 'SDG', '#2563eb'), ('gri', 'GRI', '#27ae60'), ('tsrs', 'TSRS', '#8e44ad'), ('report_center', self.lm.tr("card_report_center", "Rapor Merkezi"), '#6A1B9A')]:
            card = tk.Frame(cards_frame, bg=color, relief='raised', bd=1)
            card.pack(side='left', fill='x', expand=True, padx=5)
            tk.Label(card, text=title, font=('Segoe UI', 10, 'bold'), fg='white', bg=color).pack(pady=(6,0))
            val = tk.Label(card, text="%0.0", font=('Segoe UI', 14, 'bold'), fg='white', bg=color)
            val.pack(pady=(0,8))
            self._progress_cards[mod] = val

        # Detay tablo
        table_frame = tk.Frame(container, bg='white', relief='solid', bd=1)
        table_frame.pack(fill='both', expand=True)
        columns = ('module', 'step_id', 'step_title', 'status', 'updated_at')
        self._progress_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        headers = {
            'module': self.lm.tr("col_module", "Modül"),
            'step_id': self.lm.tr("col_step_id", "Adım ID"),
            'step_title': self.lm.tr("col_step_title", "Adım Başlığı"),
            'status': self.lm.tr("col_status", "Durum"),
            'updated_at': self.lm.tr("col_updated_at", "Güncelleme")
        }

        for col, text in zip(columns, [headers['module'], headers['step_id'], headers['step_title'], headers['status'], headers['updated_at']]):
            self._progress_tree.heading(col, text=text)
            self._progress_tree.column(col, width=140 if col!='step_title' else 220)
        self._progress_tree.pack(side='left', fill='both', expand=True)
        scroll = ttk.Scrollbar(table_frame, orient='vertical', command=self._progress_tree.yview)
        self._progress_tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')

        # Aksiyonlar
        actions = tk.Frame(container, bg='white')
        actions.pack(fill='x', pady=10)
        tk.Button(actions, text=self.lm.tr("btn_create_tasks", " Eksik Adımlar İçin Görev Oluştur"), bg='#f39c12', fg='white', relief='flat', padx=12, command=self._create_tasks_for_pending_steps).pack(side='left')

        # ProgressEngine
        self._pe = ProgressEngine(self._get_db_path()) if ProgressEngine else None
        self._refresh_progress_status()

    def _get_module_steps_registry(self, module_code: str):
        registries = {
            'sdg': [
                ('sdg_start', self.lm.tr("step_start", "Başlangıç")),
                ('sdg_collect', self.lm.tr("step_collect", "Veri Toplama")),
                ('sdg_validate', self.lm.tr("step_validate", "Doğrulama")),
                ('sdg_preview', self.lm.tr("step_preview", "Önizleme")),
                ('sdg_complete', self.lm.tr("step_complete", "Tamamla"))
            ],
            'report_center': [
                ('rep_start', self.lm.tr("step_start", "Başlangıç")),
                ('rep_filter', self.lm.tr("step_filter", "Filtreleri Ayarla")),
                ('rep_preview', self.lm.tr("step_preview", "Önizleme")),
                ('rep_export', self.lm.tr("step_export", "Dışa Aktarım")),
                ('rep_complete', self.lm.tr("step_complete", "Tamamla"))
            ],
            'gri': [
                ('gri_start', self.lm.tr("step_start", "Başlangıç")),
                ('gri_disclosures', self.lm.tr("step_disclosures", "Açıklamalar")),
                ('gri_materiality', self.lm.tr("step_materiality", "Materyalite")),
                ('gri_content_index', self.lm.tr("step_content_index", "İçerik İndeksi")),
                ('gri_complete', self.lm.tr("step_complete", "Tamamla"))
            ],
            'tsrs': [
                ('tsrs_start', self.lm.tr("step_start", "Başlangıç")),
                ('tsrs_requirements', self.lm.tr("step_requirements", "Gereklilikler")),
                ('tsrs_double_materiality', self.lm.tr("step_double_materiality", "Çift Önemlilik")),
                ('tsrs_reporting', self.lm.tr("step_reporting", "Raporlama")),
                ('tsrs_complete', self.lm.tr("step_complete", "Tamamla"))
            ],
            'issb': [
                ('issb_start', self.lm.tr("step_start", "Başlangıç")),
                ('issb_general', self.lm.tr("step_general", "Genel Gereklilikler")),
                ('issb_climate', self.lm.tr("step_climate", "İklim")),
                ('issb_reporting', self.lm.tr("step_reporting", "Raporlama")),
                ('issb_complete', self.lm.tr("step_complete", "Tamamla"))
            ],
        }
        return registries.get(module_code, [])

    def _refresh_progress_status(self) -> None:
        try:
            # Kartları güncelle
            for mod in self._progress_cards.keys():
                steps = self._get_module_steps_registry(mod)
                pct = 0.0
                try:
                    if self._pe and steps:
                        pct = self._pe.get_completion_percentage(company_id=1, module_code=mod, steps=steps, user_id=1)
                except Exception as e:
                    logging.error(f"Progress calc error for {mod}: {e}")
                    pct = 0.0
                self._progress_cards[mod].configure(text=f"%{int(pct)}")

            # Tabloyu temizle
            for item in self._progress_tree.get_children():
                self._progress_tree.delete(item)

            # Seçilen modüle göre yükle
            selected = (self._progress_module_var.get() or 'Tümü').strip()
            modules = ['sdg','gri','tsrs','report_center'] if selected == 'Tümü' else [selected]
            for mod in modules:
                rows = []
                try:
                    if self._pe:
                        rows = self._pe.get_module_progress(company_id=1, module_code=mod)
                except Exception as e:
                    logging.error(f"Module progress error for {mod}: {e}")
                    rows = []
                for r in rows:
                    status_text = {
                        STATUS_NOT_STARTED: 'Başlamadı',
                        STATUS_IN_PROGRESS: 'Devam Ediyor',
                        STATUS_BLOCKED: 'Bloklandı',
                        STATUS_COMPLETED: 'Tamamlandı'
                    }.get(r.get('status'), r.get('status'))
                    self._progress_tree.insert('', 'end', values=(mod, r.get('step_id'), r.get('step_title'), status_text, r.get('updated_at')))
        except Exception as e:
            logging.error(f"Refresh progress status error: {e}")

    def _create_tasks_for_pending_steps(self) -> None:
        try:
            try:
                from tasks.task_manager import TaskManager
            except Exception:
                TaskManager = None
            if not TaskManager:
                messagebox.showwarning("Uyarı", "Görev sistemi bulunamadı")
                return
            tm = TaskManager(self._get_db_path())
            created = 0
            for item in self._progress_tree.get_children():
                vals = self._progress_tree.item(item, 'values')
                mod, step_id, step_title, status_text, updated = vals
                if status_text in ('Başlamadı','Bloklandı'):
                    title = f"{mod.upper()} - {step_title} adımı için veri tamamlama"
                    description = f"Modül: {mod}, Adım: {step_id} - {step_title}. İlgili veriyi tamamlayın ve doğrulayın."
                    tm.create_task({'title': title, 'description': description, 'priority': 'Orta', 'status': 'Bekliyor', 'company_id': 1})
                    created += 1
            messagebox.showinfo("Bilgi", f"{created} görev oluşturuldu")
        except Exception as e:
            try:
                messagebox.showerror("Hata", f"Görevler oluşturulamadı: {e}")
            except Exception as log_e:
                logging.error(f"Error showing error message: {log_e}")

    def create_welcome_page(self) -> None:
        """Hoş geldin sayfası oluştur"""
        welcome_frame = tk.Frame(self.content_area, bg='#ffffff')
        welcome_frame._is_welcome_page = True  # İşaretleme
        welcome_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Büyük başlık
        title_label = tk.Label(welcome_frame, text=f"{Icons.TOOLS} {self.lm.tr('welcome_title', 'YÖNETİM MERKEZİ')}",
                              font=('Segoe UI', 24, 'bold'), fg='#2c3e50', bg='#ffffff')
        title_label.pack(pady=(50, 20))

        # Alt başlık
        subtitle_label = tk.Label(welcome_frame, text=self.lm.tr("welcome_subtitle", "Sistem yönetimi için bir modül seçin"),
                                 font=('Segoe UI', 14), fg='#7f8c8d', bg='#ffffff')
        subtitle_label.pack(pady=(0, 40))

        # Özellikler listesi
        features_frame = tk.Frame(welcome_frame, bg='#ecf0f1', relief='raised', bd=2)
        features_frame.pack(pady=20, padx=50, fill='x')

        tk.Label(features_frame, text=f"{Icons.CLIPBOARD} {self.lm.tr('available_modules', 'MEVCUT MODÜLLER')}",
                font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='#ecf0f1').pack(pady=(15, 10))

        # Modül kategorileri
        categories = [
            (f"{Icons.USERS} {self.lm.tr('cat_user_mgmt', 'Kullanıcı Yönetimi')}", self.lm.tr("desc_user_mgmt", "Kullanıcılar, Departmanlar, Yetkiler, Güvenlik")),
            (f"{Icons.WRENCH} {self.lm.tr('cat_sys_mgmt', 'Sistem Yönetimi')}", self.lm.tr("desc_sys_mgmt", "Ayarlar, Backup, Sistem Durumu, Loglar")),
            (f"{Icons.REPORT} {self.lm.tr('cat_data_mgmt', 'Veri Yönetimi')}", self.lm.tr("desc_data_mgmt", "Dokümanlar, Politikalar, Formlar, Validasyon")),
            (f"{Icons.SAVE} {self.lm.tr('cat_file_ops', 'Dosya İşlemleri')}", self.lm.tr("desc_file_ops", "Veri İçe Aktarma, Dosya Yönetimi")),
            (self.lm.tr("cat_advanced", "👑 Gelişmiş"), self.lm.tr("desc_advanced", "Ürün & Teknoloji, Super Admin"))
        ]

        for category, description in categories:
            cat_frame = tk.Frame(features_frame, bg='#ecf0f1')
            cat_frame.pack(fill='x', padx=20, pady=5)

            tk.Label(cat_frame, text=category, font=('Segoe UI', 12, 'bold'),
                    fg='#2c3e50', bg='#ecf0f1', anchor='w').pack(anchor='w')
            tk.Label(cat_frame, text=f"   {description}", font=('Segoe UI', 10),
                    fg='#7f8c8d', bg='#ecf0f1', anchor='w').pack(anchor='w', pady=(0, 5))

        tk.Label(features_frame, text="", bg='#ecf0f1').pack(pady=10)

        # Alt bilgi
        info_label = tk.Label(welcome_frame, text=self.lm.tr("welcome_info", "Sağ taraftaki menüden bir modül seçerek başlayın"),
                             font=('Segoe UI', 12, 'italic'), fg='#95a5a6', bg='#ffffff')
        info_label.pack(pady=(30, 0))

    def _is_super_admin(self) -> bool:
        """Kullanıcının süper admin olup olmadığını kontrol et"""
        try:
            if not os.path.exists(DB_PATH):
                return False
                
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            # Check for super_admin role (role_id=1)
            cur.execute("""
                SELECT 1 FROM user_roles 
                WHERE user_id=? AND role_id=1
            """, (self.current_user_id,))
            has_role = cur.fetchone()
            
            # Also check username just in case
            cur.execute("SELECT username FROM users WHERE id=?", (self.current_user_id,))
            user = cur.fetchone()
            
            conn.close()
            
            if has_role:
                return True
                
            if user and user[0] == '__super__':
                return True
                
            return False
        except Exception as e:
            logging.error(f"DEBUG: DB_PATH={DB_PATH}")
            logging.error(f"MY_SUPER_ADMIN_CHECK_ERROR: {e}")
            return False

    def create_placeholder_tab(self, frame, title, error_msg=None):
        """Placeholder sekme oluştur"""
        container = tk.Frame(frame, bg='#f5f5f5')
        container.pack(fill='both', expand=True, padx=20, pady=20)
        title_label = tk.Label(container, text=title,
                              font=('Segoe UI', 18, 'bold'), fg='#2c3e50', bg='#f5f5f5')
        title_label.pack(pady=(0, 20))
        if error_msg:
            error_frame = tk.Frame(container, bg='#e74c3c', relief='raised', bd=2)
            error_frame.pack(fill='x', pady=(0, 20))
            error_label = tk.Label(error_frame, text=f"{Icons.FAIL} {self.lm.tr('err_loading_module', 'Yükleme Hatası:\n{}')}".format(error_msg),
                                  font=('Segoe UI', 10), fg='white', bg='#e74c3c', justify='left')
            error_label.pack(padx=10, pady=10)
        content_frame = tk.Frame(container, bg='white', relief='raised', bd=1)
        content_frame.pack(fill='both', expand=True)
        scroll_bar = ttk.Scrollbar(content_frame, orient='vertical')
        scroll_bar.pack(side='right', fill='y')
        text_widget = tk.Text(content_frame, font=('Segoe UI', 11), bg='white', fg='#2c3e50',
                             relief='flat', bd=0, wrap=tk.WORD, yscrollcommand=scroll_bar.set)
        text_widget.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        scroll_bar.config(command=text_widget.yview)
        
        info_text = self.lm.tr("placeholder_module_title", "{} Modülü").format(title) + "\n\n"
        info_text += self.lm.tr("placeholder_dev_msg", "Bu modül geliştirilme aşamasında veya bağımlılıkları eksik.") + "\n\n"
        info_text += self.lm.tr("placeholder_features", "Özellikler:") + "\n"
        info_text += self.lm.tr("placeholder_feat_1", "• Modern arayüz tasarımı") + "\n"
        info_text += self.lm.tr("placeholder_feat_2", "• Kullanıcı dostu işlemler") + "\n"
        info_text += self.lm.tr("placeholder_feat_3", "• Detaylı raporlama") + "\n"
        info_text += self.lm.tr("placeholder_feat_4", "• Güvenli veri işleme") + "\n\n"
        info_text += self.lm.tr("placeholder_status_preparing", "Durum: Hazırlanıyor...") + "\n"

        text_widget.insert('1.0', info_text)
        text_widget.configure(state='disabled')
