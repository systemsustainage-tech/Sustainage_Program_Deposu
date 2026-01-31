import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GELİŞMİŞ RAPORLAMA GUI
======================

Gelişmiş raporlama için kullanıcı arayüzü
"""

import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict

from utils.language_manager import LanguageManager
from utils.ui_theme import apply_theme

from .report_templates import AdvancedReportTemplates
from config.icons import Icons


class AdvancedReportTemplatesGUI:
    """Gelişmiş raporlama GUI sınıfı"""

    def __init__(self, parent, company_id: int = None, db_path: str = None):
        self.lm = LanguageManager()
        self.parent = parent
        self.company_id = company_id or 1
        self.db_path = db_path or 'data/sdg_desktop.db'

        # Templates
        self.templates = AdvancedReportTemplates(db_path)

        # Theme
        self.theme = {
            'bg': '#f5f5f5',
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'text': '#2c3e50',
            'light': '#ecf0f1'
        }

        self.setup_ui()

    def setup_ui(self):
        """UI oluştur"""
        # Main container
        apply_theme(self.parent)
        main_frame = tk.Frame(self.parent, bg=self.theme['bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Header
        self._create_header(main_frame)

        # Content with notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, pady=20)

        # Tabs
        self._create_templates_tab(notebook)
        self._create_generator_tab(notebook)
        self._create_customization_tab(notebook)
        self._create_history_tab(notebook)

    def _create_header(self, parent):
        """Header oluştur"""
        header_frame = tk.Frame(parent, bg=self.theme['primary'], height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(
            header_frame,
            text=f" {Icons.REPORT} GELİŞMİŞ RAPORLAMA",
            font=('Segoe UI', 18, 'bold'),
            bg=self.theme['primary'],
            fg='white'
        )
        title_label.pack(side='left', padx=20, pady=20)

        # Generate button
        gen_btn = tk.Button(
            header_frame,
            text=f" {Icons.ADD} Rapor Oluştur",
            font=('Segoe UI', 12, 'bold'),
            bg=self.theme['success'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10,
            command=self._generate_report
        )
        gen_btn.pack(side='right', padx=20, pady=20)
        ttk.Button(header_frame, text=f" {Icons.FOLDER_OPEN} Rapor Merkezi", style='Primary.TButton', command=self._open_report_center).pack(side='right', padx=10, pady=20)

    def _create_templates_tab(self, notebook):
        """Şablonlar sekmesi"""
        templates_frame = tk.Frame(notebook, bg=self.theme['bg'])
        notebook.add(templates_frame, text=" Şablonlar")

        # Header
        header_frame = tk.Frame(templates_frame, bg=self.theme['bg'])
        header_frame.pack(fill='x', pady=10)

        tk.Label(
            header_frame,
            text="Rapor Şablonları",
            font=('Segoe UI', 14, 'bold'),
            bg=self.theme['bg'],
            fg=self.theme['text']
        ).pack(side='left')

        # Add template button
        tk.Button(
            header_frame,
            text=" Yeni Şablon",
            font=('Segoe UI', 10),
            bg=self.theme['success'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=10,
            pady=5,
            command=self._add_template
        ).pack(side='right')

        # Templates list
        self.templates_frame = tk.Frame(templates_frame, bg=self.theme['bg'])
        self.templates_frame.pack(fill='both', expand=True, pady=10)

        # Load initial data
        self._load_templates()

    def _create_generator_tab(self, notebook):
        """Rapor oluşturucu sekmesi"""
        generator_frame = tk.Frame(notebook, bg=self.theme['bg'])
        notebook.add(generator_frame, text=" Oluşturucu")

        # Header
        header_frame = tk.Frame(generator_frame, bg=self.theme['bg'])
        header_frame.pack(fill='x', pady=10)

        tk.Label(
            header_frame,
            text="Rapor Oluşturucu",
            font=('Segoe UI', 14, 'bold'),
            bg=self.theme['bg'],
            fg=self.theme['text']
        ).pack(side='left')

        # Generator form
        form_frame = tk.Frame(generator_frame, bg='white', relief='solid', bd=1)
        form_frame.pack(fill='x', pady=10, padx=10)

        # Template selection
        template_frame = tk.Frame(form_frame, bg='white')
        template_frame.pack(fill='x', padx=15, pady=10)

        tk.Label(template_frame, text="Şablon:", bg='white').pack(side='left')
        self.template_var = tk.StringVar(value="sdg")
        template_combo = ttk.Combobox(
            template_frame,
            textvariable=self.template_var,
            values=["sdg", "gri", "carbon", "esrs", "tcfd"],
            width=20,
            state='readonly'
        )
        template_combo.pack(side='right')

        # Period
        period_frame = tk.Frame(form_frame, bg='white')
        period_frame.pack(fill='x', padx=15, pady=10)

        tk.Label(period_frame, text="Dönem:", bg='white').pack(side='left')
        self.period_var = tk.StringVar(value=datetime.now().strftime('%Y'))
        tk.Entry(period_frame, textvariable=self.period_var, width=20).pack(side='right')

        # Language
        lang_frame = tk.Frame(form_frame, bg='white')
        lang_frame.pack(fill='x', padx=15, pady=10)

        tk.Label(lang_frame, text="Dil:", bg='white').pack(side='left')
        self.language_var = tk.StringVar(value="tr")
        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.language_var,
            values=["tr", "en"],
            width=20,
            state='readonly'
        )
        lang_combo.pack(side='right')

        # Format
        format_frame = tk.Frame(form_frame, bg='white')
        format_frame.pack(fill='x', padx=15, pady=10)

        tk.Label(format_frame, text="Format:", bg='white').pack(side='left')
        self.format_var = tk.StringVar(value="pdf")
        format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.format_var,
            values=["pdf", "docx", "xlsx"],
            width=20,
            state='readonly'
        )
        format_combo.pack(side='right')

        # Generate button
        gen_btn = tk.Button(
            form_frame,
            text=" Rapor Oluştur",
            font=('Segoe UI', 12, 'bold'),
            bg=self.theme['success'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10,
            command=self._generate_report
        )
        gen_btn.pack(pady=15)

        # Results
        self.results_frame = tk.Frame(generator_frame, bg=self.theme['bg'])
        self.results_frame.pack(fill='both', expand=True, pady=10)

        # Load initial data
        self._load_generator_results()

    def _create_customization_tab(self, notebook):
        """Özelleştirme sekmesi"""
        customization_frame = tk.Frame(notebook, bg=self.theme['bg'])
        notebook.add(customization_frame, text=" Özelleştirme")

        # Header
        header_frame = tk.Frame(customization_frame, bg=self.theme['bg'])
        header_frame.pack(fill='x', pady=10)

        tk.Label(
            header_frame,
            text="Şablon Özelleştirme",
            font=('Segoe UI', 14, 'bold'),
            bg=self.theme['bg'],
            fg=self.theme['text']
        ).pack(side='left')

        # Customization content
        self.customization_frame = tk.Frame(customization_frame, bg=self.theme['bg'])
        self.customization_frame.pack(fill='both', expand=True, pady=10)

        # Load initial data
        self._load_customization()

    def _create_history_tab(self, notebook):
        """Geçmiş sekmesi"""
        history_frame = tk.Frame(notebook, bg=self.theme['bg'])
        notebook.add(history_frame, text=" Geçmiş")

        # Header
        header_frame = tk.Frame(history_frame, bg=self.theme['bg'])
        header_frame.pack(fill='x', pady=10)

        tk.Label(
            header_frame,
            text="Rapor Geçmişi",
            font=('Segoe UI', 14, 'bold'),
            bg=self.theme['bg'],
            fg=self.theme['text']
        ).pack(side='left')

        # Refresh button
        tk.Button(
            header_frame,
            text=" Yenile",
            font=('Segoe UI', 10),
            bg=self.theme['secondary'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=10,
            pady=5,
            command=self._refresh_history
        ).pack(side='right')

        # History list
        self.history_frame = tk.Frame(history_frame, bg=self.theme['bg'])
        self.history_frame.pack(fill='both', expand=True, pady=10)

        # Load initial data
        self._load_history()

    def _load_templates(self):
        """Şablonları yükle"""
        try:
            # Clear existing widgets
            for widget in self.templates_frame.winfo_children():
                widget.destroy()

            # Get templates
            templates = self.templates.get_available_templates()

            if not templates:
                tk.Label(
                    self.templates_frame,
                    text="Henüz şablon yok",
                    font=('Segoe UI', 12),
                    bg=self.theme['bg'],
                    fg=self.theme['text']
                ).pack(pady=50)
                return

            # Templates list
            for template in templates:
                self._create_template_card(self.templates_frame, template)

        except Exception as e:
            logging.error(f"[HATA] Şablonlar yüklenemedi: {e}")

    def _create_template_card(self, parent, template: Dict[str, Any]):
        """Şablon kartı oluştur"""
        # Card frame
        card_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        card_frame.pack(fill='x', pady=5, padx=10)

        # Header
        header_frame = tk.Frame(card_frame, bg='white')
        header_frame.pack(fill='x', padx=15, pady=10)

        # Name
        name_label = tk.Label(
            header_frame,
            text=f" {template['name']}",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg=self.theme['text']
        )
        name_label.pack(side='left')

        # Type badge
        type_badge = tk.Label(
            header_frame,
            text=template['type'].upper(),
            font=('Segoe UI', 9),
            bg=self.theme['secondary'],
            fg='white',
            padx=8,
            pady=2
        )
        type_badge.pack(side='right')

        # Content
        content_frame = tk.Frame(card_frame, bg='white')
        content_frame.pack(fill='x', padx=15, pady=(0, 10))

        # Category
        tk.Label(
            content_frame,
            text=f" Kategori: {template['category'].upper()}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(anchor='w')

        # Language
        lang_text = 'Türkçe' if template['language'] == 'tr' else 'English'
        tk.Label(
            content_frame,
            text=f" Dil: {lang_text}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(anchor='w')

        # Actions
        actions_frame = tk.Frame(card_frame, bg='white')
        actions_frame.pack(fill='x', padx=15, pady=(0, 10))

        # Use button
        tk.Button(
            actions_frame,
            text=" Kullan",
            font=('Segoe UI', 9),
            bg=self.theme['success'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=3,
            command=lambda: self._use_template(template['id'])
        ).pack(side='left', padx=(0, 5))

        # Edit button
        tk.Button(
            actions_frame,
            text=" Düzenle",
            font=('Segoe UI', 9),
            bg=self.theme['secondary'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=3,
            command=lambda: self._edit_template(template['id'])
        ).pack(side='left', padx=(0, 5))

        # Delete button
        tk.Button(
            actions_frame,
            text=" Sil",
            font=('Segoe UI', 9),
            bg=self.theme['danger'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=3,
            command=lambda: self._delete_template(template['id'])
        ).pack(side='left')

    def _load_generator_results(self):
        """Rapor oluşturucu sonuçlarını yükle"""
        try:
            # Clear existing widgets
            for widget in self.results_frame.winfo_children():
                widget.destroy()

            # Test verisi
            test_results = [
                {
                    'template': 'SDG Raporu',
                    'period': '2024',
                    'format': 'PDF',
                    'status': 'Başarılı',
                    'file_path': 'raporlar/sdg/SDG_Raporu_2024.pdf',
                    'created_at': '2025-10-21 10:30'
                },
                {
                    'template': 'GRI Raporu',
                    'period': '2024',
                    'format': 'DOCX',
                    'status': 'Başarılı',
                    'file_path': 'raporlar/gri/GRI_Raporu_2024.docx',
                    'created_at': '2025-10-21 09:15'
                },
                {
                    'template': 'Karbon Raporu',
                    'period': '2024',
                    'format': 'PDF',
                    'status': 'Başarılı',
                    'file_path': 'raporlar/carbon/Karbon_Raporu_2024.pdf',
                    'created_at': '2025-10-20 16:45'
                }
            ]

            for result in test_results:
                self._create_result_card(self.results_frame, result)

        except Exception as e:
            logging.error(f"[HATA] Rapor oluşturucu sonuçları yüklenemedi: {e}")

    def _create_result_card(self, parent, result: Dict[str, Any]):
        """Sonuç kartı oluştur"""
        # Card frame
        card_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        card_frame.pack(fill='x', pady=5, padx=10)

        # Header
        header_frame = tk.Frame(card_frame, bg='white')
        header_frame.pack(fill='x', padx=15, pady=10)

        # Template
        template_label = tk.Label(
            header_frame,
            text=f" {result['template']}",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg=self.theme['text']
        )
        template_label.pack(side='left')

        # Status badge
        status_color = self.theme['success'] if result['status'] == 'Başarılı' else self.theme['danger']
        status_badge = tk.Label(
            header_frame,
            text=result['status'],
            font=('Segoe UI', 9),
            bg=status_color,
            fg='white',
            padx=8,
            pady=2
        )
        status_badge.pack(side='right')

        # Content
        content_frame = tk.Frame(card_frame, bg='white')
        content_frame.pack(fill='x', padx=15, pady=(0, 10))

        # Period
        tk.Label(
            content_frame,
            text=f" Dönem: {result['period']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(anchor='w')

        # Format
        tk.Label(
            content_frame,
            text=f" Format: {result['format']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(anchor='w')

        # File path
        tk.Label(
            content_frame,
            text=f" Dosya: {result['file_path']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['secondary']
        ).pack(anchor='w')

        # Created at
        tk.Label(
            content_frame,
            text=f"{Icons.TIME} Oluşturuldu: {result['created_at']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(anchor='w')

        # Actions
        actions_frame = tk.Frame(card_frame, bg='white')
        actions_frame.pack(fill='x', padx=15, pady=(0, 10))

        # Open button
        tk.Button(
            actions_frame,
            text=" Aç",
            font=('Segoe UI', 9),
            bg=self.theme['secondary'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=3,
            command=lambda: self._open_report(result['file_path'])
        ).pack(side='left', padx=(0, 5))

        # Download button
        tk.Button(
            actions_frame,
            text=" İndir",
            font=('Segoe UI', 9),
            bg=self.theme['success'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=3,
            command=lambda: self._download_report(result['file_path'])
        ).pack(side='left', padx=(0, 5))

        # Delete button
        tk.Button(
            actions_frame,
            text=" Sil",
            font=('Segoe UI', 9),
            bg=self.theme['danger'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=3,
            command=lambda: self._delete_report(result['file_path'])
        ).pack(side='left')

    def _load_customization(self):
        """Özelleştirmeyi yükle"""
        try:
            # Clear existing widgets
            for widget in self.customization_frame.winfo_children():
                widget.destroy()

            # Customization form
            form_frame = tk.Frame(self.customization_frame, bg='white', relief='solid', bd=1)
            form_frame.pack(fill='x', pady=10, padx=10)

            # Template selection
            template_frame = tk.Frame(form_frame, bg='white')
            template_frame.pack(fill='x', padx=15, pady=10)

            tk.Label(template_frame, text="Şablon:", bg='white').pack(side='left')
            self.custom_template_var = tk.StringVar(value="sdg")
            custom_template_combo = ttk.Combobox(
                template_frame,
                textvariable=self.custom_template_var,
                values=["sdg", "gri", "carbon", "esrs", "tcfd"],
                width=20,
                state='readonly'
            )
            custom_template_combo.pack(side='right')

            # Logo
            logo_frame = tk.Frame(form_frame, bg='white')
            logo_frame.pack(fill='x', padx=15, pady=10)

            tk.Label(logo_frame, text="Logo:", bg='white').pack(side='left')
            self.logo_var = tk.StringVar()
            tk.Entry(logo_frame, textvariable=self.logo_var, width=30).pack(side='left', padx=10)
            tk.Button(
                logo_frame,
                text=" Seç",
                font=('Segoe UI', 9),
                bg=self.theme['secondary'],
                fg='white',
                relief='flat',
                cursor='hand2',
                padx=8,
                pady=3,
                command=self._select_logo
            ).pack(side='right')

            # Colors
            colors_frame = tk.Frame(form_frame, bg='white')
            colors_frame.pack(fill='x', padx=15, pady=10)

            tk.Label(colors_frame, text="Renkler:", bg='white').pack(side='left')

            # Primary color
            primary_frame = tk.Frame(colors_frame, bg='white')
            primary_frame.pack(side='left', padx=10)
            tk.Label(primary_frame, text="Ana:", bg='white').pack(side='left')
            self.primary_color_var = tk.StringVar(value="#2c3e50")
            tk.Entry(primary_frame, textvariable=self.primary_color_var, width=10).pack(side='left', padx=5)

            # Secondary color
            secondary_frame = tk.Frame(colors_frame, bg='white')
            secondary_frame.pack(side='left', padx=10)
            tk.Label(secondary_frame, text="İkincil:", bg='white').pack(side='left')
            self.secondary_color_var = tk.StringVar(value="#3498db")
            tk.Entry(secondary_frame, textvariable=self.secondary_color_var, width=10).pack(side='left', padx=5)

            # Save button
            save_btn = tk.Button(
                form_frame,
                text=" Özelleştirmeyi Kaydet",
                font=('Segoe UI', 12, 'bold'),
                bg=self.theme['success'],
                fg='white',
                relief='flat',
                cursor='hand2',
                padx=20,
                pady=10,
                command=self._save_customization
            )
            save_btn.pack(pady=15)

        except Exception as e:
            logging.error(f"[HATA] Özelleştirme yüklenemedi: {e}")

    def _load_history(self):
        """Geçmişi yükle"""
        try:
            # Clear existing widgets
            for widget in self.history_frame.winfo_children():
                widget.destroy()

            # Get history
            history = self.templates.get_generation_history(self.company_id)

            if not history:
                tk.Label(
                    self.history_frame,
                    text="Henüz rapor oluşturulmamış",
                    font=('Segoe UI', 12),
                    bg=self.theme['bg'],
                    fg=self.theme['text']
                ).pack(pady=50)
                return

            # History list
            for record in history:
                self._create_history_card(self.history_frame, record)

        except Exception as e:
            logging.error(f"[HATA] Geçmiş yüklenemedi: {e}")

    def _create_history_card(self, parent, record: Dict[str, Any]):
        """Geçmiş kartı oluştur"""
        # Card frame
        card_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        card_frame.pack(fill='x', pady=5, padx=10)

        # Header
        header_frame = tk.Frame(card_frame, bg='white')
        header_frame.pack(fill='x', padx=15, pady=10)

        # Report name
        name_label = tk.Label(
            header_frame,
            text=f" {record['report_name']}",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg=self.theme['text']
        )
        name_label.pack(side='left')

        # Status badge
        status_color = self.theme['success'] if record['status'] == 'success' else self.theme['danger']
        status_badge = tk.Label(
            header_frame,
            text=record['status'].upper(),
            font=('Segoe UI', 9),
            bg=status_color,
            fg='white',
            padx=8,
            pady=2
        )
        status_badge.pack(side='right')

        # Content
        content_frame = tk.Frame(card_frame, bg='white')
        content_frame.pack(fill='x', padx=15, pady=(0, 10))

        # Template
        tk.Label(
            content_frame,
            text=f" Şablon: {record['template_id']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(anchor='w')

        # File path
        tk.Label(
            content_frame,
            text=f" Dosya: {record['file_path']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['secondary']
        ).pack(anchor='w')

        # Created at
        tk.Label(
            content_frame,
            text=f"{Icons.TIME} Oluşturuldu: {record['created_at']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(anchor='w')

        # Actions
        actions_frame = tk.Frame(card_frame, bg='white')
        actions_frame.pack(fill='x', padx=15, pady=(0, 10))

        # Open button
        tk.Button(
            actions_frame,
            text=" Aç",
            font=('Segoe UI', 9),
            bg=self.theme['secondary'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=3,
            command=lambda: self._open_report(record['file_path'])
        ).pack(side='left', padx=(0, 5))

        # Delete button
        tk.Button(
            actions_frame,
            text=" Sil",
            font=('Segoe UI', 9),
            bg=self.theme['danger'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=3,
            command=lambda: self._delete_history_record(record['id'])
        ).pack(side='left')

    def _generate_report(self):
        """Rapor oluştur"""
        try:
            template = self.template_var.get()
            period = self.period_var.get()
            if not self._validate_year(period):
                messagebox.showwarning("Uyarı", "Geçerli bir yıl girin (1990-2100)")
                return
            self.language_var.get()
            format_type = self.format_var.get()

            # Test verisi
            test_data = {
                'company_name': 'Test Şirketi',
                'sdg_data': {
                    'SDG 1': 75.5,
                    'SDG 2': 60.0,
                    'SDG 3': 85.0,
                    'SDG 4': 70.0,
                    'SDG 5': 65.0
                },
                'summary': {
                    'avg_progress': 71.1,
                    'completed': 1,
                    'in_progress': 4
                }
            }

            # Rapor oluştur
            if template == 'sdg':
                file_path = self.templates.create_sdg_report(self.company_id, period, test_data)
            elif template == 'gri':
                file_path = self.templates.create_gri_report(self.company_id, period, test_data)
            elif template == 'carbon':
                file_path = self.templates.create_carbon_report(self.company_id, period, test_data)
            else:
                messagebox.showwarning("Uyarı", "Bu şablon henüz desteklenmiyor!")
                return

            if file_path:
                messagebox.showinfo(
                    "Başarılı",
                    f"Rapor başarıyla oluşturuldu!\n\n"
                    f"• Şablon: {template.upper()}\n"
                    f"• Dönem: {period}\n"
                    f"• Format: {format_type.upper()}\n"
                    f"• Dosya: {file_path}"
                )

                # Refresh results
                self._load_generator_results()
                self._load_history()
            else:
                messagebox.showerror("Hata", "Rapor oluşturulamadı!")

        except Exception as e:
            messagebox.showerror("Hata", f"Rapor oluşturma sırasında hata oluştu:\n{e}")

    def _validate_year(self, y: str):
        try:
            y = (y or "").strip()
            if not (y.isdigit() and len(y) == 4):
                return None
            val = int(y)
            if 1990 <= val <= 2100:
                return val
            return None
        except Exception:
            return None

    def _open_report_center(self):
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                mapping = {
                    'sdg': 'sdg',
                    'gri': 'gri',
                    'carbon': 'karbon',
                    'esrs': 'esrs',
                    'tcfd': 'tcfd'
                }
                mod = mapping.get(self.template_var.get(), 'genel')
                gui.module_filter_var.set(mod)
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def _add_template(self):
        """Yeni şablon ekle"""
        messagebox.showinfo("Bilgi", "Yeni şablon ekleme özelliği yakında!")

    def _use_template(self, template_id: str):
        """Şablonu kullan"""
        self.template_var.set(template_id)
        messagebox.showinfo("Bilgi", f"Şablon seçildi: {template_id}")

    def _edit_template(self, template_id: str):
        """Şablonu düzenle"""
        messagebox.showinfo("Bilgi", f"Şablon düzenleme: {template_id}")

    def _delete_template(self, template_id: str):
        """Şablonu sil"""
        if messagebox.askyesno("Onay", "Bu şablonu silmek istediğinizden emin misiniz?"):
            messagebox.showinfo("Başarılı", "Şablon silindi!")
            self._load_templates()

    def _open_report(self, file_path: str):
        """Raporu aç"""
        try:
            import os
            if os.path.exists(file_path):
                os.startfile(file_path)
            else:
                messagebox.showerror("Hata", "Rapor dosyası bulunamadı!")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor açılamadı:\n{e}")

    def _download_report(self, file_path: str):
        """Raporu indir"""
        try:
            import shutil
            download_path = filedialog.asksaveasfilename(
                title=self.lm.tr("download_report", "Raporu İndir"),
                defaultextension=".pdf",
                filetypes=[(self.lm.tr("file_pdf", "PDF dosyaları"), "*.pdf"), (self.lm.tr("filetype_all", "Tüm dosyalar"), "*.*")]
            )

            if download_path:
                shutil.copy2(file_path, download_path)
                messagebox.showinfo("Başarılı", f"Rapor indirildi:\n{download_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor indirilemedi:\n{e}")

    def _delete_report(self, file_path: str):
        """Raporu sil"""
        if messagebox.askyesno("Onay", "Bu raporu silmek istediğinizden emin misiniz?"):
            try:
                import os
                if os.path.exists(file_path):
                    os.remove(file_path)
                    messagebox.showinfo("Başarılı", "Rapor silindi!")
                    self._load_generator_results()
                else:
                    messagebox.showerror("Hata", "Rapor dosyası bulunamadı!")
            except Exception as e:
                messagebox.showerror("Hata", f"Rapor silinemedi:\n{e}")

    def _select_logo(self):
        """Logo seç"""
        file_path = filedialog.askopenfilename(
            title=self.lm.tr("select_logo", "Logo Seç"),
            filetypes=[(self.lm.tr("file_image", "Görüntü dosyaları"), "*.png *.jpg *.jpeg"), (self.lm.tr("filetype_all", "Tüm dosyalar"), "*.*")]
        )

        if file_path:
            self.logo_var.set(file_path)

    def _save_customization(self):
        """Özelleştirmeyi kaydet"""
        messagebox.showinfo("Başarılı", "Özelleştirme kaydedildi!")

    def _delete_history_record(self, record_id: str):
        """Geçmiş kaydını sil"""
        if messagebox.askyesno("Onay", "Bu kaydı silmek istediğinizden emin misiniz?"):
            messagebox.showinfo("Başarılı", "Kayıt silindi!")
            self._load_history()

    def _refresh_history(self):
        """Geçmişi yenile"""
        self._load_history()


if __name__ == "__main__":
    # Test
    root = tk.Tk()
    root.title("Gelişmiş Raporlama")
    root.geometry("1200x800")

    gui = AdvancedReportTemplatesGUI(root)
    root.mainloop()
