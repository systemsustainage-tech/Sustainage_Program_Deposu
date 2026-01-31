#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OTOMATİK RAPOR GÖNDERİMİ GUI
============================

Otomatik rapor gönderimi için kullanıcı arayüzü
"""

import logging
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict

from utils.ui_theme import apply_theme

from .automated_reporting import AutomatedReportingSystem
from utils.language_manager import LanguageManager
from config.icons import Icons


class AutomatedReportingGUI:
    """Otomatik rapor gönderimi GUI sınıfı"""

    def __init__(self, parent, company_id: int = None, db_path: str = None):
        self.lm = LanguageManager()
        self.parent = parent
        self.company_id = company_id or 1
        self.db_path = db_path or 'data/sdg_desktop.db'

        # Manager
        self.system = AutomatedReportingSystem(db_path)

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
        apply_theme(self.parent)
        # Main container
        main_frame = tk.Frame(self.parent, bg=self.theme['bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Header
        self._create_header(main_frame)

        # Toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill='x', pady=(0, 10))
        ttk.Button(toolbar, text=" Rapor Merkezi", style='Primary.TButton', command=self.open_report_center).pack(side='left', padx=6)

        # Content with notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, pady=20)

        # Tabs
        self._create_schedules_tab(notebook)
        self._create_stakeholders_tab(notebook)
        self._create_history_tab(notebook)
        self._create_settings_tab(notebook)

    def _create_header(self, parent):
        """Header oluştur"""
        header_frame = tk.Frame(parent, bg=self.theme['primary'], height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(
            header_frame,
            text=f"{Icons.REPORT} OTOMATİK RAPOR GÖNDERİMİ",
            font=('Segoe UI', 18, 'bold'),
            bg=self.theme['primary'],
            fg='white'
        )
        title_label.pack(side='left', padx=20, pady=20)

        # Test button
        ttk.Button(
            header_frame,
            text=f"{Icons.EMAIL} Test Gönder",
            style='Primary.TButton',
            command=self._test_send_report
        ).pack(side='right', padx=20, pady=20)

    def _create_schedules_tab(self, notebook):
        """Zamanlamalar sekmesi"""
        schedules_frame = tk.Frame(notebook, bg=self.theme['bg'])
        notebook.add(schedules_frame, text=f"{Icons.TIME} Zamanlamalar")

        # Header
        header_frame = tk.Frame(schedules_frame, bg=self.theme['bg'])
        header_frame.pack(fill='x', pady=10)

        tk.Label(
            header_frame,
            text="Rapor Zamanlamaları",
            font=('Segoe UI', 14, 'bold'),
            bg=self.theme['bg'],
            fg=self.theme['text']
        ).pack(side='left')

        # Add schedule button
        ttk.Button(
            header_frame,
            text=" Yeni Zamanlama",
            style='Primary.TButton',
            command=self._add_schedule
        ).pack(side='right')

        # Schedules list
        self.schedules_frame = tk.Frame(schedules_frame, bg=self.theme['bg'])
        self.schedules_frame.pack(fill='both', expand=True, pady=10)

        # Load initial data
        self._load_schedules()

    def _create_stakeholders_tab(self, notebook):
        """Paydaşlar sekmesi"""
        stakeholders_frame = tk.Frame(notebook, bg=self.theme['bg'])
        notebook.add(stakeholders_frame, text=f"{Icons.USERS} Paydaşlar")

        # Header
        header_frame = tk.Frame(stakeholders_frame, bg=self.theme['bg'])
        header_frame.pack(fill='x', pady=10)

        tk.Label(
            header_frame,
            text="Paydaş Yönetimi",
            font=('Segoe UI', 14, 'bold'),
            bg=self.theme['bg'],
            fg=self.theme['text']
        ).pack(side='left')

        # Add stakeholder button
        ttk.Button(
            header_frame,
            text=f"{Icons.ADD} Yeni Paydaş",
            style='Primary.TButton',
            command=self._add_stakeholder
        ).pack(side='right')

        # Stakeholders list
        self.stakeholders_frame = tk.Frame(stakeholders_frame, bg=self.theme['bg'])
        self.stakeholders_frame.pack(fill='both', expand=True, pady=10)

        # Load initial data
        self._load_stakeholders()

    def _create_history_tab(self, notebook):
        """Geçmiş sekmesi"""
        history_frame = tk.Frame(notebook, bg=self.theme['bg'])
        notebook.add(history_frame, text=f"{Icons.TIME} Geçmiş")

        # Header
        header_frame = tk.Frame(history_frame, bg=self.theme['bg'])
        header_frame.pack(fill='x', pady=10)

        tk.Label(
            header_frame,
            text="Gönderim Geçmişi",
            font=('Segoe UI', 14, 'bold'),
            bg=self.theme['bg'],
            fg=self.theme['text']
        ).pack(side='left')

        # Refresh button
        ttk.Button(
            header_frame,
            text=f"{Icons.LOADING} Yenile",
            style='Primary.TButton',
            command=self._refresh_history
        ).pack(side='right')

        # History list
        self.history_frame = tk.Frame(history_frame, bg=self.theme['bg'])
        self.history_frame.pack(fill='both', expand=True, pady=10)

        # Load initial data
        self._load_history()

    def _create_settings_tab(self, notebook):
        """Ayarlar sekmesi"""
        settings_frame = tk.Frame(notebook, bg=self.theme['bg'])
        notebook.add(settings_frame, text=f"{Icons.SETTINGS} Ayarlar")

        # Header
        header_frame = tk.Frame(settings_frame, bg=self.theme['bg'])
        header_frame.pack(fill='x', pady=10)

        tk.Label(
            header_frame,
            text="SMTP Ayarları",
            font=('Segoe UI', 14, 'bold'),
            bg=self.theme['bg'],
            fg=self.theme['text']
        ).pack(side='left')

        # Settings content
        self.settings_frame = tk.Frame(settings_frame, bg=self.theme['bg'])
        self.settings_frame.pack(fill='both', expand=True, pady=10)

        # Load initial data
        self._load_settings()

    def _load_schedules(self):
        """Zamanlamaları yükle"""
        try:
            # Clear existing widgets
            for widget in self.schedules_frame.winfo_children():
                widget.destroy()

            # Test verisi
            test_schedules = [
                {
                    'id': 'schedule_1',
                    'report_type': 'SDG',
                    'frequency': 'Haftalık',
                    'next_send': '2025-10-28 09:00',
                    'recipients': ['admin@company.com', 'manager@company.com'],
                    'is_active': True
                },
                {
                    'id': 'schedule_2',
                    'report_type': 'GRI',
                    'frequency': 'Aylık',
                    'next_send': '2025-11-01 10:00',
                    'recipients': ['stakeholder@company.com'],
                    'is_active': True
                },
                {
                    'id': 'schedule_3',
                    'report_type': 'Karbon',
                    'frequency': 'Çeyreklik',
                    'next_send': '2026-01-01 09:00',
                    'recipients': ['investor@company.com'],
                    'is_active': False
                }
            ]

            for schedule in test_schedules:
                self._create_schedule_card(self.schedules_frame, schedule)

        except Exception as e:
            logging.error(f"[HATA] Zamanlamalar yüklenemedi: {e}")

    def _create_schedule_card(self, parent, schedule: Dict):
        """Zamanlama kartı oluştur"""
        # Card frame
        card_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        card_frame.pack(fill='x', pady=5, padx=10)

        # Header
        header_frame = tk.Frame(card_frame, bg='white')
        header_frame.pack(fill='x', padx=15, pady=10)

        # Title
        title_label = tk.Label(
            header_frame,
            text=f" {schedule['report_type']} Raporu",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg=self.theme['text']
        )
        title_label.pack(side='left')

        # Status badge
        status_color = self.theme['success'] if schedule['is_active'] else self.theme['danger']
        status_text = 'Aktif' if schedule['is_active'] else 'Pasif'
        status_badge = tk.Label(
            header_frame,
            text=status_text,
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

        # Frequency
        tk.Label(
            content_frame,
            text=f"{Icons.TIME} Sıklık: {schedule['frequency']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(side='left', padx=(0, 20))

        # Next send
        tk.Label(
            content_frame,
            text=f" Sonraki Gönderim: {schedule['next_send']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['secondary']
        ).pack(side='left', padx=(0, 20))

        # Recipients
        recipients_text = ', '.join(schedule['recipients'])
        tk.Label(
            content_frame,
            text=f" Alıcılar: {recipients_text}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(side='left')

        # Actions
        actions_frame = tk.Frame(card_frame, bg='white')
        actions_frame.pack(fill='x', padx=15, pady=(0, 10))

        # Edit button
        ttk.Button(
            actions_frame,
            text=" Düzenle",
            style='Primary.TButton',
            command=lambda: self._edit_schedule(schedule['id'])
        ).pack(side='left', padx=(0, 5))

        # Delete button
        ttk.Button(
            actions_frame,
            text=" Sil",
            style='Accent.TButton',
            command=lambda: self._delete_schedule(schedule['id'])
        ).pack(side='left', padx=(0, 5))

        # Toggle button
        toggle_text = 'Pasifleştir' if schedule['is_active'] else 'Aktifleştir'
        ttk.Button(
            actions_frame,
            text=toggle_text,
            style='Primary.TButton',
            command=lambda: self._toggle_schedule(schedule['id'])
        ).pack(side='left')

    def _load_stakeholders(self):
        """Paydaşları yükle"""
        try:
            # Clear existing widgets
            for widget in self.stakeholders_frame.winfo_children():
                widget.destroy()

            # Test verisi
            test_stakeholders = [
                {
                    'id': 'stakeholder_1',
                    'name': 'Ahmet Yılmaz',
                    'email': 'ahmet@investor.com',
                    'role': 'Yatırımcı',
                    'report_preferences': ['SDG', 'GRI'],
                    'language': 'tr',
                    'is_active': True
                },
                {
                    'id': 'stakeholder_2',
                    'name': 'Maria Garcia',
                    'email': 'maria@supplier.com',
                    'role': 'Tedarikçi',
                    'report_preferences': ['Karbon', 'SDG'],
                    'language': 'en',
                    'is_active': True
                },
                {
                    'id': 'stakeholder_3',
                    'name': 'Fatma Demir',
                    'email': 'fatma@customer.com',
                    'role': 'Müşteri',
                    'report_preferences': ['SDG'],
                    'language': 'tr',
                    'is_active': False
                }
            ]

            for stakeholder in test_stakeholders:
                self._create_stakeholder_card(self.stakeholders_frame, stakeholder)

        except Exception as e:
            logging.error(f"[HATA] Paydaşlar yüklenemedi: {e}")

    def _create_stakeholder_card(self, parent, stakeholder: Dict):
        """Paydaş kartı oluştur"""
        # Card frame
        card_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        card_frame.pack(fill='x', pady=5, padx=10)

        # Header
        header_frame = tk.Frame(card_frame, bg='white')
        header_frame.pack(fill='x', padx=15, pady=10)

        # Name
        name_label = tk.Label(
            header_frame,
            text=f" {stakeholder['name']}",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg=self.theme['text']
        )
        name_label.pack(side='left')

        # Role badge
        role_badge = tk.Label(
            header_frame,
            text=stakeholder['role'],
            font=('Segoe UI', 9),
            bg=self.theme['secondary'],
            fg='white',
            padx=8,
            pady=2
        )
        role_badge.pack(side='right')

        # Content
        content_frame = tk.Frame(card_frame, bg='white')
        content_frame.pack(fill='x', padx=15, pady=(0, 10))

        # Email
        tk.Label(
            content_frame,
            text=f" {stakeholder['email']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(anchor='w')

        # Report preferences
        prefs_text = ', '.join(stakeholder['report_preferences'])
        tk.Label(
            content_frame,
            text=f" Rapor Tercihleri: {prefs_text}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['secondary']
        ).pack(anchor='w')

        # Language
        lang_text = 'Türkçe' if stakeholder['language'] == 'tr' else 'English'
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

        # Edit button
        ttk.Button(
            actions_frame,
            text=" Düzenle",
            style='Primary.TButton',
            command=lambda: self._edit_stakeholder(stakeholder['id'])
        ).pack(side='left', padx=(0, 5))

        # Delete button
        ttk.Button(
            actions_frame,
            text=" Sil",
            style='Accent.TButton',
            command=lambda: self._delete_stakeholder(stakeholder['id'])
        ).pack(side='left')

    def _load_history(self):
        """Geçmişi yükle"""
        try:
            # Clear existing widgets
            for widget in self.history_frame.winfo_children():
                widget.destroy()

            # Test verisi
            test_history = [
                {
                    'report_type': 'SDG',
                    'sent_at': '2025-10-21 09:00',
                    'recipients': 2,
                    'status': 'Başarılı',
                    'subject': 'SDG İlerleme Raporu - 21.10.2025'
                },
                {
                    'report_type': 'GRI',
                    'sent_at': '2025-10-20 10:00',
                    'recipients': 1,
                    'status': 'Başarılı',
                    'subject': 'GRI Raporu - 20.10.2025'
                },
                {
                    'report_type': 'Karbon',
                    'sent_at': '2025-10-19 09:30',
                    'recipients': 3,
                    'status': 'Hatalı',
                    'subject': 'Karbon Ayak İzi Raporu - 19.10.2025'
                }
            ]

            for history in test_history:
                self._create_history_card(self.history_frame, history)

        except Exception as e:
            logging.error(f"[HATA] Geçmiş yüklenemedi: {e}")

    def _create_history_card(self, parent, history: Dict):
        """Geçmiş kartı oluştur"""
        # Card frame
        card_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        card_frame.pack(fill='x', pady=5, padx=10)

        # Header
        header_frame = tk.Frame(card_frame, bg='white')
        header_frame.pack(fill='x', padx=15, pady=10)

        # Report type
        type_label = tk.Label(
            header_frame,
            text=f" {history['report_type']} Raporu",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg=self.theme['text']
        )
        type_label.pack(side='left')

        # Status badge
        status_color = self.theme['success'] if history['status'] == 'Başarılı' else self.theme['danger']
        status_badge = tk.Label(
            header_frame,
            text=history['status'],
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

        # Sent at
        tk.Label(
            content_frame,
            text=f" Gönderim: {history['sent_at']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(anchor='w')

        # Recipients
        tk.Label(
            content_frame,
            text=f" Alıcı Sayısı: {history['recipients']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['secondary']
        ).pack(anchor='w')

        # Subject
        tk.Label(
            content_frame,
            text=f" Konu: {history['subject']}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.theme['text']
        ).pack(anchor='w')

    def _load_settings(self):
        """Ayarları yükle"""
        try:
            # Clear existing widgets
            for widget in self.settings_frame.winfo_children():
                widget.destroy()

            # SMTP Settings
            settings_label = tk.Label(
                self.settings_frame,
                text="SMTP E-posta Ayarları",
                font=('Segoe UI', 12, 'bold'),
                bg=self.theme['bg'],
                fg=self.theme['text']
            )
            settings_label.pack(anchor='w', pady=10)

            # Settings form
            form_frame = tk.Frame(self.settings_frame, bg='white', relief='solid', bd=1)
            form_frame.pack(fill='x', pady=10, padx=10)

            # SMTP Server
            server_frame = tk.Frame(form_frame, bg='white')
            server_frame.pack(fill='x', padx=15, pady=10)

            tk.Label(server_frame, text="SMTP Sunucu:", bg='white').pack(side='left')
            self.smtp_server_var = tk.StringVar(value="smtp.gmail.com")
            tk.Entry(server_frame, textvariable=self.smtp_server_var, width=30).pack(side='right')

            # SMTP Port
            port_frame = tk.Frame(form_frame, bg='white')
            port_frame.pack(fill='x', padx=15, pady=10)

            tk.Label(port_frame, text="Port:", bg='white').pack(side='left')
            self.smtp_port_var = tk.StringVar(value="587")
            tk.Entry(port_frame, textvariable=self.smtp_port_var, width=30).pack(side='right')

            # Username
            user_frame = tk.Frame(form_frame, bg='white')
            user_frame.pack(fill='x', padx=15, pady=10)

            tk.Label(user_frame, text="Kullanıcı Adı:", bg='white').pack(side='left')
            self.smtp_user_var = tk.StringVar(value="")
            tk.Entry(user_frame, textvariable=self.smtp_user_var, width=30).pack(side='right')

            # Password
            pass_frame = tk.Frame(form_frame, bg='white')
            pass_frame.pack(fill='x', padx=15, pady=10)

            tk.Label(pass_frame, text="Şifre:", bg='white').pack(side='left')
            self.smtp_pass_var = tk.StringVar(value="")
            tk.Entry(pass_frame, textvariable=self.smtp_pass_var, show="*", width=30).pack(side='right')

            # From Email
            from_frame = tk.Frame(form_frame, bg='white')
            from_frame.pack(fill='x', padx=15, pady=10)

            tk.Label(from_frame, text="Gönderen E-posta:", bg='white').pack(side='left')
            self.smtp_from_var = tk.StringVar(value="")
            tk.Entry(from_frame, textvariable=self.smtp_from_var, width=30).pack(side='right')

            # Save button
            ttk.Button(
                form_frame,
                text=" Ayarları Kaydet",
                style='Primary.TButton',
                command=self._save_settings
            ).pack(pady=15)

        except Exception as e:
            logging.error(f"[HATA] Ayarlar yüklenemedi: {e}")

    def _add_schedule(self):
        """Yeni zamanlama ekle"""
        dialog = ScheduleDialog(self.parent, self.company_id)
        if dialog.result:
            messagebox.showinfo("Başarılı", "Yeni zamanlama eklendi!")
            self._load_schedules()

    def _add_stakeholder(self):
        """Yeni paydaş ekle"""
        dialog = StakeholderDialog(self.parent, self.company_id)
        if dialog.result:
            messagebox.showinfo("Başarılı", "Yeni paydaş eklendi!")
            self._load_stakeholders()

    def _edit_schedule(self, schedule_id: str):
        """Zamanlamayı düzenle"""
        messagebox.showinfo("Bilgi", f"Zamanlama düzenleme: {schedule_id}")

    def _delete_schedule(self, schedule_id: str):
        """Zamanlamayı sil"""
        if messagebox.askyesno("Onay", "Bu zamanlamayı silmek istediğinizden emin misiniz?"):
            messagebox.showinfo("Başarılı", "Zamanlama silindi!")
            self._load_schedules()

    def _toggle_schedule(self, schedule_id: str):
        """Zamanlamayı aktif/pasif yap"""
        messagebox.showinfo("Başarılı", "Zamanlama durumu değiştirildi!")
        self._load_schedules()

    def _edit_stakeholder(self, stakeholder_id: str):
        """Paydaşı düzenle"""
        messagebox.showinfo("Bilgi", f"Paydaş düzenleme: {stakeholder_id}")

    def _delete_stakeholder(self, stakeholder_id: str):
        """Paydaşı sil"""
        if messagebox.askyesno("Onay", "Bu paydaşı silmek istediğinizden emin misiniz?"):
            messagebox.showinfo("Başarılı", "Paydaş silindi!")
            self._load_stakeholders()

    def _refresh_history(self):
        """Geçmişi yenile"""
        self._load_history()

    def _save_settings(self):
        """Ayarları kaydet"""
        messagebox.showinfo("Başarılı", "SMTP ayarları kaydedildi!")

    def _test_send_report(self):
        """Test raporu gönder"""
        if messagebox.askyesno("Test", "Test raporu gönderilsin mi?"):
            messagebox.showinfo("Başarılı", "Test raporu gönderildi!")
            self._load_history()

    def open_report_center(self):
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('genel')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for genel: {e}")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor Merkezi açılamadı:\n{e}")
            logging.error(f"Error opening report center: {e}")


class ScheduleDialog:
    """Zamanlama diyalogu"""

    def __init__(self, parent, company_id: int):
        self.result = None
        self.company_id = company_id

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Yeni Zamanlama")
        self.dialog.geometry("400x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_form()

    def _create_form(self):
        """Form oluştur"""
        # Main frame
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Yeni Rapor Zamanlaması",
            font=('Segoe UI', 14, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(pady=10)

        # Report type
        type_frame = tk.Frame(main_frame, bg='white')
        type_frame.pack(fill='x', pady=10)

        tk.Label(type_frame, text="Rapor Türü:", bg='white').pack(side='left')
        self.report_type_var = tk.StringVar(value="SDG")
        type_combo = ttk.Combobox(
            type_frame,
            textvariable=self.report_type_var,
            values=["SDG", "GRI", "TSRS", "Karbon", "ESRS", "TCFD"],
            width=20,
            state='readonly'
        )
        type_combo.pack(side='right')

        # Frequency
        freq_frame = tk.Frame(main_frame, bg='white')
        freq_frame.pack(fill='x', pady=10)

        tk.Label(freq_frame, text="Sıklık:", bg='white').pack(side='left')
        self.frequency_var = tk.StringVar(value="Haftalık")
        freq_combo = ttk.Combobox(
            freq_frame,
            textvariable=self.frequency_var,
            values=["Günlük", "Haftalık", "Aylık", "Çeyreklik", "Yıllık"],
            width=20,
            state='readonly'
        )
        freq_combo.pack(side='right')

        # Day of week
        dow_frame = tk.Frame(main_frame, bg='white')
        dow_frame.pack(fill='x', pady=10)

        tk.Label(dow_frame, text="Haftanın Günü:", bg='white').pack(side='left')
        self.dow_var = tk.StringVar(value="Pazartesi")
        dow_combo = ttk.Combobox(
            dow_frame,
            textvariable=self.dow_var,
            values=["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"],
            width=20,
            state='readonly'
        )
        dow_combo.pack(side='right')

        # Time
        time_frame = tk.Frame(main_frame, bg='white')
        time_frame.pack(fill='x', pady=10)

        tk.Label(time_frame, text="Saat:", bg='white').pack(side='left')
        self.hour_var = tk.StringVar(value="09")
        hour_combo = ttk.Combobox(
            time_frame,
            textvariable=self.hour_var,
            values=[f"{i:02d}" for i in range(24)],
            width=10,
            state='readonly'
        )
        hour_combo.pack(side='left', padx=(10, 5))

        tk.Label(time_frame, text="Dakika:", bg='white').pack(side='left', padx=(20, 0))
        self.minute_var = tk.StringVar(value="00")
        minute_combo = ttk.Combobox(
            time_frame,
            textvariable=self.minute_var,
            values=[f"{i:02d}" for i in range(0, 60, 15)],
            width=10,
            state='readonly'
        )
        minute_combo.pack(side='left', padx=(10, 0))

        # Recipients
        rec_frame = tk.Frame(main_frame, bg='white')
        rec_frame.pack(fill='x', pady=10)

        tk.Label(rec_frame, text="Alıcılar:", bg='white').pack(anchor='w')
        self.recipients_text = tk.Text(rec_frame, height=4, width=40)
        self.recipients_text.pack(fill='x', pady=5)
        self.recipients_text.insert('1.0', "admin@company.com\nmanager@company.com")

        # Buttons
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill='x', pady=20)

        ttk.Button(
            button_frame,
            text=self.lm.tr("btn_cancel", "İptal"),
            command=self._cancel
        ).pack(side='left')

        ttk.Button(
            button_frame,
            text=self.lm.tr("btn_save", "Kaydet"),
            style='Primary.TButton',
            command=self._save
        ).pack(side='right')

    def _save(self):
        """Kaydet"""
        self.result = {
            'report_type': self.report_type_var.get(),
            'frequency': self.frequency_var.get(),
            'day_of_week': self.dow_var.get(),
            'hour': self.hour_var.get(),
            'minute': self.minute_var.get(),
            'recipients': self.recipients_text.get('1.0', 'end-1c').strip().split('\n')
        }
        self.dialog.destroy()

    def _cancel(self):
        """İptal"""
        self.dialog.destroy()


class StakeholderDialog:
    """Paydaş diyalogu"""

    def __init__(self, parent, company_id: int):
        self.result = None
        self.company_id = company_id

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Yeni Paydaş")
        self.dialog.geometry("400x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_form()

    def _create_form(self):
        """Form oluştur"""
        # Main frame
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Yeni Paydaş",
            font=('Segoe UI', 14, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(pady=10)

        # Name
        name_frame = tk.Frame(main_frame, bg='white')
        name_frame.pack(fill='x', pady=10)

        tk.Label(name_frame, text="Ad Soyad:", bg='white').pack(side='left')
        self.name_var = tk.StringVar()
        tk.Entry(name_frame, textvariable=self.name_var, width=30).pack(side='right')

        # Email
        email_frame = tk.Frame(main_frame, bg='white')
        email_frame.pack(fill='x', pady=10)

        tk.Label(email_frame, text="E-posta:", bg='white').pack(side='left')
        self.email_var = tk.StringVar()
        tk.Entry(email_frame, textvariable=self.email_var, width=30).pack(side='right')

        # Role
        role_frame = tk.Frame(main_frame, bg='white')
        role_frame.pack(fill='x', pady=10)

        tk.Label(role_frame, text="Rol:", bg='white').pack(side='left')
        self.role_var = tk.StringVar(value="Yatırımcı")
        role_combo = ttk.Combobox(
            role_frame,
            textvariable=self.role_var,
            values=["Yatırımcı", "Müşteri", "Tedarikçi", "Çalışan", "Diğer"],
            width=20,
            state='readonly'
        )
        role_combo.pack(side='right')

        # Report preferences
        prefs_frame = tk.Frame(main_frame, bg='white')
        prefs_frame.pack(fill='x', pady=10)

        tk.Label(prefs_frame, text="Rapor Tercihleri:", bg='white').pack(anchor='w')

        self.prefs_vars = {}
        prefs = ["SDG", "GRI", "TSRS", "Karbon", "ESRS", "TCFD"]
        for pref in prefs:
            var = tk.BooleanVar()
            self.prefs_vars[pref] = var
            tk.Checkbutton(
                prefs_frame,
                text=pref,
                variable=var,
                bg='white'
            ).pack(anchor='w', padx=20)

        # Language
        lang_frame = tk.Frame(main_frame, bg='white')
        lang_frame.pack(fill='x', pady=10)

        tk.Label(lang_frame, text="Dil:", bg='white').pack(side='left')
        self.lang_var = tk.StringVar(value="tr")
        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=["tr", "en"],
            width=20,
            state='readonly'
        )
        lang_combo.pack(side='right')

        # Buttons
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill='x', pady=20)

        ttk.Button(
            button_frame,
            text=self.lm.tr("btn_cancel", "İptal"),
            command=self._cancel
        ).pack(side='left')

        ttk.Button(
            button_frame,
            text=self.lm.tr("btn_save", "Kaydet"),
            style='Primary.TButton',
            command=self._save
        ).pack(side='right')

    def _save(self):
        """Kaydet"""
        selected_prefs = [pref for pref, var in self.prefs_vars.items() if var.get()]

        self.result = {
            'name': self.name_var.get(),
            'email': self.email_var.get(),
            'role': self.role_var.get(),
            'report_preferences': selected_prefs,
            'language': self.lang_var.get()
        }
        self.dialog.destroy()

    def _cancel(self):
        """İptal"""
        self.dialog.destroy()


if __name__ == "__main__":
    # Test
    root = tk.Tk()
    root.title("Otomatik Rapor Gönderimi")
    root.geometry("1000x700")

    gui = AutomatedReportingGUI(root)
    root.mainloop()
